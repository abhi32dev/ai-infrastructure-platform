"""
FastAPI REST Service for Project 16 - AI Safety, Red-Teaming & Guardrails.
"""

from fastapi import FastAPI
from src.safety_orchestrator import AISafetyGuardrailsOrchestrator

app = FastAPI(title="Project 16 - AI Safety & Policy Guardrails Engine", version="2.0")
orchestrator = AISafetyGuardrailsOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "AI Safety & Policy Guardrails Engine"}


@app.post("/guardrails/filter")
def filter_request(user_prompt: str, simulated_response: str = "Safe response"):
    return orchestrator.process_guardrails_pipeline(user_prompt=user_prompt, simulated_llm_response=simulated_response)
