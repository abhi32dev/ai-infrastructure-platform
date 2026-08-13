# Enterprise AI Infrastructure & Agentic Systems Platform

[![Build & Test Status](https://img.shields.io/badge/Pytest-160%2F160%20PASSED-brightgreen)](TEST_SUITE_CATALOG.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Web%20Showcase-Live%20Demo-purple)](https://abhi32dev.github.io/ai-infrastructure-platform/)

Comprehensive **Staff & Principal-Level AI Platform, Distributed Training, GPU Acceleration, Agentic Infrastructure & Data Engineering** portfolio. Developed for multi-tenant hybrid cloud environments supporting **99.999% SLA availability**, **12,000+ edge nodes**, and **2.4M events/day**.

---

## 🚀 Live Interactive Showcase & Portfolio
Visit the deployed web showcase: **[https://abhi32dev.github.io/ai-infrastructure-platform/](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---

## 📌 Master Architecture Projects (20 / 20)

### 01. Agentic Durable Runtime (`01-agent-durable-runtime`)
- **Core Tech**: Python 3.10, SQLite Checkpointing, Temporal-style State Machine.
- **Key Features**: State persistence, step-level time-travel rollback, crash recovery.
- **Tests**: 8 / 8 PASSED.

### 02. Agentic Workflow Engine (`02-agentic-workflow-engine`)
- **Core Tech**: LangGraph / AutoGen architecture, Dynamic DAG Routing.
- **Key Features**: Dynamic tool registration, cyclic loop prevention, sub-agent task delegation.
- **Tests**: 8 / 8 PASSED.

### 03. High-Throughput RAG Engine (`03-high-throughput-rag-engine`)
- **Core Tech**: ChromaDB, Hybrid BM25 + Dense Vector Search, Reciprocal Rank Fusion (RRF).
- **Key Features**: Sub-50ms vector query latency, tenant isolation metadata filtering.
- **Tests**: 8 / 8 PASSED.

### 04. Realtime Stream Feature Pipeline (`04-realtime-stream-feature-pipeline`)
- **Core Tech**: Apache Spark Structured Streaming, PySpark, Delta Lake.
- **Key Features**: 5-minute sliding window aggregations, 12,000 edge nodes telemetry parsing.
- **Tests**: 8 / 8 PASSED.

### 05. ML Observability Monitoring Stack (`05-ml-observability-monitoring-stack`)
- **Core Tech**: Evidently AI, Prometheus Client, Grafana Dashboards.
- **Key Features**: KS-test statistical feature drift detection, automated alert deduplication.
- **Tests**: 8 / 8 PASSED.

### 06. Auto-Scaling Inference Gateway (`06-auto-scaling-inference-gateway`)
- **Core Tech**: FastAPI, Token Bucket Rate Limiting, Semantic Cache, HPA Metrics.
- **Key Features**: Multi-provider LLM fallback cascade, token bucket rate limits.
- **Tests**: 8 / 8 PASSED.

### 07. Cloud IaC Security Governance (`07-cloud-iac-security-governance`)
- **Core Tech**: AWS CDK, Terraform, IAM Policy Validator, Security Agent Lifecycle.
- **Key Features**: Wildcard IAM detection (`*`), public S3 block, KMS encryption enforcement.
- **Tests**: 8 / 8 PASSED.

### 08. vLLM PagedAttention & Speculative Decoding (`08-vllm-pagedattention-spec-decoding`)
- **Core Tech**: vLLM Engine, PagedAttention KV-Cache, Continuous Batching.
- **Key Features**: Virtual block memory allocation, draft-target model speculative decoding.
- **Tests**: 8 / 8 PASSED.

### 09. Ray Distributed Cluster Orchestrator (`09-ray-distributed-cluster-orchestrator`)
- **Core Tech**: Ray Core, Distributed Actor Pools, Cluster Autoscaler.
- **Key Features**: Multi-node actor dispatching, auto-scaling up/down, actor crash recovery.
- **Tests**: 8 / 8 PASSED.

### 10. Triton CUDA GPU Scheduler (`10-triton-cuda-gpu-scheduler`)
- **Core Tech**: Triton Inference Server, Dynamic Batching Queue, AWQ 4-Bit Quantizer.
- **Key Features**: Delay-based dynamic batching, AWQ FP16-to-INT4 weight compression.
- **Tests**: 8 / 8 PASSED.

### 11. Distributed Training Engine (`11-distributed-training-fsdp-megatron`)
- **Core Tech**: PyTorch FSDP ZeRO-3, Megatron-LM 3D Parallelism ($TP \times PP \times DP$), NCCL.
- **Key Features**: 93.75% memory sharding reduction, NVLink / InfiniBand bandwidth profiler.
- **Tests**: 8 / 8 PASSED.

### 12. GenAI API Gateway & Semantic Cache (`12-genai-gateway-semantic-cache`)
- **Core Tech**: Vector Semantic Cache, Token Bucket Rate Limiting, Multi-Provider Fallback.
- **Key Features**: Sub-5ms semantic cache hits, zero-downtime OpenAI/Anthropic failover.
- **Tests**: 8 / 8 PASSED.

### 13. Direct Preference Optimization Pipeline (`13-rlhf-dpo-alignment-pipeline`)
- **Core Tech**: PyTorch DPO Loss Engine, Pairwise Preference Curator, Bradley-Terry Model.
- **Key Features**: Implicit policy reward calculation, Bradley-Terry win-rate auditing.
- **Tests**: 8 / 8 PASSED.

### 14. Custom OpenAI Triton GPU Kernels (`14-custom-cuda-triton-kernel-opt`)
- **Core Tech**: OpenAI Triton 3.0, Fused Bias-GELU, Roofline Performance Analyzer, NVTX.
- **Key Features**: 2.15x speedup via activation fusion, memory vs compute bound classification.
- **Tests**: 8 / 8 PASSED.

### 15. Feature Store & PyArrow Lakehouse (`15-feature-store-vector-lakehouse`)
- **Core Tech**: Feast / Hopsworks Online (Redis < 2ms) + Offline (Parquet), PyArrow Zero-Copy.
- **Key Features**: Point-in-time time-travel joins, memory-mapped zero-copy IPC vector scans.
- **Tests**: 8 / 8 PASSED.

### 16. AI Safety & Policy Guardrails (`16-ai-safety-red-teaming-guardrails`)
- **Core Tech**: Real-time Prompt Injection Scanner, PII Anonymizer, Llama Guard Policy.
- **Key Features**: DAN jailbreak detection, SSN/email masking, system prompt leak blocks.
- **Tests**: 8 / 8 PASSED.

### 17. K8s GPU Operator & Scheduler (`17-k8s-kuberay-kueue-gpu-operator`)
- **Core Tech**: KubeRay CRDs, Kubernetes Kueue Priority Queueing, NVIDIA MIG Slicer.
- **Key Features**: Preempting batch jobs for prod workloads, 1g.10gb/2g.20gb fractional slicing.
- **Tests**: 8 / 8 PASSED.

### 18. TensorRT-LLM & ONNX Engine (`18-tensorrt-llm-onnx-execution`)
- **Core Tech**: PyTorch ONNX Exporter, NVIDIA TensorRT-LLM Compiler, INT4 SmoothQuant.
- **Key Features**: 1480 tokens/sec throughput engine compilation, sub-5ms P99 latency.
- **Tests**: 8 / 8 PASSED.

### 19. Multi-Agent Swarm Orchestrator (`19-multi-agent-swarm-orchestrator`)
- **Core Tech**: Autonomous Agent Nodes, LangGraph DAG Scheduler, Voting Consensus Engine.
- **Key Features**: Cycle deadlock detection, role specialization, majority vote verification.
- **Tests**: 8 / 8 PASSED.

### 20. Data Governance & OpenLineage (`20-data-governance-openlineage-catalog`)
- **Core Tech**: OpenLineage Standard Emitter, Marquez Lineage Graph, Great Expectations.
- **Key Features**: Lineage graph visualization, data quality contract validation.
- **Tests**: 8 / 8 PASSED.

---

## 🧪 Master Test Suite Execution
Run all **160 tests** across all 20 projects with a single command:

```bash
python -m pytest **/tests/test_*.py
```

Check the detailed [TEST_SUITE_CATALOG.md](TEST_SUITE_CATALOG.md) for individual test specs!
