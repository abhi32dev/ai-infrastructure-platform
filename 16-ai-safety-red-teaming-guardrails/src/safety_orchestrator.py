"""
Master AI Safety, Red-Teaming & Guardrails Orchestrator.
Integrates Prompt Injection Scans, PII Anonymization, and NeMo/Llama Guard Policy Enforcement.
"""

from typing import Any, Dict
from src.prompt_scanner import PromptInjectionScanner, PromptScanResult
from src.policy_engine import PolicyEvaluationResult, SafetyPolicyEngine
from src.pii_anonymizer import PIIAnonymizationResult, PIIAnonymizer


class AISafetyGuardrailsOrchestrator:
    def __init__(self):
        self.prompt_scanner = PromptInjectionScanner()
        self.pii_anonymizer = PIIAnonymizer()
        self.policy_engine = SafetyPolicyEngine()

    def process_guardrails_pipeline(self, user_prompt: str, simulated_llm_response: str) -> Dict[str, Any]:
        """Runs 3-stage security filter: Prompt Scan -> PII Redaction -> Response Policy Enforcement."""
        # Stage 1: Prompt Injection Scan
        scan_res = self.prompt_scanner.scan_prompt(user_prompt)
        if not scan_res.is_safe:
            return {
                "status": "PROMPT_INJECTION_BLOCKED",
                "risk_score": scan_res.jailbreak_risk_score,
                "violations": scan_res.violations_detected,
                "output": "[BLOCKED: Prompt Injection / Jailbreak Attack Detected]"
            }

        # Stage 2: PII Redaction
        pii_res = self.pii_anonymizer.sanitize_text(user_prompt)

        # Stage 3: Output Safety Policy Check
        policy_res = self.policy_engine.evaluate_output_safety(simulated_llm_response)
        if not policy_res.is_compliant:
            return {
                "status": "RESPONSE_POLICY_VIOLATION",
                "policy_category": policy_res.policy_category,
                "output": policy_res.redacted_response
            }

        return {
            "status": "PASSED_SAFE",
            "sanitized_prompt": pii_res.sanitized_text,
            "pii_redacted_count": pii_res.count_redacted,
            "output": policy_res.redacted_response
        }
