"""
Test Suite for Project 28: FastAPI Pydantic Schema Governance.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app import app

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["pydantic_mode"] == "strict"

@pytest.mark.asyncio
async def test_polymorphic_ingestion_google_sas():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "vendor_type": "GOOGLE_SAS",
            "event_id": "evt-sas-1001",
            "node_id": "EDGE-CA-SJC-101",
            "cbrs_grant_id": "GRANT-998822",
            "eirp_dbm": 37.0,
            "heartbeat_interval_sec": 240
        }
        response = await ac.post("/api/v1/telemetry/ingest-single", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["vendor"] == "GOOGLE_SAS"

@pytest.mark.asyncio
async def test_polymorphic_ingestion_validation_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Invalid EIRP (> 50.0 dBm violates ge/le boundary)
        payload = {
            "vendor_type": "GOOGLE_SAS",
            "event_id": "evt-sas-1001",
            "node_id": "EDGE-CA-SJC-101",
            "cbrs_grant_id": "GRANT-998822",
            "eirp_dbm": 120.0,
            "heartbeat_interval_sec": 240
        }
        response = await ac.post("/api/v1/telemetry/ingest-single", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["error_type"] == "SchemaValidationError"

@pytest.mark.asyncio
async def test_batch_ingestion_duplicate_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Duplicate event_id in batch triggers model_validator
        payload = {
            "batch_id": "batch-101",
            "protocol": "REST_HTTPS",
            "items": [
                {
                    "vendor_type": "NOKIA",
                    "event_id": "evt-dup-1",
                    "node_id": "EDGE-CA-SJC-101",
                    "bbu_chassis_id": "BBU-01",
                    "optical_rx_power_dbm": -15.5,
                    "sfp_serial": "SN-88776655"
                },
                {
                    "vendor_type": "NOKIA",
                    "event_id": "evt-dup-1",
                    "node_id": "EDGE-CA-SJC-102",
                    "bbu_chassis_id": "BBU-02",
                    "optical_rx_power_dbm": -14.2,
                    "sfp_serial": "SN-99887766"
                }
            ]
        }
        response = await ac.post("/api/v1/telemetry/ingest-batch", json=payload)
        assert response.status_code == 422
