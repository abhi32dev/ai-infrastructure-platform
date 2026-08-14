# 🎤 Staff AI Platform Interview Guide: Triton CUDA GPU Scheduler & Dynamic Batching

This guide bridges **Project 10 (`10-triton-cuda-gpu-scheduler`)** to Staff/Principal-level questions on GPU Tensor Core scheduling and AWQ kernels.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Dynamic Batching prevent thread starvation while maintaining P99 latency SLAs?"
> **Staff Engineer Answer**:
> "In `src/triton_gpu_engine.py`, incoming requests enter an asyncio buffer. The scheduler flushes the batch when batch size reaches 32 OR queue delay reaches 10ms, safeguarding latency SLAs."

### Q2: "How does AWQ INT4 GEMM quantization accelerate inference throughput?"
> **Staff Engineer Answer**:
> "Activation-aware Weight Quantization (AWQ) protects salient weight channels while quantizing 99% of weights to INT4, doubling matrix multiplication throughput on GPU Tensor Cores."

### Q3: "How do multiple CUDA streams enable concurrent kernel execution?"
> **Staff Engineer Answer**:
> "We launch preprocessing, kernel execution, and postprocessing on independent non-blocking CUDA streams, allowing host-to-device memory copies to overlap with GPU compute."
