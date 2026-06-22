from typing import List, Dict
from pydantic import BaseModel

class Insight(BaseModel):
    lat: float
    lon: float
    title: str
    description: str
    type: str # e.g. "braking", "acceleration", "cornering"

class TelemetryAnalyzer:
    def __init__(self, ml_results: List[Dict]):
        self.ml_results = ml_results

    def generate_insights(self, diff_threshold=10.0) -> List[Insight]:
        """
        Analyzes the ML results (actual vs predicted) and generates insights.
        diff_threshold: minimum difference in Kmh to flag an insight.
        """
        insights = []
        
        # Add some smoothing or grouping to avoid duplicate insights in the same corner
        skip_frames = 0
        
        for i, row in enumerate(self.ml_results):
            if skip_frames > 0:
                skip_frames -= 1
                continue
                
            diff = row['diff'] # predicted - actual
            if diff > diff_threshold:
                # the model says we should go faster here
                accel = row['accel']
                speed = row['actual_speed']
                
                if accel < -1.0:
                    # Braking hard but earlier or more than the model suggests
                    insights.append(Insight(
                        lat=row['lat'],
                        lon=row['lon'],
                        title="Frenada Conservadora",
                        description=f"Frenaste más de lo necesario. La IA sugiere pasar a {row['predicted_speed']:.1f} km/h (Ibas a {speed:.1f} km/h).",
                        type="braking"
                    ))
                    skip_frames = 10 # skip next few points
                elif accel > 0.5:
                    # Accelerating but speed is too low -> late acceleration
                    insights.append(Insight(
                        lat=row['lat'],
                        lon=row['lon'],
                        title="Aceleración Tardía",
                        description=f"Retomaste el gas muy tarde. Potencial: {row['predicted_speed']:.1f} km/h.",
                        type="acceleration"
                    ))
                    skip_frames = 10
                elif abs(accel) < 0.5 and speed < 40:
                    # Slow cornering speed
                    insights.append(Insight(
                        lat=row['lat'],
                        lon=row['lon'],
                        title="Paso por curva lento",
                        description=f"Mantén más velocidad en el ápice. La trazada ideal permite {row['predicted_speed']:.1f} km/h.",
                        type="cornering"
                    ))
                    skip_frames = 10

        return insights

    def generate_gt3_report(self, session_data, insights: List[Insight]) -> str:
        # A simple string builder for the GT3 report. Will be passed to Jinja later.
        num_insights = len(insights)
        max_speed = session_data.maxSpeed
        
        report = f"""
        ### Análisis de Rendimiento GT3
        
        **Resumen de la Sesión:**
        Piloto, la telemetría indica que alcanzaste una velocidad máxima de {max_speed:.1f} km/h. 
        El análisis de la IA detectó {num_insights} áreas críticas de mejora en el trazado.
        
        **Comentarios del Ingeniero de Pista:**
        """
        
        if num_insights == 0:
            report += "Excelente vuelta, el ritmo es constante y estás maximizando la adherencia en todos los sectores.\n"
        else:
            report += "Hemos notado que estás perdiendo tiempo valioso. "
            braking = sum(1 for i in insights if i.type == 'braking')
            accel = sum(1 for i in insights if i.type == 'acceleration')
            
            if braking > 0:
                report += f"Estás siendo muy conservador en las zonas de frenada ({braking} puntos). Apura más el punto de frenado y lleva la velocidad hacia el ápice (trail braking).\n"
            if accel > 0:
                report += f"Falta agresividad a la salida de las curvas ({accel} puntos). Necesitamos que pises el acelerador antes para maximizar la velocidad en la recta.\n"
                
        report += "\nRevisa el mapa de calor y las tarjetas para ver los puntos exactos de mejora."
        return report
