"""
FastAPI REST Service for Project 13 - RLHF & Direct Preference Optimization (DPO).
"""

from fastapi import FastAPI
from src.alignment_orchestrator import RLHFAlignmentOrchestrator

app = FastAPI(title="Project 13 - RLHF & DPO Alignment Pipeline", version="2.0")
orchestrator = RLHFAlignmentOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "RLHF & DPO Alignment Pipeline"}


@app.post("/align/dpo-step")
def run_dpo_step():
    return orchestrator.run_dpo_epoch()
