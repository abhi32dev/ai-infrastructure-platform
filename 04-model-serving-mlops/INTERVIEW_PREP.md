# 🎤 Staff AI Platform Interview Guide: High-Throughput Model Serving & Observability

This guide bridges **Project 4 (`04-model-serving-mlops`)** to Staff/Principal-level questions on production serving and OpenTelemetry.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you implement canary deployments for model serving clusters?"
> **Staff Engineer Answer**:
> "In `src/streaming_proxy.py`, we route a configurable percentage (e.g. 10%) of incoming inference requests to candidate canary containers while sending 90% to stable baseline instances, monitoring real-time error rates and P99 latency."

### Q2: "How do you maintain distributed request tracing across microservices using OpenTelemetry?"
> **Staff Engineer Answer**:
> "In `src/recsys_engine.py`, we extract W3C `traceparent` headers, bind spans to incoming inference requests, and export traces to OpenTelemetry collectors, capturing per-layer compute latency."

### Q3: "How does backpressure shedding protect model serving nodes from OOM crashes?"
> **Staff Engineer Answer**:
> "When active worker thread queues exceed maximum capacity (>50 requests), the gateway immediately returns HTTP 429 Too Many Requests, preventing GPU VRAM exhaustion."
