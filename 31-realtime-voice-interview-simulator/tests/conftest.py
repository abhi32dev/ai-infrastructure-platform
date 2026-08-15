import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from src.voice_interviewer.models import Difficulty, Question
from src.voice_interviewer.question_bank import QuestionBank
from src.voice_interviewer.storage import SQLiteSessionStore


@pytest.fixture
def questions():
    return [
        Question(id="q-1", project="p1", prompt="How do retries remain safe in a distributed workflow?", reference_answer="Use stable idempotency keys, durable checkpoints, deadlines, reconciliation and metrics.", tags=("reliability",), difficulty=Difficulty.STAFF, required_concepts=("idempotency", "checkpoint", "deadline"), follow_ups=("Where is the linearization point?",)),
        Question(id="q-2", project="p2", prompt="How should a platform enforce tenant isolation at scale?", reference_answer="Authenticate identity, authorize every resource, partition storage, encrypt data and audit access.", tags=("security",), difficulty=Difficulty.PRINCIPAL, required_concepts=("identity", "authorize", "partition", "audit")),
        Question(id="q-3", project="p1", prompt="Which signals should trigger automated model rollback?", reference_answer="Use quality, safety, p99 latency, cost and error-budget burn with a versioned decision policy.", tags=("observability",), difficulty=Difficulty.STAFF, required_concepts=("quality", "safety", "latency", "cost")),
    ]


@pytest.fixture
def bank(questions):
    return QuestionBank(questions)


@pytest.fixture
def store(tmp_path):
    value = SQLiteSessionStore(tmp_path / "sessions.db")
    yield value
    value.close()
