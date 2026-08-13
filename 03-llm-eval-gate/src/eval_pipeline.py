"""
Master AI Evaluation Gate Pipeline Orchestrator.
Combines Dataset Batch Processing, LLM-as-a-Judge Evaluation, MLflow Tracking,
and Statistical P-Value Release Gates.
"""

from typing import Any, Dict, List
from src.llm_as_judge import LLMAsJudgeEngine
from src.mlflow_tracker import MLflowTracker
from src.statistical_gate import ReleaseGateDecision, StatisticalReleaseGate


class EvalPipeline:
    def __init__(self):
        print("[EVAL PIPELINE] Initializing AI Evaluation Gate Engine...")
        self.judge = LLMAsJudgeEngine()
        self.tracker = MLflowTracker()
        self.gate = StatisticalReleaseGate(significance_threshold_p=0.05)

    async def evaluate_dataset(
        self, 
        eval_run_name: str,
        prompt_version: str,
        test_dataset: List[Dict[str, Any]],
        candidate_model_name: str = "candidate-v1"
    ) -> Dict[str, Any]:
        """
        Runs batch evaluation over a dataset, tracking results in MLflow.
        """
        results = []
        groundedness_scores = []
        relevance_scores = []
        faithfulness_scores = []

        for idx, item in enumerate(test_dataset):
            eval_id = f"eval-{idx+1}"
            query = item["query"]
            response = item["response"]
            context = item["context"]
            ground_truth = item.get("ground_truth", "")

            eval_res = await self.judge.evaluate_candidate(
                eval_id=eval_id,
                query=query,
                candidate_response=response,
                retrieved_context=context,
                ground_truth=ground_truth,
                candidate_model_name=candidate_model_name
            )

            results.append(eval_res.dict())
            groundedness_scores.append(eval_res.groundedness.score)
            relevance_scores.append(eval_res.context_relevance.score)
            faithfulness_scores.append(eval_res.answer_faithfulness.score)

        avg_groundedness = float(sum(groundedness_scores) / len(groundedness_scores)) if groundedness_scores else 0.0
        avg_relevance = float(sum(relevance_scores) / len(relevance_scores)) if relevance_scores else 0.0
        avg_faithfulness = float(sum(faithfulness_scores) / len(faithfulness_scores)) if faithfulness_scores else 0.0
        pass_rate = float(sum(1 for r in results if r["overall_pass"]) / len(results)) if results else 0.0

        metrics = {
            "avg_groundedness": avg_groundedness,
            "avg_relevance": avg_relevance,
            "avg_faithfulness": avg_faithfulness,
            "pass_rate": pass_rate
        }

        # Log to MLflow
        run_id = self.tracker.log_evaluation_run(
            run_name=eval_run_name,
            prompt_version=prompt_version,
            params={"model_name": candidate_model_name, "dataset_size": len(test_dataset)},
            metrics=metrics,
            artifacts={"results": results}
        )

        return {
            "run_id": run_id,
            "run_name": eval_run_name,
            "prompt_version": prompt_version,
            "metrics": metrics,
            "groundedness_scores": groundedness_scores,
            "results": results
        }

    def evaluate_release_gate(
        self, 
        baseline_run: Dict[str, Any], 
        candidate_run: Dict[str, Any]
    ) -> ReleaseGateDecision:
        """
        Compares Baseline vs Candidate runs using p-value hypothesis testing.
        """
        decision = self.gate.evaluate_release_significance(
            baseline_version=baseline_run.get("prompt_version", "v1.0"),
            candidate_version=candidate_run.get("prompt_version", "v2.0"),
            metric_name="avg_groundedness",
            baseline_scores=baseline_run.get("groundedness_scores", []),
            candidate_scores=candidate_run.get("groundedness_scores", [])
        )
        return decision
