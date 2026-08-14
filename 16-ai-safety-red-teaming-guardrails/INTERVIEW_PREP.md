# 🎤 Staff AI Platform Interview Guide: AI Safety, Jailbreak Defense & PII Guardrails

This guide bridges **Project 16 (`16-ai-safety-red-teaming-guardrails`)** to Staff/Principal-level questions on AI safety, red-teaming, and Llama Guard policies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you detect and neutralize adversarial prompt injection and DAN jailbreaks?"
> **Staff Engineer Answer**:
> "In `src/safety_guardrails.py`, input prompts pass through heuristic normalization and semantic jailbreak detectors, identifying role-play overrides (`DAN`, `unrestricted mode`) and blocking requests with HTTP 400."

### Q2: "How do you ensure zero PII data leakage in LLM completions?"
> **Staff Engineer Answer**:
> "We scan completions using compiled regex patterns for SSNs, credit cards, and emails, redacting sensitive tokens into `[REDACTED]` tokens."

### Q3: "How does Llama Guard policy enforcement protect enterprise models?"
> **Staff Engineer Answer**:
> "Completions are classified against enterprise safety policies (hate speech, weapons, malware). Unsafe outputs are quarantined before reaching end-users."
