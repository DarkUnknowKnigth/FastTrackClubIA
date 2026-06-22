import numpy as np
import pandas as pd
import tensorflow as tf
from typing import List, Dict, Optional
import json
import os
from sklearn.cluster import DBSCAN
from .models import DriverProfile, Session, TelemetryPoint

class TrackModel:
    def __init__(self, track_id: int):
        self.track_id = track_id
        self.model = self._build_model()
        self.is_trained = False
        
        self.lat_min = 0.0
        self.lat_max = 1.0
        self.lon_min = 0.0
        self.lon_max = 1.0
        self.speed_max = 1.0
        
        self.centroid_lat = 0.0
        self.centroid_lon = 0.0

    def _build_model(self) -> tf.keras.Model:
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(2,)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def _normalize_features(self, lat: np.ndarray, lon: np.ndarray):
        n_lat = (lat - self.lat_min) / (self.lat_max - self.lat_min + 1e-9)
        n_lon = (lon - self.lon_min) / (self.lon_max - self.lon_min + 1e-9)
        return np.column_stack((n_lat, n_lon))

    def train(self, sessions: List[Session], epochs=20, batch_size=32):
        lats = []
        lons = []
        speeds = []
        
        for session in sessions:
            if session.rank != "A" and session.maxSpeed < 50:
                continue
            for pt in session.telemetry:
                lats.append(pt.lat)
                lons.append(pt.lon)
                speeds.append(pt.speedKmh)
                
        if not lats:
            print(f"No valid data to train Track {self.track_id}.")
            return
            
        lats = np.array(lats)
        lons = np.array(lons)
        speeds = np.array(speeds)
        
        self.lat_min, self.lat_max = lats.min(), lats.max()
        self.lon_min, self.lon_max = lons.min(), lons.max()
        self.speed_max = speeds.max() if speeds.max() > 0 else 1.0
        self.centroid_lat = float(np.mean(lats))
        self.centroid_lon = float(np.mean(lons))
        
        X = self._normalize_features(lats, lons)
        y = speeds / self.speed_max
        
        print(f"Training Track {self.track_id} on {len(X)} telemetry points...")
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        self.is_trained = True

    def evaluate(self, session: Session) -> List[Dict]:
        results = []
        if not self.is_trained or not session.telemetry:
            return results
            
        lats = np.array([pt.lat for pt in session.telemetry])
        lons = np.array([pt.lon for pt in session.telemetry])
        actual_speeds = np.array([pt.speedKmh for pt in session.telemetry])
        timestamps = [pt.timestamp for pt in session.telemetry]
        accels = [pt.accel for pt in session.telemetry]
        
        X = self._normalize_features(lats, lons)
        preds = self.model.predict(X, verbose=0)
        predicted_speeds = preds.flatten() * self.speed_max
        
        for i in range(len(session.telemetry)):
            results.append({
                'timestamp': timestamps[i],
                'lat': lats[i],
                'lon': lons[i],
                'actual_speed': actual_speeds[i],
                'predicted_speed': predicted_speeds[i],
                'accel': accels[i],
                'diff': predicted_speeds[i] - actual_speeds[i]
            })
            
        return results

    def save(self, filepath: str):
        if not self.is_trained:
            return
        self.model.save(filepath + ".keras")
        bounds = {
            'lat_min': float(self.lat_min),
            'lat_max': float(self.lat_max),
            'lon_min': float(self.lon_min),
            'lon_max': float(self.lon_max),
            'speed_max': float(self.speed_max),
            'centroid_lat': float(self.centroid_lat),
            'centroid_lon': float(self.centroid_lon)
        }
        with open(filepath + "_bounds.json", 'w') as f:
            json.dump(bounds, f)

    def load(self, filepath: str) -> bool:
        if os.path.exists(filepath + ".keras") and os.path.exists(filepath + "_bounds.json"):
            self.model = tf.keras.models.load_model(filepath + ".keras")
            with open(filepath + "_bounds.json", 'r') as f:
                bounds = json.load(f)
            self.lat_min = bounds['lat_min']
            self.lat_max = bounds['lat_max']
            self.lon_min = bounds['lon_min']
            self.lon_max = bounds['lon_max']
            self.speed_max = bounds['speed_max']
            self.centroid_lat = bounds['centroid_lat']
            self.centroid_lon = bounds['centroid_lon']
            self.is_trained = True
            return True
        return False

class TelemetryMLModel:
    def __init__(self):
        self.tracks: Dict[int, TrackModel] = {}
        
    def _get_session_centroid(self, session: Session):
        lats = [pt.lat for pt in session.telemetry]
        lons = [pt.lon for pt in session.telemetry]
        return np.mean(lats), np.mean(lons)
        
    def train(self, profiles: List[DriverProfile], epochs=20, batch_size=32):
        print("Grouping sessions by physical track location...")
        valid_sessions = []
        for profile in profiles:
            for s in profile.sessions:
                if s.telemetry:
                    valid_sessions.append(s)
                    
        if not valid_sessions:
            print("No valid sessions found.")
            return
            
        centroids = np.array([self._get_session_centroid(s) for s in valid_sessions])
        
        # eps=0.01 degrees is roughly 1km
        clustering = DBSCAN(eps=0.01, min_samples=1).fit(centroids)
        labels = clustering.labels_
        
        grouped = {}
        for session, label in zip(valid_sessions, labels):
            grouped.setdefault(label, []).append(session)
            
        print(f"Identified {len(grouped)} distinct tracks.")
        
        for track_id, track_sessions in grouped.items():
            track_id = int(track_id)
            print(f"--- Processing Track ID {track_id} ({len(track_sessions)} sessions) ---")
            tm = TrackModel(track_id)
            tm.train(track_sessions, epochs=epochs, batch_size=batch_size)
            if tm.is_trained:
                self.tracks[track_id] = tm

    def evaluate_session(self, session: Session) -> List[Dict]:
        if not self.tracks or not session.telemetry:
            return []
            
        c_lat, c_lon = self._get_session_centroid(session)
        
        closest_track = None
        min_dist = float('inf')
        for tm in self.tracks.values():
            dist = (tm.centroid_lat - c_lat)**2 + (tm.centroid_lon - c_lon)**2
            if dist < min_dist:
                min_dist = dist
                closest_track = tm
                
        if closest_track is None or min_dist > 0.005:
            # Distance too large, unknown track
            return []
            
        return closest_track.evaluate(session)
        
    def save(self, base_filepath: str):
        if not self.tracks:
            print("No tracks to save.")
            return
            
        manifest = {"track_ids": list(self.tracks.keys())}
        with open(base_filepath + "_manifest.json", 'w') as f:
            json.dump(manifest, f)
            
        for tid, tm in self.tracks.items():
            tm.save(f"{base_filepath}_track_{tid}")
        print("All track models saved.")

    def load(self, base_filepath: str) -> bool:
        if not os.path.exists(base_filepath + "_manifest.json"):
            return False
            
        with open(base_filepath + "_manifest.json", 'r') as f:
            manifest = json.load(f)
            
        self.tracks = {}
        for tid in manifest["track_ids"]:
            tm = TrackModel(tid)
            if tm.load(f"{base_filepath}_track_{tid}"):
                self.tracks[tid] = tm
                
        if self.tracks:
            print(f"Loaded models for {len(self.tracks)} tracks.")
            return True
        return False
