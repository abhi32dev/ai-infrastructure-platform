# 🎤 Staff AI Platform Interview Guide: Medusa Multi-Head Speculative Decoding & Tree Attention

This guide bridges **Project 25 (`25-speculative-medusa-multi-head-verifier`)** to Staff/Principal-level questions on Medusa speculative decoding and Tree Attention.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Medusa achieve speculative decoding without hosting a separate draft model?"
> **Staff Engineer Answer**:
> "In `src/medusa_verifier.py`, Medusa attaches 4 lightweight MLP heads directly on top of the base model's final hidden states, predicting tokens $t+1, t+2, t+3, t+4$ simultaneously in parallel with zero auxiliary model VRAM footprint."

### Q2: "How does 2D Tree Attention verify multiple speculative candidate tokens in a single pass?"
> **Staff Engineer Answer**:
> "We construct a candidate token tree and apply custom 2D Tree Attention causal masks. The base model processes the tree in a single forward pass, accepting 2 to 4 tokens and achieving up to 2.85x speedup."

### Q3: "How does the engine handle partial speculative verification matches?"
> **Staff Engineer Answer**:
> "If only tokens 1 and 2 match target logits, the engine accepts the 2 verified tokens, resamples the true 3rd token from target logits, and advances generation without wasting work."
