import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.medusa_verifier import (
    MedusaVerifier,
    MedusaCandidate,
    MedusaHeadPredictor,
    TreeAttentionVerifier
)

@pytest.fixture
def verifier():
    return MedusaVerifier(num_heads=4)

def test_01_all_candidates_accepted(verifier):
    gt = [101, 102, 103, 104]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 4
    assert res.status == "MEDUSA_MAX_ACCELERATION"
    assert res.speedup_multiplier == 2.85

def test_02_partial_candidates_accepted(verifier):
    gt = [101, 102, 999, 104]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 2
    assert res.accepted_token_ids == [101, 102]
    assert res.status == "MEDUSA_PARTIAL_ACCELERATION"

def test_03_zero_candidates_accepted(verifier):
    gt = [999, 999, 999, 999]
    res = verifier.generate_speculative(current_token=100, ground_truth_stream=gt)
    assert res.tokens_accepted == 0
    assert res.speedup_multiplier == 1.0
    assert res.status == "FALLBACK_SINGLE_TOKEN"

def test_04_candidate_generation_count():
    cands = MedusaHeadPredictor.predict_candidates(50, num_heads=4)
    assert len(cands) == 4
    assert cands[0].token_id == 51
    assert cands[3].token_id == 54

def test_05_tree_attention_early_stopping():
    cands = [MedusaCandidate(head_index=i, token_id=i+1, confidence=0.9) for i in range(4)]
    count, accepted = TreeAttentionVerifier.verify_tree(cands, [1, 2, 99, 4])
    assert count == 2
    assert accepted == [1, 2]

def test_06_tree_attention_empty_ground_truth():
    cands = [MedusaCandidate(head_index=0, token_id=1, confidence=0.9)]
    count, accepted = TreeAttentionVerifier.verify_tree(cands, [])
    assert count == 0
    assert accepted == []

def test_07_custom_head_count():
    v = MedusaVerifier(num_heads=2)
    res = v.generate_speculative(10, [11, 12])
    assert res.heads_verified == 2

def test_08_schema_validation():
    cand = MedusaCandidate(head_index=0, token_id=10, confidence=0.95)
    assert cand.head_index == 0
    assert cand.token_id == 10

def test_09_confidence_decay():
    cands = MedusaHeadPredictor.predict_candidates(10, num_heads=4)
    assert cands[0].confidence > cands[3].confidence

def test_10_speedup_calculation_two_tokens(verifier):
    res = verifier.generate_speculative(100, [101, 102, 0, 0])
    assert res.speedup_multiplier == 1.90

def test_11_single_head_prediction():
    cands = MedusaHeadPredictor.predict_candidates(1, num_heads=1)
    assert len(cands) == 1

def test_12_medusa_result_schema(verifier):
    res = verifier.generate_speculative(100, [101])
    assert hasattr(res, "tokens_accepted")
    assert hasattr(res, "speedup_multiplier")
    assert hasattr(res, "status")
