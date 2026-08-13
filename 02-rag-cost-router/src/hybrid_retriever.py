"""
Hybrid Dense Vector + Sparse BM25 Retriever with Reciprocal Rank Fusion (RRF).
Combines semantic vector embeddings with exact keyword matches to maximize retrieval recall & precision.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from src.document_loader import DocumentChunk


class HybridRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", collection_name: str = "rag_collection"):
        print(f"[HYBRID RETRIEVER] Initializing SentenceTransformer model '{model_name}'...")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Persistent ChromaDB client setup on disk
        import os
        os.makedirs("data/chroma_db", exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path="data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        
        self.chunks_db: Dict[str, DocumentChunk] = {}
        self.bm25_index: Optional[BM25Okapi] = None
        self.bm25_chunk_ids: List[str] = []

    def index_chunks(self, chunks: List[DocumentChunk]):
        """
        Indexes chunks across both Dense Vector Store (ChromaDB) and Sparse Keyword Index (BM25).
        """
        if not chunks:
            return

        texts = [chk.text for chk in chunks]
        ids = [chk.chunk_id for chk in chunks]
        metadatas = [{"doc_id": chk.doc_id, "strategy": chk.strategy.value} for chk in chunks]

        # Generate Dense Vector Embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        # Store in local memory map
        for chk in chunks:
            self.chunks_db[chk.chunk_id] = chk

        # Tokenize for BM25 Sparse Index
        tokenized_corpus = [doc.lower().split() for doc in texts]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        self.bm25_chunk_ids = ids

        print(f"[HYBRID RETRIEVER] Successfully indexed {len(chunks)} document chunks in Vector DB & BM25 index.")

    def dense_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Performs Dense Vector Cosine Similarity Search."""
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=top_k)
        
        dense_results = []
        if results and results["ids"] and results["ids"][0]:
            chunk_ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0]*len(chunk_ids)
            for cid, dist in zip(chunk_ids, distances):
                score = 1.0 / (1.0 + dist)  # Convert distance to similarity score
                dense_results.append((cid, score))
        return dense_results

    def sparse_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Performs Sparse BM25 Keyword Search."""
        if not self.bm25_index:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]

        sparse_results = []
        for idx in top_indices:
            cid = self.bm25_chunk_ids[idx]
            score = float(scores[idx])
            if score >= 0:
                sparse_results.append((cid, score))

        return sparse_results

    def hybrid_search(self, query: str, top_k: int = 5, rrf_k: int = 60) -> List[Tuple[DocumentChunk, float]]:
        """
        Reciprocal Rank Fusion (RRF) Hybrid Search.
        RRF Score(d) = 1 / (rrf_k + rank_dense(d)) + 1 / (rrf_k + rank_sparse(d))
        """
        dense_hits = self.dense_search(query, top_k=top_k * 2)
        sparse_hits = self.sparse_search(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}

        # Accumulate Dense RRF Scores
        for rank, (cid, _) in enumerate(dense_hits):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        # Accumulate Sparse RRF Scores
        for rank, (cid, _) in enumerate(sparse_hits):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        # Sort candidate chunks by RRF score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

        output = []
        for cid, score in sorted_candidates:
            chunk = self.chunks_db.get(cid)
            if chunk:
                output.append((chunk, score))

        return output
