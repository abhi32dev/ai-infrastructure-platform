# 🎤 Staff / Principal AI Infrastructure Interview Guide: Model Serving, RecSys & MLOps Observability

This guide bridges the code in **Project 4 (`04-model-serving-mlops`)** directly to Staff/Principal-level questions asked by FAANG, Tier-1 AI startups, and top product companies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you design a high-throughput recommendation serving system that delivered measured business revenue impact?"
> **Staff Engineer Answer**:
> "In `04-model-serving-mlops`, we built a **Personalized Recommendation Subsystem** ([`src/recsys_engine.py`](src/recsys_engine.py)) combining Matrix Factorization / User-Item Embedding Cosine Similarity with deterministic A/B test variant assignment.
> 
> Incoming user requests are deterministically hashed into either `CONTROL_POPULARITY` or `VARIANT_ML_EMBEDDINGS`. The ML variant scores item relevance by taking the dot product of user latent vectors against item candidate vectors. 
> 
> In production at Smith Micro, this personalized recommendation engine converted behavioral and account telemetry into targeted recommendations, increasing project revenue by **7.4%**, which we validated using $p$-value statistical hypothesis testing."

---

### Q2: "How do you handle backpressure and protect downstream GPU/LLM inference servers under traffic spikes?"
> **Staff Engineer Answer**:
> "Without backpressure isolation, sudden traffic spikes saturate inference workers, increasing queue delays, blowing past latency SLAs, and causing cascading thread memory crashes.
> 
> In our serving architecture ([`src/streaming_proxy.py`](src/streaming_proxy.py)), we implement **Queue Depth Bounding & Load-Shedding**. The proxy tracks active in-flight requests against `max_queue_depth`.
> 
> If incoming request concurrency exceeds capacity, the proxy sheds load immediately by returning an explicit `BACKPRESSURE_QUEUE_FULL` SSE error stream (or HTTP 429). This decouples downstream model workers from sudden traffic bursts, preserving our 99.999% SLA availability for existing active requests."

---

### Q3: "What key telemetry metrics do you track for real-time model serving health?"
> **Staff Engineer Answer**:
> "Traditional HTTP request metrics (like total latency) are insufficient for LLM streaming. We track 4 core MLOps telemetry dimensions ([`src/mlops_metrics.py`](src/mlops_metrics.py)):
> 1. **Time-To-First-Token (TTFT)**: Measures perceived user responsiveness (time elapsed until the first token is emitted).
> 2. **Tokens-Per-Second (TPS)**: Measures inference throughput.
> 3. **P95 / P99 Tail Latencies**: Tracks tail latency SLA compliance (e.g. TTFT $\le 500$ms).
> 4. **Cost Governance ($/Token)**: Accumulates token expenditure in real time.
> 
> We export these metrics in standard **Prometheus Exposition Format**, allowing Grafana and Datadog to trigger automated alerts whenever P99 latency degrades."

---

## 🧪 Quick Test Checklist for Candidates
Run these commands in your workspace to test and demonstrate:
- `python3 demo_runner.py`: Executes all 4 model serving and MLOps scenarios live.
- `pytest tests/`: Verifies unit and integration test suite.
- `python3 app.py`: Opens MLOps Control Dashboard at `http://127.0.0.1:8003` to visually inspect RecSys A/B variants, trigger live SSE token streams, and view Prometheus metric exports.
