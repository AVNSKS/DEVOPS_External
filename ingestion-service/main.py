# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List
import time
import os
import random

app = FastAPI(title="AgroNet Sensor Ingestion Gateway", version="1.0.0")
START_TIME = time.time()

# In-memory telemetry log storage for live dashboard visualization
TELEMETRY_LOGS = []

# Vault secret retrieval logic
VAULT_SECRET_PATH = "/vault/secrets/database"

def get_vault_secrets():
    secrets = {
        "db_password": "FALLBACK_SECURE_PASSWORD_2026",
        "api_key": "FALLBACK_API_KEY_XYZ",
        "loaded_from_vault": False
    }
    if os.path.exists(VAULT_SECRET_PATH):
        try:
            with open(VAULT_SECRET_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        k, v = line.split("=", 1)
                        secrets[k.strip()] = v.strip()
            secrets["loaded_from_vault"] = True
        except Exception as e:
            pass
    return secrets

def mask_secret(value: str) -> str:
    if len(value) <= 6:
        return "****"
    return value[:4] + "****************" + value[-3:]

class SensorTelemetry(BaseModel):
    device_id: str
    sensor_type: str  # weather, soil, irrigation, drone, equipment
    soil_moisture: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: Optional[float] = None

@app.get("/")
def read_root():
    uptime = int(time.time() - START_TIME)
    secrets = get_vault_secrets()
    
    vault_status_class = "vault-success" if secrets["loaded_from_vault"] else "vault-warning"
    vault_status_text = "Secured by HashiCorp Vault" if secrets["loaded_from_vault"] else "Vault Agent Not Injected (Fallback Active)"
    
    masked_pwd = mask_secret(secrets["db_password"])
    masked_key = mask_secret(secrets["api_key"])
    
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgroNet Operations Control</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-gradient: radial-gradient(circle at top left, #070f0b, #030604);
      --card-bg: rgba(9, 21, 15, 0.6);
      --card-border: 1px solid rgba(16, 185, 129, 0.15);
      --primary: #10b981;
      --primary-glow: rgba(16, 185, 129, 0.3);
      --text-main: #e2e8f0;
      --text-muted: #94a3b8;
    }}
    body {{
      margin: 0;
      font-family: 'Inter', sans-serif;
      background: var(--bg-gradient);
      color: var(--text-main);
      min-height: 100vh;
      overflow-x: hidden;
    }}
    header {{
      background: rgba(4, 12, 8, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(16, 185, 129, 0.1);
      padding: 20px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-logo {{
      font-family: 'Outfit', sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1.5px;
      text-shadow: 0 0 12px var(--primary-glow);
    }}
    .vault-badge {{
      display: inline-flex;
      align-items: center;
      padding: 6px 16px;
      border-radius: 99px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}
    .vault-success {{
      background: rgba(16, 185, 129, 0.12);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
    }}
    .vault-warning {{
      background: rgba(245, 158, 11, 0.12);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
      box-shadow: 0 0 8px rgba(245, 158, 11, 0.2);
    }}
    main {{
      padding: 40px;
      max-width: 1280px;
      margin: 0 auto;
    }}
    h2 {{
      font-family: 'Outfit', sans-serif;
      font-size: 22px;
      font-weight: 700;
      margin-top: 0;
      margin-bottom: 20px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .grid-metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }}
    .card {{
      background: var(--card-bg);
      backdrop-filter: blur(8px);
      border: var(--card-border);
      border-radius: 12px;
      padding: 24px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .card:hover {{
      transform: translateY(-4px);
      border-color: rgba(16, 185, 129, 0.4);
      box-shadow: 0 8px 30px rgba(16, 185, 129, 0.08);
    }}
    .metric {{
      font-family: 'Outfit', sans-serif;
      font-size: 38px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 8px;
    }}
    .label {{
      color: var(--text-muted);
      font-size: 14px;
      font-weight: 500;
      line-height: 1.4;
    }}
    .grid-sections {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 28px;
    }}
    @media (max-width: 900px) {{
      .grid-sections {{
        grid-template-columns: 1fr;
      }}
    }}
    .btn {{
      background: var(--primary);
      color: #030604;
      font-weight: 600;
      border: none;
      padding: 12px 20px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .btn:hover {{
      opacity: 0.9;
      transform: scale(1.02);
      box-shadow: 0 0 15px var(--primary-glow);
    }}
    .btn-secondary {{
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--primary);
      margin-top: 15px;
    }}
    .btn-secondary:hover {{
      background: rgba(16, 185, 129, 0.2);
    }}
    .btn-sim {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      padding: 10px 14px;
      font-size: 13px;
    }}
    .btn-sim:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}
    .sim-buttons {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 20px;
    }}
    .log-container {{
      background: rgba(0, 0, 0, 0.4);
      border-radius: 8px;
      padding: 18px;
      height: 250px;
      overflow-y: auto;
      font-family: monospace;
      font-size: 13px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .log-entry {{
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      line-height: 1.5;
    }}
    .log-time {{
      color: var(--primary);
    }}
    .log-tag {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--primary);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
    }}
    code {{
      font-family: monospace;
      background: rgba(255, 255, 255, 0.06);
      padding: 3px 6px;
      border-radius: 4px;
      color: #38bdf8;
    }}
    .secret-field {{
      background: rgba(255, 255, 255, 0.03);
      padding: 12px 16px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      margin-bottom: 10px;
      font-family: monospace;
      font-size: 13px;
    }}
    .secret-label {{
      color: var(--text-muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 4px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-logo">AgroNet Operations</div>
    <div class="vault-badge {vault_status_class}">{vault_status_text}</div>
  </header>
  <main>
    <section class="grid-metrics">
      <div class="card">
        <div class="metric">2 / 6</div>
        <div class="label">Kubernetes API Replicas<br><span style="font-size:11px; color:#10b981;">HPA Scaling Target 50% CPU</span></div>
      </div>
      <div class="card">
        <div class="metric">15s</div>
        <div class="label">Observability Scrape Interval<br><span style="font-size:11px; color:#10b981;">Prometheus ServiceMonitor Active</span></div>
      </div>
      <div class="card">
        <div class="metric">{uptime}s</div>
        <div class="label">Current API Container Uptime<br><span style="font-size:11px; color:#38bdf8;">Kubernetes Readiness Probe OK</span></div>
      </div>
      <div class="card">
        <div class="metric">Live</div>
        <div class="label">Grafana Core Integration<br><span style="font-size:11px; color:#10b981;">Prometheus Observability Active</span></div>
      </div>
    </section>

    <div class="grid-sections">
      <!-- Section 1: Telemetry Simulation -->
      <section class="card">
        <h2>Ingestion Control Center</h2>
        <p class="label" style="margin-bottom: 20px;">Trigger simulated smart-agri sensor events to test Kubernetes workloads, scale patterns, and network traffic response.</p>
        
        <div class="sim-buttons">
          <button class="btn btn-sim" onclick="simulateTelemetry('weather')">🌧️ Weather</button>
          <button class="btn btn-sim" onclick="simulateTelemetry('soil')">🌱 Soil</button>
          <button class="btn btn-sim" onclick="simulateTelemetry('irrigation')">💦 Irrigation</button>
          <button class="btn btn-sim" onclick="simulateTelemetry('drone')">🛸 Drone</button>
          <button class="btn btn-sim" onclick="simulateTelemetry('equipment')">🚜 Equipment</button>
        </div>

        <div class="log-container" id="logs-box">
          <div style="color: var(--text-muted); text-align: center; margin-top: 100px;">Waiting for telemetry stream...</div>
        </div>
      </section>

      <!-- Section 2: Vault Credentials & Grafana -->
      <section class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <h2>Vault Credentials Storage</h2>
          <p class="label" style="margin-bottom: 20px;">Sensitive DB connections and tokens are securely injected at startup directly by the Vault Sidecar Agent.</p>
          
          <div class="secret-field">
            <div class="secret-label">Database Password (DB_PASSWORD)</div>
            <div style="color: #f43f5e;">{masked_pwd}</div>
          </div>
          
          <div class="secret-field">
            <div class="secret-label">API Gateway Token (API_KEY)</div>
            <div style="color: #38bdf8;">{masked_key}</div>
          </div>
        </div>

        <div style="margin-top: 30px;">
          <h2>Operational Monitoring</h2>
          <p class="label">Access live Grafana metrics and Kubernetes computing resources analysis dashboards.</p>
          <button class="btn btn-secondary" onclick="window.open('http://' + window.location.hostname + ':3000')">📊 Launch Grafana Control Board</button>
        </div>
      </section>
    </div>
  </main>

  <script>
    async function simulateTelemetry(type) {{
      const devices = {{
        'weather': 'WEATHER-STN-09',
        'soil': 'SOIL-SENS-12',
        'irrigation': 'IRR-VALVE-04',
        'drone': 'DRN-CAM-88',
        'equipment': 'TRCTR-GPS-10'
      }};
      
      const payload = {{
        device_id: devices[type],
        sensor_type: type,
        soil_moisture: type === 'soil' ? parseFloat((Math.random() * 20 + 30).toFixed(2)) : null,
        temperature: type === 'weather' ? parseFloat((Math.random() * 15 + 20).toFixed(2)) : null,
        humidity: type === 'weather' ? parseFloat((Math.random() * 20 + 60).toFixed(2)) : null,
        timestamp: Date.now() / 1000
      }};

      try {{
        const response = await fetch('/api/v1/telemetry', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        await loadRecentLogs();
      }} catch (err) {{
        console.error('Failed to post telemetry', err);
      }}
    }}

    async function loadRecentLogs() {{
      try {{
        const response = await fetch('/api/v1/telemetry/recent');
        const logs = await response.json();
        const logsBox = document.getElementById('logs-box');
        if (logs.length === 0) {{
          logsBox.innerHTML = '<div style="color: var(--text-muted); text-align: center; margin-top: 100px;">Waiting for telemetry stream...</div>';
          return;
        }}
        logsBox.innerHTML = logs.map(l => `
          <div class="log-entry">
            <span class="log-time">[${{new Date(l.ingested_at * 1000).toLocaleTimeString()}}]</span> 
            <span class="log-tag">${{l.sensor_type}}</span> 
            device <strong>${{l.processed_device}}</strong> ingested successfully.
            <br>
            <span style="color: var(--text-muted); font-size:11px;">Payload details: ${{JSON.stringify(l.details)}}</span>
          </div>
        `).join('');
      }} catch (err) {{
        console.error('Failed to load logs', err);
      }}
    }}

    // Initial load and periodic refresh of telemetry logs
    loadRecentLogs();
    setInterval(loadRecentLogs, 2000);
  </script>
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

@app.get("/api/v1/telemetry/recent", response_model=List[dict])
async def get_recent_telemetry():
    return TELEMETRY_LOGS

@app.post("/api/v1/telemetry")
async def receive_telemetry(data: SensorTelemetry):
    if not data.device_id:
        raise HTTPException(status_code=400, detail="Invalid device_id profile")
    
    # Store event details locally for live dashboard streaming
    event_details = {}
    if data.soil_moisture is not None:
        event_details["soil_moisture"] = data.soil_moisture
    if data.temperature is not None:
        event_details["temperature"] = data.temperature
    if data.humidity is not None:
        event_details["humidity"] = data.humidity

    log_entry = {
        "sensor_type": data.sensor_type.upper(),
        "processed_device": data.device_id,
        "ingested_at": time.time(),
        "details": event_details
    }
    
    TELEMETRY_LOGS.insert(0, log_entry)
    # Keep only the last 5 logs
    if len(TELEMETRY_LOGS) > 5:
        TELEMETRY_LOGS.pop()
        
    return {
        "status": "success",
        "processed_device": data.device_id,
        "metrics_captured": data.sensor_type,
        "ingested_at": log_entry["ingested_at"]
    }
