# Production Architecture & Design Trade-offs: Event Stream PySpark ETL Pipeline

## 1. Executive Context & Business Motivation
Ingesting high-volume event streams (2.4M SNMP telemetry events/day from 12,000 edge nodes) requires fault-tolerant stream processing, schema enforcement, sliding window aggregations, and dead-letter queue routing.

This pipeline provides a **PySpark Streaming ETL & Edge Telemetry Processing Engine**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. PySpark Structured Streaming vs Batch Processing
- **Chosen Option**: **PySpark Structured Streaming with Watermarking**.
- **Alternative Evaluated**: Overnight Batch Cron ETL.
- **Trade-Off Rationale**:
  - *Batch Cron*: Delays anomaly detection features by up to 24 hours, making real-time edge node fault mitigation impossible.
  - *Structured Streaming*: Computes continuous 5-minute sliding metrics with sub-second processing latency.

---

## 3. Best Practices & Production Design Principles
1. **Dead-Letter Queue (DLQ)**: Routes corrupt JSON events to isolated DLQ storage.
2. **Event-Time Watermarking**: Drops events arriving older than 10 minutes to prevent state accumulation.
3. **Partitioned Parquet / Delta Writes**: Writes output metrics partitioned by date and node region.

---

## 4. Production Failure Modes & Mitigations
| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Malformed Telemetry Schema** | Parser crash | Schema validation DLQ routing. |
| **Unbounded State Store Growth** | Executor OOM | Event-time watermarks bound state retention window. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Processes streaming Kafka event logs with 10-minute watermark deduplication and atomically commits validated data to Delta Lake Gold ACID tables with OpenLineage lineage tracking.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "event_id": "evt_773190",
  "device_id": "edge-node-1044",
  "event_timestamp": "2026-08-14T12:30:00Z",
  "metrics": {"gpu_util": 0.88, "vram_used_mb": 18400}
}
```
**Input Parameter Specification**:
Continuous JSON streaming event logs containing event timestamps, device IDs, and telemetry metrics.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Watermark Ingestion**: Applies a 10-minute Structured Streaming event watermark boundary.
- **2. Decision 1 (Late Event Filter)**: Compares event timestamp against watermark. If late (> 10 mins old), drops record to prevent state store memory bloat.
- **3. Deduplication & Schema Validation**: Executes 3-pass deduplication and verifies schema against Delta Lake Gold contract.
- **4. Decision 2 (Data Quality Contract Check)**: If record passes schema rules, performs atomic ACID append to Delta Lake Gold table. If corrupted, routes record to Dead-Letter Queue (DLQ).
- **5. Decision 3 (DLQ S3 Quarantine)**: Writes malformed records to S3 DLQ bucket and emits an OpenLineage telemetry run event.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "delta_table": "gold.edge_telemetry_v1",
  "commit_version": 1042,
  "records_committed": 50000,
  "dlq_records": 3,
  "openlineage_event_emitted": true
}
```
**Output Specification**:
Delta Lake Gold table commit metadata, records ingested count, and OpenLineage job execution event.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 05-event-stream-pyspark-etl/tests/test_event_pipeline.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/05-event-stream-pyspark-etl/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/05-event-stream-pyspark-etl/FLOWCHART.svg)
