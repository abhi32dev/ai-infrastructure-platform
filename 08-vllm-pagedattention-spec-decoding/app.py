"""
FastAPI REST Application & Web UI for Project 8 - vLLM & PagedAttention.
Provides REST endpoints for PagedAttention GPU KV-cache allocation,
Speculative Decoding, and Continuous Batching scheduler.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict
import uvicorn

from src.vllm_engine import VLLMInferenceEngine

app = FastAPI(
    title="vLLM High-Throughput Inference Engine",
    version="1.0.0",
    description="PagedAttention KV-cache block allocator, Speculative Decoding, and Continuous Batching."
)

engine = VLLMInferenceEngine()


@app.post("/vllm/allocate-cache")
async def allocate_cache(payload: Dict[str, Any] = Body(...)):
    req_id = payload.get("request_id", "req-101")
    tokens = payload.get("num_tokens", 48)
    res = engine.allocate_kv_cache(req_id, tokens)
    return res


@app.post("/vllm/spec-decode")
async def spec_decode(payload: Dict[str, Any] = Body(...)):
    prompt = payload.get("prompt", "Architect scalable distributed AI infrastructure")
    res = engine.execute_speculative_decoding(prompt)
    return res.dict()


@app.post("/vllm/step-batch")
async def step_batch():
    res = engine.run_continuous_batch_iteration()
    return res


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>vLLM PagedAttention & Speculative Decoding Dashboard</title>
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
        <h1>⚡ vLLM PagedAttention & Speculative Decoding Engine</h1>
        <div class="card">
            <h3>🎛️ Execute Speculative Decoding (1B Draft + 70B Target Parallel Pass)</h3>
            <button class="btn" onclick="runSpecDecode()">Run Speculative Decoding</button>
            <pre id="specOutput">Click button to run speculative decoding step...</pre>
        </div>
        <script>
            async function runSpecDecode() {
                const res = await fetch('/vllm/spec-decode', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ prompt: 'Architect AI Platform' }) });
                const data = await res.json();
                document.getElementById('specOutput').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8007)
