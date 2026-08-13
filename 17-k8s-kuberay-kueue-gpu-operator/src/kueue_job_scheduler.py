"""
Kubernetes Kueue Priority Queueing & Multi-Tenant GPU Preemption Engine.
Manages LocalQueues and ClusterQueues, admitting high-priority ML jobs while preempting low-priority batches.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class KueueJobStatus(BaseModel):
    job_name: str
    priority_class: str  # HIGH_PRIORITY, MEDIUM, BATCH
    status: str          # ADMITTED, QUEUED, PREEMPTED
    gpus_allocated: int


class KueueJobScheduler:
    def __init__(self, cluster_gpu_capacity: int = 32):
        self.capacity = cluster_gpu_capacity
        self.allocated_gpus = 0
        self.active_jobs: Dict[str, KueueJobStatus] = {}

    def submit_kueue_job(self, job_name: str, priority_class: str, gpus_requested: int) -> KueueJobStatus:
        """Admits job if quota available, or preempts lower priority jobs if needed."""
        if self.allocated_gpus + gpus_requested <= self.capacity:
            self.allocated_gpus += gpus_requested
            status = KueueJobStatus(
                job_name=job_name, priority_class=priority_class, status="ADMITTED", gpus_allocated=gpus_requested
            )
            self.active_jobs[job_name] = status
            return status

        # Try preemption of BATCH jobs for HIGH_PRIORITY
        if priority_class == "HIGH_PRIORITY":
            for jname, job in list(self.active_jobs.items()):
                if job.priority_class == "BATCH" and job.status == "ADMITTED":
                    job.status = "PREEMPTED"
                    self.allocated_gpus -= job.gpus_allocated
                    if self.allocated_gpus + gpus_requested <= self.capacity:
                        self.allocated_gpus += gpus_requested
                        status = KueueJobStatus(
                            job_name=job_name, priority_class=priority_class, status="ADMITTED", gpus_allocated=gpus_requested
                        )
                        self.active_jobs[job_name] = status
                        return status

        status = KueueJobStatus(
            job_name=job_name, priority_class=priority_class, status="QUEUED", gpus_allocated=0
        )
        return status
