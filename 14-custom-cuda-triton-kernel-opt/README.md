# Project 14: Custom OpenAI Triton & CUDA GPU Kernel Optimization

GPU performance engineering platform implementing **OpenAI Triton Fused GPU Kernels** (Fused Bias-GELU & Blocked Attention), **Roofline Model Performance Analysis** (Memory-Bound vs Compute-Bound classification), and **NVTX Range Profiling**.

---

## 🛠️ Architecture Components
- **Triton Fused Kernel Engine**: Fuses activation and bias passes to eliminate VRAM global memory roundtrips (2.15x speedup).
- **Roofline Analyzer**: Computes Operational Intensity (FLOPs / Byte) against hardware ridge points.
- **NVTX Profiler**: Instruments NVTX execution ranges for NVIDIA Nsight Systems tracing.

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```
