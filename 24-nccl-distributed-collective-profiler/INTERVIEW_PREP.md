# 🎤 Staff AI Platform Interview Guide: NCCL Multi-GPU Communication & Straggler Detection

This guide bridges **Project 24 (`24-nccl-distributed-collective-profiler`)** to Staff/Principal-level questions on NCCL collective communication algorithms and topology.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you calculate NCCL Bus Bandwidth for All-Reduce collectives?"
> **Staff Engineer Answer**:
> "In `src/nccl_profiler.py`, Algorithmic Bandwidth is $B_{alg} = \frac{\text{Bytes}}{\text{Time}}$. Bus Bandwidth accounts for multi-GPU traffic multiplication: $B_{bus} = \frac{2(N-1)}{N} \cdot B_{alg}$ (for 8 GPUs, factor is 1.75x), measuring NVLink (900 GB/s) saturation."

### Q2: "How do you detect and isolate straggler GPU ranks in distributed training?"
> **Staff Engineer Answer**:
> "Synchronous distributed training stalls if one rank is slow. We profile per-rank kernel completion times. Any rank exhibiting $>5\%$ latency variance from the cluster mean is flagged for thermal throttling or PCIe link degradation."

### Q3: "When should you switch from Ring to Tree collective topologies?"
> **Staff Engineer Answer**:
> "Ring collectives excel for large message payloads where bandwidth dominates ($O(N)$ latency hops). 2D-Tree topologies excel for small/medium payloads across multi-node clusters by reducing latency hops to $O(\log N)$."
