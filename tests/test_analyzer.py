from src.analyzer import TelemetryAnalyzer

def test_generate_insights():
    # Mock ml_results
    ml_results_spaced = []
    
    # Normal
    ml_results_spaced.append({'timestamp': 1, 'lat': 0.0, 'lon': 0.0, 'actual_speed': 50.0, 'predicted_speed': 52.0, 'accel': 0.0, 'diff': 2.0})
    
    for i in range(15):
        ml_results_spaced.append({'timestamp': 1, 'lat': 0.0, 'lon': 0.0, 'actual_speed': 50.0, 'predicted_speed': 50.0, 'accel': 0.0, 'diff': 0.0})
        
    # Braking too early / too much
    ml_results_spaced.append({'timestamp': 2, 'lat': 0.1, 'lon': 0.1, 'actual_speed': 40.0, 'predicted_speed': 55.0, 'accel': -1.5, 'diff': 15.0})
    
    for i in range(15):
        ml_results_spaced.append({'timestamp': 1, 'lat': 0.0, 'lon': 0.0, 'actual_speed': 50.0, 'predicted_speed': 50.0, 'accel': 0.0, 'diff': 0.0})
        
    # Slow corner
    ml_results_spaced.append({'timestamp': 3, 'lat': 0.2, 'lon': 0.2, 'actual_speed': 30.0, 'predicted_speed': 45.0, 'accel': 0.1, 'diff': 15.0})
    
    for i in range(15):
        ml_results_spaced.append({'timestamp': 1, 'lat': 0.0, 'lon': 0.0, 'actual_speed': 50.0, 'predicted_speed': 50.0, 'accel': 0.0, 'diff': 0.0})
        
    # Late acceleration
    ml_results_spaced.append({'timestamp': 4, 'lat': 0.3, 'lon': 0.3, 'actual_speed': 60.0, 'predicted_speed': 80.0, 'accel': 0.8, 'diff': 20.0})
    
    analyzer = TelemetryAnalyzer(ml_results_spaced)
    insights = analyzer.generate_insights(diff_threshold=10.0)
    
    assert len(insights) == 3
    assert insights[0].type == "braking"
    assert insights[1].type == "cornering"
    assert insights[2].type == "acceleration"
