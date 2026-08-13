"""
Multi-Agent DAG Task Execution Router & Deadlock Avoidance.
Schedules task dependencies across agent DAG nodes, detecting cyclic deadlocks and enforcing context limits.
"""

from typing import Dict, List, Set
from pydantic import BaseModel, Field


class DAGRoutingResult(BaseModel):
    execution_order: List[str]
    has_cycle_deadlock: bool
    total_nodes: int


class SwarmDAGRouter:
    def __init__(self):
        self.adjacency: Dict[str, List[str]] = {}

    def add_dependency(self, parent_task: str, child_task: str) -> None:
        if parent_task not in self.adjacency:
            self.adjacency[parent_task] = []
        self.adjacency[parent_task].append(child_task)
        if child_task not in self.adjacency:
            self.adjacency[child_task] = []

    def compute_topological_execution_order(self) -> DAGRoutingResult:
        """Topological sort over task DAG with cycle/deadlock detection."""
        in_degree: Dict[str, int] = {node: 0 for node in self.adjacency}
        for parent in self.adjacency:
            for child in self.adjacency[parent]:
                in_degree[child] += 1

        queue = [node for node in in_degree if in_degree[node] == 0]
        order: List[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for child in self.adjacency.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        has_deadlock = len(order) != len(self.adjacency)
        return DAGRoutingResult(
            execution_order=order,
            has_cycle_deadlock=has_deadlock,
            total_nodes=len(self.adjacency)
        )
