import pytest
from src.benchmarks.metrics import MetricsCalculator
from src.benchmarks.engine import BenchmarkEngine

def test_01_metrics_empty_results():
    stats = MetricsCalculator.calculate([], 100.0, 100.0)
    assert stats["total_requests"] == 0
    assert stats["successful_requests"] == 0
    assert stats["failed_requests"] == 0
    assert stats["mean_ttft_ms"] == 0.0
    assert stats["tokens_per_sec"] == 0.0

def test_02_metrics_calculations():
    results = [
        {"success": True, "ttft_ms": 50.0, "tpot_ms": 10.0, "duration_ms": 250.0, "tokens": 20},
        {"success": True, "ttft_ms": 150.0, "tpot_ms": 20.0, "duration_ms": 350.0, "tokens": 10},
        {"success": False, "ttft_ms": 0.0, "tpot_ms": 0.0, "duration_ms": 500.0, "tokens": 0}
    ]
    stats = MetricsCalculator.calculate(results, 50.0, 60.0)
    assert stats["total_requests"] == 3
    assert stats["successful_requests"] == 2
    assert stats["failed_requests"] == 1
    assert stats["mean_ttft_ms"] == 100.0  # (50 + 150) / 2
    assert stats["mean_tpot_ms"] == 15.0   # (10 + 20) / 2
    assert stats["memory_delta_mb"] == 10.0

def test_03_system_memory_retrieval():
    mem = MetricsCalculator.get_system_memory_mb()
    assert isinstance(mem, float)
    assert mem > 0.0

@pytest.mark.asyncio
async def test_04_benchmark_engine_mock_run():
    engine = BenchmarkEngine(concurrency=2, model_name="mock-model")
    res = await engine.run_single_request("Test prompt", 1)
    assert "ttft_ms" in res
    assert "tpot_ms" in res
    assert "tokens" in res
    assert isinstance(res["success"], bool)
