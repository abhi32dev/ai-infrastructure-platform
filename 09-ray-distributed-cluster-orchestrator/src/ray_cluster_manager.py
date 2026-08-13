"""
Master Ray Distributed Cluster Orchestrator.
Integrates Ray Actor Worker Pools, Plasma Zero-Copy Shared Memory, and Dynamic Autoscaling.
"""

from typing import Any, Dict, List
from src.cluster_autoscaler import ClusterResourceMetrics, RayClusterAutoscaler
from src.ray_actor_pool import DistributedRayActorPool, RayObjectRef


class RayClusterOrchestrator:
    def __init__(self, num_nodes: int = 4, gpus_per_node: int = 8):
        print("[RAY CLUSTER] Initializing Ray Distributed Compute Platform...")
        self.actor_pool = DistributedRayActorPool(num_nodes=num_nodes, gpus_per_node=gpus_per_node)
        self.autoscaler = RayClusterAutoscaler(min_nodes=num_nodes, max_nodes=16, gpus_per_node=gpus_per_node)

    def submit_shared_tensor(self, object_id: str, size_mb: float) -> RayObjectRef:
        """Puts object reference into Plasma zero-copy memory."""
        return self.actor_pool.put_object_in_plasma(object_id, int(size_mb * 1024 * 1024))

    def run_distributed_task(self, task_name: str, object_ref_id: str) -> Dict[str, Any]:
        """Dispatches distributed task to Ray Actor."""
        return self.actor_pool.dispatch_task(task_name, object_ref_id)

    def evaluate_autoscaling(self, queue_depth: int, gpu_util_pct: float) -> ClusterResourceMetrics:
        """Evaluates autoscaling recommendations."""
        return self.autoscaler.evaluate_cluster_scale(queue_depth, gpu_util_pct)

    def simulate_failure_recovery(self, failed_node_id: str) -> List[str]:
        """Recovers actors on node death."""
        return self.actor_pool.simulate_node_failure_and_recover(failed_node_id)
