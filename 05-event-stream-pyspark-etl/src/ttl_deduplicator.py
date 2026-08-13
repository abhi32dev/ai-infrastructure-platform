"""
TTL-Based Idempotency & Collision Avoidance Engine.
Implements per-file/per-event TTL-keyed deduplication markers (emulating DynamoDB TTL)
to prevent double-counting and stale multi-node overwrites during high-throughput ingestion.
"""

import time
from typing import Dict, Optional, Tuple


class TTLDeduplicator:
    def __init__(self, default_ttl_seconds: float = 300.0):
        self.default_ttl_seconds = default_ttl_seconds
        # In-memory TTL key table: {dedup_key: (expiration_timestamp, payload_hash)}
        self._table: Dict[str, Tuple[float, str]] = {}

    def is_duplicate(self, dedup_key: str, payload_hash: str) -> bool:
        """
        Checks if dedup_key exists within valid TTL window.
        Returns True if duplicate (should be dropped), False if new.
        """
        now = time.time()

        # Clean expired entries
        self._purge_expired(now)

        if dedup_key in self._table:
            exp_time, existing_hash = self._table[dedup_key]
            if now < exp_time:
                # Key is active inside TTL window!
                print(f"[TTL DEDUP] Blocked duplicate event for key '{dedup_key}' (TTL active for {round(exp_time - now, 1)}s).")
                return True

        # New key or expired key: record marker with fresh TTL
        self._table[dedup_key] = (now + self.default_ttl_seconds, payload_hash)
        return False

    def _purge_expired(self, current_time: float):
        expired_keys = [k for k, (exp, _) in self._table.items() if current_time >= exp]
        for k in expired_keys:
            del self._table[k]
