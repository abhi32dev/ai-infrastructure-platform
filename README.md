# 🚀 Master Enterprise AI/ML Infrastructure & High-Demand Systems Portfolio

A comprehensive, production-grade suite of **10 local-first AI Infrastructure, Inference Optimization (vLLM, Ray, Triton), Fine-Tuning, MLOps, Enterprise Guardrails, and Distributed Systems projects**.

Every project includes both **local zero-friction `.venv` execution** and **real, containerized Docker & Kubernetes production infrastructure**.

---

## 🐳 Real Containerization & Kubernetes Architecture (`docker-k8s/` & `k8s/`)

Unlike mock tutorials, this portfolio features **real, production-grade containerization and Kubernetes orchestration files**:

1. **Per-Project Production Dockerfiles**: Every single one of the 10 project directories contains an explicit production `Dockerfile` (`01-agent-durable-runtime/Dockerfile`, etc.).
2. **Real Agent-to-Agent MCP HTTP Socket Server**: Project 1 includes a live REST / JSON-RPC 2.0 socket server (`POST /mcp`) and [`mcp_peer_node_2.py`](01-agent-durable-runtime/mcp_peer_node_2.py) subagent node communicating over HTTP sockets across containers.
3. **Master Kubernetes Deployment Suite (`k8s/`)**:
   - `00-namespace-and-configs.yaml`: K8s Namespace (`ai-platform`), ConfigMaps, Secrets, RBAC.
   - `01-agent-runtime-k8s.yaml`: K8s Deployment (2 replicas), Service & PVC.
   - `04-model-serving-mlops-k8s.yaml`: K8s Deployment with OpenTelemetry Collector Sidecar Container.
   - `08-vllm-engine-k8s.yaml`: K8s vLLM Deployment with NVIDIA GPU limits & HPA.
   - `09-ray-kuberay-cluster.yaml`: KubeRay CRD defining RayHead and 4 RayWorker Pods.
   - `10-triton-server-k8s.yaml`: NVIDIA Triton Inference Server K8s StatefulSet with `/dev/shm` IPC volume.
   - `deploy-k8s-cluster.sh`: Executable deployment script.

To launch all containers via Docker Compose:
```bash
cd docker-k8s && docker-compose up --build
```

To apply Kubernetes manifests to your EKS / GKE / Minikube cluster:
```bash
cd k8s && ./deploy-k8s-cluster.sh
```

---

## 🏛️ Master 10-Project Portfolio Matrix

| Project Directory | Core Architecture & System Concepts | Enterprise & Real Container Artifacts | Primary Frameworks | Isolated Local Command |
| :--- | :--- | :--- | :--- | :--- |
| [`01-agent-durable-runtime`](01-agent-durable-runtime/) | Multi-Step Agent Orchestration, SQLite Checkpointing, Replay | **Real REST MCP Agent-to-Agent Socket Server (`POST /mcp`)**, `mcp_peer_node_2.py`, PII Redaction, `Dockerfile` | Python, FastAPI, Asyncio, Pytest | `.venv/bin/python demo_runner.py` |
| [`02-rag-cost-router`](02-rag-cost-router/) | 7-Stage RAG Pipeline, Dense ChromaDB + BM25, Cross-Encoder | **FinOps Model Cost Router**, Token Budget Enforcement, `Dockerfile` | ChromaDB, SentenceTransformers, FastAPI | `.venv/bin/python demo_runner.py` |
| [`03-llm-eval-gate`](03-llm-eval-gate/) | Multi-Model LLM-as-a-Judge, MLflow Tracking, P-Value Gate | **RAG Triad Evals** (Context Precision, Recall, Faithfulness), `Dockerfile` | MLflow, SciPy, Ollama API, FastAPI | `.venv/bin/python demo_runner.py` |
| [`04-model-serving-mlops`](04-model-serving-mlops/) | RecSys Matrix Factorization (7.4% lift), A/B Testing, SSE Proxy | **OpenTelemetry W3C Distributed Tracing**, Prometheus Exporter, K8s Sidecar Pod, `Dockerfile` | FastAPI, Scikit-Learn, OpenTelemetry | `.venv/bin/python demo_runner.py` |
| [`05-event-stream-pyspark-etl`](05-event-stream-pyspark-etl/) | MIB OID Packet Decoder, Persistent UDP Trap Receiver, PySpark | High-Throughput Ingestion Observability, 3-Pass Reconciliation, `Dockerfile` | PySpark, Pandas, FastAPI, Pytest | `.venv/bin/python demo_runner.py` |
| [`06-finetuning-lora-alignment`](06-finetuning-lora-alignment/) | SFT Instruction Dataset Curation, LoRA PEFT ($r=8, \alpha=16$) | Loss Convergence & Perplexity Tracking, GGUF Edge Model Export, `Dockerfile` | PyTorch, Transformers, FastAPI | `.venv/bin/python demo_runner.py` |
| [`07-cloud-iac-security-governance`](07-cloud-iac-security-governance/) | Multi-Account AWS CDK Stack Generator (Dev, QA, Stage, Prod) | **Least-Privilege Static IAM Policy Validator**, EC2 Security Monitoring, `Dockerfile` | AWS CDK, Constructs, FastAPI | `.venv/bin/python demo_runner.py` |
| [`08-vllm-pagedattention-spec-decoding`](08-vllm-pagedattention-spec-decoding/) | PagedAttention GPU Block Allocator, 0.0% VRAM Fragmentation | **Speculative Decoding** (1B Draft + 70B Target Parallel Pass), K8s GPU HPA Manifest, `Dockerfile` | PyTorch, PagedAttention, FastAPI | `.venv/bin/python demo_runner.py` |
| [`09-ray-distributed-cluster-orchestrator`](09-ray-distributed-cluster-orchestrator/) | Stateful Ray Actor Worker Pool, Plasma Zero-Copy Shared Memory | **Multi-GPU Cluster Dynamic Autoscaler**, KubeRay Cluster CRD Manifest, `Dockerfile` | Ray Core, Ray Serve, FastAPI | `.venv/bin/python demo_runner.py` |
| [`10-triton-cuda-gpu-scheduler`](10-triton-cuda-gpu-scheduler/) | NVIDIA Triton Dynamic Batching Queue, Power-of-2 CUDA Alignment | **AWQ FP8/INT8 Weight Matrix Quantization**, Triton K8s StatefulSet Manifest, `Dockerfile` | Triton Spec, NumPy, SciPy, FastAPI | `.venv/bin/python demo_runner.py` |

---

## 🚦 Quick Start Guide

```bash
# Run the full 80-test suite across all 10 projects:
cd /Users/abhi/Documents/Antigravity
for dir in 0*; do echo "=== TESTING $dir ==="; (cd "$dir" && PYTHONPATH=. .venv/bin/pytest tests/); done
```
> 📄 Detailed test catalog and verification matrix: [`TEST_SUITE_CATALOG.md`](TEST_SUITE_CATALOG.md)

---

## 🌐 Publishing to GitHub Pages (`github.io`)

```bash
git init
git add .
git commit -m "feat: Master 10-project AI/ML Infrastructure, Docker & Kubernetes portfolio"
git branch -M main
git remote add origin git@github.com:singh-abhi/ai-infra-portfolio.git
git push -u origin main
```
Then enable **GitHub Pages** under repository settings pointing to `main` branch / root `README.md` to host your showcase live at `https://singh-abhi.github.io/ai-infra-portfolio/`!
