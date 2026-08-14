# 🎤 Staff AI Platform Interview Guide: K8s KubeRay & Kueue Multi-Tenant GPU Scheduling

This guide bridges **Project 17 (`17-k8s-kuberay-kueue-gpu-operator`)** to Staff/Principal-level questions on Kubernetes GPU orchestration and NVIDIA MIG.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "When would you use NVIDIA MIG vs. Time-Slicing vs. MPS in Kubernetes?"
> **Staff Engineer Answer**:
> "In `src/k8s_gpu_manager.py`, Multi-Instance GPU (MIG) physically partitions an H100 into up to 7 hardware-isolated instances with dedicated memory paths for hard multi-tenant isolation. Time-slicing shares compute temporally without isolation. MPS shares CUDA contexts for high small-batch compute density."

### Q2: "How does Kueue priority preemption guarantee GPU resources for real-time inference?"
> **Staff Engineer Answer**:
> "Kueue ClusterQueue evaluates incoming PriorityClasses. High-priority inference workloads preempt lower-priority batch training jobs, releasing GPU capacity immediately."

### Q3: "How does KubeRay manage distributed Ray cluster lifecycle on Kubernetes?"
> **Staff Engineer Answer**:
> "The KubeRay operator reconciles RayCluster Custom Resources, managing head and worker pod provisioning, auto-scaling, and zero-downtime rolling upgrades."
