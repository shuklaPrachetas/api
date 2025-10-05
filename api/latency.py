# Add FastAPI CORS middleware and implement the POST endpoint for latency metrics
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data once at startup (assume telemetry.jsonl in project root or /data)
TELEMETRY_PATHS = ["telemetry.jsonl", "data/telemetry.jsonl"]
TELEMETRY = []
for path in TELEMETRY_PATHS:
    if os.path.exists(path):
        with open(path) as f:
            TELEMETRY = [json.loads(line) for line in f]
        break

@app.post("/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    result = {}
    for region in regions:
        region_data = [r for r in TELEMETRY if r.get("region") == region]
        if not region_data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue
        latencies = np.array([r["latency_ms"] for r in region_data])
        uptimes = np.array([r["uptime"] for r in region_data])
        breaches = int((latencies > threshold).sum())
        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches
        }
    return JSONResponse(result)
