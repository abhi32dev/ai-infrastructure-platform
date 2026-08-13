# Project 17: K8s Cloud-Native GPU Operator & Job Scheduler (KubeRay, Kueue & MIG)

Cloud-native Kubernetes GPU orchestration platform managing **KubeRay Operator CRDs** (RayCluster / RayJob), **Kubernetes Kueue Priority Job Queueing & Preemption**, and **NVIDIA MIG Fractional GPU Partitioning**.

---

## 🛠️ Architecture Components
- **KubeRay CRD Manager**: Synthesizes production RayCluster Custom Resource Definitions.
- **Kueue Job Scheduler**: Enforces multi-tenant cluster GPU quotas and pre-empts batch workloads for high-priority production jobs.
- **NVIDIA MIG Slicer**: Partitions A100/H100 GPUs into hardware-isolated instances (1g.10gb, 2g.20gb).

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```
