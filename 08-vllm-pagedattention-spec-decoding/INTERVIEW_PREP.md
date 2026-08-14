# 🎤 Staff AI Platform Interview Guide: vLLM PagedAttention & Speculative Decoding

This guide bridges **Project 8 (`08-vllm-pagedattention-spec-decoding`)** to Staff/Principal-level questions on LLM serving engine internals.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does PagedAttention eliminate VRAM memory fragmentation?"
> **Staff Engineer Answer**:
> "In `src/paged_kv_cache.py`, traditional contiguous KV cache allocation wastes up to 80% of VRAM. PagedAttention partitions the cache into 16-token physical blocks, mapping logical sequence tokens to non-contiguous physical blocks via a Block Table, reducing memory waste to $<4\%$."

### Q2: "How does Speculative Decoding achieve 2.67x generation speedup?"
> **Staff Engineer Answer**:
> "In `src/speculative_decoder.py`, a lightweight 1B draft model speculates $K=4$ candidate tokens. The 70B target model verifies all 4 tokens in a single parallel forward pass. Accepted tokens advance generation position by $K$ steps simultaneously."

### Q3: "What is continuous iteration-level batching?"
> **Staff Engineer Answer**:
> "In `src/continuous_batcher.py`, new requests enter the active iteration batch immediately upon arrival, while completed sequences release their physical blocks at token boundaries."
