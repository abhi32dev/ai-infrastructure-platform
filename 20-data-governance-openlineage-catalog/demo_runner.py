"""
CLI Demo Runner for Project 20 - Data Governance & OpenLineage Catalog.
"""

from src.governance_orchestrator import DataGovernanceOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 20: Data Governance & OpenLineage Catalog Pipeline")
    print("==================================================================")
    orch = DataGovernanceOrchestrator()
    records = [{"entity_id": "e-108", "timestamp": 100.0, "payload": "sample_telemetry"}]
    res = orch.run_governance_pipeline("condor_feature_etl_job", records)
    print(f"Status: {res['status']} | Job: {res['job_name']} ({res['run_id']})")
    print(f"OpenLineage Event: {res['openlineage_event_type']}")
    print(f"Dataset Lineage Edges: {res['lineage_edges']}")
    print(f"Data Quality Score: {res['quality_score_pct']}%")
    print("==================================================================")
