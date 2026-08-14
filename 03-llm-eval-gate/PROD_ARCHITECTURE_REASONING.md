# Production Architecture & Design Trade-offs: LLM Evaluation Gate Engine

## 1. Executive Context & Business Motivation
Deploying new fine-tuned or aligned LLM checkpoints into production requires automated evaluation quality gates. Manual human evaluation takes days and does not scale; un-evaluated model deployments risk regressions in hallucination rates, toxicity, or domain accuracy.

This component provides an **Automated LLM Evaluation Quality Gate Engine** executing multi-metric scoring (Faithfulness, Answer Relevance, Hallucination Index, Toxicity).

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Automated LLM-as-a-Judge Evaluation vs Manual Human Sampling
- **Chosen Option**: **Automated Multi-Metric LLM-as-a-Judge Gate**.
- **Alternative Evaluated**: Manual spot-checking by domain annotators.
- **Trade-Off Rationale**:
  - *Manual Spot-Checking*: Slow, non-deterministic, and cannot block CI/CD pipelines automatically.
  - *Automated Eval Gate*: Computes exact metric scores across benchmark evaluation datasets in <30 seconds, returning automated PASS/FAIL status for CI/CD pipeline promotion.

---

## 3. Best Practices & Production Design Principles
1. **Threshold-Based Deployment Blocking**: Blocks model promotion if faithfulness score falls below 0.85 or toxicity exceeds 0.01.
2. **Deterministic Evaluation Seeding**: Uses fixed temperature (0.0) for reproducible judge scoring.
3. **Multi-Aspect Scoring Breakdown**: Separates retrieval relevance from generation correctness.

---

## 4. Production Failure Modes & Mitigations
| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Judge Model Hallucination** | Inaccurate eval score | Ensemble judge consensus across multiple evaluation prompts. |
| **Evaluation Dataset Bias** | Overfitting to test set | Dynamic evaluation set rotation across CI runs. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Prevents degraded or toxic model variants from reaching production. Evaluates candidate LLMs against golden benchmark datasets using Welch's t-test for statistical significance, RAG triad quality scores, and automated toxicity classifiers.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "candidate_model": "mistral-7b-finetuned-v2",
  "baseline_model": "mistral-7b-prod-v1",
  "sample_size": 500,
  "p_value_threshold": 0.05,
  "min_accuracy_delta": 0.05
}
```
**Input Parameter Specification**:
Candidate model ID, baseline model ID, and evaluation dataset containing 500 prompt-response pairs.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Compute Evaluation Metrics**: Runs candidate and baseline models over golden dataset, calculating Faithfulness, Answer Relevance, and Groundedness.
- **2. Decision 1 (Welch t-Test Statistical Gate)**: Computes two-sample Welch t-test. If p-value < 0.05 and accuracy delta > +5%, marks quality gain. If not statistically significant, blocks build.
- **3. Toxicity & PII Audit**: Passes candidate responses through toxicity evaluation classifier.
- **4. Decision 2 (Toxicity Threshold Check)**: If toxicity score <= 0.05, approves release gate and registers model in MLflow Production stage. If toxic (> 0.05), blocks deployment.
- **5. Decision 3 (Sample Size & Re-eval)**: If sample size is insufficient, triggers re-sampling from golden dataset.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "gate_status": "APPROVED",
  "p_value": 0.0142,
  "accuracy_delta": "+0.078",
  "toxicity_score": 0.002,
  "promoted_to_mlflow": true,
  "registry_stage": "Production"
}
```
**Output Specification**:
A statistical release gate report with p-values, confidence intervals, toxicity score, and promotion status.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 03-llm-eval-gate/tests/test_eval_gate.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/03-llm-eval-gate/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/03-llm-eval-gate/FLOWCHART.svg)
