"""
Direct Preference Optimization (DPO) Loss & Reward Calculation Engine.
Calculates implicit rewards from policy log-ratios relative to reference model:
$r(x,y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}$
and computes DPO loss $\mathcal{L}_{\text{DPO}} = -\mathbb{E} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right]$.
"""

import math
from typing import Any, Dict
from pydantic import BaseModel, Field


class DPOLossResult(BaseModel):
    dpo_loss: float
    chosen_reward: float
    rejected_reward: float
    reward_margin: float
    kl_divergence_estimate: float


class DPOLossCalculator:
    def __init__(self, beta: float = 0.1):
        self.beta = beta  # KL penalty coefficient beta=0.1

    def compute_dpo_loss(
        self, 
        policy_logprob_chosen: float, 
        ref_logprob_chosen: float,
        policy_logprob_rejected: float, 
        ref_logprob_rejected: float
    ) -> DPOLossResult:
        """
        Computes DPO loss and implicit reward metrics.
        """
        # Implicit rewards
        reward_chosen = self.beta * (policy_logprob_chosen - ref_logprob_chosen)
        reward_rejected = self.beta * (policy_logprob_rejected - ref_logprob_rejected)
        margin = reward_chosen - reward_rejected

        # Numerically stable sigmoid of logit margin: \sigma(r_w - r_l)
        if margin >= 0.0:
            z = math.exp(-margin)
            sigmoid_val = 1.0 / (1.0 + z)
        else:
            z = math.exp(margin)
            sigmoid_val = z / (1.0 + z)

        dpo_loss = -math.log(max(1e-7, sigmoid_val))

        # KL divergence proxy
        kl_div = abs(policy_logprob_chosen - ref_logprob_chosen)

        return DPOLossResult(
            dpo_loss=round(dpo_loss, 4),
            chosen_reward=round(reward_chosen, 4),
            rejected_reward=round(reward_rejected, 4),
            reward_margin=round(margin, 4),
            kl_divergence_estimate=round(kl_div, 4)
        )
