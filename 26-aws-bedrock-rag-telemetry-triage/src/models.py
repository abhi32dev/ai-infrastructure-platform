"""
Pydantic v2 Domain Models for Multi-Vendor Edge Telemetry,
AWS Bedrock Triage, and Multi-Agent Orchestration.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class VendorType(str, Enum):
    GOOGLE_SAS = "GOOGLE_SAS"
    FEDERATED_WIRELESS = "FEDERATED_WIRELESS"
    SAMSUNG = "SAMSUNG"
    NOKIA = "NOKIA"
    INTERNAL_CONDOR = "INTERNAL_CONDOR"

class AlarmSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    WARNING = "WARNING"
    CLEARED = "CLEARED"

class TelemetryTrapPayload(BaseModel):
    """
    Ingested SNMP/UDP or REST Telemetry Trap from Multi-Vendor Edge Fleet.
    """
    event_id: str = Field(..., description="Unique event UUID")
    node_id: str = Field(..., description="Edge Node ID e.g. EDGE-CA-SJC-104")
    vendor: VendorType = Field(..., description="Hardware vendor source")
    severity: AlarmSeverity = Field(..., description="Reported alarm severity")
    oid: str = Field(..., description="SNMP OID or REST event path")
    raw_message: str = Field(..., description="Unstructured trap diagnostic message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = Field(default_factory=dict, description="Numerical counters e.g. packet_loss, cpu_temp")

    @field_validator("raw_message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Telemetry raw_message cannot be empty")
        return clean

class RunbookDoc(BaseModel):
    """
    Historical Incident Post-Mortem or Runbook stored in PGVector / Vector Index.
    """
    runbook_id: str
    vendor: VendorType
    error_pattern: str
    root_cause: str
    remediation_steps: List[str]
    similarity_score: Optional[float] = 0.0

class TriageDiagnosis(BaseModel):
    """
    Structured Output synthesized by AWS Bedrock (Claude 3.5 Sonnet / Haiku).
    """
    event_id: str
    node_id: str
    predicted_root_cause: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    matching_runbook_id: Optional[str] = None
    recommended_action: str
    automated_remediation_eligible: bool = False
    remediation_command: Optional[str] = None
    escalation_team: str = Field(default="SRE-Edge-Tier2")
    synthesized_at: datetime = Field(default_factory=datetime.utcnow)

class AgenticReviewTask(BaseModel):
    """
    Task payload for Multi-Agent PR Review & Pytest Synthesis.
    """
    service_name: str
    endpoint_path: str
    http_method: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    generated_pytest_code: Optional[str] = None
