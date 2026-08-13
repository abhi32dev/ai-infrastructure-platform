# Project 20: Data Governance, OpenLineage & Data Quality Catalog

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/20-data-governance-openlineage-catalog/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---

Enterprise data governance and compliance lineage tracking platform implementing **OpenLineage Standard Event Emitters** (START, COMPLETE, FAIL), **Marquez / DataHub Lineage Dependency Graph Visualizers**, and **Great Expectations Data Quality Contract Validation**.

---

## 🛠️ Architecture Components
- **OpenLineage Emitter**: Emits standardized JSON telemetry tracking dataset inputs/outputs and schemas.
- **Marquez Lineage Tracker**: Constructs dataset dependency graphs for auditability and compliance.
- **Data Contract Validator**: Enforces schema contracts, non-null constraints, and data quality scores.

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```