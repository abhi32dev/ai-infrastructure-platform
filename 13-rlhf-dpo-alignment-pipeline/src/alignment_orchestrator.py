"""
Master RLHF & Direct Preference Optimization (DPO) Alignment Orchestrator.
Integrates Pairwise Dataset Curation, DPO Loss Calculation, and Bradley-Terry Model Auditing.
"""

from typing import Any, Dict
from src.preference_dataset import PreferenceDatasetCurator
from src.dpo_loss import DPOLossCalculator, DPOLossResult
from src.reward_model_auditor import AlignmentAuditResult, RewardModelAuditor


class RLHFAlignmentOrchestrator:
    def __init__(self, beta: float = 0.1):
        self.curator = PreferenceDatasetCurator()
        self.dpo = DPOLossCalculator(beta=beta)
        self.auditor = RewardModelAuditor()

    def run_dpo_epoch(self) -> Dict[str, Any]:
        """Runs a simulated DPO optimization step over preference data."""
        # Curate sample preferences
        self.curator.add_preference(
            sample_id="pref-001",
            prompt="Write a safe Python function for file upload.",
            chosen="Validate file extension and use secure filename sanitization.",
            rejected="Save file directly with user provided filename.",
            margin=1.5
        )

        # Compute DPO loss step
        loss_res = self.dpo.compute_dpo_loss(
            policy_logprob_chosen=-0.2,
            ref_logprob_chosen=-0.5,
            policy_logprob_rejected=-1.8,
            ref_logprob_rejected=-1.2
        )

        # Audit alignment performance
        audit = self.auditor.audit_alignment_epoch(
            margins=[loss_res.reward_margin],
            kl_drifts=[loss_res.kl_divergence_estimate]
        )

        return {
            "status": "DPO_EPOCH_COMPLETED",
            "dpo_loss": loss_res.dpo_loss,
            "chosen_reward": loss_res.chosen_reward,
            "rejected_reward": loss_res.rejected_reward,
            "reward_margin": loss_res.reward_margin,
            "win_rate_pct": audit.win_rate_pct,
            "kl_drift_within_bounds": audit.kl_drift_within_bounds,
            "alignment_status": audit.status
        }
