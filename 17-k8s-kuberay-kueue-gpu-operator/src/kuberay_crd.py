"""
KubeRay Custom Resource Definition (CRD) Spec Generator & Cluster Monitor.
Generates Kubernetes YAML manifests for RayCluster and RayJob CRDs, tracking head node and worker pod health.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RayClusterCRD(BaseModel):
    name: str
    namespace: str
    ray_version: str = "2.35.0"
    head_node_cpu: int = 4
    head_node_memory_gb: int = 16
    worker_group_replicas: int
    gpus_per_worker: int


class KubeRayCRDManager:
    def __init__(self, namespace: str = "ai-platform"):
        self.namespace = namespace

    def generate_raycluster_crd_spec(self, name: str, replicas: int = 4, gpus_per_worker: int = 8) -> RayClusterCRD:
        return RayClusterCRD(
            name=name,
            namespace=self.namespace,
            worker_group_replicas=replicas,
            gpus_per_worker=gpus_per_worker
        )

    def to_yaml_dict(self, crd: RayClusterCRD) -> Dict[str, Any]:
        return {
            "apiVersion": "ray.io/v1000",
            "kind": "RayCluster",
            "metadata": {"name": crd.name, "namespace": crd.namespace},
            "spec": {
                "rayVersion": crd.ray_version,
                "headGroupSpec": {"template": {"spec": {"containers": [{"name": "ray-head", "resources": {"limits": {"cpu": crd.head_node_cpu, "memory": f"{crd.head_node_memory_gb}Gi"}}}]}}},
                "workerGroupSpecs": [{"replicas": crd.worker_group_replicas, "template": {"spec": {"containers": [{"name": "ray-worker", "resources": {"limits": {"nvidia.com/gpu": crd.gpus_per_worker}}}]}}}]
            }
        }
