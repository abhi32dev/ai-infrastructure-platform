# 🎤 Staff AI Platform & Agent Systems Interview Guide (MCP & Guardrails Standard)

This guide bridges the code in **Project 1 (`01-agent-durable-runtime`)** directly to Staff/Principal-level questions asked by Anthropic, OpenAI, Meta AI, and Google DeepMind.

---

## 💡 Tech Community Requirements at Staff AI Level

> **Industry Context (2025-2026)**:
> Autonomous Agent Infrastructure requires robust protocol standards and safety guardrails:
> 1. **Model Context Protocol (MCP)**: The industry-standard JSON-RPC 2.0 protocol for agent tool discovery, prompt templates, and inter-agent communication.
> 2. **Agent-to-Agent (A2A) Messaging**: How peer subagents perform handshakes, exchange JSON Schema tool definitions, and delegate subtasks.
> 3. **Enterprise Guardrails**: Pre-execution PII redaction (SSNs, API keys, emails) and prompt injection / jailbreak attack defense (`DAN`, `system prompt override`).

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Model Context Protocol (MCP) enable standardized Agent-to-Agent (A2A) tool discovery and communication?"
> **Staff Engineer Answer**:
> "In `01-agent-durable-runtime` ([`src/mcp_agent_protocol.py`](src/mcp_agent_protocol.py)), we implement Anthropic's **Model Context Protocol (MCP)** over JSON-RPC 2.0:
> - **Handshake (`initialize`)**: Autonomous agents negotiate protocol version (`2024-11-05`) and capabilities (`tools`, `prompts`, `resources`).
> - **Tool Discovery (`tools/list`)**: Agents dynamically query peer capabilities, receiving JSON Schema input definitions for remote tools.
> - **Tool Invocation (`tools/call`)**: Subagents invoke remote tools with validated arguments and permission gates (`READ_ONLY`, `WRITE_SAFE`, `SENSITIVE_REQUIRES_APPROVAL`).
> 
> This decouples agent logic from specific API wrappers, enabling seamless multi-agent orchestration."

---

### Q2: "How do you enforce PII redaction and prompt injection defense in autonomous agent workflows?"
> **Staff Engineer Answer**:
> "Before any prompt is dispatched to an LLM or remote tool, we pass it through multi-layered enterprise guardrails ([`src/enterprise_guardrails.py`](src/enterprise_guardrails.py)):
> 1. **Prompt Injection Defense**: Regex and semantic pattern matching detect jailbreak attempts (`DAN`, `ignore previous instructions`, `bypass safety filter`), blocking execution immediately.
> 2. **PII Sanitization**: Automatic regex scanners detect SSNs, credit cards, emails, and API keys (`sk-*`), redacting sensitive data into `[REDACTED_SSN]` or `[REDACTED_EMAIL]` tokens before logging or API transmission.
> 
> This prevents data exfiltration and prompt override attacks across all agent execution steps."

---

### Q3: "How does SQLite step checkpointing guarantee deterministic replay and state recovery?"
> **Staff Engineer Answer**:
> "Agent workflows are non-deterministic and prone to step failures (e.g. transient API timeouts at step 3).
> 
> In [`src/checkpoint_store.py`](src/checkpoint_store.py) and [`src/agent_orchestrator.py`](src/agent_orchestrator.py), we record atomic SQLite step checkpoints (`PENDING`, `RUNNING`, `CHECKPOINTED`, `COMPLETED`, `FAILED`).
> When a failure occurs at step 2, the agent state machine rewinds without re-executing steps 0 and 1. Upon fixing the root cause or obtaining HITL approval, the orchestrator replays execution deterministically from the last valid checkpoint."
