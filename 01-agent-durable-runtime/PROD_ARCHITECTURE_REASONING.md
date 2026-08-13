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
