# Production Architecture & Design Trade-offs: Feature Store & PyArrow Vector Lakehouse

## 1. Executive Context & Business Motivation
In enterprise machine learning, training offline models on features extracted at point-in-time $T_1$ while serving real-time inference using features from $T_2$ creates **training-serving skew**, causing silent model performance degradation in production.

This system provides a **Feast / Hopsworks Dual-Storage Feature Store (Redis Online + Parquet Offline) with PyArrow Zero-Copy Vector Serialization**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Dual Online + Offline Storage Architecture vs Single Database
- **Chosen Option**: **Redis Online Store (<2ms) + Parquet/S3 Offline Lakehouse Store**.
- **Alternative Evaluated**: Single relational or document database.
- **Trade-Off Rationale**:
  - *Single RDBMS*: Cannot handle sub-2ms key-value lookups for thousands of concurrent inference entities while supporting petabyte-scale offline historical queries.
  - *Dual Architecture*: Low-latency in-memory Online Store serves real-time inference, while columnar Parquet/Iceberg handles historical batch extraction.

### B. PyArrow Zero-Copy IPC Serialization vs Python Object Deserialization
- **Chosen Option**: **PyArrow Zero-Copy Memory-Mapped IPC Buffers**.
- **Trade-Off Rationale**: Eliminates Python object allocation and memory copying when scanning high-dimensional vector embeddings, scanning 100k+ rows in <5ms.

---

## 3. Best Practices & Production Design Principles

1. **Point-In-Time Time-Travel Joins**:
   - Joins feature values strictly as-of historical observation timestamps (`timestamp <= as_of`), preventing future data leakage into training sets.
2. **Column Pruning & Zero-Copy Scans**:
   - Reads only requested embedding vector columns directly from memory-mapped Parquet buffers.
3. **Multi-Feature Batch Lookups**:
   - Serves multi-feature vectors in single batched operations.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Training-Serving Feature Skew** | Model accuracy drop in prod | Point-in-time time-travel feature join logic. |
| **Missing Entity Feature Lookup** | Inference crash | Safe fallback values returned with `found=False` status flag. |
| **Memory Allocation Overhead on Large Vectors** | High GC latency in Python | Memory-mapped PyArrow zero-copy IPC buffer queries. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Provides dual-layer feature storage: sub-2ms online feature serving from Redis in-memory cache and point-in-time correct temporal joins on Parquet lakehouse tables without data leakage.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "entity_ids": ["user_102", "user_103"],
  "feature_names": ["avg_spend_30d", "fraud_risk_score"],
  "event_timestamp": "2026-08-14T10:00:00Z"
}
```
**Input Parameter Specification**:
Entity IDs, requested feature names, and observation timestamp for temporal join.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Redis Online Cache Lookup**: Queries Redis hash key store for pre-materialized online feature vectors.
- **2. Decision 1 (Online Cache Hit)**: If feature vectors exist in Redis, returns payload immediately (<2ms, $0 lakehouse read cost).
- **3. PyArrow ASOF Point-in-Time Join**: If cache miss, executes PyArrow ASOF join against Parquet lakehouse storage.
- **4. Decision 2 (Temporal Data Leakage Check)**: Verifies that feature timestamps strictly precede observation event timestamp (`feature_time <= event_time`). If valid, populates Redis cache and returns vector.
- **5. Decision 3 (Missing Feature Imputation)**: If entity feature is absent, injects mean-imputed baseline default values to prevent model null exceptions.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "features": {
    "user_102": {"avg_spend_30d": 412.50, "fraud_risk_score": 0.02}
  },
  "served_from": "REDIS_ONLINE_CACHE",
  "latency_ms": 1.4,
  "data_leakage_detected": false
}
```
**Output Specification**:
Feature tensor record batch, source served (Redis vs Lakehouse), and imputation flags.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 15-feature-store-vector-lakehouse/tests/test_feature_lakehouse.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/15-feature-store-vector-lakehouse/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/15-feature-store-vector-lakehouse/FLOWCHART.svg)
