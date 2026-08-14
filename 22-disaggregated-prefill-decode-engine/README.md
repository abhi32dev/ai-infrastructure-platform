# Project 22: Disaggregated Prefill vs. Decode Serving & Handoff Engine

## 📌 Executive Overview
Eliminates head-of-line interference and latency jitter by separating compute-bound prompt ingestion (Prefill) from memory-bandwidth-bound token generation (Decode) across distinct GPU worker pools with GPUDirect RDMA KV cache transfer.

---

## 🏗️ Architecture Blueprints
- **Interactive 2D HTML Flowchart**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/22-disaggregated-prefill-decode-engine/FLOWCHART.html)
- **Standalone Vector SVG**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/22-disaggregated-prefill-decode-engine/FLOWCHART.svg)
- **Production Architecture Reasoning**: [Open `PROD_ARCHITECTURE_REASONING.md`](file:///Users/abhi/Documents/Antigravity/22-disaggregated-prefill-decode-engine/PROD_ARCHITECTURE_REASONING.md)

---

## ⚡ Key Technical Features
- Modular, production-grade Python implementation in `src/`.
- 12 comprehensive unit and integration tests in `tests/`.
- Strict schema validation and error-handling boundaries.

---

## 🚀 Quickstart & Testing
```bash
python3 -m pytest 22-disaggregated-prefill-decode-engine/tests/test_disaggregated.py -v
```
