"""
FastAPI REST Application & Web UI for Project 10 - Triton & CUDA GPU Scheduler.
Provides REST endpoints for Triton dynamic batching, CUDA alignment, and AWQ FP8/INT8 quantization.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict, List
import uvicorn

from src.triton_serving_engine import TritonCUDAServingEngine

app = FastAPI(
    title="NVIDIA Triton & CUDA GPU Scheduler Engine",
    version="1.0.0",
    description="Hardware-aligned dynamic batching queues and AWQ FP8/INT8 weight quantization."
)

engine = TritonCUDAServingEngine()


@app.post("/triton/enqueue")
async def enqueue_req(payload: Dict[str, Any] = Body(...)):
    req_id = payload.get("request_id", "req-triton-01")
    shape = payload.get("tensor_shape", [1, 512])
    engine.submit_triton_request(req_id, shape)
    return {"status": "ENQUEUED", "request_id": req_id}


@app.post("/triton/flush-batch")
async def flush_batch():
    res = engine.execute_dynamic_batch_step()
    return res.dict()


@app.post("/triton/quantize")
async def quantize_model(payload: Dict[str, Any] = Body(...)):
    model_id = payload.get("model_id", "meta-llama/Llama-3-70B")
    fmt = payload.get("target_format", "AWQ_INT4")
    res = engine.audit_model_quantization(model_id, fmt)
    return res.dict()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NVIDIA Triton CUDA GPU Control Center</title>
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
        <h1>🟢 NVIDIA Triton CUDA GPU Control Center</h1>
        <div class="card">
            <h3>⚡ Audit AWQ INT4 Model Quantization & Perplexity Loss</h3>
            <button class="btn" onclick="runQuantize()">Audit AWQ Quantization</button>
            <pre id="quantOutput">Click button to run AWQ quantization audit...</pre>
        </div>
        <script>
            async function runQuantize() {
                const res = await fetch('/triton/quantize', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ model_id: 'meta-llama/Llama-3-70B', target_format: 'AWQ_INT4' }) });
                const data = await res.json();
                document.getElementById('quantOutput').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8009)
