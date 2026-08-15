from __future__ import annotations

import re
import time
from collections import defaultdict, deque


class GuardrailViolation(ValueError):
    """Raised when untrusted interview input violates a hard policy."""


_SECRET_PATTERNS = (
    re.compile(r"\b(?:sk|rk|pk)-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b[A-Za-z0-9+/]{32,}={0,2}\b"),
)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_PHONE = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}(?!\d)")
_INJECTION = re.compile(
    r"(?:ignore|override|reveal|print|repeat).{0,40}(?:system|developer|hidden|instruction|prompt|secret)|"
    r"(?:act as|you are now).{0,30}(?:unrestricted|developer mode)",
    re.I | re.S,
)


def validate_text(value: str, *, field: str = "text", maximum: int = 30_000) -> str:
    if not isinstance(value, str):
        raise GuardrailViolation(f"{field} must be a string")
    normalized = value.replace("\x00", "").strip()
    if not normalized:
        raise GuardrailViolation(f"{field} cannot be empty")
    if len(normalized) > maximum:
        raise GuardrailViolation(f"{field} exceeds {maximum} characters")
    return normalized


def redact_sensitive(value: str) -> tuple[str, tuple[str, ...]]:
    findings: list[str] = []
    redacted = value
    for pattern in _SECRET_PATTERNS:
        if pattern.search(redacted):
            findings.append("secret")
            redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    if _EMAIL.search(redacted):
        findings.append("email")
        redacted = _EMAIL.sub("[REDACTED_EMAIL]", redacted)
    if _PHONE.search(redacted):
        findings.append("phone")
        redacted = _PHONE.sub("[REDACTED_PHONE]", redacted)
    return redacted, tuple(dict.fromkeys(findings))


def detect_prompt_injection(value: str) -> bool:
    return bool(_INJECTION.search(value))


class SlidingWindowRateLimiter:
    def __init__(self, limit: int = 30, window_seconds: float = 60.0) -> None:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("rate-limit configuration must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, subject: str, now: float | None = None) -> bool:
        if not subject:
            return False
        current = time.monotonic() if now is None else now
        events = self._events[subject]
        cutoff = current - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(current)
        return True
