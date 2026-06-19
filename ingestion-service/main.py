# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="AgroNet Sensor Ingestion Gateway", version="1.0.0")
START_TIME = time.time()

# Data structure model matching the problem statement requirements
class SensorTelemetry(BaseModel):
    device_id: str
    sensor_type: str  # weather, soil, irrigation, drone
    soil_moisture: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[float] = None

@app.get("/")
def read_root():
    uptime = int(time.time() - START_TIME)
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgroNet Operations</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #17231f; background: #f4f7f2; }}
    header {{ background: #12372a; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #d9e2d4; border-radius: 8px; padding: 18px; }}
    .metric {{ font-size: 30px; font-weight: 700; color: #1f7a4d; }}
    .label {{ color: #5b6b63; font-size: 14px; }}
    .status {{ display: inline-block; background: #dcfce7; color: #166534; padding: 6px 10px; border-radius: 999px; font-weight: 700; }}
    code {{ background: #edf2ea; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>AgroNet Smart Agriculture Operations Platform</h1>
    <div class="status">Ingestion pipeline operational</div>
  </header>
  <main>
    <section class="grid">
      <div class="card"><div class="metric">2+</div><div class="label">Kubernetes replicas with HPA scaling</div></div>
      <div class="card"><div class="metric">15s</div><div class="label">Metrics collection interval</div></div>
      <div class="card"><div class="metric">{uptime}s</div><div class="label">Current API container uptime</div></div>
      <div class="card"><div class="metric">Live</div><div class="label">Health, readiness, and Prometheus metrics enabled</div></div>
    </section>
    <section class="card" style="margin-top: 18px;">
      <h2>Telemetry API</h2>
      <p>Send weather, soil, irrigation, drone, and equipment readings to <code>POST /api/v1/telemetry</code>.</p>
      <p>Open API documentation is available at <code>/docs</code>. Health checks are available at <code>/healthz</code> and <code>/readyz</code>.</p>
    </section>
  </main>
</body>
</html>
""")

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "uptime_seconds": int(time.time() - START_TIME)}

@app.get("/readyz")
def readyz():
    return {"status": "ready"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    uptime = int(time.time() - START_TIME)
    return f"""# HELP agronet_api_up AgroNet API health status
# TYPE agronet_api_up gauge
agronet_api_up 1
# HELP agronet_api_uptime_seconds AgroNet API uptime in seconds
# TYPE agronet_api_uptime_seconds counter
agronet_api_uptime_seconds {uptime}
"""

@app.post("/api/v1/telemetry")
async def receive_telemetry(data: SensorTelemetry):
    # This endpoint handles incoming real-time traffic spikes
    if not data.device_id:
        raise HTTPException(status_code=400, detail="Invalid device_id profile")
    
    # Simulating data parsing and database ingestion validation
    return {
        "status": "success",
        "processed_device": data.device_id,
        "metrics_captured": data.sensor_type,
        "ingested_at": time.time()
    }
