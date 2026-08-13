"""
Master 7-Stage RAG Pipeline Orchestrator & Cost Engineering Suite.
Integrates Document Ingestion, Multi-Strategy Chunking, Hybrid Vector/BM25 Search, RRF Fusion,
Cross-Encoder Reranking, HyDE Query Rewriting, and Cost-Aware Model Routing.
"""

from typing import Any, Dict, List, Optional
from src.cost_aware_router import CostAwareRouter, RoutingDecision
from src.document_loader import ChunkingStrategy, DocumentChunk, DocumentLoader
from src.hybrid_retriever import HybridRetriever
from src.query_transformer import QueryTransformer
from src.reranker import RerankerEngine


class RAGPipeline:
    def __init__(self):
        print("[RAG PIPELINE] Initializing 7-Stage RAG Engine...")
        self.loader = DocumentLoader()
        self.retriever = HybridRetriever()
        self.reranker = RerankerEngine()
        self.query_transformer = QueryTransformer()
        self.router = CostAwareRouter()

    def ingest_documents(
        self, 
        docs: List[Dict[str, Any]], 
        strategy: ChunkingStrategy = ChunkingStrategy.PARENT_CHILD
    ) -> int:
        """
        Stage 1 & 2: Ingests documents, applies chunking strategy, and indexes into Hybrid Store.
        """
        all_chunks: List[DocumentChunk] = []
        for doc in docs:
            chunks = self.loader.chunk_document(doc, strategy=strategy)
            all_chunks.extend(chunks)

        # Stage 3: Vector Embeddings & BM25 Indexing
        self.retriever.index_chunks(all_chunks)
        return len(all_chunks)

    def execute_rag(
        self, 
        user_query: str, 
        top_k: int = 3, 
        use_hyde: bool = True,
        use_reranker: bool = True
    ) -> Dict[str, Any]:
        """
        Executes full 7-Stage RAG workflow:
        Stage 4: Query Transformation / HyDE
        Stage 5: Hybrid Retrieval (Dense + BM25 + RRF)
        Stage 6: Cross-Encoder Reranking
        Stage 7: Context Assembly & Cost-Aware Model Routing
        """
        # Stage 4: Query Transformation
        rewritten_query = self.query_transformer.rewrite_query(user_query)
        search_query = rewritten_query

        if use_hyde:
            search_query = self.query_transformer.generate_hypothetical_document(user_query)

        # Stage 5: Hybrid Retrieval (Dense Vector + BM25 Sparse + RRF)
        hybrid_candidates = self.retriever.hybrid_search(search_query, top_k=top_k * 2)

        # Stage 6: Cross-Encoder Reranking
        if use_reranker and hybrid_candidates:
            reranked_hits = self.reranker.rerank(rewritten_query, hybrid_candidates, top_k=top_k)
        else:
            reranked_hits = hybrid_candidates[:top_k]

        # Assemble Generation Context (using parent text if Parent-Child / Sentence-Window chunking)
        context_blocks = []
        retrieved_sources = []

        for chk, score in reranked_hits:
            source_text = chk.parent_text if chk.parent_text else chk.text
            context_blocks.append(source_text)
            retrieved_sources.append({
                "chunk_id": chk.chunk_id,
                "doc_id": chk.doc_id,
                "strategy": chk.strategy.value,
                "rerank_score": round(score, 4),
                "text_snippet": source_text[:150] + "..."
            })

        assembled_context = "\n---\n".join(context_blocks)

        # Stage 7: Cost & Intent-Aware Dynamic Model Routing
        routing_decision = self.router.route_query(user_query, retrieved_context=assembled_context)

        # Simulated Model Generation
        simulated_response = (
            f"Based on retrieved infrastructure documentation: For '{user_query}', "
            f"the system maintains 99.999% SLA using health-checked EC2 receivers behind NLB "
            f"with SQS backpressure isolation."
        )

        return {
            "user_query": user_query,
            "rewritten_query": rewritten_query,
            "used_hyde": use_hyde,
            "retrieved_sources": retrieved_sources,
            "assembled_context": assembled_context,
            "routing_decision": routing_decision.dict(),
            "generated_response": simulated_response
        }
