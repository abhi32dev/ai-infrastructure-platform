"""
FastAPI REST Service for Project 20 - Data Governance & OpenLineage Catalog.
"""

from fastapi import FastAPI
from src.governance_orchestrator import DataGovernanceOrchestrator

app = FastAPI(title="Project 20 - Data Governance & OpenLineage Catalog", version="2.0")
orchestrator = DataGovernanceOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "Data Governance & OpenLineage Catalog"}


@app.post("/governance/run")
def run_governance(job_name: str = "spark_etl_pass"):
    records = [{"entity_id": "e-108", "timestamp": 100.0, "payload": "sample_telemetry"}]
    return orchestrator.run_governance_pipeline(job_name=job_name, records=records)
