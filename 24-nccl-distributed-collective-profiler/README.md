# Project 24: NCCL Distributed Collective Communication & Topology Profiler

## 📌 Executive Overview
Profiles multi-GPU collective communication bandwidth (All-Reduce, All-Gather, Reduce-Scatter) across Ring and Tree topologies, detecting straggler GPU ranks and measuring NVLink / RoCE network saturation.

---

## 🏗️ Architecture Blueprints
- **Interactive 2D HTML Flowchart**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/24-nccl-distributed-collective-profiler/FLOWCHART.html)
- **Standalone Vector SVG**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/24-nccl-distributed-collective-profiler/FLOWCHART.svg)
- **Production Architecture Reasoning**: [Open `PROD_ARCHITECTURE_REASONING.md`](file:///Users/abhi/Documents/Antigravity/24-nccl-distributed-collective-profiler/PROD_ARCHITECTURE_REASONING.md)

---

## ⚡ Key Technical Features
- Modular, production-grade Python implementation in `src/`.
- 12 comprehensive unit and integration tests in `tests/`.
- Strict schema validation and error-handling boundaries.

---

## 🚀 Quickstart & Testing
```bash
python3 -m pytest 24-nccl-distributed-collective-profiler/tests/test_nccl_profiler.py -v
```
