import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.nccl_profiler import (
    NCCLProfiler,
    CollectiveType,
    BandwidthAnalyzer,
    StragglerDetector
)

@pytest.fixture
def profiler():
    return NCCLProfiler(world_size=8, nvlink_peak_gb=900.0)

def test_01_optimal_nccl_profile(profiler):
    latencies = [1.2, 1.21, 1.19, 1.20, 1.21, 1.20, 1.19, 1.20]
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, message_size_mb=500.0, per_rank_latencies_ms=latencies)
    assert res["status"] in ["OPTIMAL_COMMUNICATION", "BANDWIDTH_BOTTLENECK"]
    assert len(res["straggler_ranks"]) == 0

def test_02_straggler_rank_detection(profiler):
    latencies = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.8]
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, message_size_mb=100.0, per_rank_latencies_ms=latencies)
    assert res["status"] == "STRAGGLER_RANK_DETECTED"
    assert 7 in res["straggler_ranks"]

def test_03_bus_bandwidth_formula():
    bus_bw = BandwidthAnalyzer.calculate_bus_bw(CollectiveType.ALL_REDUCE, 1e9, 1.0, 8)
    assert round(bus_bw, 2) == 1.75

def test_04_reduce_scatter_factor():
    bus_bw = BandwidthAnalyzer.calculate_bus_bw(CollectiveType.REDUCE_SCATTER, 1e9, 1.0, 8)
    assert round(bus_bw, 3) == 0.875

def test_05_zero_latency_protection():
    bw = BandwidthAnalyzer.calculate_bus_bw(CollectiveType.ALL_REDUCE, 1e6, 0.0, 8)
    assert bw == 0.0

def test_06_straggler_empty_list():
    res = StragglerDetector.detect_stragglers([])
    assert not res["straggler_detected"]

def test_07_all_gather_profiling(profiler):
    latencies = [0.8] * 8
    res = profiler.profile_collectives(CollectiveType.ALL_GATHER, message_size_mb=200.0, per_rank_latencies_ms=latencies)
    assert res["collective"] == CollectiveType.ALL_GATHER

def test_08_high_bandwidth_saturation(profiler):
    latencies = [0.1] * 8
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, message_size_mb=50.0, per_rank_latencies_ms=latencies)
    assert res["bus_bandwidth_gbs"] > 0.0

def test_09_multiple_stragglers():
    latencies = [1.0, 1.0, 2.5, 1.0, 1.0, 2.8, 1.0, 1.0]
    res = StragglerDetector.detect_stragglers(latencies, max_variance_pct=10.0)
    assert 2 in res["straggler_ranks"]
    assert 5 in res["straggler_ranks"]

def test_10_world_size_configuration():
    p16 = NCCLProfiler(world_size=16)
    assert p16.world_size == 16

def test_11_mean_latency_reported(profiler):
    latencies = [2.0, 4.0]
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, 10.0, latencies)
    assert res["mean_latency_ms"] == 3.0

def test_12_schema_completeness(profiler):
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, 10.0, [1.0]*8)
    for k in ["status", "collective", "world_size", "bus_bandwidth_gbs", "nvlink_saturation_pct"]:
        assert k in res
