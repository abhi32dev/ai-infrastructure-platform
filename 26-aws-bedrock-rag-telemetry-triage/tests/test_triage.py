"""
Test Suite for Project 26: AWS Bedrock RAG Telemetry Triage & Multi-Agent Swarm.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app import app
from src.models import TelemetryTrapPayload, VendorType, AlarmSeverity, AgenticReviewTask
from src.vector_store import PGVectorRunbookStore

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "CONDOR" in data["platform"]

@pytest.mark.asyncio
async def test_vector_similarity_search():
    store = PGVectorRunbookStore()
    results = store.search_similar_runbooks("CBRS SAS Spectrum Grant Revocation timeout", vendor=VendorType.GOOGLE_SAS)
    assert len(results) > 0
    best = results[0]
    assert best.runbook_id == "RB-SAS-503"
    assert best.similarity_score > 0.4
    assert "chrony" in best.remediation_steps[0]

@pytest.mark.asyncio
async def test_triage_telemetry_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "event_id": "evt-test-8891",
            "node_id": "EDGE-CA-SJC-104",
            "vendor": "GOOGLE_SAS",
            "severity": "WARNING",
            "oid": ".1.3.6.1.4.1.503.1",
            "raw_message": "CBRS SAS Spectrum Grant Revocation 503 heartbeat timeout",
            "metrics": {"packet_loss": 0.0, "cpu_temp": 42.5}
        }
        response = await ac.post("/api/v1/triage/telemetry", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == "evt-test-8891"
        assert data["confidence_score"] > 0.4
        assert data["matching_runbook_id"] == "RB-SAS-503"
        assert "chrony" in data["recommended_action"].lower()

@pytest.mark.asyncio
async def test_multi_agent_pytest_synthesis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        task = {
            "service_name": "Inventory-API",
            "endpoint_path": "/api/v1/nodes",
            "http_method": "POST",
            "input_schema": {"node_id": "str", "ip": "str"},
            "output_schema": {"status": "str"}
        }
        response = await ac.post("/api/v1/agentic/synthesize-tests", json=task)
        assert response.status_code == 200
        data = response.json()
        assert data["schema_architect_status"] == "APPROVED"
        assert "def test_inventory_api_post_success" in data["generated_pytest_code"]
