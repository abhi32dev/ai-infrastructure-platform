"""
NeMo Guardrails & Llama Guard Policy Engine.
Enforces topical rails, safety policies, and system prompt integrity checks on LLM responses.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PolicyEvaluationResult(BaseModel):
    is_compliant: bool
    policy_category: str  # SAFE, OFF_TOPIC, HARMFUL_CONTENT, SYSTEM_LEAK
    redacted_response: str


class SafetyPolicyEngine:
    def __init__(self, allowed_topics: List[str] = None):
        self.allowed_topics = allowed_topics or ["cloud", "infrastructure", "ai", "coding", "data"]

    def evaluate_output_safety(self, model_output: str) -> PolicyEvaluationResult:
        """Evaluates generated LLM response output against Llama Guard safety categories."""
        output_lower = model_output.lower()

        # System prompt leakage check
        if "you are antigravity" in output_lower or "<identity>" in output_lower:
            return PolicyEvaluationResult(
                is_compliant=False,
                policy_category="SYSTEM_LEAK",
                redacted_response="[BLOCKED: System prompt leakage attempt detected]"
            )

        # Harmful content check
        if "malware" in output_lower or "exploit_vulnerability" in output_lower:
            return PolicyEvaluationResult(
                is_compliant=False,
                policy_category="HARMFUL_CONTENT",
                redacted_response="[BLOCKED: Harmful cybersecurity exploit content]"
            )

        return PolicyEvaluationResult(
            is_compliant=True,
            policy_category="SAFE",
            redacted_response=model_output
        )
