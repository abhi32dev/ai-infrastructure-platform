# 🎤 Staff AI Platform & Agent Systems Interview Guide (MCP & Guardrails Standard)

This guide bridges the code in **Project 1 (`01-agent-durable-runtime`)** directly to Staff/Principal-level questions asked by Anthropic, OpenAI, Meta AI, and Google DeepMind.

---

## 💡 Tech Community Requirements at Staff AI Level
Autonomous Agent Infrastructure requires robust protocol standards and safety guardrails:
1. **Model Context Protocol (MCP)**: The industry-standard JSON-RPC 2.0 protocol for agent tool discovery and prompt templates.
2. **Durable Step Checkpointing**: Atomic SQLite WAL step checkpoints enabling $O(1)$ crash recovery and step rewinds.
3. **Enterprise Guardrails**: Pre-execution PII redaction and prompt injection defense.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Model Context Protocol (MCP) enable standardized Agent-to-Agent (A2A) tool discovery?"
> **Staff Engineer Answer**:
> "In `01-agent-durable-runtime` (`src/mcp_tool_registry.py`), we implement Anthropic's **Model Context Protocol (MCP)** over JSON-RPC 2.0. Agents negotiate protocol capabilities (`tools`, `prompts`) and dynamically query peer tool definitions using JSON Schema, decoupling agent logic from vendor APIs."

### Q2: "How do you enforce PII redaction and prompt injection defense in autonomous agent workflows?"
> **Staff Engineer Answer**:
> "Before any prompt reaches an LLM or tool, multi-layered guardrails scan for jailbreak patterns (`DAN`, `ignore previous instructions`) and regex-redact sensitive SSNs, emails, and API keys (`sk-*`) into `[REDACTED]` tokens."

### Q3: "How does SQLite step checkpointing guarantee deterministic replay and state recovery?"
> **Staff Engineer Answer**:
> "In `src/checkpoint_store.py`, we record atomic SQLite WAL transactions at each step boundary (`PENDING`, `CHECKPOINTED`, `COMPLETED`). If a worker crashes at step 4, the runtime reads the latest snapshot and resumes without wasting LLM tokens on steps 1–3."
