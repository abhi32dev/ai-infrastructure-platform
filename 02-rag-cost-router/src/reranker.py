"""
Cross-Encoder Reranking Engine.
Rescores and re-orders hybrid retrieval candidates using Cross-Attention transformer models.
Dramatically reduces false-positives and improves top-K context precision for LLM generation.
"""

from typing import List, Tuple
from sentence_transformers import CrossEncoder
from src.document_loader import DocumentChunk


class RerankerEngine:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        print(f"[RERANKER ENGINE] Loading Cross-Encoder model '{model_name}'...")
        try:
            self.model = CrossEncoder(model_name)
            self.is_loaded = True
        except Exception as e:
            print(f"[RERANKER WARNING] Could not load model '{model_name}': {e}. Using fallback heuristic scorer.")
            self.model = None
            self.is_loaded = False

    def rerank(
        self, 
        query: str, 
        candidate_chunks: List[Tuple[DocumentChunk, float]], 
        top_k: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Rescores (query, chunk_text) pairs using Cross-Encoder.
        Returns re-ranked list of (DocumentChunk, score) tuples.
        """
        if not candidate_chunks:
            return []

        chunks = [item[0] for item in candidate_chunks]
        
        if self.is_loaded and self.model:
            # Build query-document pairs
            pairs = [[query, chk.text] for chk in chunks]
            scores = self.model.predict(pairs)

            scored_chunks = []
            for chk, score in zip(chunks, scores):
                scored_chunks.append((chk, float(score)))
        else:
            # Fallback heuristic: keyword term overlap + initial score boost
            query_terms = set(query.lower().split())
            scored_chunks = []
            for chk, init_score in candidate_chunks:
                text_terms = set(chk.text.lower().split())
                overlap = len(query_terms.intersection(text_terms))
                boosted_score = init_score * 1.5 + (overlap * 0.2)
                scored_chunks.append((chk, float(boosted_score)))

        # Sort descending by cross-encoder score
        reranked = sorted(scored_chunks, key=lambda x: x[1], reverse=True)[:top_k]
        return reranked
