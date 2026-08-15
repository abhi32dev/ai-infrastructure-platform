from __future__ import annotations

import re
from collections import Counter

from .guardrails import validate_text
from .models import AnswerEvaluation, Question, ScoreDimension


_TOKEN = re.compile(r"[a-z][a-z0-9+#.-]{2,}", re.I)
_DIMENSIONS = {
    "technical_correctness": (("because",), ("therefore",), ("mechanism",), ("invariant",), ("guarantee", "guarantees")),
    "architecture_boundaries": (("boundary", "boundaries"), ("service", "worker"), ("store", "database"), ("control plane",), ("data plane",), ("interface", "api")),
    "trade_offs": (("trade-off", "tradeoff", "trade off"), ("versus", "compared with"), ("however",), ("cost",), ("latency",), ("complexity",)),
    "failure_modes": (("failure", "unavailable"), ("timeout", "deadline"), ("retry",), ("fallback", "graceful degradation"), ("rollback",), ("degrade", "degradation"), ("reconcile",)),
    "security_governance": (("security", "secure"), ("tenant",), ("authorization", "permission"), ("privacy", "redact"), ("audit",), ("least privilege", "api key never")),
    "observability_operations": (("metric", "monitor"), ("trace",), ("alert",), ("slo", "service level"), ("p95",), ("p99",), ("runbook",)),
    "scale_capacity": (("scale", "10x", "100x", "autoscale"), ("throughput", "concurrency"), ("capacity", "admission control"), ("partition", "regionalize"), ("shard", "isolate tenants"), ("backpressure", "bound concurrency"), ("gpu",)),
    "communication": (("first",), ("second",), ("finally",), ("example",), ("specifically", "relevant implementation")),
}


class DeterministicScorer:
    """Inspectable offline scorer; an LLM judge can augment but never replace it."""

    def evaluate(self, question: Question, answer: str, duration_seconds: float = 0.0) -> AnswerEvaluation:
        clean = validate_text(answer, field="answer")
        lowered = clean.lower()
        tokens = _TOKEN.findall(lowered)
        token_counts = Counter(tokens)
        required = tuple(item.lower() for item in question.required_concepts)
        required_hits = tuple(item for item in required if item in lowered)
        required_missing = tuple(item for item in required if item not in lowered)
        dimensions: list[ScoreDimension] = []
        for name, signal_groups in _DIMENSIONS.items():
            hits = tuple(group[0] for group in signal_groups if any(signal in lowered for signal in group))
            base = min(3.5, len(hits) * 0.9)
            if name == "technical_correctness":
                coverage = len(required_hits) / max(len(required), 1)
                base = min(5.0, 1.0 + coverage * 4.0)
            elif name == "communication":
                length_score = 2.0 if 60 <= len(tokens) <= 450 else 1.0
                repetition = max(token_counts.values(), default=0) / max(len(tokens), 1)
                base = min(5.0, length_score + len(hits) * 0.7 - (1.0 if repetition > 0.12 else 0.0))
            dimensions.append(ScoreDimension(
                name=name, score=max(0.0, round(base, 2)), evidence=hits,
                missing=required_missing if name == "technical_correctness" else tuple(group[0] for group in signal_groups[:3] if not any(signal in lowered for signal in group)),
            ))
        raw = sum(item.score for item in dimensions) / (len(dimensions) * 5.0) * 100.0
        total = round(max(0.0, min(100.0, raw)), 1)
        level = "principal-ready" if total >= 85 else "staff-ready" if total >= 72 else "senior" if total >= 55 else "developing"
        strongest = sorted(dimensions, key=lambda item: item.score, reverse=True)[:3]
        weakest = sorted(dimensions, key=lambda item: item.score)[:3]
        gaps = tuple(f"Strengthen {item.name.replace('_', ' ')}: {', '.join(item.missing[:3]) or 'add concrete evidence'}" for item in weakest)
        strengths = tuple(f"{item.name.replace('_', ' ').title()} ({item.score:.1f}/5)" for item in strongest)
        improved = self._improved_answer(question, required_missing, clean)
        follow_up = question.follow_ups[0] if question.follow_ups else self._follow_up(question, weakest[0].name)
        return AnswerEvaluation(
            question_id=question.id, total_score=total, level=level,
            dimensions=tuple(dimensions), strengths=strengths, gaps=gaps,
            improved_answer=improved, recommended_follow_up=follow_up,
            word_count=len(tokens), duration_seconds=max(0.0, duration_seconds),
        )

    @staticmethod
    def _improved_answer(question: Question, missing: tuple[str, ...], answer: str) -> str:
        reference = re.sub(r"\s+", " ", question.reference_answer).strip()
        missing_text = ", ".join(missing[:6]) or "production evidence"
        return (
            f"Lead with the invariant and decision, then explain the mechanism. "
            f"Add the missing concepts: {missing_text}. Cover failure behavior, observability, security, "
            f"cost, and the point where the design changes at scale. Reference answer: {reference[:1200]}"
        )

    @staticmethod
    def _follow_up(question: Question, weakest: str) -> str:
        return f"You covered the basic mechanism. Now explain the {weakest.replace('_', ' ')} implications and cite a concrete implementation boundary for: {question.prompt}"
