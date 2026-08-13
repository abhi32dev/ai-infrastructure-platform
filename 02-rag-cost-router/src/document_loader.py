"""
Enterprise Document Loader & Multi-Strategy Chunking Engine.
Supports 3 chunking strategies:
1. FIXED_OVERLAP: Fixed character/token window with sliding overlap.
2. PARENT_CHILD: Hierarchical parent-child chunking for high retrieval precision + rich generation context.
3. SENTENCE_WINDOW: Target sentence embedding with surrounding context window padding.
"""

from enum import Enum
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class ChunkingStrategy(str, Enum):
    FIXED_OVERLAP = "FIXED_OVERLAP"
    PARENT_CHILD = "PARENT_CHILD"
    SENTENCE_WINDOW = "SENTENCE_WINDOW"


class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chk-{uuid.uuid4().hex[:8]}")
    doc_id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    strategy: ChunkingStrategy
    parent_chunk_id: Optional[str] = None
    parent_text: Optional[str] = None


class DocumentLoader:
    def __init__(self):
        pass

    def load_raw_text(self, doc_id: str, text_content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Loads and normalizes raw text document."""
        return {
            "doc_id": doc_id,
            "text": text_content.strip(),
            "metadata": metadata or {}
        }

    def chunk_document(
        self, 
        doc: Dict[str, Any], 
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_OVERLAP,
        chunk_size: int = 300,
        chunk_overlap: int = 50
    ) -> List[DocumentChunk]:
        """
        Applies target chunking strategy to document text.
        """
        doc_id = doc["doc_id"]
        text = doc["text"]
        meta = doc.get("metadata", {})

        if strategy == ChunkingStrategy.FIXED_OVERLAP:
            return self._chunk_fixed_overlap(doc_id, text, meta, chunk_size, chunk_overlap)
        elif strategy == ChunkingStrategy.PARENT_CHILD:
            return self._chunk_parent_child(doc_id, text, meta, parent_size=600, child_size=150)
        elif strategy == ChunkingStrategy.SENTENCE_WINDOW:
            return self._chunk_sentence_window(doc_id, text, meta, window_size=2)
        else:
            raise ValueError(f"Unsupported chunking strategy: {strategy}")

    def _chunk_fixed_overlap(
        self, 
        doc_id: str, 
        text: str, 
        metadata: Dict[str, Any], 
        chunk_size: int, 
        overlap: int
    ) -> List[DocumentChunk]:
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_text = text[start:end]
            chunks.append(DocumentChunk(
                doc_id=doc_id,
                text=chunk_text,
                metadata={**metadata, "start_char": start, "end_char": end},
                strategy=ChunkingStrategy.FIXED_OVERLAP
            ))
            if end == text_len:
                break
            start += (chunk_size - overlap)

        return chunks

    def _chunk_parent_child(
        self, 
        doc_id: str, 
        text: str, 
        metadata: Dict[str, Any], 
        parent_size: int = 600, 
        child_size: int = 150
    ) -> List[DocumentChunk]:
        """
        Parent-Child Chunking:
        Creates large parent chunks for generation context, and breaks each parent into child chunks for retrieval matching.
        """
        chunks = []
        parent_chunks = self._chunk_fixed_overlap(doc_id, text, metadata, parent_size, overlap=100)

        for p_idx, p_chunk in enumerate(parent_chunks):
            parent_id = f"parent-{p_idx}-{p_chunk.chunk_id}"
            child_chunks = self._chunk_fixed_overlap(doc_id, p_chunk.text, metadata, child_size, overlap=25)

            for c_chunk in child_chunks:
                c_chunk.strategy = ChunkingStrategy.PARENT_CHILD
                c_chunk.parent_chunk_id = parent_id
                c_chunk.parent_text = p_chunk.text
                chunks.append(c_chunk)

        return chunks

    def _chunk_sentence_window(
        self, 
        doc_id: str, 
        text: str, 
        metadata: Dict[str, Any], 
        window_size: int = 2
    ) -> List[DocumentChunk]:
        """
        Sentence Window Chunking:
        Embeds target sentence, but sets surrounding N sentences as context window in parent_text.
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]
        chunks = []

        for i, sentence in enumerate(sentences):
            start_win = max(0, i - window_size)
            end_win = min(len(sentences), i + window_size + 1)
            window_context = " ".join(sentences[start_win:end_win])

            chunks.append(DocumentChunk(
                doc_id=doc_id,
                text=sentence,
                parent_text=window_context,
                metadata={**metadata, "sentence_index": i},
                strategy=ChunkingStrategy.SENTENCE_WINDOW
            ))

        return chunks
