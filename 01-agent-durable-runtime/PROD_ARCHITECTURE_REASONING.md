# Production Architecture & Design Trade-offs: Agentic Durable Runtime

## 1. Executive Context & Business Motivation
In autonomous AI agent systems executing complex multi-step tasks (e.g. multi-hour code generation, infrastructure provisioning, complex workflows), process crashes, network disconnects, or deployment restarts frequently wipe out transient in-memory state. Re-executing an entire LLM agent workflow from scratch incurs severe costs (token overhead, latency penalties) and causes non-idempotent side effects.

This component provides a **durable, fault-tolerant execution engine** with deterministic state checkpointing and step-level time-travel rollback capabilities.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. SQLite State Store vs In-Memory / Redis vs PostgreSQL
- **Chosen Option**: **SQLite / Embedded Relational Checkpoint Engine** (WAL Mode).
- **Alternative Evaluated**: Redis / In-memory state dicts.
- **Trade-Off Rationale**:
  - *In-Memory/Redis*: In-memory dictionaries lose all state on process termination. Redis adds network hop overhead (~1-5ms) and operational cluster maintenance complexity for local worker tasks.
  - *SQLite*: Provides zero-network overhead (<0.2ms writes), atomic ACID transactions (`BEGIN IMMEDIATE`), single-file portability, and WAL (Write-Ahead Logging) concurrency.
  - *Trade-off*: SQLite cannot scale writes across multi-master nodes without LiteFS/rqlite, but for single-agent durable runtimes, local embedded transactions eliminate network latency and single-point-of-failure network outages.

### B. Full State Snapshots vs Event Sourcing Delta Logs
- **Chosen Option**: **Hybrid State Snapshot + Event Log**.
- **Trade-Off Rationale**: Replaying thousands of granular log events to reconstruct state takes $O(N)$ time on recovery. Snapshots store complete state dicts at every step boundary, enabling $O(1)$ instant recovery and step-level time-travel rollback.

---

## 3. Best Practices & Production Design Principles

1. **Null & Malformed Payload Resilience**:
   - Defensive schema parsing on state recovery. Unreadable or corrupted JSON checkpoints trigger automatic fallbacks to the last verified healthy checkpoint step rather than crashing worker threads.
2. **Deterministic Step ID Generation**:
   - Prevents duplicate state writes during network retries by generating deterministic UUIDv5 step keys derived from `(workflow_id, step_index)`.
3. **Graceful Degradation & WAL Checkpointing**:
   - Uses SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL`) to allow non-blocking concurrent reads while state checkpoints are being committed.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Worker Process Crash Mid-Execution** | In-memory state lost | Engine reads latest checkpoint from SQLite on boot and resumes from exact step index. |
| **Corrupted SQLite Database File** | Read query failure | Fallback to safe initial state + database integrity check (`PRAGMA quick_check`). |
| **Concurrent Write Contention** | `database is locked` error | Busy timeout configuration (`timeout=10.0`s) + exponential backoff retry. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Provides crash-resilient execution for autonomous AI agent workflows. If an agent worker terminates unexpectedly during a 4-hour task, this engine restores state from SQLite WAL checkpoints and resumes without re-running completed steps or wasting LLM tokens.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "workflow_id": "wf-agent-9921",
  "step_index": 3,
  "step_name": "query_analytics_database",
  "step_input": {"sql": "SELECT SUM(tokens) FROM usage_logs WHERE date >= '2026-01-01'"}
}
```
**Input Parameter Specification**:
A JSON payload containing `workflow_id` (string), `step_index` (int), `step_name` (string), and `step_input` (dict with tool arguments).

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Ingest Payload & Validate Schema**: Ingests the step payload and verifies field types against Pydantic schema.
- **2. Decision 1 (Check Idempotency in WAL)**: Queries SQLite WAL database using deterministic UUIDv5 hash. If already executed (Cache Hit), immediately replays cached state ($0.00 compute). If new, proceeds to execution.
- **3. Invoke Tool / Action**: Executes the external agent action or LLM call via `DurableAgentRuntime._invoke_tool()`.
- **4. Decision 2 (Check Execution Status)**: If invocation succeeded without unhandled exceptions, writes an atomic WAL checkpoint transaction and advances workflow state offset.
- **5. Decision 3 (Exception & Retry Boundary)**: If an exception occurred (e.g. API timeout), checks retry counter (< 3 attempts). If valid, rewinds state machine to last valid checkpoint with exponential backoff (2.0s). If retries exhausted, halts workflow and routes payload to Human-In-The-Loop (HITL) review queue.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "status": "COMPLETED",
  "workflow_id": "wf-agent-9921",
  "step_index": 3,
  "checkpoint_id": "chk_8a7f92b1",
  "state_delta": {"rows_retrieved": 1420, "cached": false},
  "latency_ms": 142.5
}
```
**Output Specification**:
A serialized checkpoint record containing execution status, execution duration, and persisted state delta.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 01-agent-durable-runtime/tests/test_agent_runtime.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/01-agent-durable-runtime/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/01-agent-durable-runtime/FLOWCHART.svg)
