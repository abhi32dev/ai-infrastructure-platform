import pytest
import numpy as np
from src.retrieval.embedder import LocalEmbedder
from src.retrieval.vector_store import VectorStore
from src.retrieval.reranker import CrossEncoderReranker
from src.retrieval.pipeline import RetrievalPipeline

@pytest.fixture
def embedder():
    return LocalEmbedder()

@pytest.fixture
def store():
    vs = VectorStore()
    vs.create_collection_if_not_exists(vector_size=1536)
    return vs

@pytest.fixture
def reranker():
    return CrossEncoderReranker()

@pytest.fixture
def pipe():
    return RetrievalPipeline()

def test_05_local_embedder_fallback(embedder):
    vector = embedder.get_embedding("Check fallback embeddings")
    assert len(vector) == 1536
    assert isinstance(vector[0], float)

def test_06_embedding_batch_generation(embedder):
    vectors = embedder.get_embeddings(["Query one", "Query two"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 1536

def test_07_vector_store_recreate_upsert(store):
    store.upsert_chunks(
        ids=[101, 102],
        vectors=[[0.1]*1536, [0.2]*1536],
        payloads=[{"text": "Chunk 1", "candidate_id": "c-101"}, {"text": "Chunk 2", "candidate_id": "c-102"}]
    )
    res = store.search_nearest([0.1]*1536, top_k=2)
    assert len(res) >= 1
    assert res[0]["payload"]["candidate_id"] in ["c-101", "c-102"]

def test_08_reranker_fallback_sort(reranker):
    chunks = [
        {"payload": {"text": "Highly relevant Python Triton scheduling kernel details"}},
        {"payload": {"text": "Unrelated fruit salad preparation instructions"}}
    ]
    res = reranker.rerank(query="Triton GPU scheduler kernel", chunks=chunks, top_k=2)
    assert len(res) == 2
    # The relevant one should rank higher
    assert "Triton" in res[0]["payload"]["text"]

def test_09_pipeline_semantic_chunking(pipe):
    text = " ".join([f"word{i}" for i in range(500)])
    chunks = pipe.semantic_chunk_text(text, chunk_size_words=200, overlap_words=25)
    assert len(chunks) == 3  # (500 - 200) / 175 = 1.7 -> ceil is 3
    assert len(chunks[0].split()) == 200
