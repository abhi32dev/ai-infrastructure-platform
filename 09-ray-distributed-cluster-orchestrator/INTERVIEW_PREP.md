# 🎤 Staff AI Platform Interview Guide: Ray Distributed Cluster Orchestrator & Plasma

This guide bridges **Project 9 (`09-ray-distributed-cluster-orchestrator`)** to Staff/Principal-level questions on Ray Core and shared memory IPC.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Ray Core's Plasma Store achieve zero-copy deserialization across worker processes?"
> **Staff Engineer Answer**:
> "In `src/ray_cluster_orchestrator.py`, objects are written to POSIX shared memory (`/dev/shm`). Workers on the same node memory-map this buffer with PyArrow, reading tensor pointers directly without memory copying."

### Q2: "How does Ray dynamic actor autoscaling prevent cluster cost overruns?"
> **Staff Engineer Answer**:
> "We monitor pending task queue depth against active Ray actors. When load ratio $>1.5$, additional worker pods are provisioned; when idle for $>300\text{s}$, workers drain gracefully to baseline limits."

### Q3: "How do you handle worker node preemption during distributed task execution?"
> **Staff Engineer Answer**:
> "Tasks returning Ray `ObjectRef` handles support automatic task lineage reconstruction. If a worker node crashes, the Ray GCS re-schedules the task on an available node."
