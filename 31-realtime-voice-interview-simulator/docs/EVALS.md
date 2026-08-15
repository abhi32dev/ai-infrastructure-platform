# Evaluation Design

The deterministic scorer produces eight 0–5 dimensions: technical correctness, architecture boundaries, trade-offs, failure modes, security/governance, observability/operations, scale/capacity and communication. Scores are inspectable and repeatable.

An LLM judge may be added for semantic nuance, but it must be versioned, calibrated against blinded expert labels, evaluated for verbosity/style/demographic bias, and compared against deterministic checks. It cannot be the only release or hiring control.

## Required evaluation suites

1. Golden answers and known omissions for every dimension.
2. Paraphrase invariance and concise-correct-answer cases.
3. Confidently incorrect and fabricated-code-reference cases.
4. Prompt injection attempting to reveal the reference answer.
5. PII/secret-containing answers and retention-disabled sessions.
6. Adaptive versus fixed-path coverage and difficulty parity.
7. Browser transcript noise, partial turns and repeated fragments.
8. Score distribution and judge-disagreement drift over releases.

Promotion requires deterministic suite pass, no security regression, bounded score drift, resolved code references and human review of changed rubric behavior.
