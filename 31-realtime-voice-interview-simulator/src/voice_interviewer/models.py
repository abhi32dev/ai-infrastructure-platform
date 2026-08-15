from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InterviewMode(StrEnum):
    SCREENING = "screening"
    SYSTEM_DESIGN = "system_design"
    INCIDENT = "incident"
    CODE_REVIEW = "code_review"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"


class Difficulty(StrEnum):
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"


class SessionState(StrEnum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Question(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(min_length=3, max_length=160, pattern=r"^[a-zA-Z0-9._-]+$")
    project: str = Field(min_length=1, max_length=160)
    prompt: str = Field(min_length=10, max_length=8000)
    reference_answer: str = Field(min_length=10, max_length=30000)
    tags: tuple[str, ...] = ()
    difficulty: Difficulty = Difficulty.STAFF
    code_references: tuple[str, ...] = ()
    required_concepts: tuple[str, ...] = ()
    follow_ups: tuple[str, ...] = ()


class InterviewConfig(BaseModel):
    mode: InterviewMode = InterviewMode.MIXED
    difficulty: Difficulty = Difficulty.STAFF
    projects: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    question_limit: int = Field(default=8, ge=1, le=50)
    duration_minutes: int = Field(default=45, ge=5, le=180)
    adaptive: bool = True
    record_audio: bool = False
    retain_transcript: bool = True
    seed: int = Field(default=17, ge=0, le=2**31 - 1)

    @field_validator("projects", "tags")
    @classmethod
    def normalize_filters(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(dict.fromkeys(item.strip().lower() for item in value if item.strip()))
        if len(normalized) > 50:
            raise ValueError("no more than 50 filters are allowed")
        return normalized


class ScoreDimension(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=5.0)
    evidence: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


class AnswerEvaluation(BaseModel):
    question_id: str
    total_score: float = Field(ge=0.0, le=100.0)
    level: str
    dimensions: tuple[ScoreDimension, ...]
    strengths: tuple[str, ...]
    gaps: tuple[str, ...]
    improved_answer: str
    recommended_follow_up: str | None = None
    word_count: int = Field(ge=0)
    duration_seconds: float = Field(ge=0.0)


class InterviewTurn(BaseModel):
    sequence: int = Field(ge=1)
    question: Question
    answer: str | None = None
    evaluation: AnswerEvaluation | None = None
    started_at: datetime = Field(default_factory=utc_now)
    answered_at: datetime | None = None


class InterviewSession(BaseModel):
    id: str
    config: InterviewConfig
    state: SessionState = SessionState.CREATED
    turns: list[InterviewTurn] = Field(default_factory=list)
    pending_question_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class SessionSummary(BaseModel):
    session_id: str
    state: SessionState
    questions_answered: int
    average_score: float
    strongest_dimensions: tuple[str, ...]
    weakest_dimensions: tuple[str, ...]
    recommended_topics: tuple[str, ...]
    elapsed_seconds: float


class Event(BaseModel):
    session_id: str
    sequence: int
    event_type: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=utc_now)
