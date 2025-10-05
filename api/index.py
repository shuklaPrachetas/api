from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load sample telemetry data (replace with your telemetry file)
with open("telemetry.json", "r") as f:
    telemetry = json.load(f)

@app.post("/")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    results = {}
    for region in regions:
        data = telemetry.get(region, [])
        latencies = [r["latency_ms"] for r in data]
        uptimes = [r["uptime"] for r in data]

        if not latencies:
            continue

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for x in latencies if x > threshold)

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return results
