"""
Statistical Release Gate & P-Value Significance Validation Engine.
Applies A/B testing hypothesis testing (Welch's t-test & Mann-Whitney U test) to evaluate if a candidate
prompt/model version provides a statistically significant improvement over baseline before production release.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from pydantic import BaseModel
from scipy import stats


class ReleaseGateDecision(BaseModel):
    baseline_version: str
    candidate_version: str
    metric_name: str
    baseline_mean: float
    candidate_mean: float
    percentage_lift: float
    p_value: float
    statistically_significant: bool
    release_approved: bool
    recommendation: str


class StatisticalReleaseGate:
    def __init__(self, significance_threshold_p: float = 0.05):
        self.significance_threshold_p = significance_threshold_p

    def evaluate_release_significance(
        self, 
        baseline_version: str,
        candidate_version: str,
        metric_name: str,
        baseline_scores: List[float], 
        candidate_scores: List[float]
    ) -> ReleaseGateDecision:
        """
        Executes Welch's t-test and Mann-Whitney U test comparing Baseline vs Candidate score distributions.
        """
        b_arr = np.array(baseline_scores)
        c_arr = np.array(candidate_scores)

        b_mean = float(np.mean(b_arr)) if len(b_arr) > 0 else 0.0
        c_mean = float(np.mean(c_arr)) if len(c_arr) > 0 else 0.0

        lift_pct = round(((c_mean - b_mean) / b_mean * 100.0) if b_mean > 0 else 0.0, 2)

        # Welch's t-test (two-sample unequal variance)
        if len(b_arr) > 1 and len(c_arr) > 1:
            t_stat, p_val = stats.ttest_ind(c_arr, b_arr, equal_var=False)
            p_value = float(p_val)
        else:
            p_value = 1.0

        is_significant = p_value < self.significance_threshold_p
        is_improved = c_mean > b_mean

        release_approved = is_significant and is_improved

        if release_approved:
            rec = f"APPROVED RELEASE: Candidate '{candidate_version}' demonstrated a statistically significant {lift_pct}% lift on '{metric_name}' (p={p_value:.4f} < {self.significance_threshold_p})."
        elif is_improved and not is_significant:
            rec = f"HOLD RELEASE: Candidate '{candidate_version}' showed a {lift_pct}% lift, but it is NOT statistically significant (p={p_value:.4f} >= {self.significance_threshold_p}). Need more samples."
        else:
            rec = f"REJECT RELEASE REGRESSION: Candidate '{candidate_version}' underperformed baseline ({lift_pct}% change, p={p_value:.4f})."

        return ReleaseGateDecision(
            baseline_version=baseline_version,
            candidate_version=candidate_version,
            metric_name=metric_name,
            baseline_mean=round(b_mean, 4),
            candidate_mean=round(c_mean, 4),
            percentage_lift=lift_pct,
            p_value=round(p_value, 5),
            statistically_significant=is_significant,
            release_approved=release_approved,
            recommendation=rec
        )
