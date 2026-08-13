"""
Expanded Test Suite for Project 11 - Distributed Training (PyTorch FSDP & Megatron 3D Parallelism).
Tests FSDP ZeRO-3 memory sharding calculations, Megatron-LM 3D grid rank allocations (TP*PP*DP),
NCCL All-Reduce bus bandwidth saturation, and cross-node network bottlenecks.
"""

import pytest
from src.fsdp_sharder import FSDPSharder, FSDPShardingConfig
from src.megatron_parallelism import MegatronParallelismEngine
from src.nccl_communicator import NCCLCommunicatorProfiler
from src.training_orchestrator import DistributedTrainingOrchestrator


@pytest.fixture
def fsdp():
    return FSDPSharder(FSDPShardingConfig(model_name="Llama-70B", total_params_billions=70.0, num_gpus=16))


@pytest.fixture
def megatron():
    return MegatronParallelismEngine(tensor_parallel_size=2, pipeline_parallel_size=2, data_parallel_size=4)


@pytest.fixture
def nccl():
    return NCCLCommunicatorProfiler()


@pytest.fixture
def orchestrator():
    return DistributedTrainingOrchestrator(model_name="Llama-70B", num_nodes=2, gpus_per_node=8)


def test_01_fsdp_memory_sharding_calculation(fsdp):
    """Test 1: Verifies FSDP ZeRO-3 memory reduction per GPU rank."""
    state = fsdp.calculate_fsdp_sharding_memory()
    assert state.total_vram_required_gb == 1120.0  # 70B * 16GB = 1120GB total
    assert state.vram_per_gpu_gb == 70.0          # 1120GB / 16 GPUs = 70GB per GPU
    assert state.memory_savings_pct == 93.75       # (1 - 1/16) = 93.75% savings


def test_02_fsdp_cpu_offloading_savings():
    """Test 2: Verifies memory reduction when CPU offloading is enabled."""
    fsdp_offload = FSDPSharder(FSDPShardingConfig(
        model_name="Llama-70B", total_params_billions=70.0, num_gpus=16, cpu_offload=True
    ))
    state = fsdp_offload.calculate_fsdp_sharding_memory()
    assert state.vram_per_gpu_gb < 70.0


def test_03_megatron_3d_rank_grid(megatron):
    """Test 3: Verifies Megatron 3D Parallelism rank coordinates (TP=2, PP=2, DP=4)."""
    grid = megatron.build_3d_rank_grid()
    assert grid.world_size == 16
    assert len(grid.rank_assignments) == 16
    
    rank_0_coords = megatron.get_rank_coordinates(0)
    assert rank_0_coords == {"tp_rank": 0, "pp_rank": 0, "dp_rank": 0}


def test_04_megatron_rank_out_of_bounds_error(megatron):
    """Test 4: Verifies exception handling when querying invalid global rank."""
    with pytest.raises(ValueError):
        megatron.get_rank_coordinates(99)


def test_05_nccl_allreduce_bandwidth_profiling(nccl):
    """Test 5: Verifies NCCL NVLink intra-node All-Reduce bandwidth computation."""
    metrics = nccl.profile_collective_op("ALL_REDUCE", data_size_mb=100.0, num_ranks=8, is_cross_node=False)
    assert metrics.bus_bandwidth_gbps > 800.0
    assert metrics.network_interconnect == "NVLink_4"
    assert metrics.is_network_bottleneck is False


def test_06_nccl_cross_node_bottleneck_detection(nccl):
    """Test 6: Verifies InfiniBand network bottleneck flag on heavy cross-node transfers."""
    metrics = nccl.profile_collective_op("ALL_REDUCE", data_size_mb=800.0, num_ranks=16, is_cross_node=True)
    assert metrics.network_interconnect == "InfiniBand_400G"
    assert metrics.is_network_bottleneck is True


def test_07_orchestrator_training_step(orchestrator):
    """Test 7: Verifies end-to-end distributed training step execution."""
    res = orchestrator.run_training_step(batch_size=16)
    assert res["status"] == "STEP_COMPLETED"
    assert res["world_size"] == 16
    assert res["3d_grid"]["tp"] == 2


def test_08_fsdp_small_cluster_scaling():
    """Test 8: Verifies FSDP memory allocation on single-node 4-GPU setup."""
    fsdp_4gpu = FSDPSharder(FSDPShardingConfig(model_name="Llama-8B", total_params_billions=8.0, num_gpus=4))
    state = fsdp_4gpu.calculate_fsdp_sharding_memory()
    assert state.vram_per_gpu_gb == 32.0
