"""
Master Kubernetes Cloud-Native GPU Operator & Scheduling Orchestrator.
Integrates KubeRay CRD spec generation, Kueue Priority Queueing, and NVIDIA MIG fractional GPU slicing.
"""

from typing import Any, Dict
from src.kuberay_crd import KubeRayCRDManager, RayClusterCRD
from src.kueue_job_scheduler import KueueJobScheduler, KueueJobStatus
from src.mig_gpu_slicer import MIGGPUSlicer, MIGInstance


class K8sGPUCloudNativeOrchestrator:
    def __init__(self, namespace: str = "ai-platform"):
        self.kuberay = KubeRayCRDManager(namespace=namespace)
        self.kueue = KueueJobScheduler(cluster_gpu_capacity=32)
        self.mig_slicer = MIGGPUSlicer()

    def deploy_k8s_ai_workload(self, cluster_name: str, priority_class: str = "HIGH_PRIORITY") -> Dict[str, Any]:
        """Synthesizes KubeRay CRD, schedules job via Kueue, and provisions MIG GPU slice."""
        crd = self.kuberay.generate_raycluster_crd_spec(name=cluster_name, replicas=4, gpus_per_worker=4)
        crd_yaml = self.kuberay.to_yaml_dict(crd)

        job_status = self.kueue.submit_kueue_job(job_name=f"{cluster_name}-job", priority_class=priority_class, gpus_requested=16)
        mig_slice = self.mig_slicer.partition_gpu("2g.20gb")

        return {
            "status": "WORKLOAD_DEPLOYED",
            "cluster_name": cluster_name,
            "crd_kind": crd_yaml["kind"],
            "kueue_status": job_status.status,
            "gpus_allocated": job_status.gpus_allocated,
            "mig_profile": mig_slice.mig_profile,
            "mig_vram_gb": mig_slice.vram_gb
        }
