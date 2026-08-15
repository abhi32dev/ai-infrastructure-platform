import json

import pytest

from src.voice_interviewer.models import Difficulty
from src.voice_interviewer.question_bank import QuestionBank
from src.voice_interviewer.scoring import DeterministicScorer


def test_bank_rejects_empty_and_duplicate(questions):
    with pytest.raises(ValueError, match="empty"): QuestionBank([])
    with pytest.raises(ValueError, match="duplicate"): QuestionBank([questions[0], questions[0]])


def test_bank_get_unknown(bank):
    with pytest.raises(ValueError, match="unknown question"): bank.get("missing")


def test_bank_filters_projects_tags_and_difficulty(bank):
    assert len(bank.filter(projects=("p1",))) == 2
    assert [q.id for q in bank.filter(tags=("security",))] == ["q-2"]
    assert [q.id for q in bank.filter(difficulty=Difficulty.PRINCIPAL)] == ["q-2"]


def test_bank_loads_json(tmp_path, questions):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps([questions[0].model_dump(mode="json")]))
    assert QuestionBank.from_json(path).get("q-1").project == "p1"


def test_bank_rejects_non_list_json(tmp_path):
    path = tmp_path / "questions.json"; path.write_text("{}")
    with pytest.raises(ValueError, match="must be a list"): QuestionBank.from_json(path)


def test_repository_parser_extracts_answer_code_and_tags(tmp_path):
    project = tmp_path / "01-rag"; project.mkdir()
    (project / "INTERVIEW_PREP.md").write_text("""# Prep\n### Q1: How does RAG retrieval fail safely?\n**Answer:** Use a fallback, metric and audit boundary in `src/retrieval.py`.\n""")
    bank = QuestionBank.from_repository(tmp_path)
    question = bank.questions[0]
    assert question.project == "01-rag"
    assert "src/retrieval.py" in question.code_references
    assert "rag" in question.tags


def test_repository_parser_skips_unanswered_questions(tmp_path):
    project = tmp_path / "01-empty"; project.mkdir()
    (project / "INTERVIEW_PREP.md").write_text("### Q1: Why is this unanswered?\n")
    with pytest.raises(ValueError, match="empty"): QuestionBank.from_repository(tmp_path)


def test_scorer_rewards_required_concept_coverage(questions):
    scorer = DeterministicScorer()
    weak = scorer.evaluate(questions[0], "Retries are useful.")
    strong = scorer.evaluate(questions[0], "Because the invariant requires idempotency, use a durable checkpoint and one deadline. Add retry, fallback, metrics, trace, audit, tenant security, cost budget, backpressure and a concrete service boundary.")
    assert strong.total_score > weak.total_score
    assert strong.word_count > weak.word_count


def test_scorer_is_deterministic(questions):
    scorer = DeterministicScorer(); answer = "Use idempotency, checkpoint and deadline because retries can duplicate effects."
    assert scorer.evaluate(questions[0], answer) == scorer.evaluate(questions[0], answer)


def test_scorer_rejects_empty_answer(questions):
    with pytest.raises(ValueError): DeterministicScorer().evaluate(questions[0], " ")


def test_scorer_clamps_negative_duration(questions):
    result = DeterministicScorer().evaluate(questions[0], "Use idempotency and checkpoint with deadline.", -10)
    assert result.duration_seconds == 0


def test_scorer_returns_all_dimensions(questions):
    result = DeterministicScorer().evaluate(questions[0], "Use idempotency and checkpoint with deadline.")
    assert len(result.dimensions) == 8
    assert all(0 <= item.score <= 5 for item in result.dimensions)
    assert result.improved_answer
    assert result.recommended_follow_up == "Where is the linearization point?"


def test_scorer_recognizes_production_synonyms(questions):
    answer = (
        "The API boundary keeps the key private. If the service is unavailable, graceful degradation "
        "preserves the session. Monitor connection latency and autoscale workers at 10x concurrency; "
        "use admission control at 100x. Redact secrets and isolate tenants."
    )
    result = DeterministicScorer().evaluate(questions[0], answer)
    by_name = {item.name: item for item in result.dimensions}
    assert by_name["architecture_boundaries"].score > 0
    assert by_name["observability_operations"].score > 0
    assert by_name["scale_capacity"].score >= 2.7
    assert by_name["security_governance"].score > 0
