# Production Architecture & Design Trade-offs: Data Governance & OpenLineage Catalog

## 1. Executive Context & Business Motivation
In enterprise data & AI platforms processing thousands of streaming and batch data pipelines, tracking data lineage (where data came from, how it was transformed) and enforcing data quality contracts is mandatory for regulatory compliance (GDPR, HIPAA, SOC2) and debugging broken ML pipelines.

This framework provides an **OpenLineage Event Telemetry Emitter, Marquez Lineage Graph Tracker, and Great Expectations Data Quality Contract Engine**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. OpenLineage Telemetry Standard vs Proprietary Logging
- **Chosen Option**: **OpenLineage Standard JSON Telemetry Emitter**.
- **Alternative Evaluated**: Proprietary custom logging format.
- **Trade-Off Rationale**:
  - *Custom Logging*: Requires custom parser maintenance and isolates data lineage inside local silos.
  - *OpenLineage Standard*: Interoperable schema format compatible with Marquez, DataHub, and Apache Airflow.

### B. Automated Data Quality Contracts vs Post-Hoc Data Auditing
- **Chosen Option**: **Pre-Commit Data Quality Contract Validation**.
- **Trade-Off Rationale**: Validates schema contracts, required fields, non-null constraints, and data quality scores *before* data is committed to the feature store. If contract validation fails, pipeline execution is halted.

---

## 3. Best Practices & Production Design Principles

1. **Lineage Graph Dependency Reconstruction**:
   - Constructs dataset dependency graphs ($Dataset_A \rightarrow [Job] \rightarrow Dataset_B$) for auditability.
2. **Quality Score Calculation**:
   - Computes record-level contract quality percentages (`quality_score_pct`).
3. **Empty Batch Resiliency**:
   - Handles empty dataset batches gracefully (`total_records_checked = 0`, `is_valid = True`).

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Corrupted / Schema-Violating Data** | Downstream ML model failure | Pre-commit Data Contract Validator halts pipeline execution. |
| **Un-trackable Data Lineage** | Compliance & audit failure | OpenLineage telemetry emitter logs input/output dataset URIs on job completion. |
| **Missing Required Contract Fields** | Null pointer errors in feature code | Contract validator detects missing keys and emits detailed violation logs. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Enforces strict data quality contracts with Great Expectations, traces end-to-end dataset lineage in Marquez, and emits OpenLineage ABORT / COMPLETE telemetry events to halt pipelines before corrupt data spreads.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "job_name": "gold_user_aggregate_daily",
  "dataset_urn": "lakehouse://gold/user_features",
  "expectation_suite": "no_null_customer_ids"
}
```
**Input Parameter Specification**:
Dataset identifier, input PySpark DataFrame or SQL table, and Great Expectations expectation suite.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Pre-Job Data Contract Validation**: Evaluates incoming dataset against Great Expectations schema rules (non-null IDs, valid ranges).
- **2. Decision 1 (Contract Check Gate)**: If pre-job check passes, emits OpenLineage START event and proceeds. If violations exist, immediately emits OpenLineage ABORT event to Marquez and quarantines corrupt dataset.
- **3. Execute Transformation Job**: Runs data transformation pipeline and computes output table row count metrics.
- **4. Decision 2 (Transformation Success Verification)**: If transformation completes without unhandled errors, emits OpenLineage COMPLETE event with row count metadata and updates Marquez lineage graph.
- **5. Decision 3 (Marquez Health & Queue)**: If Marquez API server is temporarily unreachable, buffers lineage telemetry events in local disk queue for automated retry.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "contract_status": "PASSED",
  "violations_count": 0,
  "openlineage_event": "COMPLETE",
  "rows_processed": 150000,
  "marquez_lineage_updated": true
}
```
**Output Specification**:
Data contract validation report, OpenLineage run state event, and Marquez lineage graph update status.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 20-data-governance-openlineage-catalog/tests/test_data_governance.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/20-data-governance-openlineage-catalog/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/20-data-governance-openlineage-catalog/FLOWCHART.svg)
