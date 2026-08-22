# Project 27: PGVector Incident Runbook Retriever

Production-grade implementation of **PGVector on Amazon RDS PostgreSQL** for **Sub-millisecond Incident Runbook Retrieval and Hybrid Search** (combining Dense HNSW Vector Cosine Distance + Sparse BM25 Keyword Matching).

---

## 🏗️ Architecture Overview

```
[ Alarm Event / Query ] 
       │
       ▼
[ FastAPI Hybrid Search Router ]
       │
       ├──► [ Amazon Titan Dense Embeddings ] ──► [ PGVector HNSW Cosine Index ] ──┐
       │                                                                           ▼
       └──► [ PostgreSQL tsvector / BM25 ] ────► [ GIN Full-Text Index ] ─────────► [ Reciprocal Rank Fusion (RRF) ]
                                                                                   │
                                                                                   ▼
                                                                        [ Top-K Scored Runbooks ]
```

---

## 🚀 Key Architectural Highlights

1. **Hybrid Search ($\alpha$-blended):** Combines semantic vector similarity (`alpha=0.7`) with exact keyword tokens (`1-alpha=0.3`) to prevent hallucinations and match exact error codes (e.g. `503`, `SFP+`, `SCTP-38412`).
2. **Metadata Filtering (WHERE clause pushdown):** Executes vendor and severity filtering directly inside PostgreSQL before vector distance calculation.
3. **HNSW vs IVFFlat Indexing:** Utilizes Hierarchical Navigable Small World (HNSW) graphs on RDS PostgreSQL for $O(\log N)$ search latency with high recall under continuous write updates.

---

## 🧪 Testing

```bash
cd 27-pgvector-incident-runbook-retriever
pytest tests/ -v
```
