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
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Orchestrates multi-node distributed task scheduling and zero-copy shared memory object transfers (Plasma Store) with dynamic worker autoscaling.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "task_name": "distributed_feature_transform",
  "payload_size_mb": 250,
  "required_cpus": 4,
  "required_gpus": 1
}
```
**Input Parameter Specification**:
Task graph specification, input payload tensors, and worker resource requirements (CPUs, GPUs).

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Write Payload to Plasma Store**: Writes large tensor data to local shared-memory Plasma object store for zero-copy IPC.
- **2. Decision 1 (Autoscaler Capacity Audit)**: Compares pending task queue depth to active Ray actors. If load ratio exceeds scale-up threshold, provisions additional worker nodes via cloud API.
- **3. Dispatch Task to Idle Actor**: Dispatches task reference (`ObjectRef`) to idle Ray actor worker.
- **4. Decision 2 (Scale Down Idle Check)**: If worker nodes remain idle with zero tasks for > 300 seconds, evaluates scale down.
- **5. Decision 3 (Maintain Baseline Limits)**: Gracefully drains active tasks and terminates excess idle worker nodes while preserving static minimum cluster capacity.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "object_ref": "obj_9f82b1a03c",
  "executed_on_node": "ray-worker-node-04",
  "execution_time_ms": 312.4,
  "shared_memory_zero_copy": true,
  "cluster_active_nodes": 6
}
```
**Output Specification**:
Ray ObjectRef result, worker execution node ID, and Plasma shared memory read latency.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 09-ray-distributed-cluster-orchestrator/tests/test_ray_cluster.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/09-ray-distributed-cluster-orchestrator/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/09-ray-distributed-cluster-orchestrator/FLOWCHART.svg)
