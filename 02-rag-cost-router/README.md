# 🔍 Project 2: Advanced RAG, Hybrid Search & Cost-Aware Model Router

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/02-rag-cost-router/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---

A production-grade, local-first **7-Stage Retrieval-Augmented Generation (RAG)** pipeline and **Cost Engineering Suite** implementing multi-strategy chunking, ChromaDB vector embeddings, BM25 sparse retrieval, Reciprocal Rank Fusion (RRF), Cross-Encoder reranking, HyDE query rewriting, and intent/token-cost-aware dynamic model routing.

---

## 🎯 Resume & Architecture Mapping

| Feature / RAG Stage | Resume Claim Mapped | Implementation Module |
| :--- | :--- | :--- |
| **Multi-Strategy Chunking** | Fixed-overlap, Parent-Child, Sentence-Window | [`src/document_loader.py`](src/document_loader.py) |
| **Hybrid Dense + Sparse Search** | ChromaDB vector search + BM25 keyword search | [`src/hybrid_retriever.py`](src/hybrid_retriever.py) |
| **Reciprocal Rank Fusion (RRF)** | Dense/Sparse score fusion ($k=60$) | [`src/hybrid_retriever.py`](src/hybrid_retriever.py) |
| **Cross-Encoder Reranking** | Rescoring top-$K$ candidates for precision context | [`src/reranker.py`](src/reranker.py) |
| **HyDE & Query Transformation** | Hypothetical document embeddings & acronym expansion | [`src/query_transformer.py`](src/query_transformer.py) |
| **Token & Cost-Aware Model Router**| Query classification, context length & cost tracking | [`src/cost_aware_router.py`](src/cost_aware_router.py) |

---

## 📁 Repository Structure

```text
02-rag-cost-router/
├── src/
│   ├── document_loader.py    # Document parsing & chunking (Fixed, Parent-Child, Sentence-Window)
│   ├── hybrid_retriever.py   # Dense (ChromaDB) + Sparse (BM25) + Reciprocal Rank Fusion (RRF)
│   ├── reranker.py           # Cross-Encoder rescoring engine
│   ├── query_transformer.py  # HyDE generation & domain acronym expansion
│   ├── cost_aware_router.py  # Intent-aware dynamic query router & token cost calculator
│   └── rag_pipeline.py       # Master 7-Stage RAG Pipeline Orchestrator
├── data/
│   └── sample_docs/          # Enterprise infrastructure architecture specifications
├── tests/
│   └── test_rag_pipeline.py  # Pytest test suite for RAG retrieval & router logic
├── app.py                    # FastAPI REST server & embedded RAG Visualizer Playground
├── demo_runner.py            # Interactive CLI script running 5 core RAG & routing scenarios
├── requirements.txt          # Project dependencies
├── README.md                 # System documentation
└── INTERVIEW_PREP.md          # Staff AI Infra Interview Guide
```

---

## 🚦 Quick Start & Interactive Demo

### 1. Run the Interactive CLI Demo
```bash
python3 demo_runner.py
```
This executes 5 core production scenarios:
- **Scenario 1**: Multi-Strategy Chunking comparison.
- **Scenario 2**: Dense Vector Search vs BM25 Keyword Search vs RRF Fusion.
- **Scenario 3**: Cross-Encoder Reranking for high top-$K$ precision.
- **Scenario 4**: HyDE & Acronym query rewriting.
- **Scenario 5**: Token-Cost-Aware Model Routing (calculating query cost in USD).

### 2. Run Pytest Suite
```bash
pytest tests/
```

### 3. Launch FastAPI Server & RAG Playground
```bash
python3 app.py
```
Then open your browser to **http://127.0.0.1:8001** to test technical queries, inspect rerank scores, and view dynamic cost routing!