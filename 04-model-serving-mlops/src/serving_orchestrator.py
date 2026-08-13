"""
Master Model Serving & MLOps Platform Orchestrator.
Integrates Recommendation Serving, SSE Token Streaming Proxy, Backpressure Control,
and OpenTelemetry / Prometheus Metrics Collection.
"""

from typing import Any, Dict, List, Tuple
from src.mlops_metrics import MLOpsMetricsCollector, ServingMetricsSnapshot
from src.recsys_engine import RecSysEngine
from src.streaming_proxy import StreamingProxy


class ServingOrchestrator:
    def __init__(self):
        print("[SERVING ORCHESTRATOR] Initializing Production Model Serving & MLOps Platform...")
        self.recsys = RecSysEngine()
        self.streaming_proxy = StreamingProxy(max_queue_depth=10, max_concurrency=4)
        self.metrics = MLOpsMetricsCollector(ttft_slo_target_ms=500.0)

    def get_user_recommendations(self, user_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Serves personalized A/B recommendations and logs conversion telemetry.
        """
        items, variant = self.recsys.get_recommendations(user_id, top_k=top_k)
        return {
            "user_id": user_id,
            "assigned_variant": variant,
            "recommendations": [item.dict() for item in items]
        }

    def record_simulated_inference(self, ttft_ms: float, tokens: int, duration_sec: float, cost: float, status: str = "SUCCESS"):
        """Records telemetry data point into MLOps Collector."""
        self.metrics.record_inference_request(
            ttft_ms=ttft_ms,
            tokens_count=tokens,
            duration_sec=duration_sec,
            cost_usd=cost,
            status=status
        )

    def get_platform_telemetry(self) -> ServingMetricsSnapshot:
        """Fetches current serving metrics snapshot."""
        return self.metrics.get_snapshot()
