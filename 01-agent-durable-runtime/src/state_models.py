"""
State Models for Multi-Step Agent Runtime & Durable Execution Engine.
Defines data structures for task lifecycles, step checkpoints, tool execution schemas, and state transitions.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    CHECKPOINTED = "CHECKPOINTED"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REPLAYING = "REPLAYING"


class ToolPermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE_SAFE = "WRITE_SAFE"
    SENSITIVE_REQUIRES_APPROVAL = "SENSITIVE_REQUIRES_APPROVAL"


class StepCheckpoint(BaseModel):
    step_id: str
    step_name: str
    step_index: int
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class TaskState(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    current_step_index: int = 0
    total_steps: int = 0
    checkpoints: List[StepCheckpoint] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    name: str
    description: str
    permission_level: ToolPermissionLevel
    parameters_schema: Dict[str, Any]
