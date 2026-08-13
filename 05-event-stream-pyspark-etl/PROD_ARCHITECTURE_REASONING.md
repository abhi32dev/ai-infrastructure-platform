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
