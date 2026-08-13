"""
CLI Demo Runner for Project 15 - Feature Store & Vector Lakehouse.
"""

from src.lakehouse_orchestrator import FeatureLakehouseOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 15: Enterprise ML Feature Store & PyArrow Vector Lakehouse")
    print("==================================================================")
    orch = FeatureLakehouseOrchestrator()
    res = orch.process_feature_pipeline("entity-108", {"click_rate_7d": 0.42, "churn_risk": 0.05})
    print(f"Status: {res['status']} | Entity: {res['entity_id']}")
    print(f"Online Features Served: {res['online_features']} (Latency: {res['online_latency_ms']} ms)")
    print(f"Lakehouse Scan: {res['lakehouse_rows_scanned']} rows ({res['zero_copy_bytes']} bytes zero-copy in {res['lakehouse_scan_ms']} ms)")
    print("==================================================================")
