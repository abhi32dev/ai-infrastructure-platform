import os

base_dir = "/Users/abhi/Documents/Antigravity"

project_interview_data = {
    "01-agent-durable-runtime": """# 🎤 Staff AI Platform & Agent Systems Interview Guide (MCP & Guardrails Standard)

This guide bridges the code in **Project 1 (`01-agent-durable-runtime`)** directly to Staff/Principal-level questions asked by Anthropic, OpenAI, Meta AI, and Google DeepMind.

---

## 💡 Tech Community Requirements at Staff AI Level
Autonomous Agent Infrastructure requires robust protocol standards and safety guardrails:
1. **Model Context Protocol (MCP)**: The industry-standard JSON-RPC 2.0 protocol for agent tool discovery and prompt templates.
2. **Durable Step Checkpointing**: Atomic SQLite WAL step checkpoints enabling $O(1)$ crash recovery and step rewinds.
3. **Enterprise Guardrails**: Pre-execution PII redaction and prompt injection defense.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Model Context Protocol (MCP) enable standardized Agent-to-Agent (A2A) tool discovery?"
> **Staff Engineer Answer**:
> "In `01-agent-durable-runtime` (`src/mcp_tool_registry.py`), we implement Anthropic's **Model Context Protocol (MCP)** over JSON-RPC 2.0. Agents negotiate protocol capabilities (`tools`, `prompts`) and dynamically query peer tool definitions using JSON Schema, decoupling agent logic from vendor APIs."

### Q2: "How do you enforce PII redaction and prompt injection defense in autonomous agent workflows?"
> **Staff Engineer Answer**:
> "Before any prompt reaches an LLM or tool, multi-layered guardrails scan for jailbreak patterns (`DAN`, `ignore previous instructions`) and regex-redact sensitive SSNs, emails, and API keys (`sk-*`) into `[REDACTED]` tokens."

### Q3: "How does SQLite step checkpointing guarantee deterministic replay and state recovery?"
> **Staff Engineer Answer**:
> "In `src/checkpoint_store.py`, we record atomic SQLite WAL transactions at each step boundary (`PENDING`, `CHECKPOINTED`, `COMPLETED`). If a worker crashes at step 4, the runtime reads the latest snapshot and resumes without wasting LLM tokens on steps 1–3."
""",

    "02-rag-cost-router": """# 🎤 Staff AI Platform Interview Guide: RAG Cost Router & Semantic Cache

This guide bridges **Project 2 (`02-rag-cost-router`)** directly to Staff/Principal-level questions asked by Databricks, Pinecone, and OpenAI.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you reduce enterprise LLM inference bills by 80%+ without degrading response quality?"
> **Staff Engineer Answer**:
> "In `02-rag-cost-router` (`src/cost_aware_router.py`), we implement a 3-tier routing architecture:
> 1. **Semantic Vector Cache**: Exact/semantic hits ($\ge 0.95$ cosine similarity) are served instantly from ChromaDB in $<5\\text{ms}$ at $\\$0.00$ cost.
> 2. **Local SLM Routing**: Low-complexity queries (syntactic score $\le 0.40$) route to local Ollama Llama-3-8B instances.
> 3. **Frontier Model Cascade**: Only high-complexity queries route to frontier models (Claude 3.5 Sonnet)."

### Q2: "How do you combine dense vector search with sparse keyword search effectively?"
> **Staff Engineer Answer**:
> "In `src/hybrid_retriever.py`, we compute dense HNSW vector similarity and BM25 sparse keyword scores, fusing rank orders using Reciprocal Rank Fusion (RRF): $\\text{RRF}(d) = \\sum_{m \\in M} \\frac{1}{k + r_m(d)}$. A Cross-Encoder reranker selects the top 3 passages."

### Q3: "What is the primary failure mode of vector semantic caching, and how is it mitigated?"
> **Staff Engineer Answer**:
> "Semantic false positives occur when prompts share structure but differ in entities (e.g. 'Apple revenue in 2023' vs '2024'). We mitigate this by extracting temporal and named entities before cache lookup, forcing a cache miss if entity values diverge."
""",

    "03-llm-eval-gate": """# 🎤 Staff AI Platform Interview Guide: LLM Evaluation Gate & Statistical CI/CD

This guide bridges **Project 3 (`03-llm-eval-gate`)** to Staff/Principal-level questions on continuous model evaluation and statistical validation.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is mean accuracy insufficient for model deployment gates, and why is Welch's t-test mandatory?"
> **Staff Engineer Answer**:
> "LLM generations are non-deterministic. A candidate model scoring $84\\%$ vs baseline $82\\%$ over small sample sets may reflect random noise. In `src/statistical_gate.py`, we compute Welch's two-sample t-test ($p < 0.05$) to prove statistical significance before promoting candidate weights in MLflow."

### Q2: "How do you measure Faithfulness, Answer Relevance, and Groundedness (RAG Triad)?"
> **Staff Engineer Answer**:
> "In `src/eval_rubrics.py`, we evaluate:
> 1. **Faithfulness**: Proportion of generated claims supported by retrieved context.
> 2. **Answer Relevance**: Semantic cosine alignment between query and response.
> 3. **Groundedness**: Ratio of hallucinated tokens to verified reference citations."

### Q3: "How do automated toxicity classifiers prevent harmful model releases in CI/CD?"
> **Staff Engineer Answer**:
> "In `src/llm_as_judge.py`, candidate responses are evaluated across toxicity rubrics. If the toxicity score exceeds $0.05$, the deployment pipeline halts and alerts the ML platform team."
""",

    "04-model-serving-mlops": """# 🎤 Staff AI Platform Interview Guide: High-Throughput Model Serving & Observability

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
""",

    "05-event-stream-pyspark-etl": """# 🎤 Staff AI Platform Interview Guide: Event Stream PySpark ETL & Delta Lake

This guide bridges **Project 5 (`05-event-stream-pyspark-etl`)** to Staff/Principal-level questions on streaming architectures and Delta Lake ACID transactions.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you handle late-arriving streaming data and deduplication in PySpark Structured Streaming?"
> **Staff Engineer Answer**:
> "In `src/event_pipeline.py`, we apply a 10-minute event watermark boundary (`withWatermark('event_timestamp', '10 minutes')`). Late records past the watermark are dropped, and `dropDuplicates(['event_id'])` eliminates duplicate events."

### Q2: "How do Delta Lake Gold tables enforce ACID transaction guarantees during streaming ingestion?"
> **Staff Engineer Answer**:
> "Delta Lake uses atomic commit logs (`_delta_log/`) with optimistic concurrency control. Each streaming micro-batch commits atomically as a new version snapshot, preventing partial reads."

### Q3: "How do you isolate corrupted telemetry payloads without halting streaming jobs?"
> **Staff Engineer Answer**:
> "Records failing schema validation are routed to an S3 Dead-Letter Queue (DLQ) bucket, allowing healthy micro-batches to commit while quarantined records trigger OpenLineage alerting."
""",

    "06-finetuning-lora-alignment": """# 🎤 Staff AI Platform Interview Guide: PEFT LoRA Fine-Tuning & Quantized Export

This guide bridges **Project 6 (`06-finetuning-lora-alignment`)** to Staff/Principal-level questions on parameter-efficient fine-tuning.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does LoRA reduce trainable parameter count by 99%+, and what are the mathematical mechanics?"
> **Staff Engineer Answer**:
> "In `src/lora_trainer.py`, base model weights $W_0 \\in \\mathbb{R}^{d \\times k}$ are frozen. We inject low-rank decomposition matrices $A \\in \\mathbb{R}^{r \\times k}$ and $B \\in \\mathbb{R}^{d \\times r}$ ($r=8$). Forward pass compute is $h = W_0 x + \\frac{\\alpha}{r} B A x$, reducing trainable parameters from 8B to 16.8M."

### Q2: "How do you prevent overfitting and compute waste during fine-tuning?"
> **Staff Engineer Answer**:
> "We monitor validation loss derivatives across evaluation intervals. If validation loss plateaus for 3 consecutive checkpoints, early stopping terminates training and fuses adapter weights back into the base model."

### Q3: "How do you export fine-tuned models for edge and on-device deployment?"
> **Staff Engineer Answer**:
> "We export fused weights to GGUF quantized formats (Q4_K_M, Q8_0), reducing model memory footprint from 16GB FP16 down to 4.2GB for low-latency inference on local nodes."
""",

    "07-cloud-iac-security-governance": """# 🎤 Staff AI Platform Interview Guide: Cloud IaC Security Governance & AST Analysis

This guide bridges **Project 7 (`07-cloud-iac-security-governance`)** to Staff/Principal-level questions on automated cloud infrastructure security.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you prevent overly permissive IAM policies in CI/CD before infrastructure deployment?"
> **Staff Engineer Answer**:
> "In `src/cloud_governance.py`, we parse synthesized AWS CDK and CloudFormation Abstract Syntax Trees (AST). Any IAM policy containing wildcard actions (`Action: '*'`) or wildcard principals triggers a critical security build failure."

### Q2: "How do you enforce mandatory customer-managed encryption (KMS) on all cloud storage buckets?"
> **Staff Engineer Answer**:
> "The AST evaluator inspects S3 bucket property nodes. If `ServerSideEncryptionConfiguration` is missing or uses default keys, CDK Aspects inject customer-managed KMS key policies automatically."

### Q3: "How are infrastructure compliance findings exported for enterprise SOC auditing?"
> **Staff Engineer Answer**:
> "Violations are exported in standardized SARIF (Static Analysis Results Interchange Format) JSON format, integrating with GitHub Advanced Security and Datadog Compliance monitors."
""",

    "08-vllm-pagedattention-spec-decoding": """# 🎤 Staff AI Platform Interview Guide: vLLM PagedAttention & Speculative Decoding

This guide bridges **Project 8 (`08-vllm-pagedattention-spec-decoding`)** to Staff/Principal-level questions on LLM serving engine internals.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does PagedAttention eliminate VRAM memory fragmentation?"
> **Staff Engineer Answer**:
> "In `src/paged_kv_cache.py`, traditional contiguous KV cache allocation wastes up to 80% of VRAM. PagedAttention partitions the cache into 16-token physical blocks, mapping logical sequence tokens to non-contiguous physical blocks via a Block Table, reducing memory waste to $<4\\%$."

### Q2: "How does Speculative Decoding achieve 2.67x generation speedup?"
> **Staff Engineer Answer**:
> "In `src/speculative_decoder.py`, a lightweight 1B draft model speculates $K=4$ candidate tokens. The 70B target model verifies all 4 tokens in a single parallel forward pass. Accepted tokens advance generation position by $K$ steps simultaneously."

### Q3: "What is continuous iteration-level batching?"
> **Staff Engineer Answer**:
> "In `src/continuous_batcher.py`, new requests enter the active iteration batch immediately upon arrival, while completed sequences release their physical blocks at token boundaries."
""",

    "09-ray-distributed-cluster-orchestrator": """# 🎤 Staff AI Platform Interview Guide: Ray Distributed Cluster Orchestrator & Plasma

This guide bridges **Project 9 (`09-ray-distributed-cluster-orchestrator`)** to Staff/Principal-level questions on Ray Core and shared memory IPC.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Ray Core's Plasma Store achieve zero-copy deserialization across worker processes?"
> **Staff Engineer Answer**:
> "In `src/ray_cluster_orchestrator.py`, objects are written to POSIX shared memory (`/dev/shm`). Workers on the same node memory-map this buffer with PyArrow, reading tensor pointers directly without memory copying."

### Q2: "How does Ray dynamic actor autoscaling prevent cluster cost overruns?"
> **Staff Engineer Answer**:
> "We monitor pending task queue depth against active Ray actors. When load ratio $>1.5$, additional worker pods are provisioned; when idle for $>300\\text{s}$, workers drain gracefully to baseline limits."

### Q3: "How do you handle worker node preemption during distributed task execution?"
> **Staff Engineer Answer**:
> "Tasks returning Ray `ObjectRef` handles support automatic task lineage reconstruction. If a worker node crashes, the Ray GCS re-schedules the task on an available node."
""",

    "10-triton-cuda-gpu-scheduler": """# 🎤 Staff AI Platform Interview Guide: Triton CUDA GPU Scheduler & Dynamic Batching

This guide bridges **Project 10 (`10-triton-cuda-gpu-scheduler`)** to Staff/Principal-level questions on GPU Tensor Core scheduling and AWQ kernels.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Dynamic Batching prevent thread starvation while maintaining P99 latency SLAs?"
> **Staff Engineer Answer**:
> "In `src/triton_gpu_engine.py`, incoming requests enter an asyncio buffer. The scheduler flushes the batch when batch size reaches 32 OR queue delay reaches 10ms, safeguarding latency SLAs."

### Q2: "How does AWQ INT4 GEMM quantization accelerate inference throughput?"
> **Staff Engineer Answer**:
> "Activation-aware Weight Quantization (AWQ) protects salient weight channels while quantizing 99% of weights to INT4, doubling matrix multiplication throughput on GPU Tensor Cores."

### Q3: "How do multiple CUDA streams enable concurrent kernel execution?"
> **Staff Engineer Answer**:
> "We launch preprocessing, kernel execution, and postprocessing on independent non-blocking CUDA streams, allowing host-to-device memory copies to overlap with GPU compute."
""",

    "11-distributed-training-fsdp-megatron": """# 🎤 Staff AI Platform Interview Guide: PyTorch FSDP ZeRO-3 & Megatron 3D Parallelism

This guide bridges **Project 11 (`11-distributed-training-fsdp-megatron`)** to Staff/Principal-level questions on multi-node distributed model training.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Compare PyTorch FSDP (ZeRO-3) vs. Megatron Tensor Parallelism. When would you use each?"
> **Staff Engineer Answer**:
> "In `src/distributed_trainer.py`, FSDP ZeRO-3 shards Optimizer States, Gradients, and Model Parameters across data-parallel ranks, reconstructing weights on-the-fly via `All-Gather`. Megatron Tensor Parallelism splits linear projection matrices intra-node over NVLink (900 GB/s). Standard practice: TP intra-node, FSDP inter-node."

### Q2: "What causes gradient overflow during FP16 mixed-precision training, and how is it resolved?"
> **Staff Engineer Answer**:
> "FP16 has a dynamic range of $[10^{-5}, 65504]$. Large gradient norms cause Inf/NaN overflows. We audit gradient norms, clip gradients to 1.0, and dynamically reduce the loss scale factor upon overflow."

### Q3: "How do you calculate distributed training bus bandwidth?"
> **Staff Engineer Answer**:
> "Using the All-Reduce bus bandwidth formula: $B_{bus} = \\frac{2(N-1)}{N} \\cdot \\frac{\\text{Payload Size}}{\\text{Duration}}$, evaluating NVLink and RoCE network saturation."
""",

    "12-genai-gateway-semantic-cache": """# 🎤 Staff AI Platform Interview Guide: GenAI Gateway & Redis Semantic Cache

This guide bridges **Project 12 (`12-genai-gateway-semantic-cache`)** to Staff/Principal-level questions on enterprise API gateways and rate limiting.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you implement distributed token-bucket rate limiters in Redis?"
> **Staff Engineer Answer**:
> "In `src/gateway_proxy.py`, we execute atomic Redis Lua scripts computing token replenishment based on timestamp deltas, enforcing per-API-key requests-per-minute (RPM) quotas."

### Q2: "How does multi-provider failover cascade prevent customer-facing outages?"
> **Staff Engineer Answer**:
> "If primary provider OpenAI returns 5xx errors or timeouts, the gateway automatically cascades to Anthropic Claude 3.5 Sonnet, and then to local Ollama instances."

### Q3: "How does semantic vector caching reduce downstream API billing?"
> **Staff Engineer Answer**:
> "Prompts with cosine similarity $\\ge 0.92$ return cached completions from ChromaDB in $<5\\text{ms}$ at $\\$0$ cost."
""",

    "13-rlhf-dpo-alignment-pipeline": """# 🎤 Staff AI Platform Interview Guide: Direct Preference Optimization (DPO) & RLHF

This guide bridges **Project 13 (`13-rlhf-dpo-alignment-pipeline`)** to Staff/Principal-level questions on LLM alignment and preference optimization.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "What are the primary mathematical advantages of DPO over PPO (RLHF)?"
> **Staff Engineer Answer**:
> "In `src/dpo_alignment_engine.py`, PPO requires 4 concurrent models (Policy, Reference, Reward, Critic) in VRAM. DPO expresses the optimal reward in closed form, optimizing policy weights directly on pairwise chosen/rejected responses: $\\mathcal{L}_{\\text{DPO}} = -\\log \\sigma \\left(\\beta \\log \\frac{\\pi_\\theta(y_w)}{\\pi_{ref}(y_w)} - \\beta \\log \\frac{\\pi_\\theta(y_l)}{\\pi_{ref}(y_l)}\\right)$."

### Q2: "How do you evaluate Bradley-Terry win-rate margins during training?"
> **Staff Engineer Answer**:
> "We compute the implicit reward margin $r_w - r_l$. A win-rate $\\ge 75\\%$ confirms policy alignment with human preferences."

### Q3: "How do you ensure numerical stability in DPO log-ratio calculations?"
> **Staff Engineer Answer**:
> "We clamp log-probability ratios within $[-20.0, 20.0]$ before passing through the sigmoid activation to prevent gradient saturation."
""",

    "14-custom-cuda-triton-kernel-opt": """# 🎤 Staff AI Platform Interview Guide: Custom OpenAI Triton GPU Kernels & SRAM Tiling

This guide bridges **Project 14 (`14-custom-cuda-triton-kernel-opt`)** to Staff/Principal-level questions on GPU kernel optimization and SRAM memory bandwidth.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is a fused Bias-GELU Triton kernel faster than standard PyTorch?"
> **Staff Engineer Answer**:
> "In `src/triton_kernel_engine.py`, standard PyTorch executes 3 separate memory roundtrips over high-bandwidth memory (HBM). A fused Triton kernel loads tensor tiles into on-chip SRAM (19 TB/s on H100), computes bias addition and GELU activation in registers, and writes back to HBM once (1.99x speedup)."

### Q2: "How do you determine the optimal block size for GPU kernel tiling?"
> **Staff Engineer Answer**:
> "We balance register pressure and shared memory capacity per Streaming Multiprocessor (SM). `BLOCK_SIZE=1024` maximizes occupancy without causing register spilling to global memory."

### Q3: "How does the Roofline model guide GPU performance engineering?"
> **Staff Engineer Answer**:
> "It relates attainable TFLOPS to Operational Intensity (FLOPs/byte). If operational intensity is below the hardware ridge point, performance is memory-bandwidth-bound; if above, it is compute-bound."
""",

    "15-feature-store-vector-lakehouse": """# 🎤 Staff AI Platform Interview Guide: Feature Store & Vector Lakehouse

This guide bridges **Project 15 (`15-feature-store-vector-lakehouse`)** to Staff/Principal-level questions on online/offline feature serving and point-in-time joins.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you prevent temporal data leakage during training set generation?"
> **Staff Engineer Answer**:
> "In `src/feature_lakehouse_engine.py`, we execute PyArrow ASOF joins where feature observation timestamps strictly precede the label event timestamp (`feature_time <= event_time`)."

### Q2: "How does the dual-layer feature store architecture balance latency and scale?"
> **Staff Engineer Answer**:
> "Online features are pre-materialized in Redis for sub-2ms real-time inference serving, while offline features reside in Parquet/Delta Lake tables for large-scale distributed model training."

### Q3: "How do you handle missing feature values during online inference?"
> **Staff Engineer Answer**:
> "We apply pre-calculated mean/median baseline imputation directly in the feature retrieval client to prevent model null exceptions."
""",

    "16-ai-safety-red-teaming-guardrails": """# 🎤 Staff AI Platform Interview Guide: AI Safety, Jailbreak Defense & PII Guardrails

This guide bridges **Project 16 (`16-ai-safety-red-teaming-guardrails`)** to Staff/Principal-level questions on AI safety, red-teaming, and Llama Guard policies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you detect and neutralize adversarial prompt injection and DAN jailbreaks?"
> **Staff Engineer Answer**:
> "In `src/safety_guardrails.py`, input prompts pass through heuristic normalization and semantic jailbreak detectors, identifying role-play overrides (`DAN`, `unrestricted mode`) and blocking requests with HTTP 400."

### Q2: "How do you ensure zero PII data leakage in LLM completions?"
> **Staff Engineer Answer**:
> "We scan completions using compiled regex patterns for SSNs, credit cards, and emails, redacting sensitive tokens into `[REDACTED]` tokens."

### Q3: "How does Llama Guard policy enforcement protect enterprise models?"
> **Staff Engineer Answer**:
> "Completions are classified against enterprise safety policies (hate speech, weapons, malware). Unsafe outputs are quarantined before reaching end-users."
""",

    "17-k8s-kuberay-kueue-gpu-operator": """# 🎤 Staff AI Platform Interview Guide: K8s KubeRay & Kueue Multi-Tenant GPU Scheduling

This guide bridges **Project 17 (`17-k8s-kuberay-kueue-gpu-operator`)** to Staff/Principal-level questions on Kubernetes GPU orchestration and NVIDIA MIG.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "When would you use NVIDIA MIG vs. Time-Slicing vs. MPS in Kubernetes?"
> **Staff Engineer Answer**:
> "In `src/k8s_gpu_manager.py`, Multi-Instance GPU (MIG) physically partitions an H100 into up to 7 hardware-isolated instances with dedicated memory paths for hard multi-tenant isolation. Time-slicing shares compute temporally without isolation. MPS shares CUDA contexts for high small-batch compute density."

### Q2: "How does Kueue priority preemption guarantee GPU resources for real-time inference?"
> **Staff Engineer Answer**:
> "Kueue ClusterQueue evaluates incoming PriorityClasses. High-priority inference workloads preempt lower-priority batch training jobs, releasing GPU capacity immediately."

### Q3: "How does KubeRay manage distributed Ray cluster lifecycle on Kubernetes?"
> **Staff Engineer Answer**:
> "The KubeRay operator reconciles RayCluster Custom Resources, managing head and worker pod provisioning, auto-scaling, and zero-downtime rolling upgrades."
""",

    "18-tensorrt-llm-onnx-execution": """# 🎤 Staff AI Platform Interview Guide: TensorRT-LLM Engine & INT4 SmoothQuant

This guide bridges **Project 18 (`18-tensorrt-llm-onnx-execution`)** to Staff/Principal-level questions on TensorRT-LLM and ONNX graph optimization.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does TensorRT-LLM compile PyTorch models into optimized execution plans?"
> **Staff Engineer Answer**:
> "In `src/tensorrt_engine.py`, PyTorch computation graphs are traced into ONNX format. TensorRT fuses multi-head attention (FMHA) kernels, applies INT4 SmoothQuant calibration, and builds a static `.engine` execution plan delivering up to 1,480 tokens/sec."

### Q2: "What is SmoothQuant calibration, and why is it superior to naive INT8/INT4 quantization?"
> **Staff Engineer Answer**:
> "Activations have outlier channels that cause quantization errors. SmoothQuant applies a per-channel scaling factor to migrate difficulty from activations to weights, preserving model perplexity."

### Q3: "How do you manage dynamic input shapes in TensorRT execution profiles?"
> **Staff Engineer Answer**:
> "We configure optimization profiles with minimum, optimal, and maximum batch sizes and sequence lengths (`min=1, opt=32, max=64`), allowing the engine to allocate optimal memory buffers."
""",

    "19-multi-agent-swarm-orchestrator": """# 🎤 Staff AI Platform Interview Guide: Multi-Agent Swarm DAG Orchestrator & Consensus

This guide bridges **Project 19 (`19-multi-agent-swarm-orchestrator`)** to Staff/Principal-level questions on multi-agent consensus and DAG scheduling.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you detect and prevent circular deadlock cycles in multi-agent DAGs?"
> **Staff Engineer Answer**:
> "In `src/swarm_orchestrator.py`, we construct a directed acyclic graph of task dependencies and execute Kahn's algorithm topological sorting. If an in-degree cycle is detected ($A \\rightarrow B \\rightarrow A$), the runtime aborts immediately with `CycleDeadlockException`."

### Q2: "How does majority voting consensus validate multi-agent synthesis?"
> **Staff Engineer Answer**:
> "Independent agent candidate outputs are evaluated for agreement. If $\\ge 66\\%$ of swarm agents agree on key conclusions, the synthesized result is committed; otherwise, a senior evaluator breaks the tie."

### Q3: "How do stateful agent nodes communicate context without race conditions?"
> **Staff Engineer Answer**:
> "Tasks communicate via immutable state dictionaries passed along DAG edges, preventing concurrent state corruption."
""",

    "20-data-governance-openlineage-catalog": """# 🎤 Staff AI Platform Interview Guide: Data Governance, OpenLineage & Quality Contracts

This guide bridges **Project 20 (`20-data-governance-openlineage-catalog`)** to Staff/Principal-level questions on dataset lineage and Great Expectations contracts.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do OpenLineage telemetry events track end-to-end dataset lineage?"
> **Staff Engineer Answer**:
> "In `src/data_governance_engine.py`, data jobs emit standardized OpenLineage `START`, `COMPLETE`, and `ABORT` JSON events containing input/output dataset URNs and run state facets to the Marquez catalog."

### Q2: "How do Data Quality Contracts prevent silent model failure in production?"
> **Staff Engineer Answer**:
> "Before pipeline execution, Great Expectations schema suites audit incoming tables for non-null primary keys and valid numerical ranges. Violations trigger an immediate OpenLineage ABORT event, halting downstream feature generation."

### Q3: "How do you handle catalog server downtime without dropping lineage telemetry?"
> **Staff Engineer Answer**:
> "Lineage events are buffered in local persistent disk queues, retrying delivery with exponential backoff upon server reconnection."
""",

    "21-vllm-multi-lora-dynamic-serving": """# 🎤 Staff AI Platform Interview Guide: vLLM Multi-LoRA Dynamic Serving & Segmented GEMM

This guide bridges **Project 21 (`21-vllm-multi-lora-dynamic-serving`)** to Staff/Principal-level questions on multi-tenant LoRA serving (S-LoRA / Punica).

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you serve 100+ fine-tuned customer LoRA adapters on a single base model without stalling inference?"
> **Staff Engineer Answer**:
> "In `src/multi_lora_engine.py`, base model weights reside permanently in VRAM. Lightweight LoRA adapter weights (50MB) are paged into dynamic VRAM buffers using LRU cache eviction. A custom Segmented GEMM kernel applies distinct adapter weights to different sequence slices in the same batch simultaneously with zero stalling."

### Q2: "How does Segmented GEMM differ from standard PyTorch batch matrix multiplication?"
> **Staff Engineer Answer**:
> "Standard `torch.bmm` requires all batch elements to multiply against the same weight matrix. Segmented GEMM partitions batch sequences and multiplies each segment by its respective LoRA adapter matrix ($B_i A_i$) in a single fused GPU kernel."

### Q3: "How do you manage VRAM memory pressure with dynamic adapter caching?"
> **Staff Engineer Answer**:
> "When active adapter memory exceeds the allocated VRAM pool (e.g. 500MB), the cache manager evicts the least-recently-used adapter back to host RAM via non-blocking pinned memory."
""",

    "22-disaggregated-prefill-decode-engine": """# 🎤 Staff AI Platform Interview Guide: Disaggregated Prefill vs. Decode & RDMA KV Pools

This guide bridges **Project 22 (`22-disaggregated-prefill-decode-engine`)** to Staff/Principal-level questions on Splitwise, DistServe, and Mooncake architectures.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why is colocation of Prefill and Decode suboptimal, and how does Disaggregation solve Head-of-Line blocking?"
> **Staff Engineer Answer**:
> "In `src/disaggregated_engine.py`, Prefill (prompt processing) is compute-bound, while Decode (token generation) is memory-bandwidth-bound. Colocating them causes long prompts to block ongoing token generation. Disaggregation routes prompts to dedicated Prefill GPUs, transfers computed KV caches over 100 Gbps GPUDirect RDMA in $<2\\text{ms}$, and generates tokens on dedicated Decode GPUs."

### Q2: "How does Disaggregated serving improve Time to First Token (TTFT) and Time Per Output Token (TPOT)?"
> **Staff Engineer Answer**:
> "By isolating compute-heavy prompts from token generation, TTFT is reduced by up to 70% and TPOT jitter is virtually eliminated."

### Q3: "How do you handle RDMA network queue timeouts during KV cache transfer?"
> **Staff Engineer Answer**:
> "If an RDMA QP timeout occurs, the transfer client falls back automatically to high-speed TCP socket streams to preserve request continuity."
""",

    "23-fp8-mixed-precision-gemm-engine": """# 🎤 Staff AI Platform Interview Guide: Native FP8 (E4M3 / E5M2) GEMM & Delayed Scaling

This guide bridges **Project 23 (`23-fp8-mixed-precision-gemm-engine`)** to Staff/Principal-level questions on NVIDIA Hopper H100 FP8 Tensor Cores.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "What are the mathematical differences between FP8 E4M3 and E5M2 formats?"
> **Staff Engineer Answer**:
> "In `src/fp8_gemm_engine.py`, **E4M3** (1 sign, 4 exp, 3 mantissa) has range $[-448, 448]$ with higher precision, making it ideal for forward pass activations and weights. **E5M2** (1 sign, 5 exp, 2 mantissa) has range $[-57344, 57344]$ with higher dynamic range, ideal for backward pass gradients."

### Q2: "Why are delayed dynamic scaling factors necessary for FP8 Tensor Core matrix multiplication?"
> **Staff Engineer Answer**:
> "Calculating exact maximum absolute values ($\text{amax}$) on every layer causes GPU pipeline stalls. We maintain a sliding history of $\text{amax}$ to compute delayed scaling factors: $S = \\text{FP8\\_MAX} / \\max(\\text{history}(\\text{amax}))$, unlocking 1,979 TFLOPS on Hopper."

### Q3: "How does FP8 GEMM achieve a 1.86x speedup over FP16?"
> **Staff Engineer Answer**:
> "8-bit operands halve memory bandwidth requirements and double Tensor Core arithmetic density compared to 16-bit floats."
""",

    "24-nccl-distributed-collective-profiler": """# 🎤 Staff AI Platform Interview Guide: NCCL Multi-GPU Communication & Straggler Detection

This guide bridges **Project 24 (`24-nccl-distributed-collective-profiler`)** to Staff/Principal-level questions on NCCL collective communication algorithms and topology.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you calculate NCCL Bus Bandwidth for All-Reduce collectives?"
> **Staff Engineer Answer**:
> "In `src/nccl_profiler.py`, Algorithmic Bandwidth is $B_{alg} = \\frac{\\text{Bytes}}{\\text{Time}}$. Bus Bandwidth accounts for multi-GPU traffic multiplication: $B_{bus} = \\frac{2(N-1)}{N} \\cdot B_{alg}$ (for 8 GPUs, factor is 1.75x), measuring NVLink (900 GB/s) saturation."

### Q2: "How do you detect and isolate straggler GPU ranks in distributed training?"
> **Staff Engineer Answer**:
> "Synchronous distributed training stalls if one rank is slow. We profile per-rank kernel completion times. Any rank exhibiting $>5\\%$ latency variance from the cluster mean is flagged for thermal throttling or PCIe link degradation."

### Q3: "When should you switch from Ring to Tree collective topologies?"
> **Staff Engineer Answer**:
> "Ring collectives excel for large message payloads where bandwidth dominates ($O(N)$ latency hops). 2D-Tree topologies excel for small/medium payloads across multi-node clusters by reducing latency hops to $O(\\log N)$."
""",

    "25-speculative-medusa-multi-head-verifier": """# 🎤 Staff AI Platform Interview Guide: Medusa Multi-Head Speculative Decoding & Tree Attention

This guide bridges **Project 25 (`25-speculative-medusa-multi-head-verifier`)** to Staff/Principal-level questions on Medusa speculative decoding and Tree Attention.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How does Medusa achieve speculative decoding without hosting a separate draft model?"
> **Staff Engineer Answer**:
> "In `src/medusa_verifier.py`, Medusa attaches 4 lightweight MLP heads directly on top of the base model's final hidden states, predicting tokens $t+1, t+2, t+3, t+4$ simultaneously in parallel with zero auxiliary model VRAM footprint."

### Q2: "How does 2D Tree Attention verify multiple speculative candidate tokens in a single pass?"
> **Staff Engineer Answer**:
> "We construct a candidate token tree and apply custom 2D Tree Attention causal masks. The base model processes the tree in a single forward pass, accepting 2 to 4 tokens and achieving up to 2.85x speedup."

### Q3: "How does the engine handle partial speculative verification matches?"
> **Staff Engineer Answer**:
> "If only tokens 1 and 2 match target logits, the engine accepts the 2 verified tokens, resamples the true 3rd token from target logits, and advances generation without wasting work."
"""
}

print("Writing dedicated local INTERVIEW_PREP.md question banks for all 25 projects...")
for p_dir, content in project_interview_data.items():
    full_path = os.path.join(base_dir, p_dir, "INTERVIEW_PREP.md")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated local INTERVIEW_PREP.md for {p_dir}")

print("All 25 local INTERVIEW_PREP.md files successfully written and synchronized!")
