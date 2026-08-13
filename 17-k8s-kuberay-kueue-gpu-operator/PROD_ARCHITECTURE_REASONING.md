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
