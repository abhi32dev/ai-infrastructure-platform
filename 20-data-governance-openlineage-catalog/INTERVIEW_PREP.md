# 🎤 Staff AI Platform Interview Guide: Data Governance, OpenLineage & Quality Contracts

This guide bridges **Project 20 (`20-data-governance-openlineage-catalog`)** to Staff/Principal-level questions on dataset lineage and Great Expectations contracts.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do OpenLineage telemetry events track end-to-end dataset lineage?"
> **Staff Engineer Answer**:
> "In `src/data_governance_engine.py`, data jobs emit standardized OpenLineage `START`, `COMPLETE`, and `ABORT` JSON events containing input/output dataset URNs and run state facets to the Marquez catalog."

### Q2: "How do Data Quality Contracts prevent silent model failure in production?"
> **Staff Engineer Answer**:
> "Before pipeline execution, Great Expectations schema suites audit incoming tables for non-null primary keys and valid numerical ranges. Violations trigger an immediate OpenLineage ABORT event, halting downstream feature generation."

### Q3: "How do you handle catalog server downtime without dropping lineage telemetry?"
> **Staff Engineer Answer**:
> "Lineage events are buffered in local persistent disk queues, retrying delivery with exponential backoff upon server reconnection."
