"""
FastAPI REST Service for Project 12 - GenAI Gateway, Semantic Cache & Rate Limiter.
"""

from fastapi import FastAPI
from src.gateway_orchestrator import GenAIGatewayOrchestrator

app = FastAPI(title="Project 12 - GenAI API Gateway & Semantic Cache", version="2.0")
gateway = GenAIGatewayOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "GenAI API Gateway"}


@app.post("/v1/chat/completions")
def chat_completions(client_id: str, prompt: str, max_tokens: int = 100):
    return gateway.process_request(client_id=client_id, prompt=prompt, max_tokens=max_tokens)
