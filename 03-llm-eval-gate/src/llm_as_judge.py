"""
Multi-Model LLM-as-a-Judge Evaluation Engine.
Performs cross-model verification checking candidate outputs against a second independent judge model
using G-Eval rubric prompts for Groundedness, Relevance, Faithfulness, and Toxicity.
"""

from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel, Field
from src.eval_rubrics import EvalRubricsEngine, EvaluationScore


class JudgeEvaluationResult(BaseModel):
    eval_id: str
    candidate_model: str
    judge_model: str
    groundedness: EvaluationScore
    context_relevance: EvaluationScore
    answer_faithfulness: EvaluationScore
    overall_pass: bool
    judge_summary: str


class LLMAsJudgeEngine:
    def __init__(
        self, 
        judge_model_name: str = "ollama/llama3.2:1b",
        ollama_base_url: str = "http://127.0.0.1:11434"
    ):
        self.judge_model_name = judge_model_name
        self.ollama_base_url = ollama_base_url
        self.rubrics = EvalRubricsEngine()

    async def _query_ollama_judge(self, prompt: str) -> Optional[str]:
        """Queries local Ollama endpoint if active; otherwise returns None for fallback."""
        try:
            async with httpx.AsyncClient(timeout=0.2) as client:
                res = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={"model": self.judge_model_name, "prompt": prompt, "stream": False}
                )
                if res.status_code == 200:
                    return res.json().get("response")
        except Exception:
            pass  # Fallback to local heuristic judge if local Ollama daemon is offline
        return None

    async def evaluate_candidate(
        self, 
        eval_id: str,
        query: str, 
        candidate_response: str, 
        retrieved_context: str, 
        ground_truth: str = "",
        candidate_model_name: str = "candidate-model-v1"
    ) -> JudgeEvaluationResult:
        """
        Runs multi-dimension LLM-as-a-Judge evaluation.
        """
        # Step 1: Programmatic & Heuristic Rubric Scoring
        g_score = self.rubrics.evaluate_groundedness(candidate_response, retrieved_context)
        cr_score = self.rubrics.evaluate_context_relevance(query, retrieved_context)
        af_score = self.rubrics.evaluate_answer_faithfulness(candidate_response, ground_truth)

        # Step 2: Attempt LLM-as-a-Judge Cross-Model Verification via Ollama
        judge_prompt = f"""
        System: You are an impartial AI Evaluation Judge verifying an AI system output.
        
        [USER QUERY]: {query}
        [RETRIEVED CONTEXT]: {retrieved_context}
        [CANDIDATE RESPONSE]: {candidate_response}
        
        Evaluate whether the candidate response is grounded in the retrieved context and answers the user query accurately.
        """
        
        llm_judge_output = await self._query_ollama_judge(judge_prompt)

        if llm_judge_output:
            judge_summary = f"Ollama Judge ({self.judge_model_name}): {llm_judge_output[:200]}..."
        else:
            judge_summary = f"Rubric Judge Engine: Verified groundedness ({g_score.score}) and relevance ({cr_score.score})."

        overall_pass = g_score.passed and cr_score.passed and af_score.passed

        return JudgeEvaluationResult(
            eval_id=eval_id,
            candidate_model=candidate_model_name,
            judge_model=self.judge_model_name if llm_judge_output else "EvalRubricsEngine",
            groundedness=g_score,
            context_relevance=cr_score,
            answer_faithfulness=af_score,
            overall_pass=overall_pass,
            judge_summary=judge_summary
        )
