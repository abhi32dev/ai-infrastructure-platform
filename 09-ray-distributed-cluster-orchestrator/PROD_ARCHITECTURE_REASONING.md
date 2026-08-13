# Production Architecture & Design Trade-offs: Ray Distributed Cluster Orchestrator

## 1. Executive Context & Business Motivation
Scaling Python ML workloads across multi-node GPU clusters requires distributed task scheduling, stateful worker actor management, dynamic autoscaling, and fault recovery. Traditional RPC frameworks lack low-overhead object sharing and actor state tracking across heterogeneous compute nodes.

This engine implements a **Ray Distributed Cluster Orchestrator with Stateful Actor Pools & Dynamic Queue Autoscaling**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Ray Distributed Actor Pools vs ProcessPoolExecutor / Celery
- **Chosen Option**: **Ray Core Stateful Actor Pools with Shared Plasma Memory**.
- **Alternative Evaluated**: Celery / Multiprocessing.
- **Trade-Off Rationale**:
  - *Celery/Multiprocessing*: Serialization overhead (Pickle) copying large model weights or tensors between processes.
  - *Ray Core*: Shared-memory object store (Plasma) allowing zero-copy read access to GPU arrays across worker actors on the same node.

### B. Dynamic Queue-Based Cluster Autoscaling vs Static Worker Pools
- **Chosen Option**: **Demand-Based Queue Depth Cluster Autoscaling**.
- **Trade-Off Rationale**: Evaluates pending task queue depth to launch worker nodes dynamically, automatically scaling down idle nodes after cool-off periods to minimize cloud GPU infrastructure spend.

---

## 3. Best Practices & Production Design Principles

1. **Stateful Actor Fault Recovery**:
   - Automatically detects crashed Ray actors, reinstantiating state on healthy cluster nodes without corrupting active job streams.
2. **Resource Boundary Constraints**:
   - Enforces strict per-node CPU/GPU limits (`gpus_per_actor`, `cpus_per_actor`) to prevent worker process OOM thrashing.
3. **Round-Robin Task Dispatching**:
   - Balances load uniformly across active worker actor pools to optimize cluster throughput.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Worker Actor Process Crash** | Task execution failure | Automatic actor health checks and worker task re-dispatch. |
| **Node Resource Saturation** | OOM / System hang | Cluster autoscaler provisions additional node capacity when queue depth exceeds threshold. |
| **Maximum Worker Cap Reached** | Queue accumulation | Enforces queue priority and limits job submission bursts. |
