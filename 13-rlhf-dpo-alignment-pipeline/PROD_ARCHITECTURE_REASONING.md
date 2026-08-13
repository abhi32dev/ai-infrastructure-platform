# Production Architecture & Design Trade-offs: Direct Preference Optimization (DPO) Pipeline

## 1. Executive Context & Business Motivation
Aligning Large Language Models with human preferences via traditional Reinforcement Learning from Human Feedback (RLHF / PPO) requires training a separate reward model, sampling multiple rollout completions, and training an actor-critic PPO network—a process notorious for training instability and high VRAM overhead.

This pipeline implements **Direct Preference Optimization (DPO) Loss & Bradley-Terry Win-Rate Auditing**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Direct Preference Optimization (DPO) vs PPO (RLHF)
- **Chosen Option**: **Direct Preference Optimization (DPO)**.
- **Alternative Evaluated**: PPO (Proximal Policy Optimization).
- **Trade-Off Rationale**:
  - *PPO*: Requires 4 models simultaneously in VRAM (Actor, Critic, Reference, Reward), making multi-GPU training unstable and memory intensive.
  - *DPO*: Mathematically re-parameterizes the PPO reward formulation. Fits policy log-ratios relative to reference model directly: $r(x,y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}$, eliminating the need for a separate reward model or RL sampling.

### B. Numerically Stable Sigmoid Computation
- **Chosen Option**: **Numerically Stable Sigmoid Engine**.
- **Trade-Off Rationale**: Standard `1 / (1 + exp(-margin))` crashes with `OverflowError` when reward margins are large negative numbers ($\text{margin} \le -500$). The stable implementation branch prevents floating point overflow.

---

## 3. Best Practices & Production Design Principles

1. **Bradley-Terry Model Win-Rate Auditing**:
   - Audits pairwise model preference win-rates $P(y_w \succ y_l) = \sigma(r_w - r_l)$ across training epochs.
2. **KL Divergence Drift Guard**:
   - Measures policy logprob drift relative to reference model, halting training if KL drift exceeds safety bounds ($\text{KL} > 0.5$).
3. **Curated Pairwise Datasets**:
   - Enforces strict validation on $(prompt, y_w, y_l)$ tuples.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Extreme Reward Margin Overflow** | Math overflow exception crash | Numerically stable sigmoid branching logic. |
| **Policy Model Reward Hacking / KL Collapse** | Model outputs gibberish | Auditor monitors KL drift and flags `ALIGNMENT_NEEDS_TUNING`. |
| **Empty Pairwise Dataset Ingestion** | Zero division error | Defensive guard check returns `EMPTY_DATA` audit status. |
