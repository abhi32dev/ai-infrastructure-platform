from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .models import Difficulty, Question


_QUESTION = re.compile(r"^#{2,4}\s+(?:Q\d+[:.]?\s*|\d+[.)]\s*)?(.+\?)\s*$", re.M)
_CODE_REF = re.compile(r"`([^`]+\.(?:py|js|ts|yaml|yml|md)(?::\d+)?)`")
_WORDS = re.compile(r"[a-z][a-z0-9+#.-]{2,}", re.I)
_STOP = {"what", "when", "where", "which", "would", "could", "should", "does", "this", "that", "with", "from", "into", "your", "have", "about", "explain", "compare"}


class QuestionBank:
    def __init__(self, questions: list[Question]) -> None:
        unique: dict[str, Question] = {}
        for question in questions:
            if question.id in unique:
                raise ValueError(f"duplicate question id: {question.id}")
            unique[question.id] = question
        if not unique:
            raise ValueError("question bank cannot be empty")
        self._questions = unique

    @property
    def questions(self) -> tuple[Question, ...]:
        return tuple(self._questions.values())

    def get(self, question_id: str) -> Question:
        try:
            return self._questions[question_id]
        except KeyError as exc:
            raise ValueError(f"unknown question: {question_id}") from exc

    def filter(self, *, projects: tuple[str, ...] = (), tags: tuple[str, ...] = (), difficulty: Difficulty | None = None) -> list[Question]:
        selected = list(self._questions.values())
        if projects:
            selected = [q for q in selected if any(item in q.project.lower() for item in projects)]
        if tags:
            selected = [q for q in selected if set(tags) & {tag.lower() for tag in q.tags}]
        if difficulty:
            rank = {Difficulty.SENIOR: 1, Difficulty.STAFF: 2, Difficulty.PRINCIPAL: 3}
            selected = [q for q in selected if rank[q.difficulty] >= rank[difficulty]]
        return selected

    @classmethod
    def from_json(cls, path: Path) -> "QuestionBank":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("question-bank JSON must be a list")
        return cls([Question.model_validate(item) for item in raw])

    @classmethod
    def from_repository(cls, repository: Path, seed_path: Path | None = None) -> "QuestionBank":
        questions: list[Question] = []
        if seed_path and seed_path.is_file():
            questions.extend(cls.from_json(seed_path).questions)
        for path in sorted(repository.glob("[0-9][0-9]-*/INTERVIEW_PREP.md")):
            questions.extend(_parse_markdown(path, repository))
        root_guide = repository / "INTERVIEW_PREP.md"
        if root_guide.is_file():
            questions.extend(_parse_markdown(root_guide, repository))
        deduped: dict[str, Question] = {}
        seen_prompts: set[str] = set()
        for question in questions:
            normalized = " ".join(question.prompt.lower().split())
            if normalized in seen_prompts:
                continue
            seen_prompts.add(normalized)
            deduped[question.id] = question
        return cls(list(deduped.values()))


def _parse_markdown(path: Path, repository: Path) -> list[Question]:
    text = path.read_text(encoding="utf-8")
    matches = list(_QUESTION.finditer(text))
    result: list[Question] = []
    project = path.parent.name if path.parent != repository else "portfolio"
    for index, match in enumerate(matches):
        answer_start = match.end()
        answer_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        answer = text[answer_start:answer_end].strip()
        answer = re.split(r"\n##\s", answer, maxsplit=1)[0].strip()
        if len(answer) < 10:
            continue
        prompt = match.group(1).strip()
        digest = hashlib.sha256(f"{path.relative_to(repository)}:{prompt}".encode()).hexdigest()[:12]
        words = [word.lower() for word in _WORDS.findall(prompt) if word.lower() not in _STOP]
        concepts = tuple(dict.fromkeys(words))[:10]
        code_references = tuple(dict.fromkeys(_CODE_REF.findall(answer)))[:8]
        lower = f"{prompt} {answer}".lower()
        difficulty = Difficulty.PRINCIPAL if any(word in lower for word in ("principal", "multi-region", "organization", "100x")) else Difficulty.STAFF
        tags = _infer_tags(lower)
        result.append(Question(
            id=f"repo-{digest}", project=project, prompt=prompt,
            reference_answer=answer[:30_000], tags=tags, difficulty=difficulty,
            code_references=code_references, required_concepts=concepts,
        ))
    return result


def _infer_tags(text: str) -> tuple[str, ...]:
    vocabulary = {
        "vllm": ("vllm", "pagedattention", "kv cache"),
        "distributed-training": ("fsdp", "megatron", "deepspeed", "all-reduce"),
        "rag": ("retrieval", "rag", "embedding", "rerank"),
        "agents": ("agent", "mcp", "a2a", "tool call"),
        "gpu": ("gpu", "cuda", "triton", "tensorrt"),
        "kubernetes": ("kubernetes", "k8s", "kuberay", "kueue"),
        "security": ("security", "guardrail", "tenant", "prompt injection"),
        "observability": ("observability", "metric", "trace", "slo"),
        "cost": ("cost", "budget", "quota"),
        "reliability": ("retry", "failure", "fallback", "idempot"),
    }
    return tuple(tag for tag, signals in vocabulary.items() if any(signal in text for signal in signals)) or ("ai-infrastructure",)
