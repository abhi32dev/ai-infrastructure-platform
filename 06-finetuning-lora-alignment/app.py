"""
FastAPI REST Application & Web UI for Fine-Tuning & LoRA Alignment Engine.
Provides endpoints for SFT dataset curation, LoRA rank training, loss tracking,
and GGUF model weight export.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict, List
import uvicorn

from src.dataset_curator import DatasetCurator
from src.lora_trainer import LoRAConfig, LoRATrainer
from src.model_exporter import ModelExporter

app = FastAPI(
    title="Fine-Tuning, LoRA & Dataset Alignment Platform",
    version="1.0.0",
    description="SFT dataset curation, LoRA parameter-efficient fine-tuning, loss logging, and GGUF export."
)

curator = DatasetCurator()
trainer = LoRATrainer()
exporter = ModelExporter()


@app.post("/curate")
async def curate_dataset(payload: Dict[str, Any] = Body(...)):
    raw_samples = payload.get("samples", [
        {"instruction": "Explain CONDOR persistent socket", "output_response": "Runs Docker daemon on EC2 UDP port 162."},
        {"instruction": "Why choose ALB over API Gateway?", "output_response": "Lower cost profile and built-in cross-AZ target routing."}
    ])
    train_set, val_set, stats = curator.curate_dataset(raw_samples)
    return {"stats": stats, "train_count": len(train_set), "val_count": len(val_set)}


@app.post("/train")
async def train_lora(payload: Dict[str, Any] = Body(...)):
    r = payload.get("r", 8)
    alpha = payload.get("alpha", 16)
    epochs = payload.get("epochs", 3)

    cfg = LoRAConfig(r=r, lora_alpha=alpha, num_epochs=epochs)
    t = LoRATrainer(config=cfg)
    results = t.train_lora_adapter(train_samples_count=100, val_samples_count=20)
    return results


@app.post("/export")
async def export_model(payload: Dict[str, Any] = Body(...)):
    base_model = payload.get("base_model", "meta-llama/Llama-3.2-3B")
    adapter = payload.get("adapter", "adapters/lora-v1")
    quant = payload.get("quantization", "Q4_K_M")

    res = exporter.merge_and_export_gguf(base_model, adapter, quantization_type=quant)
    return res


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Fine-Tuning & LoRA Alignment Dashboard</title>
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
        <h1>🎛️ Fine-Tuning, LoRA & Dataset Alignment Control Center</h1>
        <div class="card">
            <h3>⚡ Execute LoRA SFT Training Simulation (Rank r=8, Alpha=16)</h3>
            <button class="btn" onclick="runTraining()">Start LoRA Fine-Tuning</button>
            <pre id="trainOutput">Click start to run training simulation...</pre>
        </div>
        <script>
            async function runTraining() {
                const res = await fetch('/train', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ r: 8, alpha: 16, epochs: 3 }) });
                const data = await res.json();
                document.getElementById('trainOutput').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
