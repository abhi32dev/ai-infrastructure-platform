# Project 16: AI Safety, Red-Teaming & Policy Guardrails Engine

AI safety and red-teaming platform implementing **Real-Time Prompt Injection Scanning** (DAN jailbreak & system prompt leak detection), **PII Anonymization** (SSN/Email/Phone masking), and **NeMo / Llama Guard Policy Enforcement**.

---

## 🛠️ Architecture Components
- **Prompt Scanner**: Detects adversarial jailbreak patterns and system prompt overrides.
- **PII Anonymizer**: Masking pipeline redacting sensitive customer data before LLM inference.
- **Policy Engine**: Llama Guard policy enforcement preventing toxic or uncompliant output.

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```
