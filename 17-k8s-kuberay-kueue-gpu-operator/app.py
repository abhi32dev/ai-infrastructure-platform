"""
FastAPI REST Service for Project 17 - K8s Cloud-Native GPU Operator (KubeRay, Kueue & MIG).
"""

from fastapi import FastAPI
from src.k8s_gpu_orchestrator import K8sGPUCloudNativeOrchestrator

app = FastAPI(title="Project 17 - K8s Cloud-Native GPU Operator", version="2.0")
orchestrator = K8sGPUCloudNativeOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "K8s Cloud-Native GPU Operator"}


@app.post("/k8s/deploy")
def deploy_workload(cluster_name: str = "kuberay-cluster-01"):
    return orchestrator.deploy_k8s_ai_workload(cluster_name=cluster_name)
