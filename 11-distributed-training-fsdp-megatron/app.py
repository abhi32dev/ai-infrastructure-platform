"""
FastAPI REST Service for Project 11 - Distributed Training (PyTorch FSDP & Megatron).
"""

from fastapi import FastAPI
from src.training_orchestrator import DistributedTrainingOrchestrator

app = FastAPI(title="Project 11 - Distributed Training (FSDP & Megatron)", version="2.0")
orchestrator = DistributedTrainingOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "Distributed Training (FSDP & Megatron)"}


@app.post("/train/step")
def run_step(batch_size: int = 16):
    return orchestrator.run_training_step(batch_size=batch_size)
