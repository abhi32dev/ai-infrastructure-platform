"""
CLI Demo Runner for Project 17 - K8s Cloud-Native GPU Operator (KubeRay, Kueue & MIG).
"""

from src.k8s_gpu_orchestrator import K8sGPUCloudNativeOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 17: K8s Cloud-Native GPU Operator (KubeRay, Kueue & MIG)")
    print("==================================================================")
    orch = K8sGPUCloudNativeOrchestrator()
    res = orch.deploy_k8s_ai_workload("prod-kuberay-cluster")
    print(f"Status: {res['status']} | Cluster: {res['cluster_name']}")
    print(f"CRD: {res['crd_kind']} | Kueue Job Status: {res['kueue_status']} ({res['gpus_allocated']} GPUs)")
    print(f"NVIDIA MIG Slice: {res['mig_profile']} ({res['mig_vram_gb']} GB VRAM)")
    print("==================================================================")
