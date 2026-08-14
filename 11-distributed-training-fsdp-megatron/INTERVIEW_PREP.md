# 🎤 Staff AI Platform Interview Guide: PyTorch FSDP ZeRO-3 & Megatron 3D Parallelism

This guide bridges **Project 11 (`11-distributed-training-fsdp-megatron`)** to Staff/Principal-level questions on multi-node distributed model training.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Compare PyTorch FSDP (ZeRO-3) vs. Megatron Tensor Parallelism. When would you use each?"
> **Staff Engineer Answer**:
> "In `src/distributed_trainer.py`, FSDP ZeRO-3 shards Optimizer States, Gradients, and Model Parameters across data-parallel ranks, reconstructing weights on-the-fly via `All-Gather`. Megatron Tensor Parallelism splits linear projection matrices intra-node over NVLink (900 GB/s). Standard practice: TP intra-node, FSDP inter-node."

### Q2: "What causes gradient overflow during FP16 mixed-precision training, and how is it resolved?"
> **Staff Engineer Answer**:
> "FP16 has a dynamic range of $[10^{-5}, 65504]$. Large gradient norms cause Inf/NaN overflows. We audit gradient norms, clip gradients to 1.0, and dynamically reduce the loss scale factor upon overflow."

### Q3: "How do you calculate distributed training bus bandwidth?"
> **Staff Engineer Answer**:
> "Using the All-Reduce bus bandwidth formula: $B_{bus} = \frac{2(N-1)}{N} \cdot \frac{\text{Payload Size}}{\text{Duration}}$, evaluating NVLink and RoCE network saturation."
