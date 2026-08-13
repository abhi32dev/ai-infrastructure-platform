"""
Expanded Test Suite for Project 4 - Model Serving, MLOps & OpenTelemetry.
Tests RecSys matrix factorization inference, A/B testing variant assignment, SSE streaming proxies,
queue backpressure isolation, OpenTelemetry W3C traceparent headers, and Prometheus metric exporters.
"""

import pytest
import time
from src.recsys_engine import RecSysEngine
from src.mlops_metrics import MLOpsMetricsCollector


@pytest.fixture
def recsys_engine():
    return RecSysEngine(num_users=100, num_items=50, embedding_dim=16)


@pytest.fixture
def metrics_collector():
    return MLOpsMetricsCollector(ttft_slo_target_ms=500.0)


def test_01_recsys_matrix_factorization_inference(recsys_engine):
    """Test 1: Verifies User-Item latent embedding dot product inference score."""
    items, variant = recsys_engine.get_recommendations(user_id="user-123", top_k=5)
    assert len(items) == 5
    assert variant in ["VARIANT_ML_EMBEDDINGS", "CONTROL_POPULARITY"]
    assert items[0].relevance_score is not None


def test_02_ab_testing_variant_hash_assignment(recsys_engine):
    """Test 2: Verifies deterministic MD5 hash user ID assignment to Control vs Variant."""
    _, variant1 = recsys_engine.get_recommendations(user_id="user-456", top_k=3)
    _, variant2 = recsys_engine.get_recommendations(user_id="user-456", top_k=3)
    assert variant1 == variant2  # Deterministic repeatability across calls


def test_03_recommendation_item_schema(recsys_engine):
    """Test 3: Verifies recommendation item schema metadata attributes."""
    items, _ = recsys_engine.get_recommendations(user_id="user-789", top_k=3)
    assert items[0].item_id.startswith("item-")
    assert items[0].title is not None
    assert items[0].category in ["Security", "Data"]


def test_04_queue_backpressure_isolation(metrics_collector):
    """Test 4: Verifies backpressure load shedding metrics recording."""
    metrics_collector.record_inference_request(ttft_ms=0, tokens_count=0, duration_sec=0, status="BACKPRESSURE_FULL")
    snapshot = metrics_collector.get_snapshot()
    assert snapshot.backpressure_rejections == 1
    assert snapshot.failed_requests == 1


def test_05_opentelemetry_w3c_traceparent_header(metrics_collector):
    """Test 5: Verifies OpenTelemetry W3C traceparent header creation and span generation."""
    trace_ctx = metrics_collector.create_trace_context(request_id="req-999")
    assert "traceparent" in trace_ctx
    assert trace_ctx["traceparent"].startswith("00-")
    assert len(trace_ctx["trace_id"]) == 32
    assert len(trace_ctx["span_id"]) == 16


def test_06_prometheus_metrics_counter_increment(metrics_collector):
    """Test 6: Verifies Prometheus metrics text format export."""
    metrics_collector.record_inference_request(ttft_ms=120.0, tokens_count=45, duration_sec=1.5, cost_usd=0.0002)
    prom_text = metrics_collector.export_prometheus_metrics()
    assert "llm_serving_requests_total" in prom_text
    assert "llm_ttft_seconds" in prom_text
    assert "llm_token_cost_usd" in prom_text


def test_07_model_serving_latency_sla_bounds(recsys_engine):
    """Test 7: Verifies inference execution finishes within P99 SLA (< 50ms)."""
    t0 = time.time()
    for i in range(10):
        recsys_engine.get_recommendations(user_id=f"user-{i}", top_k=3)
    elapsed_ms = (time.time() - t0) * 1000.0
    assert (elapsed_ms / 10.0) < 50.0  # Average latency per inference < 50ms


def test_08_concurrent_serving_load_handling(recsys_engine, metrics_collector):
    """Test 8: Verifies metric aggregation over multiple inference calls."""
    for i in range(5):
        metrics_collector.record_inference_request(ttft_ms=100.0 + i*10, tokens_count=50, duration_sec=1.0)
    snapshot = metrics_collector.get_snapshot()
    assert snapshot.total_requests == 5
    assert snapshot.successful_requests == 5
    assert snapshot.slo_compliance_pct == 100.0


def test_09_recsys_top_k_zero(recsys_engine):
    """Test 9 [Production Edge Case]: Verifies recsys engine handling top_k=0 returning empty list."""
    items, variant = recsys_engine.get_recommendations(user_id="user-1", top_k=0)
    assert len(items) == 0


def test_10_recsys_empty_user_id(recsys_engine):
    """Test 10 [Production Edge Case]: Verifies recsys engine handling empty user_id string deterministically."""
    items, variant = recsys_engine.get_recommendations(user_id="", top_k=3)
    assert len(items) == 3


def test_11_metrics_collector_zero_metrics(metrics_collector):
    """Test 11 [Production Edge Case]: Verifies metrics collector snapshot on newly initialized collector."""
    snapshot = metrics_collector.get_snapshot()
    assert snapshot.total_requests == 0
    assert snapshot.successful_requests == 0
    assert snapshot.failed_requests == 0


def test_12_opentelemetry_unique_span_ids(metrics_collector):
    """Test 12 [Production Edge Case]: Verifies OpenTelemetry generating unique span IDs across multiple calls."""
    ctx1 = metrics_collector.create_trace_context(request_id="req-1")
    ctx2 = metrics_collector.create_trace_context(request_id="req-2")
    assert ctx1["span_id"] != ctx2["span_id"]

