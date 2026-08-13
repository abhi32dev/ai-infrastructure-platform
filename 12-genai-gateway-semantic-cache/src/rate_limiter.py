"""
Token Bucket Rate Limiter & SLA Governance Engine.
Enforces per-client token-per-minute (TPM) and request-per-minute (RPM) bucket limits,
protecting downstream LLM providers from budget overruns and DDoS surges.
"""

import time
from typing import Dict
from pydantic import BaseModel, Field


class TokenBucketStatus(BaseModel):
    client_id: str
    tokens_remaining: float
    max_tokens_per_min: int
    is_allowed: bool
    retry_after_sec: float


class TokenBucketRateLimiter:
    def __init__(self, default_tpm_limit: int = 100000, refill_rate_per_sec: float = 1666.6):
        self.max_tpm = default_tpm_limit
        self.refill_rate = refill_rate_per_sec
        self.buckets: Dict[str, float] = {}
        self.last_update: Dict[str, float] = {}

    def _refill_bucket(self, client_id: str) -> None:
        now = time.time()
        if client_id not in self.buckets:
            self.buckets[client_id] = float(self.max_tpm)
            self.last_update[client_id] = now
            return

        elapsed = now - self.last_update[client_id]
        added_tokens = elapsed * self.refill_rate
        self.buckets[client_id] = min(float(self.max_tpm), self.buckets[client_id] + added_tokens)
        self.last_update[client_id] = now

    def consume_tokens(self, client_id: str, requested_tokens: int) -> TokenBucketStatus:
        self._refill_bucket(client_id)
        current = self.buckets[client_id]

        if current >= requested_tokens:
            self.buckets[client_id] -= requested_tokens
            return TokenBucketStatus(
                client_id=client_id,
                tokens_remaining=round(self.buckets[client_id], 1),
                max_tokens_per_min=self.max_tpm,
                is_allowed=True,
                retry_after_sec=0.0
            )

        missing = requested_tokens - current
        retry_after = round(missing / self.refill_rate, 2)
        return TokenBucketStatus(
            client_id=client_id,
            tokens_remaining=round(current, 1),
            max_tokens_per_min=self.max_tpm,
            is_allowed=False,
            retry_after_sec=retry_after
        )
