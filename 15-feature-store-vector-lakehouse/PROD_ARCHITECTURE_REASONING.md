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
