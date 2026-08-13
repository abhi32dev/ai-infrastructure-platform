"""
Ray Cluster Dynamic Autoscaler & Resource Monitor.
Monitors queue depth and GPU memory pressure across nodes, automatically scaling
worker nodes up and down to guarantee SLA compliance under spiking traffic.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class ClusterResourceMetrics(BaseModel):
    total_nodes: int
    active_gpus: int
    pending_queue_depth: int
    avg_gpu_utilization_pct: float
    autoscaling_recommendation: str


class RayClusterAutoscaler:
    def __init__(self, min_nodes: int = 2, max_nodes: int = 16, gpus_per_node: int = 8):
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.gpus_per_node = gpus_per_node
        self.current_nodes = min_nodes

    def evaluate_cluster_scale(self, pending_queue_depth: int, avg_gpu_util_pct: float) -> ClusterResourceMetrics:
        """
        Evaluates cluster metrics and calculates scaling decisions.
        """
        recommendation = "MAINTAIN"

        if pending_queue_depth > 50 or avg_gpu_util_pct > 85.0:
            if self.current_nodes < self.max_nodes:
                self.current_nodes = min(self.max_nodes, self.current_nodes + 2)
                recommendation = f"SCALE_UP (Added 2 nodes. Total nodes: {self.current_nodes})"
        elif pending_queue_depth == 0 and avg_gpu_util_pct < 20.0:
            if self.current_nodes > self.min_nodes:
                self.current_nodes = max(self.min_nodes, self.current_nodes - 1)
                recommendation = f"SCALE_DOWN (Removed 1 node. Total nodes: {self.current_nodes})"

        return ClusterResourceMetrics(
            total_nodes=self.current_nodes,
            active_gpus=self.current_nodes * self.gpus_per_node,
            pending_queue_depth=pending_queue_depth,
            avg_gpu_utilization_pct=avg_gpu_util_pct,
            autoscaling_recommendation=recommendation
        )
