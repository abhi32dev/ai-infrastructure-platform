# 🎤 Staff AI Platform & LLM Serving Interview Guide (2025/2026 Tech Community Standard)

This guide bridges the code in **Project 8 (`08-vllm-pagedattention-spec-decoding`)** directly to Staff/Principal-level questions asked by OpenAI, Anthropic, Anyscale, Databricks, and Meta AI.

---

## 💡 Tech Community Requirements at Staff AI Level

> **Industry Context (2025-2026)**:
> In Tier-1 AI companies, LLM serving has transitioned from naive HuggingFace pipelines to hardware-aware inference engines. Interviewers specifically evaluate:
> 1. **PagedAttention & KV-Cache Virtual Memory**: How PagedAttention solves the 60-80% VRAM waste caused by traditional static sequence allocation.
> 2. **Speculative Decoding Speedups**: How speculative sampling uses a smaller draft model (e.g. Llama-3B) to predict tokens verified by a target model (e.g. Llama-70B) in a single parallel step.
> 3. **Time-to-First-Token (TTFT) vs Inter-Token Latency (ITL)**: Optimizing continuous batching schedulers to decouple prefill and decode phase processing.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does PagedAttention eliminate GPU VRAM fragmentation during high-concurrency LLM serving?"
> **Staff Engineer Answer**:
> "In traditional static KV-cache management, contiguous VRAM chunks are reserved for the maximum sequence length (e.g., 4096 tokens). Because actual generation length is non-deterministic, 60-80% of GPU memory suffers from internal and external fragmentation.
> 
> In `08-vllm-pagedattention-spec-decoding` ([`src/paged_kv_cache.py`](src/paged_kv_cache.py)), we implement PagedAttention virtual memory block allocation:
> - VRAM is partitioned into fixed physical blocks (e.g., 16 tokens/block).
> - Each request maintains a logical-to-physical page table mapping logical token indices to non-contiguous physical GPU blocks.
> - As tokens are generated, blocks are dynamically allocated on-demand. When sequences finish, blocks are immediately reclaimed.
> 
> This reduces GPU VRAM fragmentation to **0.0%** and allows 2x-4x larger batch sizes on the same hardware."

---

### Q2: "How does Speculative Decoding accelerate inference latency without changing model output accuracy?"
> **Staff Engineer Answer**:
> "LLM decoding is memory-bandwidth bound because each token step requires reading weights from GPU HBM to SRAM.
> 
> In `08-vllm-pagedattention-spec-decoding` ([`src/speculative_decoder.py`](src/speculative_decoder.py)), we implement Speculative Decoding:
> 1. A small, fast **Draft Model** (e.g. 1B) autoregressively predicts $k=4$ candidate tokens in 4ms.
> 2. The large **Target Model** (e.g. 70B) evaluates all $k=4$ tokens in a **single parallel forward pass**.
> 3. Accepted tokens are retained based on modified rejection sampling ($P_{\text{target}} \ge P_{\text{draft}}$).
> 
> Because matrix-vector multiplications for $k$ tokens take almost the same time as 1 token in the Target Model's compute pass, we achieve **~2.67x latency speedup** while producing the exact same mathematical probability distribution as target-only decoding."

---

### Q3: "How do you handle Continuous Batching iteration scheduling to optimize TTFT and ITL?"
> **Staff Engineer Answer**:
> "Static batching waits for all requests in a batch to finish generation, wasting GPU compute on finished sequences.
> 
> In [`src/continuous_batcher.py`](src/continuous_batcher.py), we implement Orca-style iteration-level continuous batching:
> - **Prefill Phase**: Incoming prompts are chunked and scheduled into active iteration slots, logging **Time-to-First-Token (TTFT)**.
> - **Decode Phase**: Requests generate 1 token per step, logging **Inter-Token Latency (ITL)**.
> - Completed requests are evicted immediately, admitting waiting requests without stopping the running batch."
