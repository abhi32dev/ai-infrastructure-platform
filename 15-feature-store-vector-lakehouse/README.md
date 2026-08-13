# Project 15: ML Feature Store & PyArrow Vector Lakehouse

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/15-feature-store-vector-lakehouse/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---

Enterprise ML feature serving and vector lakehouse platform implementing **Feast / Hopsworks style Online (Redis < 2ms) + Offline (Parquet/S3) Feature Store** with point-in-time time-travel joins, and **Apache Iceberg / PyArrow zero-copy IPC buffer vector serialization**.

---

## 🛠️ Architecture Components
- **Online Feature Store**: Low-latency key-value feature retrieval (< 2ms) for real-time model inference.
- **Offline Time-Travel Store**: Point-in-time feature join engine eliminating training-serving skew.
- **PyArrow Vector Lakehouse**: Memory-mapped zero-copy IPC buffer column pruning scans over high-dimensional vector embeddings.

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```