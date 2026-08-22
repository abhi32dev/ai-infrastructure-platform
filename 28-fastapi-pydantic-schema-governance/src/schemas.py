"""
Pydantic v2 Schema Governance Models.
Demonstrates Rust-based performance, discriminated unions, and field validations.
"""
from typing import List, Dict, Optional, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
import re

class ProtocolType(str, Enum):
    SNMP_UDP = "SNMP_UDP"
    REST_HTTPS = "REST_HTTPS"
    SFTP_BATCH = "SFTP_BATCH"

class BaseEdgePayload(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    event_id: str = Field(..., pattern=r"^evt-[a-zA-Z0-9_-]+$")
    node_id: str = Field(..., pattern=r"^EDGE-[A-Z]{2}-[A-Z]{3}-\d{3,5}$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GoogleSASTelemetryPayload(BaseEdgePayload):
    vendor_type: Literal["GOOGLE_SAS"] = "GOOGLE_SAS"
    cbrs_grant_id: str = Field(..., min_length=5)
    eirp_dbm: float = Field(..., ge=-30.0, le=50.0)
    heartbeat_interval_sec: int = Field(default=240, ge=30, le=3600)

class NokiaTelemetryPayload(BaseEdgePayload):
    vendor_type: Literal["NOKIA"] = "NOKIA"
    bbu_chassis_id: str
    optical_rx_power_dbm: float = Field(..., ge=-40.0, le=10.0)
    sfp_serial: str = Field(..., min_length=8)

class SamsungTelemetryPayload(BaseEdgePayload):
    vendor_type: Literal["SAMSUNG"] = "SAMSUNG"
    vdu_instance_id: str
    sctp_association_state: Literal["ESTABLISHED", "SHUTDOWN", "LOST"]
    packet_drop_rate_pct: float = Field(..., ge=0.0, le=100.0)

# Polymorphic Discriminated Union
PolymorphicEdgePayload = Union[
    GoogleSASTelemetryPayload,
    NokiaTelemetryPayload,
    SamsungTelemetryPayload
]

class IngestionBatchRequest(BaseModel):
    batch_id: str = Field(..., min_length=4)
    protocol: ProtocolType
    items: List[PolymorphicEdgePayload] = Field(..., min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_batch_integrity(self) -> "IngestionBatchRequest":
        # Ensure all items in the batch share unique event_ids
        ids = [item.event_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate event_id detected within batch payload")
        return self

class IngestionBatchResponse(BaseModel):
    batch_id: str
    processed_count: int
    status: Literal["ACCEPTED", "PARTIAL", "REJECTED"]
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
