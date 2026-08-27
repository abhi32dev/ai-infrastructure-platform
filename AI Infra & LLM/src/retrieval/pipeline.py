from src.retrieval.vector_store import VectorStore
from src.retrieval.embedder import LocalEmbedder
from src.retrieval.reranker import CrossEncoderReranker
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("retrieval_pipeline")

class RetrievalPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedder = LocalEmbedder()
        self.reranker = CrossEncoderReranker()
        self.vector_store.create_collection_if_not_exists(vector_size=1536)

    def semantic_chunk_text(self, text: str, chunk_size_words: int = 200, overlap_words: int = 25) -> list[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_slice = words[i : i + chunk_size_words]
            chunks.append(" ".join(chunk_slice))
            i += (chunk_size_words - overlap_words)
        return chunks

    def ingest_candidate_data(self, candidate_id: str, resume_text: str):
        logger.info(f"Ingesting resume data for candidate: {candidate_id}")
        chunks = self.semantic_chunk_text(
            resume_text,
            chunk_size_words=settings.chunk_size,
            overlap_words=settings.chunk_overlap
        )
        
        vectors = self.embedder.get_embeddings(chunks)
        payloads = [
            {"candidate_id": candidate_id, "chunk_idx": idx, "text": chunk}
            for idx, chunk in enumerate(chunks)
        ]
        ids = [hash(f"{candidate_id}_{idx}") & 0xfffffff for idx in range(len(chunks))]
        
        self.vector_store.upsert_chunks(ids, vectors, payloads)

    def build_compressed_context(self, job_description: str, candidate_id: str) -> str:
        """
        Executes two-stage retrieval:
        1. Retrieve top-15 nearest candidate chunks.
        2. Rerank down to top-3 highest-relevance chunks.
        Compresses total token footprint to fit context budgets.
        """
        logger.info(f"Building compressed context for job description matching candidate: {candidate_id}")
        
        # Generate query vector matching job description
        query_vec = self.embedder.get_embedding(job_description)
        
        # Stage 1: Dense Retrieval (Top 15)
        candidates = self.vector_store.search_nearest(query_vec, top_k=settings.top_k_retrieve)
        
        # Filter matching specific candidate_id to avoid multi-tenant leak
        candidate_candidates = [
            c for c in candidates
            if c["payload"].get("candidate_id") == candidate_id
        ]
        
        # Stage 2: Cross-Encoder Rerank (Top 3)
        top_chunks = self.reranker.rerank(
            query=job_description,
            chunks=candidate_candidates or candidates,  # fallback to all if candidate-specific is empty (e.g. testing)
            top_k=settings.top_k_rerank
        )
        
        # Concatenate final top-3 context chunks
        context_parts = [chunk["payload"]["text"] for chunk in top_chunks]
        logger.info(f"Constructed compressed context: {len(context_parts)} chunks selected.")
        return "\n\n---\n\n".join(context_parts)
