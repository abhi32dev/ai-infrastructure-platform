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
