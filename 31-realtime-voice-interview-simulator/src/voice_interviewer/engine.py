from __future__ import annotations

import random
import uuid
from collections import defaultdict

from .guardrails import detect_prompt_injection, redact_sensitive, validate_text
from .models import Event, InterviewConfig, InterviewSession, InterviewTurn, SessionState, SessionSummary, utc_now
from .observability import Metrics
from .question_bank import QuestionBank
from .scoring import DeterministicScorer
from .storage import SQLiteSessionStore


class InvalidTransition(RuntimeError):
    pass


class InterviewEngine:
    def __init__(self, bank: QuestionBank, store: SQLiteSessionStore, scorer: DeterministicScorer | None = None, metrics: Metrics | None = None) -> None:
        self.bank = bank
        self.store = store
        self.scorer = scorer or DeterministicScorer()
        self.metrics = metrics or Metrics()

    def create(self, config: InterviewConfig) -> InterviewSession:
        candidates = self.bank.filter(projects=config.projects, tags=config.tags, difficulty=config.difficulty)
        if not candidates:
            raise ValueError("no questions match the requested filters")
        random.Random(config.seed).shuffle(candidates)
        pending = [question.id for question in candidates[: config.question_limit]]
        session = InterviewSession(id=f"int_{uuid.uuid4().hex}", config=config, pending_question_ids=pending)
        self.store.save(session)
        self._event(session, "session_created", {"mode": config.mode.value, "question_count": len(pending)})
        self.metrics.increment("sessions_total", mode=config.mode.value)
        return session

    def start(self, session_id: str) -> InterviewSession:
        session = self.store.get(session_id)
        if session.state != SessionState.CREATED:
            raise InvalidTransition(f"cannot start session from {session.state}")
        session.state = SessionState.ACTIVE
        session.updated_at = utc_now()
        self._add_next_turn(session)
        self.store.save(session)
        self._event(session, "session_started", {})
        return session

    def submit_answer(self, session_id: str, answer: str, duration_seconds: float = 0.0) -> InterviewSession:
        session = self.store.get(session_id)
        if session.state != SessionState.ACTIVE:
            raise InvalidTransition(f"cannot answer while session is {session.state}")
        if not session.turns or session.turns[-1].answer is not None:
            raise InvalidTransition("there is no unanswered question")
        clean = validate_text(answer, field="answer")
        redacted, findings = redact_sensitive(clean)
        if detect_prompt_injection(redacted):
            self.metrics.increment("guardrail_events_total", type="prompt_injection")
        with self.metrics.latency("evaluation"):
            evaluation = self.scorer.evaluate(session.turns[-1].question, redacted, duration_seconds)
        turn = session.turns[-1]
        turn.answer = redacted if session.config.retain_transcript else "[TRANSCRIPT_NOT_RETAINED]"
        turn.evaluation = evaluation
        turn.answered_at = utc_now()
        session.updated_at = utc_now()
        self._event(session, "answer_evaluated", {"question_id": turn.question.id, "score": evaluation.total_score, "redactions": findings})
        self.metrics.increment("answers_total", level=evaluation.level)
        if len(session.turns) >= session.config.question_limit or not session.pending_question_ids:
            return self.complete(session.id, session=session)
        self._adapt(session, evaluation.total_score)
        self._add_next_turn(session)
        self.store.save(session)
        return session

    def pause(self, session_id: str) -> InterviewSession:
        return self._transition(session_id, {SessionState.ACTIVE}, SessionState.PAUSED, "session_paused")

    def resume(self, session_id: str) -> InterviewSession:
        return self._transition(session_id, {SessionState.PAUSED}, SessionState.ACTIVE, "session_resumed")

    def cancel(self, session_id: str) -> InterviewSession:
        return self._transition(session_id, {SessionState.CREATED, SessionState.ACTIVE, SessionState.PAUSED}, SessionState.CANCELLED, "session_cancelled")

    def complete(self, session_id: str, *, session: InterviewSession | None = None) -> InterviewSession:
        current = session or self.store.get(session_id)
        if current.state not in {SessionState.ACTIVE, SessionState.PAUSED}:
            raise InvalidTransition(f"cannot complete session from {current.state}")
        current.state = SessionState.COMPLETED
        current.completed_at = utc_now()
        current.updated_at = current.completed_at
        self.store.save(current)
        summary = self.summary(current.id, session=current)
        self.store.save_summary(summary)
        self._event(current, "session_completed", {"average_score": summary.average_score})
        return current

    def summary(self, session_id: str, *, session: InterviewSession | None = None) -> SessionSummary:
        current = session or self.store.get(session_id)
        evaluations = [turn.evaluation for turn in current.turns if turn.evaluation]
        dimension_scores: dict[str, list[float]] = defaultdict(list)
        for evaluation in evaluations:
            for dimension in evaluation.dimensions:
                dimension_scores[dimension.name].append(dimension.score)
        averages = {name: sum(values) / len(values) for name, values in dimension_scores.items()}
        ordered = sorted(averages, key=averages.get, reverse=True)
        weak = tuple(reversed(ordered[-3:])) if ordered else ()
        elapsed = ((current.completed_at or utc_now()) - current.created_at).total_seconds()
        return SessionSummary(
            session_id=current.id, state=current.state, questions_answered=len(evaluations),
            average_score=round(sum(item.total_score for item in evaluations) / max(len(evaluations), 1), 1),
            strongest_dimensions=tuple(ordered[:3]), weakest_dimensions=weak,
            recommended_topics=weak, elapsed_seconds=max(0.0, elapsed),
        )

    def _transition(self, session_id: str, allowed: set[SessionState], target: SessionState, event_type: str) -> InterviewSession:
        session = self.store.get(session_id)
        if session.state not in allowed:
            raise InvalidTransition(f"cannot transition {session.state} to {target}")
        session.state = target
        session.updated_at = utc_now()
        if target in {SessionState.CANCELLED, SessionState.COMPLETED}:
            session.completed_at = session.updated_at
        self.store.save(session)
        self._event(session, event_type, {})
        return session

    def _add_next_turn(self, session: InterviewSession) -> None:
        if not session.pending_question_ids:
            return
        question_id = session.pending_question_ids.pop(0)
        session.turns.append(InterviewTurn(sequence=len(session.turns) + 1, question=self.bank.get(question_id)))
        self._event(session, "question_presented", {"question_id": question_id, "sequence": len(session.turns)})

    def _adapt(self, session: InterviewSession, score: float) -> None:
        if not session.config.adaptive or not session.pending_question_ids:
            return
        rank = {"senior": 0, "staff": 1, "principal": 2}
        if score < 55:
            session.pending_question_ids.sort(key=lambda item: rank[self.bank.get(item).difficulty.value])
        elif score >= 85:
            session.pending_question_ids.sort(key=lambda item: rank[self.bank.get(item).difficulty.value], reverse=True)

    def _event(self, session: InterviewSession, event_type: str, payload: dict) -> None:
        sequence = len(self.store.events(session.id)) + 1
        self.store.append_event(Event(session_id=session.id, sequence=sequence, event_type=event_type, payload=payload))
