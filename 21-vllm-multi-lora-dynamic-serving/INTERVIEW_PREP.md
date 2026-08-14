# 🎤 Staff AI Platform Interview Guide: vLLM Multi-LoRA Dynamic Serving & Segmented GEMM

This guide bridges **Project 21 (`21-vllm-multi-lora-dynamic-serving`)** to Staff/Principal-level questions on multi-tenant LoRA serving (S-LoRA / Punica).

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you serve 100+ fine-tuned customer LoRA adapters on a single base model without stalling inference?"
> **Staff Engineer Answer**:
> "In `src/multi_lora_engine.py`, base model weights reside permanently in VRAM. Lightweight LoRA adapter weights (50MB) are paged into dynamic VRAM buffers using LRU cache eviction. A custom Segmented GEMM kernel applies distinct adapter weights to different sequence slices in the same batch simultaneously with zero stalling."

### Q2: "How does Segmented GEMM differ from standard PyTorch batch matrix multiplication?"
> **Staff Engineer Answer**:
> "Standard `torch.bmm` requires all batch elements to multiply against the same weight matrix. Segmented GEMM partitions batch sequences and multiplies each segment by its respective LoRA adapter matrix ($B_i A_i$) in a single fused GPU kernel."

### Q3: "How do you manage VRAM memory pressure with dynamic adapter caching?"
> **Staff Engineer Answer**:
> "When active adapter memory exceeds the allocated VRAM pool (e.g. 500MB), the cache manager evicts the least-recently-used adapter back to host RAM via non-blocking pinned memory."
