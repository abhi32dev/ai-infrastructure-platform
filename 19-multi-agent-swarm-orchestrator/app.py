"""
FastAPI REST Service for Project 19 - Multi-Agent Swarm Orchestrator.
"""

from fastapi import FastAPI
from src.swarm_orchestrator import MultiAgentSwarmOrchestrator

app = FastAPI(title="Project 19 - Multi-Agent Swarm Orchestrator", version="2.0")
orchestrator = MultiAgentSwarmOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "Multi-Agent Swarm Orchestrator"}


@app.post("/swarm/execute")
def execute_swarm(goal: str = "Build production LLM inference service"):
    return orchestrator.execute_swarm_workflow(goal=goal)
