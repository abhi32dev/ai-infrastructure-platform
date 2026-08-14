# 🎤 Staff AI Platform Interview Guide: RAG Cost Router & Semantic Cache

This guide bridges **Project 2 (`02-rag-cost-router`)** directly to Staff/Principal-level questions asked by Databricks, Pinecone, and OpenAI.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you reduce enterprise LLM inference bills by 80%+ without degrading response quality?"
> **Staff Engineer Answer**:
> "In `02-rag-cost-router` (`src/cost_aware_router.py`), we implement a 3-tier routing architecture:
> 1. **Semantic Vector Cache**: Exact/semantic hits ($\ge 0.95$ cosine similarity) are served instantly from ChromaDB in $<5\text{ms}$ at $\$0.00$ cost.
> 2. **Local SLM Routing**: Low-complexity queries (syntactic score $\le 0.40$) route to local Ollama Llama-3-8B instances.
> 3. **Frontier Model Cascade**: Only high-complexity queries route to frontier models (Claude 3.5 Sonnet)."

### Q2: "How do you combine dense vector search with sparse keyword search effectively?"
> **Staff Engineer Answer**:
> "In `src/hybrid_retriever.py`, we compute dense HNSW vector similarity and BM25 sparse keyword scores, fusing rank orders using Reciprocal Rank Fusion (RRF): $\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$. A Cross-Encoder reranker selects the top 3 passages."

### Q3: "What is the primary failure mode of vector semantic caching, and how is it mitigated?"
> **Staff Engineer Answer**:
> "Semantic false positives occur when prompts share structure but differ in entities (e.g. 'Apple revenue in 2023' vs '2024'). We mitigate this by extracting temporal and named entities before cache lookup, forcing a cache miss if entity values diverge."
