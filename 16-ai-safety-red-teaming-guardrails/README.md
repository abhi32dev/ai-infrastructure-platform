# Project 16: AI Safety, Red-Teaming & Policy Guardrails Engine

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/16-ai-safety-red-teaming-guardrails/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**


![2D Control Flow Diagram](FLOWCHART.svg)

---

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