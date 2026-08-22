"""
PGVector / Vector Store Implementation for Edge Incident Runbooks.
Simulates PostgreSQL PGVector cosine distance ranking.
"""
from typing import List, Tuple
import numpy as np
from .models import RunbookDoc, VendorType

# Pre-seeded historical incident post-mortems and MIB dictionaries
DEFAULT_RUNBOOKS = [
    RunbookDoc(
        runbook_id="RB-SAS-503",
        vendor=VendorType.GOOGLE_SAS,
        error_pattern="CBRS SAS Spectrum Grant Revocation 503 heartbeat timeout",
        root_cause="Spectrum Access System (SAS) token expiration due to NTP drift on edge radio.",
        remediation_steps=[
            "1. Verify chrony NTP sync on node via chronyc tracking.",
            "2. Force SAS token refresh: cbrs-cli refresh-grant --force.",
            "3. Restart CBRS CBSD daemon."
        ]
    ),
    RunbookDoc(
        runbook_id="RB-NOKIA-TRAP-882",
        vendor=VendorType.NOKIA,
        error_pattern="gNodeB BBU SFP+ Optical Rx Power Degradation Low Threshold",
        root_cause="Failing optical transceiver module on 10Gbps front-haul link.",
        remediation_steps=[
            "1. Inspect optical Rx power in dBm via SNMP OID .1.3.6.1.4.1.94.1.2.",
            "2. Dispatch field technician for SFP+ optic replacement if Rx < -18dBm.",
            "3. Reroute carrier bandwidth to backup redundant optical path."
        ]
    ),
    RunbookDoc(
        runbook_id="RB-SAMSUNG-CELL-404",
        vendor=VendorType.SAMSUNG,
        error_pattern="Samsung 5G vDU SCTP Multi-Homing Association Lost",
        root_cause="SCTP heartbeat failure across secondary IP subnet due to VPC security group misconfiguration.",
        remediation_steps=[
            "1. Verify SCTP port 38412 ingress rule on VPC Security Group.",
            "2. Ping secondary gateway IP with DF-bit set to check MTU 1500.",
            "3. Restart vDU SCTP transport daemon."
        ]
    ),
    RunbookDoc(
        runbook_id="RB-FEDERATED-AUTH-401",
        vendor=VendorType.FEDERATED_WIRELESS,
        error_pattern="Federated Wireless SAS Mutual TLS Certificate Handshake Failure",
        root_cause="Expired mTLS client certificate in local AWS Secrets Manager cache.",
        remediation_steps=[
            "1. Invalidate local secret cache in ECS sidecar.",
            "2. Fetch rotated X.509 certificate from AWS Secrets Manager.",
            "3. Re-initialize TLS context and verify handshake."
        ]
    )
]

def mock_embedding(text: str) -> np.ndarray:
    """Deterministic pseudo-embedding for testing vector distance without external API keys."""
    np.random.seed(abs(hash(text)) % (2**31))
    vec = np.random.randn(384)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

class PGVectorRunbookStore:
    """
    In-memory / PGVector Runbook Retriever.
    """
    def __init__(self, runbooks: List[RunbookDoc] = None):
        self.runbooks = runbooks or DEFAULT_RUNBOOKS
        self.embeddings = {
            rb.runbook_id: mock_embedding(f"{rb.vendor} {rb.error_pattern} {rb.root_cause}")
            for rb in self.runbooks
        }

    def search_similar_runbooks(self, query_text: str, vendor: VendorType = None, top_k: int = 2) -> List[RunbookDoc]:
        """
        Cosine similarity search over embedded runbooks (simulating SQL: SELECT *, 1 - (embedding <=> query_vec) AS sim FROM runbooks).
        """
        query_vec = mock_embedding(query_text)
        scores: List[Tuple[RunbookDoc, float]] = []

        for rb in self.runbooks:
            if vendor and rb.vendor != vendor and rb.vendor != VendorType.INTERNAL_CONDOR:
                continue
            rb_vec = self.embeddings[rb.runbook_id]
            sim = float(np.dot(query_vec, rb_vec))
            scores.append((rb, sim))

        # Sort descending by similarity
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rb, score in scores[:top_k]:
            rb_copy = rb.model_copy()
            rb_copy.similarity_score = round(max(0.1, min(0.99, (score + 1) / 2)), 3)
            results.append(rb_copy)

        return results
