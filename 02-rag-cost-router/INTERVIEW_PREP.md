# 🎤 Staff / Principal AI Infrastructure Interview Guide: Advanced RAG & Cost Engineering

This guide bridges the code in **Project 2 (`02-rag-cost-router`)** directly to Staff/Principal-level questions asked by FAANG, Tier-1 AI startups, and top product companies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why do vector databases alone fail for enterprise domain search, and how do you solve it?"
> **Staff Engineer Answer**:
> "Dense vector embeddings (bi-encoders) map text into semantic space, making them exceptional at capturing broad concepts. However, they frequently fail on exact keyword matches—such as error codes (`ERR-504`), specific port numbers (`UDP 162`), or exact configuration keys—because dense vectors smooth out fine-grained lexical tokens.
> 
> In `02-rag-cost-router`, we solve this by implementing **Hybrid Retrieval with Reciprocal Rank Fusion (RRF)** ([`src/hybrid_retriever.py`](src/hybrid_retriever.py)). 
> 
> We run ChromaDB dense vector search in parallel with a sparse BM25 keyword index. We then fuse the candidate lists using RRF:
> 
> $$RRF(d) = \sum_{m \in \{Dense, Sparse\}} \frac{1}{k + r_m(d)}$$
> 
> This guarantees that exact keyword hits rank at the top without sacrificing semantic search recall."

---

### Q2: "How do you improve RAG retrieval precision without overloading the LLM context window?"
> **Staff Engineer Answer**:
> "Bi-encoders trade off ranking accuracy for speed so they can scale to millions of vectors. To get frontier-level precision for generation, we apply a two-stage retrieval architecture: **Retrieval ➔ Reranking** ([`src/reranker.py`](src/reranker.py)).
> 
> First, our hybrid retriever fetches candidate chunks (e.g. top 10-20). Then, we pass these candidates to a **Cross-Encoder model** (`ms-marco-MiniLM-L-6-v2`). The cross-encoder feeds the `(query, document)` pair together through cross-attention layers, computing exact semantic relevance. We take only the top 2-3 reranked chunks for context assembly, eliminating false-positive noise and optimizing prompt token costs."

---

### Q3: "How do you optimize LLM token costs at scale across millions of queries?"
> **Staff Engineer Answer**:
> "Not all queries require a $5/1M token frontier model like GPT-4o. We built an **Intent & Token-Cost-Aware Dynamic Model Router** ([`src/cost_aware_router.py`](src/cost_aware_router.py)).
> 
> The router analyzes query intent and estimated token payload (prompt + retrieved context):
> - **Simple Factual Lookups** (short context, basic questions) are routed to fast, zero-cost local models (such as Ollama `llama3.2:1b` / `qwen2.5`).
> - **Complex Analytical Queries** (multi-part trade-off analysis or large context windows) are routed to frontier API models.
> 
> This hybrid routing strategy reduces inference spend by 60-80% across high-volume production traffic while preserving peak model intelligence where it actually matters."

---

## 🧪 Quick Test Checklist for Candidates
Run these commands in your workspace to test and demonstrate:
- `python3 demo_runner.py`: Demonstrates all 5 RAG and cost routing scenarios live.
- `pytest tests/`: Verifies unit and integration test suite.
- `python3 app.py`: Opens RAG Playground at `http://127.0.0.1:8001` to visually inspect rerank scores and cost routing.
