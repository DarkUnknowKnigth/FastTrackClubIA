from typing import List
from pydantic import BaseModel, Field

class Vehicle(BaseModel):
    model: str
    id: int

class TelemetryPoint(BaseModel):
    timestamp: int
    lat: float
    lon: float
    speedKmh: float
    accel: float

class Session(BaseModel):
    id: int
    vehicleModel: str
    startTime: int
    endTime: int
    maxSpeed: float
    maxBrakingGForce: float
    distanceMeters: float
    rank: str
    telemetry: List[TelemetryPoint]

class DriverProfile(BaseModel):
    pilotName: str
    totalDistance: float
    level: int
    vehicles: List[Vehicle]
    sessions: List[Session]
