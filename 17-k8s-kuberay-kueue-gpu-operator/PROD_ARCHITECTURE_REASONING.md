# Production Architecture & Design Trade-offs: K8s GPU Operator & Scheduler (KubeRay, Kueue & MIG)

## 1. Executive Context & Business Motivation
Deploying distributed AI workloads on Kubernetes multi-tenant clusters requires cloud-native job scheduling, priority queuing, preemption of low-priority batch jobs during peak production demand, and fractional GPU slicing.

This platform implements **KubeRay Cluster CRDs, Kubernetes Kueue Priority Scheduler, and NVIDIA MIG Fractional GPU Slicing**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Kubernetes Kueue Priority Queueing vs Default K8s Scheduler
- **Chosen Option**: **Kubernetes Kueue Job Scheduler with Preemption**.
- **Alternative Evaluated**: Default Kubernetes Scheduler.
- **Trade-Off Rationale**:
  - *Default Scheduler*: Schedules pods individually without job-level queue awareness, leading to partial resource allocation deadlocks (e.g. 3 of 4 worker pods scheduled, 4th pending forever).
  - *Kueue Scheduler*: Manages all-or-nothing batch job admission and enforces priority-based preemption, automatically evicting `BATCH` jobs when `HIGH_PRIORITY` workloads arrive.

### B. NVIDIA MIG Fractional Slicing vs Time-Slicing
- **Chosen Option**: **NVIDIA MIG (Multi-Instance GPU) Hardware Partitioning**.
- **Trade-Off Rationale**: Time-slicing shares GPU execution time without memory isolation, allowing a single rogue process to crash other tenant workloads via OOM. NVIDIA MIG creates hardware-isolated GPU instances (e.g. `1g.10gb`, `2g.20gb`) with dedicated compute slices and memory.

---

## 3. Best Practices & Production Design Principles

1. **Declarative KubeRay CRD Synthesis**:
   - Generates valid `RayCluster` and `RayJob` Kubernetes CRD manifests with resource limits (`nvidia.com/gpu`, CPU/RAM bounds).
2. **Cluster GPU Quotas**:
   - Manages capacity bounds (`cluster_gpu_capacity=32`) to prevent cluster over-subscription.
3. **Graceful Batch Preemption**:
   - Evicts lower priority jobs gracefully, returning allocated GPU capacity back to the cluster pool.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **All-or-Nothing Pod Scheduling Deadlock** | Cluster resource lockup | Kueue all-or-nothing job admission queueing. |
| **Tenant Memory Inter-interference** | OOM crash across jobs | Hardware-isolated NVIDIA MIG slice partitioning. |
| **Capacity Saturation during Peak Demand** | High-priority job queueing | Kueue preemption evicts `BATCH` jobs to admit `HIGH_PRIORITY` workloads. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Manages enterprise multi-tenant GPU clusters in Kubernetes using Kueue ClusterQueue resource quotas, priority-based workload preemption, and NVIDIA Multi-Instance GPU (MIG) hardware slicing.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "job_name": "llama3-eval-batch-44",
  "priority_class": "high-priority-training",
  "gpu_request": 4,
  "queue_name": "cluster-queue-ai-prod"
}
```
**Input Parameter Specification**:
Kubernetes BatchJob spec containing resource requests (`nvidia.com/gpu: 4`) and PriorityClass (`high-priority-training`).

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Intercept Batch Job Spec**: Kueue admission controller intercepts incoming batch job submission.
- **2. Decision 1 (ClusterQueue Quota Check)**: If required GPUs are available within quota limits, admits job immediately and provisions KubeRay RayCluster pods.
- **3. Priority Preemption Evaluation**: If quota is full, evaluates incoming job PriorityClass against active running workloads.
- **4. Decision 2 (Preemption vs Queue)**: If incoming job priority exceeds lowest active workload, preempts lower-priority job, reconfigures NVIDIA MIG slices (1g.10gb), and admits high-priority job.
- **5. Decision 3 (Kueue Pending Queue Buffer)**: If arriving job is low priority, holds job in Kueue pending queue buffer until resources are released.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "admission_status": "ADMITTED",
  "assigned_queue": "cluster-queue-ai-prod",
  "ray_cluster_name": "raycluster-llama3-eval-batch-44",
  "mig_instances": ["mig-1g.10gb-0", "mig-1g.10gb-1"],
  "preempted_jobs": []
}
```
**Output Specification**:
Kueue admission status, assigned RayCluster pod names, and provisioned NVIDIA MIG slice IDs.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 17-k8s-kuberay-kueue-gpu-operator/tests/test_k8s_gpu.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/17-k8s-kuberay-kueue-gpu-operator/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/17-k8s-kuberay-kueue-gpu-operator/FLOWCHART.svg)
