# Production Architecture & Design Trade-offs: High-Throughput RAG Engine

## 1. Executive Context & Business Motivation
Standard RAG systems relying solely on dense vector search fail to capture exact keyword matches (e.g. error codes, product serial numbers, technical jargon), while keyword-only search (BM25) fails on semantic meaning. Furthermore, multi-tenant enterprise search requires sub-50ms retrieval SLAs and strict tenant metadata isolation.

This engine implements a **High-Throughput Hybrid BM25 + Vector Search Engine with Reciprocal Rank Fusion (RRF)**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Hybrid Search (Dense + Sparse RRF) vs Dense Vector Only
- **Chosen Option**: **Hybrid BM25 Keyword + Vector Search combined via Reciprocal Rank Fusion (RRF)**.
- **Alternative Evaluated**: Vector-only search (Cosine similarity).
- **Trade-Off Rationale**:
  - *Vector-Only*: Fails on exact code queries like `ERR_NEXUS_9012`.
  - *Hybrid RRF*: Combines top-K dense embeddings with top-K BM25 lexical results using formula $RRF\_Score(d) = \sum \frac{1}{k + r_i(d)}$.
  - *Trade-off*: Performs two query passes (dense + sparse), increasing latency slightly (~10ms). Mitigated by parallel async execution.

### B. Embedded ChromaDB vs Remote Managed Vector DB (Pinecone/Milvus)
- **Chosen Option**: **ChromaDB Vector Store with Metadata Filtering**.
- **Trade-Off Rationale**:
  - *Remote SaaS Vector DB*: Adds network latency (~30-80ms) and per-query API costs.
  - *Embedded ChromaDB*: Sub-10ms query performance, zero network overhead, native metadata filtering by `tenant_id`.

---

## 3. Best Practices & Production Design Principles

1. **Reciprocal Rank Fusion (RRF) Re-ranking**:
   - Merges disparate ranking metrics without needing score normalization across different vector spaces.
2. **Metadata-Based Multi-Tenant Isolation**:
   - Enforces strict tenant filtering (`{"tenant_id": "$TENANT"}`) at the vector index query level to prevent cross-tenant data leakage.
3. **Empty Collection Handling**:
   - Safe fallbacks when querying un-indexed collections or zero-match search inputs.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Empty / Zero Match Query** | Index error or empty list crash | Graceful empty list return with zero score flags. |
| **Cross-Tenant Data Exposure** | Critical security/compliance violation | Index-level mandatory `tenant_id` metadata filter scoping. |
| **High Latency Re-Ranking** | SLA breach (>50ms) | Top-K candidate capping ($K=20$) before RRF scoring. |
