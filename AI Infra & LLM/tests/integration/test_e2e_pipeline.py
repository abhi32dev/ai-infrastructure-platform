import pytest
from fastapi.testclient import TestClient
from src.gateway.main import app
from src.gateway.schemas import CandidateEvaluation

client = TestClient(app)

def test_integration_e2e_evaluate_candidate():
    payload = {
        "candidate_id": "abhishek-singh-108",
        "job_description": "We are seeking a Staff/Principal AI Platform Architect with expertise in Triton CUDA scheduling, distributed training FSDP, and PagedAttention KV-caches.",
        "resume_text": "Abhishek Singh is a Staff/Principal AI Platform Architect. He designed Comcast CONDOR scaling 12,000 edge nodes. Expert in custom Triton CUDA kernel execution schedules, distributed model training FSDP, PagedAttention block optimization, and Langfuse observability gateways."
    }

    response = client.post("/v1/candidate/evaluate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["candidate_id"] == "abhishek-singh-108"
    assert "fit_score" in data
    assert len(data["key_strengths"]) > 0
    assert "confidence_score" in data

def test_integration_e2e_cover_letter_streaming():
    payload = {
        "candidate_name": "Abhishek Singh",
        "job_title": "Principal AI Engineer",
        "company_name": "Nexus Systems",
        "job_description": "Triton kernels and LLM serving design.",
        "resume_context": "Designed advanced CUDA schedulers."
    }

    response = client.post("/v1/candidate/cover-letter", json=payload)
    assert response.status_code == 200
    # Streaming response content
    assert len(response.text) > 0
