import pytest
from fastapi.testclient import TestClient
from src.gateway.main import app
from src.gateway.schemas import CandidateEvaluation
from src.gateway.grammar import SchemaEnforcer

client = TestClient(app)

def test_10_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_11_schema_enforcer_recovery():
    # Valid json matching schema format
    raw_json = '{"candidate_id": "test-c", "fit_score": 0.85, "key_strengths": ["FastAPI", "Python"], "growth_areas": [], "source_citations": [], "confidence_score": 0.9}'
    eval_obj = SchemaEnforcer.enforce(raw_json, CandidateEvaluation)
    assert eval_obj.candidate_id == "test-c"
    assert eval_obj.fit_score == 0.85

    # Malformed JSON recovery fallback test
    malformed = 'this is conversational text with json {"candidate_id": "test-c-2", "fit_score": 0.5, "key_strengths": [], "growth_areas": [], "source_citations": [], "confidence_score": 0.5} and trailing garbage'
    eval_obj_2 = SchemaEnforcer.enforce(malformed, CandidateEvaluation)
    assert eval_obj_2.candidate_id == "test-c-2"

def test_12_schema_enforcer_unresolvable_fallback():
    # Unresolvable content triggers fallback building
    garbage = "totally unresolvable text"
    eval_obj = SchemaEnforcer.enforce(garbage, CandidateEvaluation)
    assert eval_obj.candidate_id == "unknown"
    assert eval_obj.fit_score == 0.5
    assert len(eval_obj.key_strengths) == 1
