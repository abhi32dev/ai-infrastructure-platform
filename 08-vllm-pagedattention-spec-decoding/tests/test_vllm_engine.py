"""
Expanded Test Suite for Project 8 - vLLM, PagedAttention & Speculative Decoding.
Tests PagedAttention physical GPU block allocation (16 tokens/block), logical-to-physical page table mapping,
0.0% VRAM memory fragmentation, Speculative Decoding ~2.67x speedup, and continuous batching schedulers.
"""

import pytest
from src.paged_kv_cache import PagedKVCacheManager
from src.speculative_decoder import SpeculativeDecoder
from src.continuous_batcher import ContinuousBatcher, RequestPhase


@pytest.fixture
def kv_manager():
    return PagedKVCacheManager(num_gpu_blocks=64, block_size=16)


@pytest.fixture
def spec_decoder():
    return SpeculativeDecoder(spec_k=4)


@pytest.fixture
def batcher():
    return ContinuousBatcher(max_batch_size=8)


def test_01_paged_attention_physical_block_allocator(kv_manager):
    """Test 1: Verifies PagedAttention physical GPU block allocation (16 tokens/block)."""
    table = kv_manager.allocate_blocks_for_request(request_id="req-108", num_tokens=45)
    assert len(table.physical_block_ids) == 3  # ceil(45 / 16) = 3 blocks
    util = kv_manager.get_gpu_memory_utilization()
    assert util["allocated_blocks"] == 3
    assert util["free_blocks"] == 61


def test_02_logical_to_physical_page_mapping(kv_manager):
    """Test 2: Verifies logical sequence token mapping to physical block table indices."""
    table = kv_manager.allocate_blocks_for_request(request_id="req-201", num_tokens=35)
    assert table.request_id == "req-201"
    assert table.logical_block_ids == [0, 1, 2]
    assert len(table.physical_block_ids) == 3


def test_03_zero_vram_fragmentation_guarantee(kv_manager):
    """Test 3: Verifies 0.0% VRAM memory fragmentation calculation."""
    kv_manager.allocate_blocks_for_request("req-301", num_tokens=100)
    util = kv_manager.get_gpu_memory_utilization()
    assert util["vram_fragmentation_pct"] == 0.0  # Zero external fragmentation!


def test_04_speculative_decoding_speedup(spec_decoder):
    """Test 4: Verifies Speculative Decoding (1B Draft + 70B Target parallel pass) ~2.67x speedup."""
    res = spec_decoder.execute_speculative_step(prompt="Explain PagedAttention KV-cache")
    assert res.speedup_factor >= 2.0
    assert res.accepted_count == 3
    assert len(res.draft_tokens) == 4


def test_05_continuous_batching_scheduler(batcher):
    """Test 5: Verifies continuous batching scheduler iteration step and phase transitions."""
    batcher.submit_request(request_id="req-1", prompt="Query 1", max_tokens=2)
    batcher.submit_request(request_id="req-2", prompt="Query 2", max_tokens=2)
    
    step1 = batcher.step_iteration()
    assert step1["active_batch_size"] == 2
    assert step1["waiting_queue_size"] == 0

    step2 = batcher.step_iteration()
    assert step2["completed_this_step"] == 2


def test_06_paged_attention_free_blocks(kv_manager):
    """Test 6: Verifies freeing physical blocks upon sequence completion."""
    kv_manager.allocate_blocks_for_request("req-temp", num_tokens=32)
    assert kv_manager.get_gpu_memory_utilization()["allocated_blocks"] == 2
    
    kv_manager.free_request_blocks("req-temp")
    assert kv_manager.get_gpu_memory_utilization()["allocated_blocks"] == 0


def test_07_block_allocator_out_of_memory_handling(kv_manager):
    """Test 7: Verifies block allocator handling GPU VRAM saturation gracefully."""
    # Allocate all 64 blocks (64 * 16 = 1024 tokens)
    kv_manager.allocate_blocks_for_request("req-oom", num_tokens=1024)
    assert kv_manager.get_gpu_memory_utilization()["free_blocks"] == 0

    # Next allocation should raise OutOfMemory error
    with pytest.raises(MemoryError):
        kv_manager.allocate_blocks_for_request("req-fail", num_tokens=16)


def test_08_batch_concurrency_scaling(kv_manager):
    """Test 8: Verifies parallel block allocation across 10 concurrent sequences."""
    for i in range(10):
        kv_manager.allocate_blocks_for_request(f"req-batch-{i}", num_tokens=32)
    util = kv_manager.get_gpu_memory_utilization()
    assert util["allocated_blocks"] == 20  # 10 reqs * 2 blocks = 20 blocks
