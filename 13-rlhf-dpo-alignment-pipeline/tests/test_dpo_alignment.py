"""
Expanded Test Suite for Project 13 - Direct Preference Optimization (DPO) & RLHF Alignment.
Tests pairwise preference dataset curation, implicit reward calculation, DPO loss sigmoid scaling,
Bradley-Terry win-rate auditing, and KL divergence drift limits.
"""

import pytest
from src.preference_dataset import PreferenceDatasetCurator
from src.dpo_loss import DPOLossCalculator
from src.reward_model_auditor import RewardModelAuditor
from src.alignment_orchestrator import RLHFAlignmentOrchestrator


@pytest.fixture
def curator():
    return PreferenceDatasetCurator()


@pytest.fixture
def dpo():
    return DPOLossCalculator(beta=0.1)


@pytest.fixture
def auditor():
    return RewardModelAuditor(max_allowed_kl_drift=0.5)


@pytest.fixture
def orchestrator():
    return RLHFAlignmentOrchestrator(beta=0.1)


def test_01_preference_dataset_curation(curator):
    """Test 1: Verifies structuring pairwise (prompt, chosen, rejected) tuple."""
    sample = curator.add_preference("s-1", "Prompt", "Chosen text", "Rejected text", margin=1.2)
    assert sample.sample_id == "s-1"
    assert sample.chosen_completion == "Chosen text"
    summary = curator.get_dataset_summary()
    assert summary["total_preference_pairs"] == 1


def test_02_dpo_implicit_reward_calculation(dpo):
    """Test 2: Verifies implicit reward calculation r(x,y) = beta * log(pi_theta / pi_ref)."""
    res = dpo.compute_dpo_loss(
        policy_logprob_chosen=-0.2,
        ref_logprob_chosen=-0.5,
        policy_logprob_rejected=-1.8,
        ref_logprob_rejected=-1.2
    )
    assert res.chosen_reward == round(0.1 * (-0.2 - (-0.5)), 4)  # +0.03
    assert res.rejected_reward == round(0.1 * (-1.8 - (-1.2)), 4)  # -0.06
    assert res.reward_margin == round(0.03 - (-0.06), 4)  # +0.09


def test_03_dpo_loss_bounds(dpo):
    """Test 3: Verifies DPO loss non-negativity and convergence behavior."""
    res = dpo.compute_dpo_loss(-0.1, -0.5, -2.0, -1.0)
    assert res.dpo_loss >= 0.0


def test_04_auditor_win_rate_pass(auditor):
    """Test 4: Verifies Bradley-Terry model win-rate pass threshold (>= 75%)."""
    res = auditor.audit_alignment_epoch(margins=[0.1, 0.2, 0.05, 0.3], kl_drifts=[0.1, 0.2, 0.1, 0.1])
    assert res.win_rate_pct == 100.0
    assert res.status == "ALIGNMENT_APPROVED"


def test_05_auditor_kl_drift_violation(auditor):
    """Test 5: Verifies audit failure when KL divergence drift exceeds threshold."""
    res = auditor.audit_alignment_epoch(margins=[0.1, 0.2], kl_drifts=[0.8, 0.9])  # Exceeds max 0.5!
    assert res.kl_drift_within_bounds is False
    assert res.status == "ALIGNMENT_NEEDS_TUNING"


def test_06_orchestrator_dpo_step(orchestrator):
    """Test 6: Verifies end-to-end RLHF alignment orchestrator DPO step."""
    res = orchestrator.run_dpo_epoch()
    assert res["status"] == "DPO_EPOCH_COMPLETED"
    assert res["reward_margin"] > 0.0
    assert res["alignment_status"] == "ALIGNMENT_APPROVED"


def test_07_empty_auditor_handling(auditor):
    """Test 7: Verifies auditor handling empty margins safely."""
    res = auditor.audit_alignment_epoch([], [])
    assert res.status == "EMPTY_DATA"


def test_08_dpo_beta_scaling(dpo):
    """Test 8: Verifies beta coefficient impact on implicit reward margins."""
    dpo_high_beta = DPOLossCalculator(beta=0.5)
    res_high = dpo_high_beta.compute_dpo_loss(-0.2, -0.5, -1.8, -1.2)
    res_low = dpo.compute_dpo_loss(-0.2, -0.5, -1.8, -1.2)
    assert res_high.reward_margin > res_low.reward_margin
