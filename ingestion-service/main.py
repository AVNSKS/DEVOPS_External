# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="AgroNet Sensor Ingestion Gateway", version="1.0.0")

# Data structure model matching the problem statement requirements
class SensorTelemetry(BaseModel):
    device_id: str
    sensor_type: str  # weather, soil, irrigation, drone
    soil_moisture: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: float = time.time()

@app.get("/")
def read_root():
    return {"status": "AgroNet Ingestion Pipeline Operational", "timestamp": time.time()}

@app.post("/api/v1/telemetry")
async def receive_telemetry(data: SensorTelemetry):
    # This endpoint handles incoming real-time traffic spikes
    if not data.device_id:
        raise HTTPException(status_code=400, detail="Invalid device_id profile")
    
    # Simulating data parsing and database ingestion validation
    return {
        "status": "success",
        "processed_device": data.device_id,
        "metrics_captured": data.sensor_type
    }