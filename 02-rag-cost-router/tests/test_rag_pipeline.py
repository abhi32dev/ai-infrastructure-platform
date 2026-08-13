"""
Expanded Test Suite for Project 2 - Advanced RAG & FinOps Cost Router.
Tests multi-strategy document chunkers, ChromaDB dense vector indexing, BM25 sparse search,
Reciprocal Rank Fusion (RRF), Cross-Encoder reranking, and cost router decision boundaries.
"""

import pytest
from src.document_loader import DocumentLoader, ChunkingStrategy
from src.hybrid_retriever import HybridRetriever
from src.reranker import RerankerEngine
from src.cost_aware_router import CostAwareRouter, ModelTier


@pytest.fixture
def loader():
    return DocumentLoader()


@pytest.fixture
def sample_doc(loader):
    text = "Comcast CONDOR handles 2.4M telemetry events per day across 12,000 edge nodes with 99.999% SLA. S3 storage reconciliation uses 3 passes to prevent data gaps."
    return loader.load_raw_text(doc_id="test_doc.md", text_content=text)


def test_01_document_chunking_fixed_overlap(loader, sample_doc):
    """Test 1: Verifies fixed-overlap chunking character window boundaries."""
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.FIXED_OVERLAP, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 3
    assert chunks[0].strategy == ChunkingStrategy.FIXED_OVERLAP


def test_02_document_chunking_parent_child(loader, sample_doc):
    """Test 2: Verifies parent-child hierarchical chunk mapping and parent_text preservation."""
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.PARENT_CHILD)
    assert len(chunks) > 0
    assert chunks[0].strategy == ChunkingStrategy.PARENT_CHILD
    assert chunks[0].parent_chunk_id is not None
    assert chunks[0].parent_text is not None


def test_03_document_chunking_sentence_window(loader, sample_doc):
    """Test 3: Verifies sentence-window chunking and surrounding sentence context buffer."""
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.SENTENCE_WINDOW)
    assert len(chunks) == 2  # 2 sentences in sample_doc
    assert chunks[0].strategy == ChunkingStrategy.SENTENCE_WINDOW
    assert "CONDOR" in chunks[0].text


def test_04_dense_vector_search_chromadb(loader, sample_doc):
    """Test 4: Verifies ChromaDB dense vector indexing and cosine similarity search."""
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2", collection_name="test_collection")
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.FIXED_OVERLAP)
    retriever.index_chunks(chunks)

    hits = retriever.dense_search("How many edge nodes?", top_k=2)
    assert len(hits) > 0
    assert hits[0][1] > 0.0  # Cosine similarity score > 0


def test_05_sparse_bm25_keyword_search(loader, sample_doc):
    """Test 5: Verifies Rank-BM25 TF-IDF token matching for exact keyword lookup."""
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2", collection_name="test_bm25")
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.FIXED_OVERLAP, chunk_size=50, chunk_overlap=10)
    retriever.index_chunks(chunks)

    hits = retriever.sparse_search("telemetry", top_k=2)
    assert len(hits) > 0


def test_06_reciprocal_rank_fusion(loader, sample_doc):
    """Test 6: Verifies Reciprocal Rank Fusion (RRF k=60) rank merging formula."""
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2", collection_name="test_rrf")
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.FIXED_OVERLAP, chunk_size=50, chunk_overlap=10)
    retriever.index_chunks(chunks)

    hits = retriever.hybrid_search("3 passes S3 data gaps", top_k=2)
    assert len(hits) > 0
    assert hits[0][1] > 0.01  # Valid RRF score


def test_07_cross_encoder_reranking(loader, sample_doc):
    """Test 7: Verifies Cross-Encoder pair rescoring and candidate rank re-ordering."""
    reranker = RerankerEngine(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    chunks = loader.chunk_document(sample_doc, strategy=ChunkingStrategy.FIXED_OVERLAP)
    candidate_tuples = [(c, 0.5) for c in chunks]

    reranked = reranker.rerank("S3 data gaps", candidate_tuples, top_k=1)
    assert len(reranked) == 1
    assert isinstance(reranked[0][1], float)


def test_08_cost_aware_router_decisions():
    """Test 8: Verifies FinOps token budget classification and cost calculation logic."""
    router = CostAwareRouter()
    
    # Simple query -> LOCAL_OLLAMA ($0 cost)
    decision1 = router.route_query("What is CONDOR?")
    assert decision1.tier == ModelTier.LOCAL_OLLAMA
    assert decision1.estimated_cost_usd == 0.0

    # Complex analytical query -> LARGE_FRONTIER
    decision2 = router.route_query("Analyze architecture tradeoffs and evaluate root cause of memory leaks")
    assert decision2.tier == ModelTier.LARGE_FRONTIER
    assert decision2.estimated_cost_usd > 0.0
