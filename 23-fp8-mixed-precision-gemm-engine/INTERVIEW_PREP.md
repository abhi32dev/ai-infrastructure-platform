# 🎤 Staff AI Platform Interview Guide: Native FP8 (E4M3 / E5M2) GEMM & Delayed Scaling

This guide bridges **Project 23 (`23-fp8-mixed-precision-gemm-engine`)** to Staff/Principal-level questions on NVIDIA Hopper H100 FP8 Tensor Cores.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "What are the mathematical differences between FP8 E4M3 and E5M2 formats?"
> **Staff Engineer Answer**:
> "In `src/fp8_gemm_engine.py`, **E4M3** (1 sign, 4 exp, 3 mantissa) has range $[-448, 448]$ with higher precision, making it ideal for forward pass activations and weights. **E5M2** (1 sign, 5 exp, 2 mantissa) has range $[-57344, 57344]$ with higher dynamic range, ideal for backward pass gradients."

### Q2: "Why are delayed dynamic scaling factors necessary for FP8 Tensor Core matrix multiplication?"
> **Staff Engineer Answer**:
> "Calculating exact maximum absolute values ($	ext{amax}$) on every layer causes GPU pipeline stalls. We maintain a sliding history of $	ext{amax}$ to compute delayed scaling factors: $S = \text{FP8\_MAX} / \max(\text{history}(\text{amax}))$, unlocking 1,979 TFLOPS on Hopper."

### Q3: "How does FP8 GEMM achieve a 1.86x speedup over FP16?"
> **Staff Engineer Answer**:
> "8-bit operands halve memory bandwidth requirements and double Tensor Core arithmetic density compared to 16-bit floats."
