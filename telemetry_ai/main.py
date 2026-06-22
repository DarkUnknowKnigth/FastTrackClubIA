import os
import argparse
from src.loader import TelemetryLoader
from src.ml_model import TelemetryMLModel
from src.analyzer import TelemetryAnalyzer
from src.map_builder import MapGenerator
from src.frontend_generator import FrontendGenerator

def main():
    parser = argparse.ArgumentParser(description="Fast Track Club AI Telemetry")
    parser.add_argument('--mode', type=str, choices=['train', 'analyze'], required=True, 
                        help="Modo de ejecución: 'train' para aprender de los datos, 'analyze' para generar reporte.")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    output_dir = os.path.join(base_dir, 'output')
    templates_dir = os.path.join(base_dir, 'templates')
    model_path = os.path.join(base_dir, 'saved_model', 'telemetry_model')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(os.path.dirname(model_path)):
        os.makedirs(os.path.dirname(model_path))

    print("--- Fast Track Club AI Telemetry Analyzer ---")
    
    loader = TelemetryLoader(data_dir)
    profiles = loader.load_all_profiles()
    
    if not profiles:
        print(f"No JSON files found in {data_dir}. Please add data files.")
        return

    ml_model = TelemetryMLModel()

    if args.mode == 'train':
        print("Modo: ENTRENAMIENTO")
        ml_model.train(profiles, epochs=20, batch_size=64)
        ml_model.save(model_path)
        print("Entrenamiento finalizado. Modelo guardado con éxito.")
        
    elif args.mode == 'analyze':
        print("Modo: ANÁLISIS E INFERENCIA")
        if not ml_model.load(model_path):
            print("Error: No se encontró un modelo pre-entrenado. Ejecuta primero con '--mode train'.")
            return
            
        map_gen = MapGenerator(output_dir)
        frontend_data = []
        
        for profile in profiles:
            for session in profile.sessions:
                if not session.telemetry:
                    continue
                    
                print(f"Analyzing session {session.id} for pilot {profile.pilotName}...")
                
                # Evaluate using ML
                ml_results = ml_model.evaluate_session(session)
                
                # Generate Insights
                analyzer = TelemetryAnalyzer(ml_results)
                insights = analyzer.generate_insights(diff_threshold=8.0)
                
                # Generate Report
                report = analyzer.generate_gt3_report(session, insights)
                
                # Generate Map
                map_filename = f"map_session_{session.id}.html"
                map_gen.generate_session_map(session, insights, map_filename)
                
                # Append to frontend data
                frontend_data.append({
                    'id': session.id,
                    'pilot': profile.pilotName,
                    'distance': session.distanceMeters,
                    'maxSpeed': session.maxSpeed,
                    'map_file': map_filename,
                    'report': report
                })
                
        # Generate Frontend SPA
        print("Generating SPA...")
        frontend = FrontendGenerator(templates_dir, output_dir)
        index_path = frontend.generate_index(frontend_data)
        
        print(f"Proceso completado. Reporte disponible en: {index_path}")

if __name__ == "__main__":
    main()
