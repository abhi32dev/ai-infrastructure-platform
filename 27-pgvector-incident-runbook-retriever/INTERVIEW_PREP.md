# Interview Preparation Guide: Project 27

### 1. How to describe this project in an interview:
> "To support automated incident triage at Comcast, we needed sub-millisecond retrieval of historical incident runbooks across 4 hardware vendors. Rather than managing a separate vector database cluster like Pinecone or Milvus, I utilized **PGVector on our existing Amazon RDS PostgreSQL instance**. I designed a hybrid search pipeline combining dense embeddings (HNSW cosine similarity) and sparse keyword matching (tsvector) with SQL metadata filtering (vendor, severity), achieving 99.4% recall on historical error patterns in under 12ms."

### 2. Deep-Dive Architectural Questions:
* **Why HNSW over IVFFlat in pgvector?**
  * `IVFFlat` creates Voronoi cells; it requires periodic retraining (`VACUUM / REINDEX`) as new data is inserted and has lower recall on un-clustered points.
  * `HNSW` builds a multi-layer graph index that supports incremental real-time insertions with zero index downtime and higher recall ($>98\%$) at p99 $<15\text{ms}$.
* **How did you handle Hybrid Search in PostgreSQL?**
  * We combined `ORDER BY embedding <=> query_vec` (dense) and `ts_rank_cd(to_tsvector(content), query)` (sparse) using a weighted linear combination or Reciprocal Rank Fusion (RRF), ensuring exact error codes (like `503` or `SFP+`) are never missed by vector-only fuzzy matching.
