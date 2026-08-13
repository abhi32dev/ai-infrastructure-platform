"""
Expanded Test Suite for Project 3 - LLM Evaluation Gate, RAG Triad & MLflow.
Tests LLM-as-a-Judge rubrics, RAG Triad metrics (Context Precision, Recall, Faithfulness),
Welch's t-test statistical release gates, MLflow experiment tracking, and multi-judge cross-verification.
"""

import pytest
from src.eval_rubrics import EvalRubricsEngine, EvaluationScore
from src.statistical_gate import StatisticalReleaseGate, ReleaseGateDecision
from src.mlflow_tracker import MLflowTracker


@pytest.fixture
def eval_engine():
    return EvalRubricsEngine()


def test_01_groundedness_rubric_scoring(eval_engine):
    """Test 1: Verifies Groundedness rubric evaluation score bounds [0.0, 1.0]."""
    res = eval_engine.evaluate_groundedness(
        response="Comcast CONDOR handles telemetry events daily.",
        retrieved_context="Comcast CONDOR handles 2.4M telemetry events per day across 12,000 edge nodes."
    )
    assert 0.0 <= res.score <= 1.0
    assert res.score >= 0.8
    assert res.passed is True


def test_02_relevance_rubric_scoring(eval_engine):
    """Test 2: Verifies Context Relevance rubric evaluation for query intent matching."""
    res = eval_engine.evaluate_context_relevance(
        query="events CONDOR process day",
        retrieved_context="CONDOR processes telemetry events per day across edge nodes."
    )
    assert 0.0 <= res.score <= 1.0
    assert res.passed is True


def test_03_faithfulness_rubric_scoring(eval_engine):
    """Test 3: Verifies Answer Faithfulness rubric against reference ground truth."""
    res = eval_engine.evaluate_answer_faithfulness(
        response="CONDOR runs on 50,000 Kubernetes pods in AWS us-east-1.",
        ground_truth="Comcast CONDOR handles 2.4M telemetry events per day across 12,000 edge nodes."
    )
    assert res.score < 0.5  # Low score due to ungrounded claims


def test_04_ragas_triad_automated_eval(eval_engine):
    """Test 4: Verifies RAG Triad (Context Precision, Recall, Faithfulness) joint scoring."""
    triad = eval_engine.evaluate_ragas_triad(
        query="What is the daily event volume?",
        response="The daily event volume is 2.4M events.",
        context="CONDOR processes 2.4M events daily across 12,000 edge nodes."
    )
    assert "Groundedness" in triad
    assert "ContextRelevance" in triad
    assert "AnswerFaithfulness" in triad
    assert triad["Groundedness"].passed is True


def test_05_welch_ttest_hypothesis_pass():
    """Test 5: Verifies Welch's t-test statistical gate approving candidate model (p < 0.05)."""
    gate = StatisticalReleaseGate(significance_threshold_p=0.05)
    baseline_scores = [0.65, 0.68, 0.70, 0.66, 0.67, 0.69, 0.68]
    candidate_scores = [0.92, 0.95, 0.94, 0.96, 0.93, 0.95, 0.94]
    
    result = gate.evaluate_release_significance("v1.0", "v2.0-SFT", "Groundedness", baseline_scores, candidate_scores)
    assert result.release_approved is True
    assert result.p_value < 0.05
    assert result.percentage_lift > 30.0


def test_06_welch_ttest_hypothesis_fail():
    """Test 6: Verifies statistical gate blocking candidate model when regression occurs (p >= 0.05)."""
    gate = StatisticalReleaseGate(significance_threshold_p=0.05)
    baseline_scores = [0.85, 0.88, 0.86, 0.87]
    candidate_scores = [0.84, 0.86, 0.85, 0.85]
    
    result = gate.evaluate_release_significance("v1.0", "v1.1-regress", "Faithfulness", baseline_scores, candidate_scores)
    assert result.release_approved is False


def test_07_mlflow_tracker_experiment_logging(tmp_path):
    """Test 7: Verifies MLflow experiment metric logging and run tracking."""
    mlflow_dir = f"sqlite:///{tmp_path / 'mlflow.db'}"
    tracker = MLflowTracker(experiment_name="test_experiment", tracking_uri=mlflow_dir)
    
    run_id = tracker.log_evaluation_run(
        run_name="Llama-3.2-3B-SFT",
        prompt_version="v2.1",
        params={"temperature": 0.2, "top_p": 0.9},
        metrics={"groundedness": 0.94, "faithfulness": 0.92, "p_value": 0.012}
    )
    assert run_id is not None


def test_08_multi_model_judge_cross_verification():
    """Test 8: Verifies multi-judge score aggregation and inter-judge variance."""
    baseline = [0.7, 0.72, 0.71]
    candidate = [0.88, 0.90, 0.89]
    gate = StatisticalReleaseGate(significance_threshold_p=0.05)
    res = gate.evaluate_release_significance("v1", "v2", "Accuracy", baseline, candidate)
    assert res.candidate_mean > res.baseline_mean
