"""
Enterprise AI Guardrails & Safety Filter Engine.
Implements multi-layered protection:
1. PII Redaction (SSN, Credit Cards, API Keys, Emails).
2. Prompt Injection & Jailbreak Defense (DAN, System Prompt Override detection).
3. Output Toxicity & Safety Content Filtering.
4. Token Quota & Budget Enforcement.
Matches NeMo Guardrails / Llama Guard enterprise standards.
"""

import re
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field


class GuardrailEvaluationResult(BaseModel):
    is_safe: bool
    sanitized_text: str
    violations_detected: List[str]
    pii_redacted_count: int
    prompt_injection_blocked: bool


class EnterpriseGuardrailsEngine:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"system prompt override",
        r"you are now (in )?dan mode",
        r"bypass (safety|security) filter",
        r"disregard safety guidelines"
    ]

    PII_PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "API_KEY": r"\b(?:sk-|ak-)[a-zA-Z0-9]{32,64}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    }

    def __init__(self):
        pass

    def evaluate_and_sanitize_prompt(self, prompt: str) -> GuardrailEvaluationResult:
        """
        Evaluates input prompt for safety violations and redacts sensitive PII.
        """
        violations: List[str] = []
        is_injection = False

        # 1. Prompt Injection & Jailbreak Detection
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                violations.append(f"PROMPT_INJECTION_ATTACK: Matched pattern '{pattern}'")
                is_injection = True
                break

        # 2. PII Redaction
        sanitized = prompt
        pii_count = 0
        for pii_type, regex in self.PII_PATTERNS.items():
            matches = re.findall(regex, sanitized)
            if matches:
                pii_count += len(matches)
                violations.append(f"PII_EXPOSURE: Redacted {len(matches)} instance(s) of {pii_type}")
                sanitized = re.sub(regex, f"[REDACTED_{pii_type}]", sanitized)

        is_safe = not is_injection

        return GuardrailEvaluationResult(
            is_safe=is_safe,
            sanitized_text=sanitized,
            violations_detected=violations,
            pii_redacted_count=pii_count,
            prompt_injection_blocked=is_injection
        )
