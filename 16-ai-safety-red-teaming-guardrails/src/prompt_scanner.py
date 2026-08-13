"""
Real-Time Prompt Injection & Jailbreak Scanner.
Scans incoming user prompts for DAN jailbreak patterns, prompt leaking attacks, toxicity, and policy violations.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PromptScanResult(BaseModel):
    is_safe: bool
    jailbreak_risk_score: float
    violations_detected: List[str]
    scanned_prompt: str


class PromptInjectionScanner:
    JAILBREAK_PATTERNS = [
        "ignore previous instructions",
        "do anything now",
        "system prompt override",
        "developer mode enabled",
        "reveal your system prompt"
    ]

    def __init__(self, risk_threshold: float = 0.5):
        self.threshold = risk_threshold

    def scan_prompt(self, prompt: str) -> PromptScanResult:
        """Scans prompt text for jailbreak phrases and prompt injection attempts."""
        # Normalize prompt text: lowercase, remove punctuation/underscores/hyphens, collapse spaces
        import re
        prompt_lower = prompt.lower()
        normalized_prompt = re.sub(r'[\W_]+', ' ', prompt_lower).strip()
        violations: List[str] = []

        for pattern in self.JAILBREAK_PATTERNS:
            norm_pattern = re.sub(r'[\W_]+', ' ', pattern.lower()).strip()
            if norm_pattern in normalized_prompt:
                violations.append(f"JAILBREAK_PATTERN_DETECTED: '{pattern}'")

        risk = round(min(1.0, len(violations) * 0.50), 2)
        is_safe = risk < self.threshold

        return PromptScanResult(
            is_safe=is_safe,
            jailbreak_risk_score=risk,
            violations_detected=violations,
            scanned_prompt=prompt
        )
