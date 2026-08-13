"""
Marquez / DataHub Lineage Graph Visualizer & Dependency Tracker.
Maintains dataset lineage graphs ($Dataset_A \rightarrow Job_1 \rightarrow Dataset_B$) for auditability.
"""

from typing import Dict, List, Set
from pydantic import BaseModel, Field


class DatasetLineageGraph(BaseModel):
    total_datasets: int
    total_jobs: int
    lineage_edges: List[str]


class MarquezLineageTracker:
    def __init__(self):
        self.datasets: Set[str] = set()
        self.jobs: Set[str] = set()
        self.edges: List[str] = []

    def record_job_lineage(self, job_name: str, inputs: List[str], outputs: List[str]) -> None:
        self.jobs.add(job_name)
        for inp in inputs:
            self.datasets.add(inp)
            self.edges.append(f"{inp} -> [{job_name}]")
        for out in outputs:
            self.datasets.add(out)
            self.edges.append(f"[{job_name}] -> {out}")

    def export_graph_summary(self) -> DatasetLineageGraph:
        return DatasetLineageGraph(
            total_datasets=len(self.datasets),
            total_jobs=len(self.jobs),
            lineage_edges=self.edges
        )
