"""
Test Suite for Project 27: PGVector Incident Runbook Retriever.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app import app
from src.models import HardwareVendor, IncidentSeverity

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["engine"] == "PGVector-PostgreSQL-RDS"

@pytest.mark.asyncio
async def test_hybrid_search_google_sas():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "query_text": "CBRS SAS Spectrum Grant Revocation timeout NTP drift",
            "vendor": "GOOGLE_SAS",
            "top_k": 2,
            "alpha": 0.7
        }
        response = await ac.post("/api/v1/runbooks/hybrid-search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) > 0
        best = data["matches"][0]
        assert best["runbook"]["runbook_id"] == "RB-SAS-503"
        assert best["combined_hybrid_score"] > 0.3
        assert "chronyc" in best["runbook"]["remediation_runbook"]

@pytest.mark.asyncio
async def test_upsert_and_retrieval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        new_rb = {
            "runbook_id": "RB-CUSTOM-999",
            "title": "Custom Test Runbook for Memory Leak",
            "vendor": "GLOBAL",
            "severity": "SEV3_MINOR",
            "error_signature": "Memory leak detected in python daemon thread pool",
            "root_cause_analysis": "Unclosed database session handles in long-running daemon loop.",
            "remediation_runbook": "Restart daemon with connection pool recycling.",
            "tags": ["memory", "python", "leak"]
        }
        upsert_res = await ac.post("/api/v1/runbooks/upsert", json=new_rb)
        assert upsert_res.status_code == 201

        search_payload = {
            "query_text": "Memory leak python daemon thread pool connection",
            "top_k": 1
        }
        search_res = await ac.post("/api/v1/runbooks/hybrid-search", json=search_payload)
        assert search_res.status_code == 200
        data = search_res.json()
        assert data["matches"][0]["runbook"]["runbook_id"] == "RB-CUSTOM-999"
