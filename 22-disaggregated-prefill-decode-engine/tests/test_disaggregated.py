import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.disaggregated_engine import (
    DisaggregatedRouter,
    DisaggregatedRequest,
    RequestPhase,
    PrefillWorkerPool,
    KVCacheTransferClient
)

@pytest.fixture
def router():
    return DisaggregatedRouter()

def test_01_standard_prefill_handoff(router):
    req = DisaggregatedRequest(prompt="Explain CUDA kernels", tokens=[1]*50)
    res = router.route_request(req)
    assert res.status == "RDMA_OK"
    assert res.kv_cache_size_bytes > 0
    assert res.ttft_ms > 0.0

def test_02_direct_decode_routing(router):
    req = DisaggregatedRequest(prompt="", tokens=[1], phase=RequestPhase.DECODE, kv_cache_id="kv_123")
    res = router.route_request(req)
    assert res.status == "DIRECT_DECODE_ACTIVE"
    assert res.prefill_gpu_id == "BYPASSED"

def test_03_rdma_fallback_to_tcp_socket(router):
    req = DisaggregatedRequest(prompt="Stress test", tokens=[1]*100)
    res = router.route_request(req, force_rdma_fail=True)
    assert res.status == "TCP_FALLBACK_OK"
    assert res.rdma_latency_ms == 5.5

def test_04_kv_cache_size_scaling():
    pool = PrefillWorkerPool()
    req_small = DisaggregatedRequest(prompt="a", tokens=[1]*10)
    req_large = DisaggregatedRequest(prompt="b", tokens=[1]*1000)
    res_small = pool.compute_prefill(req_small)
    res_large = pool.compute_prefill(req_large)
    assert res_large["kv_cache_size_bytes"] > res_small["kv_cache_size_bytes"]

def test_05_ttft_computation():
    pool = PrefillWorkerPool()
    req = DisaggregatedRequest(prompt="c", tokens=[1]*200)
    res = pool.compute_prefill(req)
    assert res["ttft_ms"] == 20.0

def test_06_rdma_client_latency_calculation():
    lat = KVCacheTransferClient.transfer_rdma("kv_01", 1024*1024*100, "gpu-02")
    assert lat > 0.0

def test_07_empty_token_prefill(router):
    req = DisaggregatedRequest(prompt="", tokens=[])
    res = router.route_request(req)
    assert res.status == "RDMA_OK"
    assert res.kv_cache_size_bytes == 0

def test_08_multiple_decode_gpu_targets(router):
    assert len(router.decode_gpus) >= 2

def test_09_unique_request_id_generation():
    req1 = DisaggregatedRequest(prompt="1", tokens=[1])
    req2 = DisaggregatedRequest(prompt="2", tokens=[2])
    assert req1.request_id != req2.request_id

def test_10_heavy_context_prefill(router):
    req = DisaggregatedRequest(prompt="long context", tokens=[1]*4096)
    res = router.route_request(req)
    assert res.kv_cache_size_bytes == 4096 * 16 * 1024

def test_11_rdma_exception_handling():
    with pytest.raises(ConnectionError):
        KVCacheTransferClient.transfer_rdma("kv_x", 100, "gpu-x", force_fail=True)

def test_12_schema_validation():
    req = DisaggregatedRequest(prompt="hello", tokens=[101, 102])
    assert req.phase == RequestPhase.PREFILL
