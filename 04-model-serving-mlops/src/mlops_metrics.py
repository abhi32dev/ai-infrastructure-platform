"""
OpenTelemetry & Prometheus MLOps Metrics Engine.
Collects real-time serving telemetry: Time-To-First-Token (TTFT), Tokens-Per-Second (TPS),
P95/P99 latency SLA compliance, token cost governance, and Prometheus metrics export.
"""

from typing import Any, Dict, List
import numpy as np
from pydantic import BaseModel, Field


class ServingMetricsSnapshot(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    backpressure_rejections: int
    avg_ttft_ms: float
    p95_ttft_ms: float
    p99_ttft_ms: float
    avg_tps: float
    total_tokens_served: int
    cumulative_cost_usd: float
    slo_compliance_pct: float


class MLOpsMetricsCollector:
    def __init__(self, ttft_slo_target_ms: float = 500.0):
        self.ttft_slo_target_ms = ttft_slo_target_ms
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.backpressure_rejections = 0
        
        self.ttft_records_ms: List[float] = []
        self.tps_records: List[float] = []
        self.total_tokens_served = 0
        self.cumulative_cost_usd = 0.0

    def record_inference_request(
        self, 
        ttft_ms: float, 
        tokens_count: int, 
        duration_sec: float, 
        cost_usd: float = 0.0,
        status: str = "SUCCESS"
    ):
        self.total_requests += 1
        if status == "SUCCESS":
            self.successful_requests += 1
            self.ttft_records_ms.append(ttft_ms)
            self.total_tokens_served += tokens_count
            self.cumulative_cost_usd += cost_usd

            if duration_sec > 0:
                tps = tokens_count / duration_sec
                self.tps_records.append(tps)
        elif status == "BACKPRESSURE_FULL":
            self.backpressure_rejections += 1
            self.failed_requests += 1
        else:
            self.failed_requests += 1

    def get_snapshot(self) -> ServingMetricsSnapshot:
        """Calculates real-time P95/P99 latency and SLO compliance metrics."""
        ttfts = np.array(self.ttft_records_ms) if self.ttft_records_ms else np.array([0.0])
        tpss = np.array(self.tps_records) if self.tps_records else np.array([0.0])

        avg_ttft = float(np.mean(ttfts))
        p95_ttft = float(np.percentile(ttfts, 95))
        p99_ttft = float(np.percentile(ttfts, 99))
        avg_tps = float(np.mean(tpss))

        # SLO Compliance Calculation (% of requests with TTFT <= 500ms)
        slo_met_count = sum(1 for t in self.ttft_records_ms if t <= self.ttft_slo_target_ms)
        slo_compliance = round((slo_met_count / len(self.ttft_records_ms) * 100.0) if self.ttft_records_ms else 100.0, 2)

        return ServingMetricsSnapshot(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            backpressure_rejections=self.backpressure_rejections,
            avg_ttft_ms=round(avg_ttft, 2),
            p95_ttft_ms=round(p95_ttft, 2),
            p99_ttft_ms=round(p99_ttft, 2),
            avg_tps=round(avg_tps, 2),
            total_tokens_served=self.total_tokens_served,
            cumulative_cost_usd=round(self.cumulative_cost_usd, 6),
            slo_compliance_pct=slo_compliance
        )

    def create_trace_context(self, request_id: str) -> Dict[str, str]:
        """Generates OpenTelemetry W3C Trace Context headers (trace_id, span_id) for distributed tracing."""
        import uuid
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        return {
            "traceparent": f"00-{trace_id}-{span_id}-01",
            "trace_id": trace_id,
            "span_id": span_id,
            "request_id": request_id
        }

    def export_prometheus_metrics(self) -> str:
        """Exports metrics in standard Prometheus text exposition format."""
        snapshot = self.get_snapshot()
        return f"""# HELP llm_serving_requests_total Total serving requests
# TYPE llm_serving_requests_total counter
llm_serving_requests_total{{status="success"}} {snapshot.successful_requests}
llm_serving_requests_total{{status="backpressure_rejected"}} {snapshot.backpressure_rejections}

# HELP llm_ttft_seconds Time to First Token latency
# TYPE llm_ttft_seconds gauge
llm_ttft_seconds{{quantile="0.95"}} {snapshot.p95_ttft_ms / 1000.0}
llm_ttft_seconds{{quantile="0.99"}} {snapshot.p99_ttft_ms / 1000.0}

# HELP llm_tps_tokens_per_second Serving throughput tokens per second
# TYPE llm_tps_tokens_per_second gauge
llm_tps_tokens_per_second {snapshot.avg_tps}

# HELP llm_token_cost_usd Total estimated token cost in USD
# TYPE llm_token_cost_usd counter
llm_token_cost_usd {snapshot.cumulative_cost_usd}
"""
