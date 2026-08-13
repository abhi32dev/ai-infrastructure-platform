# 🎤 Staff AI Platform & Distributed Systems Interview Guide (Anyscale / Ray Standard)

This guide bridges the code in **Project 9 (`09-ray-distributed-cluster-orchestrator`)** directly to Staff/Principal-level questions asked by Anyscale, Databricks, OpenAI, Meta AI, and Snowflake.

---

## 💡 Tech Community Requirements at Staff AI Level

> **Industry Context (2025-2026)**:
> Ray is the underlying orchestrator powering ChatGPT training (OpenAI), Meta's Llama cluster management, and Databricks Ray workloads. Interviewers evaluate:
> 1. **Ray Tasks vs Ray Actors**: When to use stateless distributed functions (`@ray.remote` tasks) vs stateful worker classes (`@ray.remote` actors).
> 2. **Plasma Zero-Copy Memory Store**: How Ray's shared memory Plasma store avoids expensive IPC serialization overhead when passing gigabyte model weights or embeddings between worker actors.
> 3. **Fault-Tolerant Actor Recovery & Autoscaling**: How Ray's Global Control Store (GCS) detects node failures and reschedules stateful actors on healthy nodes.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Ray's Plasma Shared Memory Store eliminate IPC serialization bottlenecks during distributed inference?"
> **Staff Engineer Answer**:
> "In traditional distributed Python systems (e.g. PyTorch DDP or standard multiprocessing), passing a 10GB tensor between worker processes incurs Python pickle serialization, socket transmission, and deserialization overhead, saturating CPU memory bandwidth.
> 
> In `09-ray-distributed-cluster-orchestrator` ([`src/ray_actor_pool.py`](src/ray_actor_pool.py)), we leverage Ray's **Plasma Zero-Copy Object Store**:
> - Payloads are written once to shared memory backing store (`ray.put()`).
> - Worker actors receive lightweight 64-byte `ObjectID` references.
> - Multiple worker actors on the same node read the shared memory tensor buffer via zero-copy pointer mapping without copying bytes into Python memory.
> 
> This cuts tensor transfer latency from seconds to microsecond pointer lookups."

---

### Q2: "How do you implement fault-tolerant actor recovery across a multi-node GPU cluster?"
> **Staff Engineer Answer**:
> "When managing a multi-node GPU cluster (e.g. 4 nodes with 32 GPUs), hardware failure (EC2 spot termination or GPU Xid errors) is inevitable.
> 
> In [`src/ray_actor_pool.py`](src/ray_actor_pool.py), we simulate Ray's GCS health checker:
> - Ray heartbeat monitors worker node health.
> - Upon detecting node loss (`ray-node-04`), stateful actors in `BUSY` or `ALIVE` states are transitioned to `RESTARTING`.
> - Ray's scheduler reconstructs the actor graph on an available backup node (`ray-node-01`), restoring the actor state without failing the parent workflow."

---

### Q3: "How does Ray Cluster Autoscaler prevent SLA breaches under spiking LLM request traffic?"
> **Staff Engineer Answer**:
> "Static cluster provisioning leads to over-spending during idle periods or queue build-up during traffic spikes.
> 
> In [`src/cluster_autoscaler.py`](src/cluster_autoscaler.py), our autoscaler continuously polls pending queue depth and GPU VRAM utilization metrics:
> - **Scale Up**: If queue depth > 50 or GPU util > 85%, the autoscaler provisions 2 new worker nodes up to `max_nodes=16`.
> - **Scale Down**: If queue depth == 0 and GPU util < 20%, nodes are drained safely and terminated to `min_nodes=2`."
