"""
Bradley-Terry Reward Model Win-Rate & Alignment Auditor.
Audits pairwise model win-rate improvements ($P(y_w \succ y_l)$) and checks KL drift.
"""

import math
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class AlignmentAuditResult(BaseModel):
    total_eval_pairs: int
    win_rate_pct: float
    avg_reward_margin: float
    kl_drift_within_bounds: bool
    status: str


class RewardModelAuditor:
    def __init__(self, max_allowed_kl_drift: float = 0.5):
        self.max_kl = max_allowed_kl_drift

    def audit_alignment_epoch(self, margins: List[float], kl_drifts: List[float]) -> AlignmentAuditResult:
        """Audits alignment epoch metrics."""
        if not margins:
            return AlignmentAuditResult(
                total_eval_pairs=0, win_rate_pct=0.0, avg_reward_margin=0.0, kl_drift_within_bounds=True, status="EMPTY_DATA"
            )

        wins = sum(1 for m in margins if m > 0.0)
        win_rate = round((wins / float(len(margins))) * 100.0, 2)
        avg_margin = round(sum(margins) / float(len(margins)), 4)
        avg_kl = sum(kl_drifts) / float(len(kl_drifts)) if kl_drifts else 0.0
        is_safe = avg_kl <= self.max_kl

        return AlignmentAuditResult(
            total_eval_pairs=len(margins),
            win_rate_pct=win_rate,
            avg_reward_margin=avg_margin,
            kl_drift_within_bounds=is_safe,
            status="ALIGNMENT_APPROVED" if win_rate >= 75.0 and is_safe else "ALIGNMENT_NEEDS_TUNING"
        )
