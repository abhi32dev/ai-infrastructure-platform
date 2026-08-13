"""
Master Feature Store & Vector Lakehouse Orchestrator.
Integrates Online + Offline ML Feature Store with Apache Iceberg / PyArrow Zero-Copy Serialization.
"""

from typing import Any, Dict, List
from src.feature_store import MLFeatureStore
from src.arrow_lakehouse import ArrowLakehouseQuery, PyArrowVectorLakehouse


class FeatureLakehouseOrchestrator:
    def __init__(self):
        self.feature_store = MLFeatureStore()
        self.lakehouse = PyArrowVectorLakehouse()

    def process_feature_pipeline(self, entity_id: str, feature_map: Dict[str, float]) -> Dict[str, Any]:
        """Pushes feature updates to Online Store and executes Arrow zero-copy lakehouse query."""
        for fname, val in feature_map.items():
            self.feature_store.push_online_feature(entity_id, fname, val)

        # Online retrieval check
        online_res = self.feature_store.get_online_features(entity_id, list(feature_map.keys()))

        # Offline Arrow Lakehouse Query
        arrow_res = self.lakehouse.query_columnar_vectors(columns=list(feature_map.keys()), max_rows=5000)

        return {
            "status": "PIPELINE_COMPLETED",
            "entity_id": entity_id,
            "online_features": online_res["features"],
            "online_latency_ms": online_res.get("latency_ms", 1.0),
            "lakehouse_rows_scanned": arrow_res.rows_scanned,
            "zero_copy_bytes": arrow_res.zero_copy_bytes,
            "lakehouse_scan_ms": arrow_res.scan_latency_ms

        }
