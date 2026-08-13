# Production Architecture & Design Trade-offs: Auto-Scaling Inference Gateway

## 1. Executive Context & Business Motivation
In multi-tenant LLM inference deployments, unthrottled API requests can exhaust GPU memory, cause HTTP 504 timeouts, and drive up API infrastructure costs. An enterprise inference gateway must protect backend models via rate limiting, reduce duplicate query computation via semantic caching, and emit autoscaling signals to Kubernetes HPA.

This component implements a **FastAPI Auto-Scaling Inference Gateway with Token Bucket Limits & Vector Semantic Cache**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Token Bucket Algorithm vs Leaky Bucket / Fixed Window
- **Chosen Option**: **Token Bucket Rate Limiter**.
- **Alternative Evaluated**: Fixed Window Rate Limiting.
- **Trade-Off Rationale**:
  - *Fixed Window*: Allows double-burst traffic at window boundary transitions (e.g. 100 requests at 00:59, 100 requests at 01:01).
  - *Token Bucket*: Smoothes traffic over time while allowing short burst capacity up to max TPM limits.

### B. Redis Vector Semantic Cache vs Exact String Match Cache
- **Chosen Option**: **Vector Semantic Cache (>0.92 Similarity Threshold)**.
- **Trade-Off Rationale**: Exact string match misses queries with slight phrasing differences (e.g., "What is vLLM?" vs "Explain vLLM"). Vector similarity matching returns cached LLM responses in <5ms, saving 100% of LLM token costs on duplicate intent queries.

---

## 3. Best Practices & Production Design Principles

1. **HTTP 429 Retry-After Headers**:
   - Computes exact `retry_after_sec` values based on token bucket refill rates when client quotas are exceeded.
2. **Provider Failover Cascade**:
   - Automatically attempts secondary LLM providers (e.g., OpenAI $\rightarrow$ Anthropic) on HTTP 5xx errors or timeouts.
3. **Custom Kubernetes HPA Metrics**:
   - Emits custom metrics (`inference_queue_depth`, `gpu_duty_cycle`) for Kubernetes Horizontal Pod Autoscaler.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Primary LLM Provider Outage** | Complete API downtime | Automated multi-provider fallback router. |
| **Token Exhaustion Surge** | GPU OOM / System Crash | Token bucket rate limiter returns immediate HTTP 429. |
| **Cache Stale Data** | Outdated answers returned | TTL expiration on semantic cache entries. |
