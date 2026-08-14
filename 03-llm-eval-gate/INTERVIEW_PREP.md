# 🎤 Staff AI Platform Interview Guide: LLM Evaluation Gate & Statistical CI/CD

This guide bridges **Project 3 (`03-llm-eval-gate`)** to Staff/Principal-level questions on continuous model evaluation and statistical validation.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is mean accuracy insufficient for model deployment gates, and why is Welch's t-test mandatory?"
> **Staff Engineer Answer**:
> "LLM generations are non-deterministic. A candidate model scoring $84\%$ vs baseline $82\%$ over small sample sets may reflect random noise. In `src/statistical_gate.py`, we compute Welch's two-sample t-test ($p < 0.05$) to prove statistical significance before promoting candidate weights in MLflow."

### Q2: "How do you measure Faithfulness, Answer Relevance, and Groundedness (RAG Triad)?"
> **Staff Engineer Answer**:
> "In `src/eval_rubrics.py`, we evaluate:
> 1. **Faithfulness**: Proportion of generated claims supported by retrieved context.
> 2. **Answer Relevance**: Semantic cosine alignment between query and response.
> 3. **Groundedness**: Ratio of hallucinated tokens to verified reference citations."

### Q3: "How do automated toxicity classifiers prevent harmful model releases in CI/CD?"
> **Staff Engineer Answer**:
> "In `src/llm_as_judge.py`, candidate responses are evaluated across toxicity rubrics. If the toxicity score exceeds $0.05$, the deployment pipeline halts and alerts the ML platform team."
