# 🎤 Staff AI Platform Interview Guide: Direct Preference Optimization (DPO) & RLHF

This guide bridges **Project 13 (`13-rlhf-dpo-alignment-pipeline`)** to Staff/Principal-level questions on LLM alignment and preference optimization.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "What are the primary mathematical advantages of DPO over PPO (RLHF)?"
> **Staff Engineer Answer**:
> "In `src/dpo_alignment_engine.py`, PPO requires 4 concurrent models (Policy, Reference, Reward, Critic) in VRAM. DPO expresses the optimal reward in closed form, optimizing policy weights directly on pairwise chosen/rejected responses: $\mathcal{L}_{\text{DPO}} = -\log \sigma \left(\beta \log \frac{\pi_\theta(y_w)}{\pi_{ref}(y_w)} - \beta \log \frac{\pi_\theta(y_l)}{\pi_{ref}(y_l)}\right)$."

### Q2: "How do you evaluate Bradley-Terry win-rate margins during training?"
> **Staff Engineer Answer**:
> "We compute the implicit reward margin $r_w - r_l$. A win-rate $\ge 75\%$ confirms policy alignment with human preferences."

### Q3: "How do you ensure numerical stability in DPO log-ratio calculations?"
> **Staff Engineer Answer**:
> "We clamp log-probability ratios within $[-20.0, 20.0]$ before passing through the sigmoid activation to prevent gradient saturation."
