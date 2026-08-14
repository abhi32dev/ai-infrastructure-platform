# Production Architecture & Design Trade-offs: Model Serving & MLOps Infrastructure

## 1. Executive Context & Business Motivation
Serving traditional MLOps models (e.g. XGBoost, PyTorch classifiers) alongside LLM services requires a standardized model registry, canary deployment rollout engine, and latency/throughput telemetry monitoring.

This system provides a **Production Model Serving & Canary MLOps Engine**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Canary Traffic Shifting vs Blue/Green Hard Cutover
- **Chosen Option**: **Canary Traffic Shifting (e.g. 10% Canary / 90% Stable)**.
- **Alternative Evaluated**: Instant 100% Blue/Green Cutover.
- **Trade-Off Rationale**:
  - *Hard Cutover*: If a new model version has hidden bugs or memory leaks under real production traffic, 100% of users experience outages.
  - *Canary Shifting*: Exposes only 10% of live traffic to the candidate model version while monitoring error rates, automatically rolling back if error metrics spike.

---

## 3. Best Practices & Production Design Principles
1. **Automated Rollback Safeguard**: Triggers immediate rollback if Canary error rate exceeds 1%.
2. **Standardized Model Artifact Versioning**: Hashes model binary weights with SHA-256 for auditability.
3. **Health & Readiness Probes**: Emits Kubernetes `/healthz` and `/readyz` endpoints.

---

## 4. Production Failure Modes & Mitigations
| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Canary Model Crash / Memory Leak** | User error rate spike | Automated traffic drain & rollback to stable version. |
| **Model Weight Artifact Corruption** | Initialization failure | SHA-256 checksum verification on artifact download. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Manages production canary rollouts, distributed OpenTelemetry tracing, and backpressure guards for high-throughput LLM serving clusters.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "prompt": "Summarize quarterly cloud expenditure report.",
  "max_tokens": 256,
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```
**Input Parameter Specification**:
HTTP inference request with prompt payload and optional W3C `traceparent` header.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Ingest & Bind OpenTelemetry Span**: Extracts W3C traceparent headers and initializes root inference span.
- **2. Decision 1 (Worker Queue Backpressure Check)**: Inspects active thread queue depth. If queue depth > 50, rejects immediately with HTTP 429 Too Many Requests to prevent OOM.
- **3. Canary Traffic Split Calculation**: Generates uniform random float [0.0, 1.0] and compares against canary rollout split (10%).
- **4. Decision 2 (Canary vs Baseline Route)**: If roll < 0.10, routes request to candidate Canary v2 container. If roll >= 0.10, routes to stable Baseline v1 container.
- **5. Decision 3 (Health Check Fallback)**: If canary container returns 5xx error or high latency, automatically falls back to baseline v1 instance.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "completion": "Cloud expenditure increased by 4.2% due to GPU cluster reservation.",
  "served_by": "canary-v2-container",
  "status_code": 200,
  "latency_ms": 38.4,
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```
**Output Specification**:
Generated completion text, container instance version served, and trace telemetry context.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 04-model-serving-mlops/tests/test_model_serving.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/04-model-serving-mlops/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/04-model-serving-mlops/FLOWCHART.svg)
