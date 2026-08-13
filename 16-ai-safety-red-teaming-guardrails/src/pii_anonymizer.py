"""
PII Anonymization & Data Redaction Pipeline.
Scans and redacts SSNs, credit card numbers, email addresses, and phone numbers before LLM inference.
"""

import re
from typing import Dict, List
from pydantic import BaseModel, Field


class PIIAnonymizationResult(BaseModel):
    sanitized_text: str
    pii_types_found: List[str]
    count_redacted: int


class PIIAnonymizer:
    PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "PHONE": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    }

    def sanitize_text(self, text: str) -> PIIAnonymizationResult:
        sanitized = text
        found_types: List[str] = []
        total_count = 0

        for ptype, regex in self.PATTERNS.items():
            matches = re.findall(regex, sanitized)
            if matches:
                found_types.append(ptype)
                total_count += len(matches)
                sanitized = re.sub(regex, f"[REDACTED_{ptype}]", sanitized)

        return PIIAnonymizationResult(
            sanitized_text=sanitized,
            pii_types_found=found_types,
            count_redacted=total_count
        )
