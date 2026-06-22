import os
from src.loader import TelemetryLoader

def test_loader(tmp_path):
    # Create a dummy json
    dummy_json = """{
        "pilotName": "test_pilot",
        "totalDistance": 100.0,
        "level": 1,
        "vehicles": [],
        "sessions": [
            {
                "id": 1,
                "vehicleModel": "car",
                "startTime": 1000,
                "endTime": 2000,
                "maxSpeed": 50.0,
                "maxBrakingGForce": -1.0,
                "distanceMeters": 100.0,
                "rank": "A",
                "telemetry": [
                    {
                        "timestamp": 1000,
                        "lat": 0.0,
                        "lon": 0.0,
                        "speedKmh": 10.0,
                        "accel": 0.0
                    }
                ]
            }
        ]
    }"""
    
    test_file = tmp_path / "dummy.json"
    test_file.write_text(dummy_json)
    
    loader = TelemetryLoader(str(tmp_path))
    profiles = loader.load_all_profiles()
    
    assert len(profiles) == 1
    assert profiles[0].pilotName == "test_pilot"
    assert len(profiles[0].sessions) == 1
    assert profiles[0].sessions[0].telemetry[0].speedKmh == 10.0
