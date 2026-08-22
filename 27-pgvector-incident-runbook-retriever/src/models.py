"""
Data Models for PGVector Incident Runbook Retriever.
"""
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class HardwareVendor(str, Enum):
    GOOGLE_SAS = "GOOGLE_SAS"
    FEDERATED_WIRELESS = "FEDERATED_WIRELESS"
    SAMSUNG = "SAMSUNG"
    NOKIA = "NOKIA"
    GLOBAL = "GLOBAL"

class IncidentSeverity(str, Enum):
    SEV1_CRITICAL = "SEV1_CRITICAL"
    SEV2_MAJOR = "SEV2_MAJOR"
    SEV3_MINOR = "SEV3_MINOR"

class RunbookEntry(BaseModel):
    runbook_id: str = Field(..., description="Unique ID e.g. RB-SAS-503")
    title: str
    vendor: HardwareVendor
    severity: IncidentSeverity
    error_signature: str
    root_cause_analysis: str
    remediation_runbook: str
    tags: List[str] = Field(default_factory=list)
    version: int = Field(default=1)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    query_text: str
    vendor: Optional[HardwareVendor] = None
    severity: Optional[IncidentSeverity] = None
    top_k: int = Field(default=3, ge=1, le=20)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0, description="Hybrid search weight: 1.0=pure dense vector, 0.0=pure sparse keyword")

class ScoredRunbook(BaseModel):
    runbook: RunbookEntry
    dense_vector_score: float
    keyword_score: float
    combined_hybrid_score: float
    retrieval_latency_ms: float

class HybridSearchResponse(BaseModel):
    query: str
    total_candidates: int
    matches: List[ScoredRunbook]
