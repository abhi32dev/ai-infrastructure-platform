import time
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
    """Simulates compute-heavy prompt ingestion GPU worker pool."""
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
    """Simulates GPUDirect RDMA / high-speed socket KV cache transfer."""
    @staticmethod
    def transfer_rdma(kv_cache_id: str, size_bytes: int, target_gpu: str, force_fail: bool = False) -> float:
        if force_fail:
            raise ConnectionError("RDMA QP Queue Timeout")
        # 100 Gbps network: transfer time ~ 0.5ms to 2.0ms
        latency = 0.5 + (size_bytes / (1024 * 1024 * 1024)) * 10.0
        return round(latency, 2)

class DisaggregatedRouter:
    """Disaggregated Prefill vs. Decode Serving & Handoff Router."""
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
