# ⚡ Project 1: Enterprise Multi-Step Agent Runtime & Durable Execution Engine

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/01-agent-durable-runtime/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---

A production-grade, local-first **Durable AI Agent Runtime** demonstrating workflow state machines, SQLite step checkpointing, deterministic replay, fan-out/fan-in parallel worker dispatching, Model Context Protocol (MCP) tool gates, and Human-in-the-Loop (HITL) approval patterns.

---

## 🎯 Resume & Architecture Mapping

| Feature / Architectural Pattern | Resume Claim Mapped | Implementation Module |
| :--- | :--- | :--- |
| **Durable Execution & Checkpoints** | S3 checkpoints, deterministic replay | [`src/checkpoint_store.py`](src/checkpoint_store.py) |
| **State Machine & Fault Isolation** | Workflow state machine, bounded retries | [`src/agent_orchestrator.py`](src/agent_orchestrator.py) |
| **Fan-Out / Fan-In Worker Scheduling**| Dynamic batching, master-worker dispatch | [`src/worker_dispatcher.py`](src/worker_dispatcher.py) |
| **MCP Concepts & Tool Scoping** | Tool execution, least-privilege access | [`src/mcp_tool_registry.py`](src/mcp_tool_registry.py) |
| **Human-In-The-Loop (HITL)** | Escalation patterns & human review gates | [`app.py`](app.py) & [`src/mcp_tool_registry.py`](src/mcp_tool_registry.py) |

---

## 📁 Repository Structure

```text
01-agent-durable-runtime/
├── src/
│   ├── state_models.py        # Pydantic state models (TaskState, StepCheckpoint, TaskStatus)
│   ├── checkpoint_store.py    # Atomic SQLite checkpoint store & state rewind logic
│   ├── mcp_tool_registry.py   # MCP Tool Registry with JSON Schema & HITL permission gates
│   ├── worker_dispatcher.py   # Asyncio Semaphore-bounded Fan-Out / Fan-In worker pool
│   └── agent_orchestrator.py  # Master Workflow Orchestrator & State Machine Engine
├── tests/
│   └── test_agent_runtime.py  # Pytest unit & integration test suite
├── app.py                     # FastAPI REST server & embedded Web Visualizer Dashboard
├── demo_runner.py             # Interactive CLI script running 4 production scenarios
├── requirements.txt           # Project dependencies
├── README.md                  # System documentation
└── INTERVIEW_PREP.md          # Staff/Principal AI Infra Interview Guide
```

---

## 🚦 Quick Start & Interactive Demo

### 1. Run the Interactive CLI Demo
```bash
python3 demo_runner.py
```
This runs 4 core real-world scenarios:
- **Scenario 1**: Normal multi-step task execution with step checkpoints.
- **Scenario 2**: Mid-flight transient failure at Step 2.
- **Scenario 3**: Deterministic Replay (rewinds state and resumes from last checkpoint).
- **Scenario 4**: Human-in-the-Loop approval gate pause & resume.

### 2. Run Pytest Suite
```bash
pytest tests/
```

### 3. Launch FastAPI Server & Web Dashboard
```bash
python3 app.py
```
Then open your browser to **http://127.0.0.1:8000** to view the interactive Task Control Center & Real-Time Timeline Visualizer!