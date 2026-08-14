import time
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
    """Manages dynamic GPU VRAM allocation and LRU eviction for LoRA adapters."""
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
    """Simulates fused multi-tenant segmented GEMM execution."""
    @staticmethod
    def execute_batch(requests: List[MultiLoRARequest], active_adapters: Dict[str, LoRAAdapterConfig]) -> float:
        # Latency model: base latency 4ms + 0.5ms per distinct active adapter
        distinct_adapters = len(set(r.adapter_id for r in requests if r.adapter_id))
        latency = 4.0 + (distinct_adapters * 0.5)
        return latency

class MultiLoRAEngine:
    """Multi-Tenant LoRA Adapter Hot-Swapping & Zero-Stall Batching Engine."""
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
