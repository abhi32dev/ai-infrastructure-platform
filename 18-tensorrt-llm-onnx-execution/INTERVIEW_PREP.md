# 🎤 Staff AI Platform Interview Guide: TensorRT-LLM Engine & INT4 SmoothQuant

This guide bridges **Project 18 (`18-tensorrt-llm-onnx-execution`)** to Staff/Principal-level questions on TensorRT-LLM and ONNX graph optimization.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does TensorRT-LLM compile PyTorch models into optimized execution plans?"
> **Staff Engineer Answer**:
> "In `src/tensorrt_engine.py`, PyTorch computation graphs are traced into ONNX format. TensorRT fuses multi-head attention (FMHA) kernels, applies INT4 SmoothQuant calibration, and builds a static `.engine` execution plan delivering up to 1,480 tokens/sec."

### Q2: "What is SmoothQuant calibration, and why is it superior to naive INT8/INT4 quantization?"
> **Staff Engineer Answer**:
> "Activations have outlier channels that cause quantization errors. SmoothQuant applies a per-channel scaling factor to migrate difficulty from activations to weights, preserving model perplexity."

### Q3: "How do you manage dynamic input shapes in TensorRT execution profiles?"
> **Staff Engineer Answer**:
> "We configure optimization profiles with minimum, optimal, and maximum batch sizes and sequence lengths (`min=1, opt=32, max=64`), allowing the engine to allocate optimal memory buffers."
