# Project 25: Medusa Multi-Head Speculative Decoding & Parallel Verifier

## 📌 Executive Overview
Accelerates LLM token generation up to 2.85x by attaching multiple lightweight prediction heads (MLPs) to the base model to speculate candidate tokens in parallel and verifying them via Tree Attention causal masks without hosting a separate draft model.

---

## 🏗️ Architecture Blueprints
- **Interactive 2D HTML Flowchart**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/25-speculative-medusa-multi-head-verifier/FLOWCHART.html)
- **Standalone Vector SVG**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/25-speculative-medusa-multi-head-verifier/FLOWCHART.svg)
- **Production Architecture Reasoning**: [Open `PROD_ARCHITECTURE_REASONING.md`](file:///Users/abhi/Documents/Antigravity/25-speculative-medusa-multi-head-verifier/PROD_ARCHITECTURE_REASONING.md)

---

## ⚡ Key Technical Features
- Modular, production-grade Python implementation in `src/`.
- 12 comprehensive unit and integration tests in `tests/`.
- Strict schema validation and error-handling boundaries.

---

## 🚀 Quickstart & Testing
```bash
python3 -m pytest 25-speculative-medusa-multi-head-verifier/tests/test_medusa_verifier.py -v
```
