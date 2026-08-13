"""
Interactive CLI Runner for Project 2 - RAG & Cost Router.
Ingests real enterprise Markdown documents from data/documents/, chunks text using
multi-strategy loaders, generates 384-dim dense vector embeddings, stores them in persistent
ChromaDB at data/chroma_db/, and performs hybrid BM25 + Vector search + Cross-Encoder reranking.
"""

import os
import glob
from src.document_loader import DocumentLoader, ChunkingStrategy
from src.hybrid_retriever import HybridRetriever
from src.reranker import RerankerEngine
from src.query_transformer import QueryTransformer
from src.cost_aware_router import CostAwareRouter


def run_demo():
    print("==========================================================================")
    print("🔍 STARTING REAL RAG RETRIEVAL & VECTOR DATABASE DEMO")
    print("==========================================================================\n")

    loader = DocumentLoader()
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2", collection_name="enterprise_knowledge")
    reranker = RerankerEngine(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    router = CostAwareRouter()

    # -------------------------------------------------------------------------
    # SCENARIO 1: Ingesting Real Enterprise Technical Documents
    # -------------------------------------------------------------------------
    print("--- [SCENARIO 1] Ingesting Real Enterprise Documents from data/documents/ ---")
    doc_files = glob.glob("data/documents/*.md")
    all_chunks = []

    for file_path in doc_files:
        doc_id = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc_obj = loader.load_raw_text(doc_id=doc_id, text_content=content)
        # Apply PARENT_CHILD hierarchical chunking
        chunks = loader.chunk_document(doc_obj, strategy=ChunkingStrategy.PARENT_CHILD)
        all_chunks.extend(chunks)
        print(f"  └─ Ingested [{doc_id}]: {len(content)} chars -> Generated {len(chunks)} Parent-Child Chunks")

    # Index chunks into persistent ChromaDB & BM25
    retriever.index_chunks(all_chunks)

    # -------------------------------------------------------------------------
    # SCENARIO 2: Hybrid Dense Vector + Sparse BM25 Search & RRF Fusion
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 2] Real Hybrid Search (ChromaDB + BM25 + RRF Fusion k=60) ---")
    query = "How does 3-pass reconciliation fix S3 data gaps?"
    print(f"User Query: '{query}'")

    hybrid_hits = retriever.hybrid_search(query, top_k=4)
    print(f"Retrieved Top-{len(hybrid_hits)} Hybrid Candidate Chunks:")
    for rank, (chunk, rrf_score) in enumerate(hybrid_hits, 1):
        print(f"  └─ [Rank {rank}] Doc: {chunk.doc_id} | RRF Score: {rrf_score:.4f} | Text: {chunk.text[:90]}...")

    # -------------------------------------------------------------------------
    # SCENARIO 3: Cross-Encoder Reranking
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 3] Cross-Encoder Reranking (ms-marco-MiniLM-L-6-v2) ---")
    reranked_hits = reranker.rerank(query, hybrid_hits, top_k=2)

    print(f"Top-{len(reranked_hits)} Re-Ranked Passages:")
    for rank, (chunk, score) in enumerate(reranked_hits, 1):
        print(f"  └─ [Rank {rank}] Score: {score:.4f} | Parent Doc: {chunk.doc_id}")
        print(f"     Text Snippet: {chunk.text}")

    # -------------------------------------------------------------------------
    # SCENARIO 4: FinOps Cost-Aware Dynamic Model Router
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 4] FinOps Cost-Aware Dynamic Model Router ---")
    route_decision = router.route_query(query, retrieved_context="3-Pass reconciliation executes Pass 1 parallel ingestion, Pass 2 S3 prefix diff, and Pass 3 NVMe raw recovery.")

    print(f"Cost Router Decision:")
    print(f"  └─ Selected Target Model: {route_decision.assigned_model}")
    print(f"  └─ Tier:                  {route_decision.tier.value}")
    print(f"  └─ Reason:                {route_decision.routing_reason}")
    print(f"  └─ Cost per Query:        ${route_decision.estimated_cost_usd:.6f}")

    print("\n==========================================================================")
    print("✅ DEMO COMPLETED SUCCESSFULLY! REAL CHROMADB PERSISTED AT data/chroma_db/")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_demo()
