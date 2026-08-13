# Production Architecture & Design Trade-offs: GenAI API Gateway & Semantic Cache

## 1. Executive Context & Business Motivation
Enterprise Generative AI gateways serving multiple business units must enforce token budget SLAs, protect downstream model providers from DDoS surges, and optimize costs by avoiding redundant LLM API calls.

This architecture provides a **Vector Semantic Caching Layer (<5ms responses), Token Bucket Rate Limiter, and Multi-Provider Fallback Cascade**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Vector Semantic Cache vs Keyword / Hash Cache
- **Chosen Option**: **Vector Embedding Semantic Similarity Match (>0.85 Threshold)**.
- **Alternative Evaluated**: MD5 / SHA-256 Exact Hash Caching.
- **Trade-Off Rationale**:
  - *Hash Caching*: Misses semantically identical user queries with trivial formatting variations.
  - *Vector Semantic Caching*: Computes embedding similarity between incoming prompts and historical queries. Returns cached responses in <5ms, saving 100% of LLM token costs.

### B. Multi-Provider Fallback Router Cascade
- **Chosen Option**: **Automated Fallback Cascade (OpenAI $\rightarrow$ Anthropic $\rightarrow$ Local Ollama)**.
- **Trade-Off Rationale**: Guarantees zero-downtime availability even during major commercial LLM provider outages.

---

## 3. Best Practices & Production Design Principles

1. **Token Bucket Rate Limiting (TPM/RPM)**:
   - Prevents tenant budget overruns using token-refill rate math.
2. **Graceful HTTP 429 Retry-After Calculation**:
   - Emits precise `retry_after_sec` values when bucket thresholds are breached.
3. **Cache Entry Freshness & TTL**:
   - Evicts stale cached responses after configurable TTL intervals.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Primary Provider Outage (HTTP 500/503)** | API downtime | Failover cascade automatically redirects traffic to secondary provider in <50ms. |
| **Tenant Token Over-consumption** | Budget overrun / GPU OOM | Token bucket rate limiter returns immediate HTTP 429. |
| **Vector DB Cache Miss Spike** | Latency degradation | Asynchronous cache write-backs ensure user response is never blocked by cache insertion. |
