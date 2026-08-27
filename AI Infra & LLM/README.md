# Enterprise AI Infrastructure & LLM Serving Platform (Local-First)

Modular monorepo monikered `nexus-ai-infra` designed to run high-throughput candidate evaluation, context compression retrieval (RAG), and performance latency sweeps directly on Apple Silicon macOS/Metal.

---

## 🏗️ Repository Layout

```
AI Infra & LLM/
├── docker/
│   └── docker-compose.yml         # Qdrant DB, Langfuse dashboard, Postgres
├── config/
│   ├── app_config.json            # Central system settings
│   └── models/                    # Model templates and options
├── src/
│   ├── common/                    # Pydantic Settings & JSON loggers
│   ├── serving/                   # Subprocess managers & SSE stream timers (TTFT)
│   ├── benchmarks/                # Load generator engines & statistical percentiles
│   ├── retrieval/                 # Two-stage vector search & Cross-Encoder pipelines
│   └── gateway/                   # FastAPI gateway & telemetry traces
├── tests/
│   ├── unit/                      # 12 isolated Pytest targets
│   └── integration/               # End-to-end flow verifications
└── scripts/
    ├── setup_env.sh               # Environment boots and preloads
    └── run_benchmarks.sh          # Concurrency sweeps load test runner
```

---

## 🚀 Step-by-Step Developer Operations Guide

### 1. Bootstrapping Dependencies
Run the bootstrap setup script to generate the virtualenv, install dependencies, and download quantized weights:
```bash
./scripts/setup_env.sh
```

### 2. Running Concurrency Sweeps (Load Tester)
Run standard sweeps over $N \in \{1, 2, 4, 8, 16, 32\}$ concurrent clients:
```bash
./scripts/run_benchmarks.sh
```

### 3. Launching Gateway Microservice
Start the FastAPI server:
```bash
.venv/bin/uvicorn src.gateway.main:app --reload --port 8000
```
- Interactive Swagger docs will be exposed at: `http://localhost:8000/docs`

---

## 🧪 Automated Testing
Run the Pytest suite verifying serving fallovers, chunk overlaps, and telemetry span recording:
```bash
.venv/bin/pytest
```
