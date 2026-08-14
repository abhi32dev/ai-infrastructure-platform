# Staff & Principal AI Platform & Infrastructure Architect: Master Interview Preparation Guide

This comprehensive technical guide provides in-depth architectural questions, deep-dive answers, mathematical justifications, and trade-off analyses across the 20 core AI infrastructure and platform patterns demonstrated in this repository.

---

## Table of Contents
1. [Inference Engine Architecture & VRAM Virtualization (vLLM PagedAttention)](#1-inference-engine-architecture--vram-virtualization)
2. [Custom GPU Kernel Optimization & SRAM Tiling (OpenAI Triton)](#2-custom-gpu-kernel-optimization--sram-tiling)
3. [Distributed Model Training & Memory Sharding (FSDP ZeRO-3 & Megatron 3D)](#3-distributed-model-training--memory-sharding)
4. [High-Throughput GPU Scheduling & Dynamic Batching](#4-high-throughput-gpu-scheduling--dynamic-batching)
5. [Distributed Cluster Orchestration & Plasma Shared Memory (Ray Core)](#5-distributed-cluster-orchestration--plasma-shared-memory)
6. [Semantic Caching & Multi-Tier RAG Cost Routing](#6-semantic-caching--multi-tier-rag-cost-routing)
7. [Statistical LLM Evaluation Gates & CI/CD Promotion (Welch's t-Test)](#7-statistical-llm-evaluation-gates--cicd-promotion)
8. [Preference Alignment & Optimization (DPO vs. PPO)](#8-preference-alignment--optimization)
9. [Enterprise Kubernetes GPU Scheduling & Hardware Slicing (KubeRay & MIG)](#9-enterprise-kubernetes-gpu-scheduling--hardware-slicing)
10. [Data Governance, OpenLineage & Quality Contracts (Great Expectations)](#10-data-governance-openlineage--quality-contracts)

---

## 1. Inference Engine Architecture & VRAM Virtualization

### Q1: Why does traditional LLM serving suffer from severe VRAM fragmentation, and how does PagedAttention solve it?
**Deep Answer**:
* **The Problem**: In autoregressive LLM decoding, the Key-Value (KV) cache grows dynamically with each generated token. Traditional serving frameworks allocated contiguous physical VRAM buffers for the maximum sequence length ($L_{max}=2048$ or $8192$). Because actual generation lengths vary widely, up to **60%–80% of VRAM** was wasted due to:
  1. *Internal Fragmentation*: Memory reserved for $L_{max}$ that was never used by shorter requests.
  2. *External Fragmentation*: Differing request lifetimes creating disjoint memory holes unable to accommodate new continuous blocks.
* **The PagedAttention Solution**: Inspired by OS virtual memory paging, PagedAttention partitions the KV cache into fixed-size physical blocks (e.g., 16 tokens). Sequences are mapped to non-contiguous physical blocks via a **Block Table**.
* **Mathematical Memory Saving**:
  $$\text{Waste}_{\text{Paged}} < \text{Block Size} \times \text{Batch Size} \ll L_{max} \times \text{Batch Size}$$
  By eliminating pre-allocation, VRAM waste drops to $<4\%$, allowing a **2x–4x increase in concurrent batch size** on the same GPU.

### Q2: How does Speculative Decoding work, and what determines its theoretical speedup limit?
**Deep Answer**:
* **Mechanism**: A small "draft" model ($M_{draft}$, e.g. 1B) speculates $K$ candidate tokens sequentially at high speed (low compute per token). Then, the large "target" model ($M_{target}$, e.g. 70B) runs a **single parallel forward pass** on all $K$ candidate tokens to verify their joint probabilities against target logits:
  $$P(\text{accept } x_{t}) = \min\left(1, \frac{P_{target}(x_t \mid x_{<t})}{P_{draft}(x_t \mid x_{<t})}\right)$$
* **Theoretical Speedup**:
  $$\text{Speedup} = \frac{1 + \alpha K}{1 + c \cdot K}$$
  Where $\alpha$ is the draft acceptance rate and $c$ is the ratio of draft latency to target latency. If $\alpha \approx 0.8$ and $K=4$, speedups of **2.0x–2.67x** are achieved with zero degradation in mathematical output quality.

---

## 2. Custom GPU Kernel Optimization & SRAM Tiling

### Q3: What is the Roofline Model, and why is fused Bias-GELU faster in OpenAI Triton than standard PyTorch?
**Deep Answer**:
* **The Roofline Model**: Relates attainable performance ($\text{TFLOPS}$) to Operational Intensity ($I = \frac{\text{FLOPs}}{\text{Bytes Transferred}}$):
  $$\text{Attainable TFLOPS} = \min\left(\text{Peak Compute TFLOPS}, \text{Peak Memory Bandwidth} \times I\right)$$
* **Why Elementwise PyTorch Operations are Slow**: In standard PyTorch, executing $Y = \text{GELU}(X \cdot W + B)$ launches 3 distinct CUDA kernels:
  1. Matrix Multiply: Reads $X, W$, writes temporary tensor $T_1$ to high-bandwidth VRAM (HBM).
  2. Bias Addition: Reads $T_1, B$ from HBM, writes $T_2$ to HBM.
  3. GELU Activation: Reads $T_2$ from HBM, applies GELU math, writes final output to HBM.
  *Total HBM Memory Traffic*: $3\times$ read/write roundtrips over the memory bus.
* **The Triton Fused Kernel Advantage**: OpenAI Triton loads the tile block directly into on-chip **Shared Memory (SRAM)** (19 TB/s on H100 vs. 3.35 TB/s HBM), computes the bias add and GELU activation inside registers in a single kernel pass, and writes to HBM once. This reduces memory traffic by $66\%$, yielding a **1.8x–2.4x speedup**.

---

## 3. Distributed Model Training & Memory Sharding

### Q4: Compare PyTorch FSDP (ZeRO-3) vs. Megatron Tensor Parallelism vs. DeepSpeed. When would you use each?
**Deep Answer**:
* **PyTorch FSDP (ZeRO-3)**:
  * *Mechanism*: Shards Optimizer States (ZeRO-1), Gradients (ZeRO-2), and Model Parameters (ZeRO-3) across data-parallel ranks. During forward/backward pass, parameters are gathered via `All-Gather` and discarded immediately via `Reduce-Scatter`.
  * *Best Used*: For scaling models across 8 to 512 GPUs when inter-node network bandwidth is standard (e.g. AWS EFA / 100Gbps RoCE).
* **Megatron Tensor Parallelism (TP)**:
  * *Mechanism*: Splits individual weight matrices ($Q, K, V$ and MLP projections) across GPUs within a node using row and column linear layer slicing. Requires `All-Reduce` inside every transformer layer.
  * *Best Used*: Strictly **within a single multi-GPU node** connected via ultra-high-speed NVLink (900 GB/s on H100). Never cross nodes with pure TP due to high communication latency.
* **The Hybrid 3D Strategy (Enterprise Gold Standard)**:
  * Intra-Node (within 8-GPU box): Megatron Tensor Parallelism ($TP=8$).
  * Inter-Node (across boxes): FSDP / Pipeline Parallelism ($PP=4, DP=16$).

---

## 4. High-Throughput GPU Scheduling & Dynamic Batching

### Q5: How does Dynamic Batching prevent thread starvation while maintaining P99 latency SLAs?
**Deep Answer**:
* **Mechanism**: Individual incoming inference requests arrive non-deterministically. A naive server executes them as single batches ($B=1$), leaving $90\%$ of GPU Tensor Cores idle.
* **Dynamic Batching Engine**:
  1. Incoming requests enter an asynchronous queue buffer.
  2. The scheduler evaluates two triggers: **Max Batch Size** (e.g., $B=32$) OR **Max Queue Latency Timeout** (e.g., $\Delta t = 10\text{ms}$).
  3. Whichever condition is met first triggers an immediate tensor stack and kernel launch on a dedicated CUDA stream.
* **SLA Protection**: The strict $10\text{ms}$ timeout ensures that early-arriving requests are never delayed beyond their P99 SLA budget, even under low-traffic periods.

---

## 5. Distributed Cluster Orchestration & Plasma Shared Memory

### Q6: How does Ray Core's Plasma Store achieve zero-copy deserialization across worker processes?
**Deep Answer**:
* **The Problem with Standard IPC**: Passing a 2GB NumPy array or PyTorch tensor across Python worker processes via standard multiprocessing `pickle` or sockets requires copying memory from process A $\rightarrow$ OS kernel $\rightarrow$ process B, causing massive memory duplication and CPU serialization overhead.
* **Plasma Shared Memory Architecture**:
  1. Ray writes objects to a POSIX shared-memory-mapped file descriptor (`/dev/shm`).
  2. PyArrow memory-maps this shared region as a read-only buffer in all worker processes on the same node.
  3. Worker tasks read the tensor memory addresses directly without memory copying ($O(1)$ transfer time regardless of tensor size).

---

## 6. Semantic Caching & Multi-Tier RAG Cost Routing

### Q7: What are the mathematical and operational failure modes of Semantic Vector Caching in production?
**Deep Answer**:
* **The Semantic Cache Dilemma**: Using vector cosine similarity to match prompt embeddings risks **Semantic False Positives**:
  * Prompt A: *"What is the revenue of Apple in 2024?"*
  * Prompt B: *"What is the revenue of Apple in 2023?"*
  * *Cosine Similarity*: $\ge 0.96$ (because sentence structures and tokens are almost identical), yet returning the cached 2024 answer for a 2023 query is a critical hallucination error.
* **Production Mitigation Architecture**:
  1. **Strict Cosine Threshold**: Set conservative threshold ($\ge 0.95$).
  2. **Named Entity & Temporal Extraction**: Extract key entities (Dates, Years, Currency, User IDs). If numerical/temporal entities differ, force a cache miss regardless of cosine similarity score.

---

## 7. Statistical LLM Evaluation Gates & CI/CD Promotion

### Q8: Why is standard mean accuracy insufficient for model release gates, and why is Welch's t-test mandatory?
**Deep Answer**:
* **The Flaw of Mean Accuracy**: In non-deterministic LLM benchmarks, a candidate model scoring $84.2\%$ accuracy over 100 prompts compared to a baseline of $82.0\%$ may look like a $+2.2\%$ improvement. However, due to high variance and small sample size, this difference may be pure random noise.
* **Welch's t-Test Formulation**:
  $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}}}$$
  $$\nu \approx \frac{\left(\frac{s_1^2}{N_1} + \frac{s_2^2}{N_2}\right)^2}{\frac{(s_1^2/N_1)^2}{N_1-1} + \frac{(s_2^2/N_2)^2}{N_2-1}}$$
* **CI/CD Rule**: We enforce $p < 0.05$ and $\Delta > +5\%$ before MLflow promotes a candidate checkpoint to Production, mathematically guaranteeing that regressions are caught before customer deployment.

---

## 8. Preference Alignment & Optimization

### Q9: What are the primary mathematical differences between PPO (RLHF) and DPO (Direct Preference Optimization)?
**Deep Answer**:
* **PPO (Proximal Policy Optimization)**:
  * Requires 4 concurrent models in GPU VRAM during training: Policy Model ($\pi_\theta$), Reference Model ($\pi_{ref}$), Reward Model ($r_\psi$), and Value/Critic Model ($V_\phi$).
  * Training is notoriously unstable, sensitive to hyperparameter tuning, and prone to reward hacking.
* **DPO (Direct Preference Optimization)**:
  * Uses mathematical substitution to express the optimal reward directly in terms of the policy probability ratio:
    $$r^*(x, y) = \beta \log \frac{\pi^*(x, y)}{\pi_{ref}(x, y)}$$
  * Derives a direct closed-form loss over pairwise chosen ($y_w$) and rejected ($y_l$) responses:
    $$\mathcal{L}_{\text{DPO}}(\theta; \pi_{ref}) = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right) \right]$$
  * *Result*: Eliminates the Reward and Critic models entirely, reducing VRAM usage by $50\%$ and ensuring stable, monotonic loss convergence.

---

## 9. Enterprise Kubernetes GPU Scheduling & Hardware Slicing

### Q10: When would you use NVIDIA Multi-Instance GPU (MIG) vs. Time-Slicing vs. MPS in Kubernetes?
**Deep Answer**:
* **NVIDIA MIG (Multi-Instance GPU)**:
  * *Mechanism*: Physically partitions an H100/A100 GPU into up to 7 hardware-isolated instances with dedicated compute engines, memory controllers, and SRAM paths.
  * *Pros*: Hard QoS isolation; a crash or OOM on instance 1 has zero impact on instance 2.
  * *Best Used*: Multi-tenant enterprise environments serving distinct teams with strict SLAs.
* **NVIDIA MPS (Multi-Process Service)**:
  * *Mechanism*: Combines CUDA contexts from multiple processes into a single hardware context to share compute pipelines.
  * *Pros*: High compute saturation for small batch inference.
  * *Cons*: Shared memory space—if one process crashes with a memory fault, all sharing processes terminate.
* **Kueue Priority Preemption**:
  * Integrates with Kubernetes to preempt lower-priority batch training pods, reallocate MIG hardware slices, and guarantee immediate GPU access for mission-critical real-time inference workloads.

---

## 10. Data Governance, OpenLineage & Quality Contracts

### Q11: How do Data Quality Contracts prevent "silent model failure" in production AI pipelines?
**Deep Answer**:
* **The Silent Failure Problem**: In upstream feature pipelines, schema changes (e.g. an upstream column renamed from `user_age` to `customer_age`, or null values injected due to an API bug) do not throw syntax errors in PySpark, but cause downstream models to output meaningless predictions silently.
* **Great Expectations + OpenLineage Defense Architecture**:
  1. *Pre-Job Evaluation*: Enforce strict expectation suites before data processing (non-null primary keys, categorical values within expected sets, numerical bounds).
  2. *Immediate Circuit Breaking*: If quality checks fail, immediately emit an `OpenLineage ABORT` run state event to the Marquez catalog.
  3. *Quarantine*: Isolate corrupt batches to an S3 Dead-Letter Queue and block pipeline promotion before corrupt records contaminate feature tables.
