# High-Throughput LLM Serving via vLLM & PagedAttention

## 1. PagedAttention Memory Architecture
Traditional LLM inference allocates contiguous GPU VRAM for the maximum sequence length (e.g. 4096 tokens). Because request outputs vary, 60% to 80% of GPU memory is wasted on internal and external fragmentation.

PagedAttention partitions KV-cache into fixed physical GPU blocks (e.g. 16 tokens/block). Logical page tables map token sequences to physical blocks on-demand, reducing VRAM memory fragmentation to 0.0% and enabling 2.5x to 4x higher batch concurrency.

## 2. Speculative Decoding Optimization
Speculative decoding uses a small draft model (e.g., Llama-3B) to generate candidate tokens sequentially. A larger target model (e.g., Llama-70B) verifies all candidate tokens in a single parallel GPU forward pass, accelerating inference throughput by 2.2x to 2.8x without compromising model accuracy.
