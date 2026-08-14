import sys
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
