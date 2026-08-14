# 🎤 Staff AI Platform Interview Guide: Custom OpenAI Triton GPU Kernels & SRAM Tiling

This guide bridges **Project 14 (`14-custom-cuda-triton-kernel-opt`)** to Staff/Principal-level questions on GPU kernel optimization and SRAM memory bandwidth.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is a fused Bias-GELU Triton kernel faster than standard PyTorch?"
> **Staff Engineer Answer**:
> "In `src/triton_kernel_engine.py`, standard PyTorch executes 3 separate memory roundtrips over high-bandwidth memory (HBM). A fused Triton kernel loads tensor tiles into on-chip SRAM (19 TB/s on H100), computes bias addition and GELU activation in registers, and writes back to HBM once (1.99x speedup)."

### Q2: "How do you determine the optimal block size for GPU kernel tiling?"
> **Staff Engineer Answer**:
> "We balance register pressure and shared memory capacity per Streaming Multiprocessor (SM). `BLOCK_SIZE=1024` maximizes occupancy without causing register spilling to global memory."

### Q3: "How does the Roofline model guide GPU performance engineering?"
> **Staff Engineer Answer**:
> "It relates attainable TFLOPS to Operational Intensity (FLOPs/byte). If operational intensity is below the hardware ridge point, performance is memory-bandwidth-bound; if above, it is compute-bound."
