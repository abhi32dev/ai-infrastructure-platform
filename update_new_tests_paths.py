import os

base_dir = "/Users/abhi/Documents/Antigravity"

p21_test = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.multi_lora_engine import (
    MultiLoRAEngine,
    LoRAAdapterConfig,
    MultiLoRARequest,
    LoRACacheManager
)

@pytest.fixture
def engine():
    eng = MultiLoRAEngine(max_vram_mb=150.0)
    for i in range(5):
        eng.register_adapter(LoRAAdapterConfig(adapter_id=f"adapter_{i}", size_mb=50.0))
    return eng

def test_01_cache_miss_and_dynamic_load(engine):
    reqs = [MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1, 2, 3])]
    res = engine.serve_batch(reqs)
    assert res.status == "SUCCESS"
    assert res.cache_misses == 1
    assert "adapter_0" in engine.cache_mgr.cached_adapters

def test_02_cache_hit_on_subsequent_request(engine):
    reqs1 = [MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1, 2, 3])]
    engine.serve_batch(reqs1)
    reqs2 = [MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[4, 5, 6])]
    res2 = engine.serve_batch(reqs2)
    assert res2.cache_hits == 1
    assert res2.cache_misses == 0

def test_03_lru_eviction_under_vram_pressure(engine):
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_1", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_2", prompt_tokens=[1])])
    assert len(engine.cache_mgr.cached_adapters) == 3

    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_3", prompt_tokens=[1])])
    assert "adapter_0" not in engine.cache_mgr.cached_adapters
    assert "adapter_3" in engine.cache_mgr.cached_adapters

def test_04_multi_tenant_batch_segmented_gemm(engine):
    reqs = [
        MultiLoRARequest(adapter_id="adapter_1", prompt_tokens=[1]),
        MultiLoRARequest(adapter_id="adapter_2", prompt_tokens=[2]),
        MultiLoRARequest(adapter_id=None, prompt_tokens=[3])
    ]
    res = engine.serve_batch(reqs)
    assert res.batch_size == 3
    assert len(res.adapters_used) == 3

def test_05_base_model_only_requests(engine):
    reqs = [MultiLoRARequest(adapter_id=None, prompt_tokens=[10, 20])]
    res = engine.serve_batch(reqs)
    assert res.adapters_used == ["base_model"]
    assert res.cache_hits == 0
    assert res.cache_misses == 0

def test_06_unregistered_adapter_fallback(engine):
    reqs = [MultiLoRARequest(adapter_id="unknown_lora", prompt_tokens=[1])]
    res = engine.serve_batch(reqs)
    assert res.status == "SUCCESS"
    assert "unknown_lora" in engine.cache_mgr.cached_adapters

def test_07_lru_update_order(engine):
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_1", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_2", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_3", prompt_tokens=[1])])
    assert "adapter_0" in engine.cache_mgr.cached_adapters
    assert "adapter_1" not in engine.cache_mgr.cached_adapters

def test_08_empty_batch_handling(engine):
    res = engine.serve_batch([])
    assert res.batch_size == 0
    assert res.status == "SUCCESS"

def test_09_vram_full_flag():
    mgr = LoRACacheManager(max_vram_mb=100.0)
    mgr.load_adapter(LoRAAdapterConfig(adapter_id="a1", size_mb=50.0))
    assert not mgr.is_full()
    mgr.load_adapter(LoRAAdapterConfig(adapter_id="a2", size_mb=50.0))
    assert mgr.is_full()

def test_10_high_concurrency_batch(engine):
    reqs = [MultiLoRARequest(adapter_id=f"adapter_{i%3}", prompt_tokens=[i]) for i in range(30)]
    res = engine.serve_batch(reqs)
    assert res.batch_size == 30

def test_11_latency_budget_check(engine):
    reqs = [MultiLoRARequest(adapter_id="adapter_1", prompt_tokens=[1])]
    res = engine.serve_batch(reqs)
    assert res.latency_ms > 0.0

def test_12_schema_validation():
    adapter = LoRAAdapterConfig(adapter_id="test", rank=16, alpha=32.0)
    assert adapter.rank == 16
    assert adapter.alpha == 32.0
"""

p22_test = """import sys
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
"""

p23_test = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.fp8_gemm_engine import (
    FP8GEMMEngine,
    FP8Format,
    DynamicScaler,
    HopperFP8Kernel
)

@pytest.fixture
def engine():
    return FP8GEMMEngine(fp8_format=FP8Format.E4M3)

def test_01_standard_fp8_gemm_execution(engine):
    res = engine.execute_gemm(m=2048, n=4096, k=4096, amax_a=12.0, amax_b=8.5)
    assert res["status"] == "HOPPER_FP8_OPTIMIZED"
    assert "1.86x" in res["speedup"]
    assert res["tflops"] > 1800.0

def test_02_dynamic_scaler_normal_range():
    scale = DynamicScaler.calculate_scale(amax=10.0, fp8_max=448.0)
    assert scale == 44.8

def test_03_dynamic_scaler_zero_or_nan():
    scale_zero = DynamicScaler.calculate_scale(amax=0.0)
    scale_nan = DynamicScaler.calculate_scale(amax=float('nan'))
    assert scale_zero == 1.0
    assert scale_nan == 1.0

def test_04_scale_factor_validation():
    assert DynamicScaler.validate_factors(10.0)
    assert not DynamicScaler.validate_factors(1e-6)
    assert not DynamicScaler.validate_factors(1e8)

def test_05_recalibration_on_invalid_scale(engine):
    res = engine.execute_gemm(m=1024, n=1024, k=1024, amax_a=1e10, amax_b=1e10)
    assert res["scale_a"] == 1.0
    assert res["scale_b"] == 1.0

def test_06_e5m2_format_initialization():
    eng_grad = FP8GEMMEngine(fp8_format=FP8Format.E5M2)
    assert eng_grad.fp8_format == FP8Format.E5M2

def test_07_hopper_kernel_flops_calculation():
    res = HopperFP8Kernel.execute_fp8_gemm(m=1000, n=1000, k=1000, scale_a=1.0, scale_b=1.0)
    assert res["flops"] == 2.0 * 1000 * 1000 * 1000

def test_08_sub_microsecond_gemm_execution(engine):
    res = engine.execute_gemm(m=512, n=512, k=512, amax_a=5.0, amax_b=5.0)
    assert res["exec_time_us"] > 0.0

def test_09_speedup_ratio_validation(engine):
    res = engine.execute_gemm(m=4096, n=4096, k=4096, amax_a=20.0, amax_b=20.0)
    assert "x" in res["speedup"]

def test_10_large_batch_matrix_dimensions(engine):
    res = engine.execute_gemm(m=8192, n=8192, k=8192, amax_a=15.0, amax_b=15.0)
    assert res["tflops"] == 1840.5

def test_11_scaler_boundary_values():
    assert DynamicScaler.validate_factors(1e-4)
    assert DynamicScaler.validate_factors(1e6)

def test_12_output_schema_keys(engine):
    res = engine.execute_gemm(m=1024, n=1024, k=1024, amax_a=1.0, amax_b=1.0)
    for key in ["status", "fp8_format", "scale_a", "scale_b", "tflops", "speedup"]:
        assert key in res
"""

p24_test = """import sys
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
"""

p25_test = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.medusa_verifier import (
    MedusaVerifier,
    MedusaCandidate,
    MedusaHeadPredictor,
    TreeAttentionVerifier
)

@pytest.fixture
def verifier():
    return MedusaVerifier(num_heads=4)

def test_01_all_candidates_accepted(verifier):
    gt = [101, 102, 103, 104]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 4
    assert res.status == "MEDUSA_MAX_ACCELERATION"
    assert res.speedup_multiplier == 2.85

def test_02_partial_candidates_accepted(verifier):
    gt = [101, 102, 999, 104]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 2
    assert res.accepted_token_ids == [101, 102]
    assert res.status == "MEDUSA_PARTIAL_ACCELERATION"

def test_03_zero_candidates_accepted(verifier):
    gt = [999, 999, 999, 999]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 0
    assert res.speedup_multiplier == 1.0
    assert res.status == "FALLBACK_SINGLE_TOKEN"

def test_04_candidate_generation_count():
    cands = MedusaHeadPredictor.predict_candidates(50, num_heads=4)
    assert len(cands) == 4
    assert cands[0].token_id == 51
    assert cands[3].token_id == 54

def test_05_tree_attention_early_stopping():
    cands = [MedusaCandidate(head_index=i, token_id=i+1, confidence=0.9) for i in range(4)]
    count, accepted = TreeAttentionVerifier.verify_tree(cands, [1, 2, 99, 4])
    assert count == 2
    assert accepted == [1, 2]

def test_06_tree_attention_empty_ground_truth():
    cands = [MedusaCandidate(head_index=0, token_id=1, confidence=0.9)]
    count, accepted = TreeAttentionVerifier.verify_tree(cands, [])
    assert count == 0
    assert accepted == []

def test_07_custom_head_count():
    v = MedusaVerifier(num_heads=2)
    res = v.generate_speculative(10, [11, 12])
    assert res.heads_verified == 2

def test_08_schema_validation():
    cand = MedusaCandidate(head_index=0, token_id=10, confidence=0.95)
    assert cand.head_index == 0
    assert cand.token_id == 10

def test_09_confidence_decay():
    cands = MedusaHeadPredictor.predict_candidates(10, num_heads=4)
    assert cands[0].confidence > cands[3].confidence

def test_10_speedup_calculation_two_tokens(verifier):
    res = verifier.generate_speculative(100, [101, 102, 0, 0])
    assert res.speedup_multiplier == 1.90

def test_11_single_head_prediction():
    cands = MedusaHeadPredictor.predict_candidates(1, num_heads=1)
    assert len(cands) == 1

def test_12_medusa_result_schema(verifier):
    res = verifier.generate_speculative(100, [101])
    assert hasattr(res, "tokens_accepted")
    assert hasattr(res, "speedup_multiplier")
    assert hasattr(res, "status")
"""

with open(os.path.join(base_dir, "21-vllm-multi-lora-dynamic-serving", "tests", "test_multi_lora.py"), "w") as f:
    f.write(p21_test)
with open(os.path.join(base_dir, "22-disaggregated-prefill-decode-engine", "tests", "test_disaggregated.py"), "w") as f:
    f.write(p22_test)
with open(os.path.join(base_dir, "23-fp8-mixed-precision-gemm-engine", "tests", "test_fp8_gemm.py"), "w") as f:
    f.write(p23_test)
with open(os.path.join(base_dir, "24-nccl-distributed-collective-profiler", "tests", "test_nccl_profiler.py"), "w") as f:
    f.write(p24_test)
with open(os.path.join(base_dir, "25-speculative-medusa-multi-head-verifier", "tests", "test_medusa_verifier.py"), "w") as f:
    f.write(p25_test)

print("Updated test files with sys.path.insert for standalone and master runner compatibility!")
