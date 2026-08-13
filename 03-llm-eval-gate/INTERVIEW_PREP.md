# 🎤 Staff / Principal AI Infrastructure Interview Guide: AI Evaluation & LLMOps Governance

This guide bridges the code in **Project 3 (`03-llm-eval-gate`)** directly to Staff/Principal-level questions asked by FAANG, Tier-1 AI startups, and top product companies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you systematically detect hallucinations and verify LLM outputs before releasing prompt or model updates?"
> **Staff Engineer Answer**:
> "We do not rely on subjective output inspection. In `03-llm-eval-gate`, we implement a **Multi-Model LLM-as-a-Judge Evaluation Gate** ([`src/llm_as_judge.py`](src/llm_as_judge.py)).
> 
> We evaluate candidate outputs against a second independent judge model using standardized G-Eval rubrics across 4 release dimensions:
> 1. **Groundedness**: Verifies what percentage of claims in the generated answer are directly supported by the retrieved source context ([`src/eval_rubrics.py`](src/eval_rubrics.py)).
> 2. **Context Relevance**: Verifies that retrieved context chunks match the user query intent.
> 3. **Answer Faithfulness**: Checks alignment with reference ground truth.
> 4. **Toxicity & Safety**: Programmatic safety gates.
> 
> If groundedness drops below our release threshold (e.g. 80%), the automated CI gate blocks the prompt or model release."

---

### Q2: "How do you track prompt templates and hyperparameter regressions across team releases?"
> **Staff Engineer Answer**:
> "We treat prompts and model configurations as versioned software artifacts managed through MLflow ([`src/mlflow_tracker.py`](src/mlflow_tracker.py)).
> 
> For every evaluation run, we log:
> - `prompt_version` (e.g. `v2.0-enhanced-context-prompt`)
> - Hyperparameters (`temperature`, `chunk_size`, `top_k`, retriever strategy)
> - Quantitative metric distributions (Groundedness score, Relevance score, Faithfulness score, Pass rate)
> - Detailed evaluation result JSON artifacts.
> 
> This provides complete historical auditability in MLflow, allowing us to catch quality regressions immediately when a team member modifies a prompt template or model version."

---

### Q3: "How do you prove that a candidate prompt or model improvement is real rather than random noise?"
> **Staff Engineer Answer**:
> "In high-scale production systems, measuring an average score increase of +5% without statistical validation can be misleading due to sample variance. We enforce a **Statistical Release Gate** using hypothesis testing ([`src/statistical_gate.py`](src/statistical_gate.py)).
> 
> We execute **Welch's t-test** (two-sample unequal variance) comparing Baseline score distribution $A$ against Candidate score distribution $B$:
> - **Null Hypothesis ($H_0$)**: Baseline and Candidate have identical mean performance.
> - **Release Criterion**: Candidate must demonstrate a statistically significant improvement ($p < 0.05$).
> 
> If $p \ge 0.05$, the system flags the release as 'Statistically Insignificant' and holds promotion, requesting additional test samples. This prevents rolling out placebo changes or hidden regressions to production."

---

## 🧪 Quick Test Checklist for Candidates
Run these commands in your workspace to test and demonstrate:
- `python3 demo_runner.py`: Executes all 4 evaluation and statistical release gate scenarios live.
- `pytest tests/`: Verifies unit and integration test suite.
- `python3 app.py`: Opens Evaluation Dashboard at `http://127.0.0.1:8002` to visually run dataset evaluations and test $p$-value release gates.
