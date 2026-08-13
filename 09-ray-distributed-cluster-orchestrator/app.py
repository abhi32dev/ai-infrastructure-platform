"""
FastAPI REST Application & Web UI for Project 9 - Ray Cluster Orchestrator.
Provides REST endpoints for Ray Actor task dispatch, Plasma object store references,
and cluster autoscaling.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict
import uvicorn

from src.ray_cluster_manager import RayClusterOrchestrator

app = FastAPI(
    title="Ray Distributed Cluster Orchestrator",
    version="1.0.0",
    description="Ray Actor worker pools, Plasma zero-copy memory, and autoscaling."
)

orchestrator = RayClusterOrchestrator()


@app.post("/ray/shared-object")
async def put_shared_object(payload: Dict[str, Any] = Body(...)):
    obj_id = payload.get("object_id", "tensor-ref-901")
    size_mb = payload.get("size_mb", 512.0)
    ref = orchestrator.submit_shared_tensor(obj_id, size_mb)
    return ref.dict()


@app.post("/ray/dispatch-task")
async def dispatch_task(payload: Dict[str, Any] = Body(...)):
    task_name = payload.get("task_name", "DistributedBatchInferenceTask")
    obj_ref = payload.get("object_ref_id", "tensor-ref-901")
    res = orchestrator.run_distributed_task(task_name, obj_ref)
    return res


@app.post("/ray/autoscale")
async def autoscale(payload: Dict[str, Any] = Body(...)):
    queue_depth = payload.get("queue_depth", 65)
    gpu_util = payload.get("avg_gpu_util_pct", 88.5)
    metrics = orchestrator.evaluate_autoscaling(queue_depth, gpu_util)
    return metrics.dict()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Ray Cluster & Actor Control Center</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
            h1 { color: #38bdf8; font-size: 1.5rem; margin-bottom: 1rem; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
            .btn { background: #38bdf8; color: #000; font-weight: 600; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; }
            pre { background: #090d16; padding: 1rem; border-radius: 6px; color: #a5f3fc; }
        </style>
    </head>
    <body>
        <h1>🛰️ Ray Distributed Cluster & Actor Control Center</h1>
        <div class="card">
            <h3>⚡ Trigger Cluster Autoscaler Evaluation (Queue Depth: 65, GPU Util: 88%)</h3>
            <button class="btn" onclick="runAutoscale()">Run Autoscaler Check</button>
            <pre id="scaleOutput">Click button to evaluate scaling...</pre>
        </div>
        <script>
            async function runAutoscale() {
                const res = await fetch('/ray/autoscale', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ queue_depth: 65, avg_gpu_util_pct: 88.5 }) });
                const data = await res.json();
                document.getElementById('scaleOutput').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8008)
