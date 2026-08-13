# Production Architecture & Design Trade-offs: Realtime Stream Feature Pipeline

## 1. Executive Context & Business Motivation
In large-scale edge networks (e.g. Comcast CONDOR with 12,000+ edge nodes emitting 2.4M SNMP events/day), feature calculation for anomaly detection cannot wait for overnight batch ETL. Features must be aggregated in real-time over sliding time windows while maintaining ACID reliability on disk.

This component implements a **PySpark Structured Streaming & Delta Lake Real-time Feature Pipeline**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. PySpark Structured Streaming vs Apache Flink vs Micro-batch Python
- **Chosen Option**: **PySpark Structured Streaming with Watermarking**.
- **Alternative Evaluated**: Apache Flink / Pure Python micro-batches.
- **Trade-Off Rationale**:
  - *Pure Python*: Fails under 100k+ events/sec throughput.
  - *Apache Flink*: Lower latency (sub-100ms), but requires complex dedicated cluster management.
  - *PySpark Structured Streaming*: Unified API for streaming and offline batch training feature consistency, native integration with Delta Lake ACID transactions.

### B. Delta Lake Storage Format vs Plain Parquet / S3
- **Chosen Option**: **Delta Lake Storage Format**.
- **Trade-Off Rationale**: Plain Parquet on S3 lacks ACID transaction support, leading to partial file reads or corrupt feature vectors during concurrent stream writes. Delta Lake transaction logs guarantee atomic commits and schema enforcement.

---

## 3. Best Practices & Production Design Principles

1. **Watermarking & Late Data Handling**:
   - Enforces 10-minute event-time watermarking (`withWatermark("timestamp", "10 minutes")`) to drop stale events and constrain state store memory growth.
2. **Schema Enforcement & Quarantine**:
   - Malformed SNMP telemetry events failing contract validation are routed to a quarantine dead-letter queue (DLQ) without interrupting the stream.
3. **Sliding Aggregation Windows**:
   - Uses 5-minute tumbling/sliding windows for smooth metric aggregation across 12,000 edge nodes.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Late / Out-of-Order Events** | State store unbounded growth | Event-time watermarking drops late data after 10-min threshold. |
| **Concurrent Write Corruption** | Partial read errors on downstream ML | Delta Lake ACID transaction log (`_delta_log`) guarantees optimistic concurrency control. |
| **Malformed JSON Stream Data** | Parser crash | Schema validation wrapper routes invalid events to DLQ. |
