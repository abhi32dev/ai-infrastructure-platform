"""
FastAPI REST Service for Project 15 - Feature Store & Vector Lakehouse.
"""

from fastapi import FastAPI
from src.lakehouse_orchestrator import FeatureLakehouseOrchestrator

app = FastAPI(title="Project 15 - Feature Store & Vector Lakehouse", version="2.0")
orchestrator = FeatureLakehouseOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "Feature Store & Vector Lakehouse"}


@app.post("/features/push")
def push_features(entity_id: str, feat_a: float = 1.0, feat_b: float = 2.0):
    return orchestrator.process_feature_pipeline(entity_id=entity_id, feature_map={"feat_a": feat_a, "feat_b": feat_b})
