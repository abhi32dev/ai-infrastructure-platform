# Project 23: Native FP8 Mixed-Precision GEMM & Delayed Scaling Engine

## 📌 Executive Overview
Accelerates matrix multiplication up to 1.86x on NVIDIA Hopper H100 native FP8 Tensor Cores (E4M3 / E5M2) with dynamic delayed scaling factors and zero perplexity degradation.

---

## 🏗️ Architecture Blueprints
- **Interactive 2D HTML Flowchart**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/23-fp8-mixed-precision-gemm-engine/FLOWCHART.html)
- **Standalone Vector SVG**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/23-fp8-mixed-precision-gemm-engine/FLOWCHART.svg)
- **Production Architecture Reasoning**: [Open `PROD_ARCHITECTURE_REASONING.md`](file:///Users/abhi/Documents/Antigravity/23-fp8-mixed-precision-gemm-engine/PROD_ARCHITECTURE_REASONING.md)

---

## ⚡ Key Technical Features
- Modular, production-grade Python implementation in `src/`.
- 12 comprehensive unit and integration tests in `tests/`.
- Strict schema validation and error-handling boundaries.

---

## 🚀 Quickstart & Testing
```bash
python3 -m pytest 23-fp8-mixed-precision-gemm-engine/tests/test_fp8_gemm.py -v
```
