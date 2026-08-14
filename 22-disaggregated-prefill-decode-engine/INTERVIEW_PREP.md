# 🎤 Staff AI Platform Interview Guide: Disaggregated Prefill vs. Decode & RDMA KV Pools

This guide bridges **Project 22 (`22-disaggregated-prefill-decode-engine`)** to Staff/Principal-level questions on Splitwise, DistServe, and Mooncake architectures.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is colocation of Prefill and Decode suboptimal, and how does Disaggregation solve Head-of-Line blocking?"
> **Staff Engineer Answer**:
> "In `src/disaggregated_engine.py`, Prefill (prompt processing) is compute-bound, while Decode (token generation) is memory-bandwidth-bound. Colocating them causes long prompts to block ongoing token generation. Disaggregation routes prompts to dedicated Prefill GPUs, transfers computed KV caches over 100 Gbps GPUDirect RDMA in $<2\text{ms}$, and generates tokens on dedicated Decode GPUs."

### Q2: "How does Disaggregated serving improve Time to First Token (TTFT) and Time Per Output Token (TPOT)?"
> **Staff Engineer Answer**:
> "By isolating compute-heavy prompts from token generation, TTFT is reduced by up to 70% and TPOT jitter is virtually eliminated."

### Q3: "How do you handle RDMA network queue timeouts during KV cache transfer?"
> **Staff Engineer Answer**:
> "If an RDMA QP timeout occurs, the transfer client falls back automatically to high-speed TCP socket streams to preserve request continuity."
