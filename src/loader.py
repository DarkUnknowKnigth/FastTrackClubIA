import json
import glob
import os
from typing import List
from .models import DriverProfile

class TelemetryLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_all_profiles(self) -> List[DriverProfile]:
        profiles = []
        pattern = os.path.join(self.data_dir, "*.json")
        for filepath in glob.glob(pattern):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                try:
                    profile = DriverProfile(**data)
                    profiles.append(profile)
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")
        return profiles

    def load_profile(self, filename: str) -> DriverProfile:
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return DriverProfile(**data)
