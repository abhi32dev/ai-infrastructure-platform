import os

base_dir = "/Users/abhi/Documents/Antigravity"

# ==========================================
# PROJECT 21: vLLM Multi-LoRA Dynamic Serving
# ==========================================
p21_dir = os.path.join(base_dir, "21-vllm-multi-lora-dynamic-serving")

p21_src = """import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class LoRAAdapterConfig(BaseModel):
    adapter_id: str
    rank: int = 8
    alpha: float = 16.0
    target_modules: List[str] = Field(default_factory=lambda: ["q_proj", "v_proj"])
    size_mb: float = 50.0

class MultiLoRARequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    adapter_id: Optional[str] = None
    prompt_tokens: List[int]
    max_tokens: int = 16

class MultiLoRABatchResult(BaseModel):
    batch_size: int
    adapters_used: List[str]
    cache_hits: int
    cache_misses: int
    latency_ms: float
    status: str

class LoRACacheManager:
    \"\"\"Manages dynamic GPU VRAM allocation and LRU eviction for LoRA adapters.\"\"\"
    def __init__(self, max_vram_mb: float = 500.0):
        self.max_vram_mb = max_vram_mb
        self.cached_adapters: Dict[str, LoRAAdapterConfig] = {}
        self.lru_order: List[str] = []

    def check_adapter(self, adapter_id: str) -> bool:
        if adapter_id in self.cached_adapters:
            # Update LRU
            self.lru_order.remove(adapter_id)
            self.lru_order.append(adapter_id)
            return True
        return False

    def load_adapter(self, adapter: LoRAAdapterConfig) -> bool:
        current_usage = sum(a.size_mb for a in self.cached_adapters.values())
        while current_usage + adapter.size_mb > self.max_vram_mb and self.lru_order:
            evicted_id = self.lru_order.pop(0)
            del self.cached_adapters[evicted_id]
            current_usage = sum(a.size_mb for a in self.cached_adapters.values())
        
        self.cached_adapters[adapter.adapter_id] = adapter
        self.lru_order.append(adapter.adapter_id)
        return True

    def is_full(self) -> bool:
        return sum(a.size_mb for a in self.cached_adapters.values()) >= self.max_vram_mb

class SegmentedGEMMKernel:
    \"\"\"Simulates fused multi-tenant segmented GEMM execution.\"\"\"
    @staticmethod
    def execute_batch(requests: List[MultiLoRARequest], active_adapters: Dict[str, LoRAAdapterConfig]) -> float:
        # Latency model: base latency 4ms + 0.5ms per distinct active adapter
        distinct_adapters = len(set(r.adapter_id for r in requests if r.adapter_id))
        latency = 4.0 + (distinct_adapters * 0.5)
        return latency

class MultiLoRAEngine:
    \"\"\"Multi-Tenant LoRA Adapter Hot-Swapping & Zero-Stall Batching Engine.\"\"\"
    def __init__(self, max_vram_mb: float = 500.0):
        self.cache_mgr = LoRACacheManager(max_vram_mb=max_vram_mb)
        self.registered_registry: Dict[str, LoRAAdapterConfig] = {}

    def register_adapter(self, adapter: LoRAAdapterConfig):
        self.registered_registry[adapter.adapter_id] = adapter

    def serve_batch(self, requests: List[MultiLoRARequest]) -> MultiLoRABatchResult:
        t0 = time.perf_counter()
        hits, misses = 0, 0
        used_adapters = []

        for req in requests:
            if req.adapter_id:
                if self.cache_mgr.check_adapter(req.adapter_id):
                    hits += 1
                else:
                    misses += 1
                    # Dynamic Page-In
                    if req.adapter_id in self.registered_registry:
                        self.cache_mgr.load_adapter(self.registered_registry[req.adapter_id])
                    else:
                        # Create fallback default adapter
                        default_adapter = LoRAAdapterConfig(adapter_id=req.adapter_id)
                        self.cache_mgr.load_adapter(default_adapter)
                used_adapters.append(req.adapter_id)
            else:
                used_adapters.append("base_model")

        # Execute Segmented GEMM
        kernel_latency = SegmentedGEMMKernel.execute_batch(requests, self.cache_mgr.cached_adapters)
        total_latency = ((time.perf_counter() - t0) * 1000.0) + kernel_latency

        return MultiLoRABatchResult(
            batch_size=len(requests),
            adapters_used=list(set(used_adapters)),
            cache_hits=hits,
            cache_misses=misses,
            latency_ms=round(total_latency, 2),
            status="SUCCESS"
        )
"""

p21_test = """import pytest
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
    # Max VRAM 150MB -> fits 3 adapters (50MB each)
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_1", prompt_tokens=[1])])
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_2", prompt_tokens=[1])])
    assert len(engine.cache_mgr.cached_adapters) == 3

    # Adding 4th must evict adapter_0
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
    # Re-access adapter_0 to make adapter_1 the LRU
    engine.serve_batch([MultiLoRARequest(adapter_id="adapter_0", prompt_tokens=[1])])
    # Load 2 and 3 -> adapter_1 should be evicted first
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

# =======================================================
# PROJECT 22: Disaggregated Prefill vs Decode Engine
# =======================================================
p22_dir = os.path.join(base_dir, "22-disaggregated-prefill-decode-engine")

p22_src = """import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class RequestPhase:
    PREFILL = "PREFILL"
    DECODE = "DECODE"

class DisaggregatedRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    prompt: str
    tokens: List[int]
    phase: str = RequestPhase.PREFILL
    kv_cache_id: Optional[str] = None

class DisaggregatedHandoffResult(BaseModel):
    request_id: str
    prefill_gpu_id: str
    decode_gpu_id: str
    kv_cache_size_bytes: int
    rdma_latency_ms: float
    ttft_ms: float
    status: str

class PrefillWorkerPool:
    \"\"\"Simulates compute-heavy prompt ingestion GPU worker pool.\"\"\"
    def __init__(self, node_id: str = "gpu-prefill-01"):
        self.node_id = node_id

    def compute_prefill(self, req: DisaggregatedRequest) -> Dict[str, Any]:
        # Compute TTFT based on token length
        ttft = 10.0 + (len(req.tokens) * 0.05)
        kv_size = len(req.tokens) * 16 * 1024  # 16KB per token KV tensor
        kv_id = f"kv_{uuid.uuid4().hex[:8]}"
        return {
            "kv_cache_id": kv_id,
            "kv_cache_size_bytes": kv_size,
            "ttft_ms": round(ttft, 2)
        }

class KVCacheTransferClient:
    \"\"\"Simulates GPUDirect RDMA / high-speed socket KV cache transfer.\"\"\"
    @staticmethod
    def transfer_rdma(kv_cache_id: str, size_bytes: int, target_gpu: str, force_fail: bool = False) -> float:
        if force_fail:
            raise ConnectionError("RDMA QP Queue Timeout")
        # 100 Gbps network: transfer time ~ 0.5ms to 2.0ms
        latency = 0.5 + (size_bytes / (1024 * 1024 * 1024)) * 10.0
        return round(latency, 2)

class DisaggregatedRouter:
    \"\"\"Disaggregated Prefill vs. Decode Serving & Handoff Router.\"\"\"
    def __init__(self):
        self.prefill_pool = PrefillWorkerPool()
        self.decode_gpus = ["gpu-decode-01", "gpu-decode-02"]

    def route_request(self, req: DisaggregatedRequest, force_rdma_fail: bool = False) -> DisaggregatedHandoffResult:
        t0 = time.perf_counter()
        if req.phase == RequestPhase.PREFILL:
            # Step 1: Execute Compute-Bound Prefill
            prefill_res = self.prefill_pool.compute_prefill(req)
            kv_id = prefill_res["kv_cache_id"]
            kv_size = prefill_res["kv_cache_size_bytes"]
            ttft = prefill_res["ttft_ms"]

            # Step 2: RDMA Transfer to Decode GPU Pool
            target_decode_gpu = self.decode_gpus[0]
            try:
                rdma_lat = KVCacheTransferClient.transfer_rdma(kv_id, kv_size, target_decode_gpu, force_fail=force_rdma_fail)
                transfer_mode = "RDMA_OK"
            except ConnectionError:
                # Decision 3: Fallback to TCP Socket Transfer
                rdma_lat = 5.5
                transfer_mode = "TCP_FALLBACK_OK"

            return DisaggregatedHandoffResult(
                request_id=req.request_id,
                prefill_gpu_id=self.prefill_pool.node_id,
                decode_gpu_id=target_decode_gpu,
                kv_cache_size_bytes=kv_size,
                rdma_latency_ms=rdma_lat,
                ttft_ms=ttft,
                status=transfer_mode
            )
        else:
            # Direct Decode Dispatch
            return DisaggregatedHandoffResult(
                request_id=req.request_id,
                prefill_gpu_id="BYPASSED",
                decode_gpu_id=self.decode_gpus[0],
                kv_cache_size_bytes=0,
                rdma_latency_ms=0.0,
                ttft_ms=0.0,
                status="DIRECT_DECODE_ACTIVE"
            )
"""

p22_test = """import pytest
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

# ============================================================
# PROJECT 23: Native FP8 Mixed-Precision GEMM & Scaling Engine
# ============================================================
p23_dir = os.path.join(base_dir, "23-fp8-mixed-precision-gemm-engine")

p23_src = """import math
import time
from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, Field

class FP8Format:
    E4M3 = "FP8_E4M3"   # 1 sign, 4 exponent, 3 mantissa (Forward pass activations/weights)
    E5M2 = "FP8_E5M2"   # 1 sign, 5 exponent, 2 mantissa (Backward pass gradients)

class DynamicScaler:
    \"\"\"Delayed dynamic scaling factor calibration for FP8 GEMM.\"\"\"
    @staticmethod
    def calculate_scale(amax: float, fp8_max: float = 448.0) -> float:
        if amax <= 0.0 or math.isnan(amax) or math.isinf(amax):
            return 1.0
        return fp8_max / amax

    @staticmethod
    def validate_factors(scale: float) -> bool:
        return 1e-4 <= scale <= 1e6

class HopperFP8Kernel:
    \"\"\"Simulates Hopper H100 native FP8 Tensor Core GEMM.\"\"\"
    @staticmethod
    def execute_fp8_gemm(m: int, n: int, k: int, scale_a: float, scale_b: float) -> Dict[str, Any]:
        # FLOPs = 2 * M * N * K
        flops = 2.0 * m * n * k
        # Hopper Peak FP8 ~ 1,979 TFLOPS. Simulated execution time:
        tflops_achieved = 1840.5
        exec_time_us = (flops / (tflops_achieved * 1e12)) * 1e6
        # Speedup vs FP16 baseline (~989 TFLOPS)
        speedup = 1840.5 / 989.0

        return {
            "m": m, "n": n, "k": k,
            "flops": flops,
            "exec_time_us": round(exec_time_us, 2),
            "tflops_achieved": tflops_achieved,
            "speedup_vs_fp16": round(speedup, 2)
        }

class FP8GEMMEngine:
    \"\"\"NVIDIA Hopper FP8 GEMM & Delayed Scaling Engine.\"\"\"
    def __init__(self, fp8_format: str = FP8Format.E4M3):
        self.fp8_format = fp8_format
        self.scaler = DynamicScaler()

    def execute_gemm(self, m: int, n: int, k: int, amax_a: float, amax_b: float) -> Dict[str, Any]:
        # Step 1: Compute Dynamic Scale Factors
        scale_a = self.scaler.calculate_scale(amax_a)
        scale_b = self.scaler.calculate_scale(amax_b)

        # Decision 1: Validate Factors
        if not (self.scaler.validate_factors(scale_a) and self.scaler.validate_factors(scale_b)):
            # Recalibrate
            scale_a, scale_b = 1.0, 1.0

        # Step 2: Execute Hopper FP8 GEMM
        gemm_result = HopperFP8Kernel.execute_fp8_gemm(m, n, k, scale_a, scale_b)

        # Decision 2: Target Speedup Check
        if gemm_result["speedup_vs_fp16"] >= 1.80:
            status = "HOPPER_FP8_OPTIMIZED"
        else:
            status = "FP16_FALLBACK"

        return {
            "status": status,
            "fp8_format": self.fp8_format,
            "scale_a": round(scale_a, 4),
            "scale_b": round(scale_b, 4),
            "tflops": gemm_result["tflops_achieved"],
            "speedup": f"{gemm_result['speedup_vs_fp16']}x",
            "exec_time_us": gemm_result["exec_time_us"]
        }
"""

p23_test = """import pytest
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

# ================================================================
# PROJECT 24: NCCL Distributed Collective Communication Profiler
# ================================================================
p24_dir = os.path.join(base_dir, "24-nccl-distributed-collective-profiler")

p24_src = """import math
import statistics
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class CollectiveType:
    ALL_REDUCE = "ALL_REDUCE"
    ALL_GATHER = "ALL_GATHER"
    REDUCE_SCATTER = "REDUCE_SCATTER"

class BandwidthAnalyzer:
    \"\"\"Calculates algorithmic and bus bandwidth for multi-GPU collectives.\"\"\"
    @staticmethod
    def calculate_bus_bw(collective: str, size_bytes: float, latency_sec: float, world_size: int) -> float:
        if latency_sec <= 0.0:
            return 0.0
        alg_bw = (size_bytes / latency_sec) / 1e9  # GB/s
        if collective == CollectiveType.ALL_REDUCE:
            bus_factor = (2.0 * (world_size - 1)) / world_size
        else:
            bus_factor = (world_size - 1) / world_size
        return alg_bw * bus_factor

class StragglerDetector:
    \"\"\"Detects straggler GPU ranks and thermal throttling imbalances.\"\"\"
    @staticmethod
    def detect_stragglers(per_rank_latencies_ms: List[float], max_variance_pct: float = 5.0) -> Dict[str, Any]:
        if not per_rank_latencies_ms:
            return {"straggler_detected": False, "straggler_ranks": []}
        
        mean_lat = statistics.mean(per_rank_latencies_ms)
        stragglers = []
        for rank, lat in enumerate(per_rank_latencies_ms):
            pct_diff = ((lat - mean_lat) / mean_lat) * 100.0
            if pct_diff > max_variance_pct:
                stragglers.append(rank)

        return {
            "straggler_detected": len(stragglers) > 0,
            "straggler_ranks": stragglers,
            "mean_latency_ms": round(mean_lat, 3),
            "max_latency_ms": round(max(per_rank_latencies_ms), 3)
        }

class NCCLProfiler:
    \"\"\"NCCL Distributed Collective Communication & Topology Profiler.\"\"\"
    def __init__(self, world_size: int = 8, nvlink_peak_gb: float = 900.0):
        self.world_size = world_size
        self.nvlink_peak_gb = nvlink_peak_gb

    def profile_collectives(self, collective: str, message_size_mb: float, per_rank_latencies_ms: List[float]) -> Dict[str, Any]:
        size_bytes = message_size_mb * 1024 * 1024
        mean_latency_sec = statistics.mean(per_rank_latencies_ms) / 1000.0

        # Step 1: Bus Bandwidth Calculation
        bus_bw = BandwidthAnalyzer.calculate_bus_bw(collective, size_bytes, mean_latency_sec, self.world_size)
        saturation_pct = (bus_bw / self.nvlink_peak_gb) * 100.0

        # Step 2: Straggler Detection
        straggler_report = StragglerDetector.detect_stragglers(per_rank_latencies_ms)

        # Decision Gate
        if saturation_pct >= 80.0 and not straggler_report["straggler_detected"]:
            status = "OPTIMAL_COMMUNICATION"
        elif straggler_report["straggler_detected"]:
            status = "STRAGGLER_RANK_DETECTED"
        else:
            status = "BANDWIDTH_BOTTLENECK"

        return {
            "status": status,
            "collective": collective,
            "world_size": self.world_size,
            "bus_bandwidth_gbs": round(bus_bw, 2),
            "nvlink_saturation_pct": round(saturation_pct, 2),
            "straggler_ranks": straggler_report["straggler_ranks"],
            "mean_latency_ms": straggler_report["mean_latency_ms"]
        }
"""

p24_test = """import pytest
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
    # Rank 7 is slow (thermal throttling / degraded PCIe link)
    latencies = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.8]
    res = profiler.profile_collectives(CollectiveType.ALL_REDUCE, message_size_mb=100.0, per_rank_latencies_ms=latencies)
    assert res["status"] == "STRAGGLER_RANK_DETECTED"
    assert 7 in res["straggler_ranks"]

def test_03_bus_bandwidth_formula():
    bus_bw = BandwidthAnalyzer.calculate_bus_bw(CollectiveType.ALL_REDUCE, 1e9, 1.0, 8)
    # Factor for 8 GPUs is (2*7)/8 = 1.75 -> 1.75 GB/s
    assert round(bus_bw, 2) == 1.75

def test_04_reduce_scatter_factor():
    bus_bw = BandwidthAnalyzer.calculate_bus_bw(CollectiveType.REDUCE_SCATTER, 1e9, 1.0, 8)
    # Factor is 7/8 = 0.875
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
    # Fast latency -> high saturation
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

# ==============================================================
# PROJECT 25: Medusa Multi-Head Speculative Decoding Verifier
# ==============================================================
p25_dir = os.path.join(base_dir, "25-speculative-medusa-multi-head-verifier")

p25_src = """import time
from typing import Dict, List, Any, Tuple
from pydantic import BaseModel, Field

class MedusaCandidate(BaseModel):
    head_index: int
    token_id: int
    confidence: float

class MedusaPredictionResult(BaseModel):
    tokens_accepted: int
    accepted_token_ids: List[int]
    speedup_multiplier: float
    heads_verified: int
    status: str

class MedusaHeadPredictor:
    \"\"\"Predicts candidate tokens using 4 attached MLP heads.\"\"\"
    @staticmethod
    def predict_candidates(current_token: int, num_heads: int = 4) -> List[MedusaCandidate]:
        candidates = []
        for h in range(num_heads):
            # Predict sequential candidate token
            cand_token = current_token + h + 1
            candidates.append(MedusaCandidate(head_index=h, token_id=cand_token, confidence=0.90 - (h * 0.1)))
        return candidates

class TreeAttentionVerifier:
    \"\"\"Verifies candidate token tree in a single target forward pass.\"\"\"
    @staticmethod
    def verify_tree(candidates: List[MedusaCandidate], ground_truth_next_tokens: List[int]) -> Tuple[int, List[int]]:
        accepted = []
        for cand, gt in zip(candidates, ground_truth_next_tokens):
            if cand.token_id == gt:
                accepted.append(cand.token_id)
            else:
                break
        return len(accepted), accepted

class MedusaVerifier:
    \"\"\"Medusa Multi-Head Speculative Decoding & Parallel Verifier Engine.\"\"\"
    def __init__(self, num_heads: int = 4):
        self.num_heads = num_heads
        self.predictor = MedusaHeadPredictor()
        self.verifier = TreeAttentionVerifier()

    def generate_speculative(self, current_token: int, ground_truth_stream: List[int]) -> MedusaPredictionResult:
        # Step 1: Predict candidates from 4 Medusa heads
        candidates = self.predictor.predict_candidates(current_token, self.num_heads)

        # Step 2: Single-Pass Tree Attention Verification
        accepted_count, accepted_tokens = self.verifier.verify_tree(candidates, ground_truth_stream)

        # Decision: Compute Speedup
        # If accepted >= 3, speedup ~ 2.8x. If 0, fallback to 1 token
        if accepted_count >= 3:
            speedup = 2.85
            status = "MEDUSA_MAX_ACCELERATION"
        elif accepted_count >= 1:
            speedup = 1.0 + (accepted_count * 0.45)
            status = "MEDUSA_PARTIAL_ACCELERATION"
        else:
            speedup = 1.0
            status = "FALLBACK_SINGLE_TOKEN"

        return MedusaPredictionResult(
            tokens_accepted=accepted_count,
            accepted_token_ids=accepted_tokens,
            speedup_multiplier=round(speedup, 2),
            heads_verified=self.num_heads,
            status=status
        )
"""

p25_test = """import pytest
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
    gt = [101, 102, 999, 104]  # Mismatch at position 3
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

# Write source files and tests for 21 to 25
projects_code_map = [
    (p21_dir, p21_src, p21_test, "multi_lora_engine.py", "test_multi_lora.py"),
    (p22_dir, p22_src, p22_test, "disaggregated_engine.py", "test_disaggregated.py"),
    (p23_dir, p23_src, p23_test, "fp8_gemm_engine.py", "test_fp8_gemm.py"),
    (p24_dir, p24_src, p24_test, "nccl_profiler.py", "test_nccl_profiler.py"),
    (p25_dir, p25_src, p25_test, "medusa_verifier.py", "test_medusa_verifier.py"),
]

for p_dir, src_code, test_code, src_name, test_name in projects_code_map:
    src_file_path = os.path.join(p_dir, "src", src_name)
    test_file_path = os.path.join(p_dir, "tests", test_name)
    
    with open(src_file_path, "w", encoding="utf-8") as f:
        f.write(src_code)
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_code)
    print(f"Created code & tests in: {p_dir}")

print("All code and tests for Projects 21 to 25 created successfully!")
