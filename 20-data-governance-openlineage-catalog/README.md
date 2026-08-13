# Project 20: Data Governance, OpenLineage & Data Quality Catalog

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
