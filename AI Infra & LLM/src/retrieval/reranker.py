import numpy as np
from src.retrieval.embedder import LocalEmbedder
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("reranker")

class CrossEncoderReranker:
    def __init__(self):
        self.model_name = settings.reranker_model
        self.embedder = LocalEmbedder()
        self.has_transformers = False
        self._init_cross_encoder()

    def _init_cross_encoder(self):
        try:
            # Check if sentence-transformers is available
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            self.has_transformers = True
            logger.info(f"Initialized sentence-transformers CrossEncoder: {self.model_name}")
        except Exception:
            logger.warn("sentence-transformers not installed or failed to load model. Falling back to Embedding Cosine Sim Reranking.")

    def rerank(self, query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
        """
        Takes candidate chunks and scores relevance using Cross-Encoder model.
        Falls back to Embedding Cosine Similarity if model is not loaded.
        """
        if not chunks:
            return []

        scored_chunks = []
        
        if self.has_transformers:
            try:
                pairs = [[query, chunk["payload"]["text"]] for chunk in chunks]
                scores = self.model.predict(pairs)
                for chunk, score in zip(chunks, scores):
                    scored_chunks.append({
                        "score": float(score),
                        "payload": chunk["payload"]
                    })
            except Exception as e:
                logger.error(f"Transformers reranking failed: {e}. Falling back.")
                self.has_transformers = False

        # Fallback logic: Compute cosine similarity using dense embedding comparisons
        if not self.has_transformers:
            query_vec = np.array(self.embedder.get_embedding(query))
            for chunk in chunks:
                chunk_text = chunk["payload"].get("text", "")
                chunk_vec = np.array(self.embedder.get_embedding(chunk_text))
                
                # Cosine Similarity
                dot_prod = np.dot(query_vec, chunk_vec)
                norm_q = np.linalg.norm(query_vec)
                norm_c = np.linalg.norm(chunk_vec)
                similarity = float(dot_prod / (norm_q * norm_c)) if (norm_q > 0 and norm_c > 0) else 0.0
                
                # Add word overlap bias to boost relevance sorting under mock embeddings
                query_words = set(query.lower().split())
                chunk_words = set(chunk_text.lower().split())
                overlap = len(query_words.intersection(chunk_words))
                similarity += overlap * 0.1

                scored_chunks.append({
                    "score": similarity,
                    "payload": chunk["payload"]
                })

        # Sort descending by relevance score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
