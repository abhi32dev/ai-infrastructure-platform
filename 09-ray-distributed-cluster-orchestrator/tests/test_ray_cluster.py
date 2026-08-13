"""
Expanded Test Suite for Project 9 - Ray Distributed Cluster & Multi-GPU Orchestrator.
Tests stateful Ray Actor pools, Plasma zero-copy shared memory object stores, dynamic cluster autoscaler queue depth,
worker actor fault-tolerant recovery, and multi-GPU task fan-out execution.
"""

import pytest
from src.ray_actor_pool import DistributedRayActorPool
from src.cluster_autoscaler import RayClusterAutoscaler
from src.ray_cluster_manager import RayClusterOrchestrator


@pytest.fixture
def actor_pool():
    return DistributedRayActorPool(num_nodes=4, gpus_per_node=8)


@pytest.fixture
def autoscaler():
    return RayClusterAutoscaler(min_nodes=2, max_nodes=16, gpus_per_node=8)


@pytest.fixture
def cluster_orch():
    return RayClusterOrchestrator()


def test_01_ray_actor_pool_initialization(actor_pool):
    """Test 1: Verifies multi-GPU worker actor pool initialization (4 nodes, 32 GPUs)."""
    assert len(actor_pool.actors) == 32
    assert actor_pool.actors["actor-001"].status == "ALIVE"


def test_02_stateful_actor_task_dispatch(actor_pool):
    """Test 2: Verifies stateful Ray Actor worker task dispatching."""
    res = actor_pool.dispatch_task(task_name="EMBEDDING_INFERENCE", object_ref_id="obj-001")
    assert res["status"] == "SUCCESS"
    assert res["executed_by_actor"] == "actor-001"


def test_03_plasma_zero_copy_shared_memory(actor_pool):
    """Test 3: Verifies Plasma zero-copy shared memory object store tensor payload referencing."""
    ref = actor_pool.put_object_in_plasma(object_id="tensor_matrix_v1", payload_size_bytes=67108864)
    assert ref.object_id == "tensor_matrix_v1"
    assert ref.is_in_plasma_store is True
    assert ref.size_bytes == 67108864


def test_04_cluster_autoscaler_scale_up(autoscaler):
    """Test 4: Verifies dynamic cluster autoscaling scale-up when queue depth exceeds threshold."""
    metrics = autoscaler.evaluate_cluster_scale(pending_queue_depth=100, avg_gpu_util_pct=90.0)
    assert "SCALE_UP" in metrics.autoscaling_recommendation
    assert metrics.total_nodes > 2


def test_05_cluster_autoscaler_scale_down(autoscaler):
    """Test 5: Verifies cluster autoscaler scaling down idle worker nodes when queue is empty."""
    autoscaler.current_nodes = 6
    metrics = autoscaler.evaluate_cluster_scale(pending_queue_depth=0, avg_gpu_util_pct=10.0)
    assert "SCALE_DOWN" in metrics.autoscaling_recommendation
    assert metrics.total_nodes < 6


def test_06_actor_failure_and_state_recovery(actor_pool):
    """Test 6: Verifies worker actor failure detection and state recovery on backup nodes."""
    restarted = actor_pool.simulate_node_failure_and_recover("ray-node-04")
    assert len(restarted) == 8
    assert actor_pool.actors["actor-032"].node_id == "ray-node-01"


def test_07_cluster_orchestrator_execution(cluster_orch):
    """Test 7: Verifies cluster orchestrator task submission and Plasma ref creation."""
    ref = cluster_orch.submit_shared_tensor("tensor-101", size_mb=128.0)
    assert ref.object_id == "tensor-101"
    res = cluster_orch.run_distributed_task("FINETUNE_PASS", "tensor-101")
    assert res["status"] == "SUCCESS"


def test_08_distributed_task_fan_out_throughput(actor_pool):
    """Test 8: Verifies distributed task fan-out execution across multiple actors."""
    for i in range(5):
        res = actor_pool.dispatch_task(task_name=f"task-{i}", object_ref_id=f"obj-{i}")
        assert res["status"] == "SUCCESS"
