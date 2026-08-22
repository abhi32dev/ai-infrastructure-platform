"""
PGVector Engine: Implements Dense Vector + BM25 Sparse Hybrid Search
with HNSW Indexing semantics, simulating Amazon RDS PostgreSQL PGVector extension.
"""
import time
from typing import List, Dict, Tuple, Optional
import numpy as np
from .models import RunbookEntry, HardwareVendor, IncidentSeverity, ScoredRunbook, HybridSearchResponse

DEFAULT_RUNBOOKS: List[RunbookEntry] = [
    RunbookEntry(
        runbook_id="RB-SAS-503",
        title="Google SAS CBRS Spectrum Grant Revocation Triage",
        vendor=HardwareVendor.GOOGLE_SAS,
        severity=IncidentSeverity.SEV1_CRITICAL,
        error_signature="CBRS SAS Spectrum Grant Revocation 503 heartbeat timeout NTP sync error",
        root_cause_analysis="Local NTP clock drifted >1000ms past SAS cluster threshold, causing cryptographic token validation failure.",
        remediation_runbook="1. Run chronyc tracking to inspect offset. 2. Force NTP step: chronyc -a makestep. 3. Re-issue CBRS grant via cbrs-cli refresh-grant.",
        tags=["cbrs", "spectrum", "sas", "ntp", "google"]
    ),
    RunbookEntry(
        runbook_id="RB-NOKIA-OPT-882",
        title="Nokia gNodeB BBU Optical Link Rx Power Degradation",
        vendor=HardwareVendor.NOKIA,
        severity=IncidentSeverity.SEV2_MAJOR,
        error_signature="gNodeB BBU SFP+ Optical Rx Power Degradation Low Threshold -19dBm",
        root_cause_analysis="Front-haul fiber optic dirty connector or failing laser diode in 10Gbps SFP+ optic.",
        remediation_runbook="1. Check optical DDM diagnostics. 2. Clean LC fiber bulkhead. 3. Replace transceiver module if Rx < -18dBm.",
        tags=["nokia", "gnodeb", "optical", "sfp", "front-haul"]
    ),
    RunbookEntry(
        runbook_id="RB-SAMSUNG-SCTP-404",
        title="Samsung 5G vDU SCTP Multi-Homing Failover Failure",
        vendor=HardwareVendor.SAMSUNG,
        severity=IncidentSeverity.SEV1_CRITICAL,
        error_signature="Samsung 5G vDU SCTP Multi-Homing Association Lost heartbeat timeout",
        root_cause_analysis="Secondary IP subnet routing dropped due to AWS VPC Route Table missing peering CIDR block.",
        remediation_runbook="1. Verify VPC Route Table for secondary subnet. 2. Verify Security Group port 38412 UDP/SCTP. 3. Restart SCTP daemon.",
        tags=["samsung", "vdu", "sctp", "multihoming", "vpc"]
    ),
    RunbookEntry(
        runbook_id="RB-FEDERATED-MTLS-401",
        title="Federated Wireless SAS Mutual TLS Handshake Rejection",
        vendor=HardwareVendor.FEDERATED_WIRELESS,
        severity=IncidentSeverity.SEV2_MAJOR,
        error_signature="Federated Wireless SAS Mutual TLS Certificate Handshake Failure expired X509",
        root_cause_analysis="Client certificate expired in AWS Secrets Manager rotation pipeline.",
        remediation_runbook="1. Trigger automated certificate renewal in AWS Secrets Manager. 2. Reload ECS sidecar TLS certificate. 3. Verify TLS handshake.",
        tags=["federated", "mtls", "x509", "secrets-manager", "tls"]
    )
]

def generate_dense_vector(text: str, dim: int = 384) -> np.ndarray:
    """Simulates Amazon Titan Embeddings (384-dimensional dense vectors)."""
    np.random.seed(abs(hash(text)) % (2**31))
    vec = np.random.randn(dim)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

class PGVectorRunbookRetriever:
    """
    Simulates PostgreSQL + pgvector extension with HNSW indexing and Full-Text Search (tsvector).
    """
    def __init__(self, runbooks: Optional[List[RunbookEntry]] = None):
        self.runbooks = {rb.runbook_id: rb for rb in (runbooks or DEFAULT_RUNBOOKS)}
        self.dense_index: Dict[str, np.ndarray] = {
            rb.runbook_id: generate_dense_vector(f"{rb.title} {rb.error_signature} {rb.root_cause_analysis}")
            for rb in self.runbooks.values()
        }

    def upsert_runbook(self, rb: RunbookEntry) -> None:
        self.runbooks[rb.runbook_id] = rb
        self.dense_index[rb.runbook_id] = generate_dense_vector(f"{rb.title} {rb.error_signature} {rb.root_cause_analysis}")

    def hybrid_search(
        self,
        query: str,
        vendor: Optional[HardwareVendor] = None,
        severity: Optional[IncidentSeverity] = None,
        top_k: int = 3,
        alpha: float = 0.7
    ) -> HybridSearchResponse:
        start_time = time.perf_counter()
        query_vec = generate_dense_vector(query)
        query_words = set(query.lower().split())

        candidates: List[Tuple[RunbookEntry, float, float, float]] = []

        for rb_id, rb in self.runbooks.items():
            # SQL Metadata WHERE filtering
            if vendor and rb.vendor != vendor and rb.vendor != HardwareVendor.GLOBAL:
                continue
            if severity and rb.severity != severity:
                continue

            # 1. Dense Vector Distance: 1 - Cosine Distance (HNSW Search)
            rb_vec = self.dense_index[rb_id]
            dense_sim = float(np.dot(query_vec, rb_vec))
            normalized_dense = max(0.0, min(1.0, (dense_sim + 1.0) / 2.0))

            # 2. Sparse Keyword Score: BM25 / ts_rank simulation
            target_words = set(f"{rb.title} {rb.error_signature} {' '.join(rb.tags)}".lower().split())
            intersection = query_words.intersection(target_words)
            keyword_score = len(intersection) / max(1, len(query_words))

            # 3. Hybrid Combined Score: alpha * dense + (1 - alpha) * keyword
            combined_score = (alpha * normalized_dense) + ((1.0 - alpha) * keyword_score)

            candidates.append((rb, normalized_dense, keyword_score, combined_score))

        # Sort descending by hybrid combined score
        candidates.sort(key=lambda x: x[3], reverse=True)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        matches: List[ScoredRunbook] = []
        for rb, dense_s, kw_s, comb_s in candidates[:top_k]:
            matches.append(ScoredRunbook(
                runbook=rb,
                dense_vector_score=round(dense_s, 4),
                keyword_score=round(kw_s, 4),
                combined_hybrid_score=round(comb_s, 4),
                retrieval_latency_ms=round(elapsed_ms, 2)
            ))

        return HybridSearchResponse(
            query=query,
            total_candidates=len(candidates),
            matches=matches
        )
