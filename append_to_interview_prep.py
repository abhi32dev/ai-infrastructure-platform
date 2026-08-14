import os

base_dir = "/Users/abhi/Documents/Antigravity"
prep_path = os.path.join(base_dir, "INTERVIEW_PREP.md")

with open(prep_path, "r", encoding="utf-8") as f:
    content = f.read()

additional_prep = """
---

## 11. Multi-LoRA Dynamic Adapter Hot-Swapping & Segmented GEMM

### Q12: How does vLLM / S-LoRA serve 100+ fine-tuned LoRA adapters on a single base model without stalling batch inference?
**Deep Answer**:
* **The Naive Approach**: Hosting separate foundation model instances in VRAM for each fine-tuned customer model ($100 \times 140\text{GB} = 14\text{TB}$ VRAM) is financially impossible.
* **The Multi-LoRA Architecture**:
  1. *Unified Base Weights*: The base model weights $W_0 \in \mathbb{R}^{d \times k}$ reside permanently in GPU VRAM.
  2. *Lightweight LoRA Memory Pool*: Each tenant adapter consists only of low-rank matrices $A_i \in \mathbb{R}^{r \times k}$ and $B_i \in \mathbb{R}^{d \times r}$ ($r=8$, $\sim 50\text{MB}$ each).
  3. *Segmented GEMM Kernel*: When requests arrive from different tenants in the same batch, standard matrix multiplication cannot multiply different weights for different batch elements. A custom **Segmented GEMM (or Punica/S-LoRA Batched GEMM)** kernel multiplies sequence segments with their respective adapter matrices $(B_i A_i)$ in a single GPU pass:
     $$Y = X W_0 + \text{SegmentedGEMM}(X, \{A_i\}, \{B_i\})$$
  4. *Dynamic Page-In/Page-Out*: Adapters are paged in asynchronously from host pinned memory via non-blocking CUDA streams using LRU cache eviction, maintaining $>95\%$ cache hit rates and $<5\text{ms}$ latency overhead.

---

## 12. Disaggregated Prefill vs. Decode & RDMA KV Pools

### Q13: Why is colocation of Prefill and Decode suboptimal, and how does Disaggregation solve Head-of-Line blocking?
**Deep Answer**:
* **The Fundamental Mismatch**:
  * *Prefill Phase*: Ingests prompt tokens in parallel. It is heavily **compute-bound** (saturates Tensor Cores at high arithmetic intensity).
  * *Decode Phase*: Generates one token at a time autoregressively. It is heavily **memory-bandwidth-bound** (low arithmetic intensity, constantly reading weights from HBM).
* **Head-of-Line Blocking**: When a new request arrives with a 4,000-token prompt on a colocated server, the compute-heavy prefill blocks the ongoing token generation of 30 other active streams, causing severe **TPOT (Time Per Output Token) jitter**.
* **Disaggregated Architecture (DistServe / Mooncake / Splitwise)**:
  1. *Dedicated Prefill Pool*: High-compute nodes (e.g. H100 SXM5) process prompts and compute the initial Key-Value cache.
  2. *Ultra-Fast RDMA Transfer*: The KV cache tensors are transferred to the Decode GPU pool over **100/400 Gbps GPUDirect RDMA** ($<2\text{ms}$ latency).
  3. *Dedicated Decode Pool*: Memory-bandwidth-optimized nodes generate tokens continuously with zero jitter, slashing TTFT (Time to First Token) by up to $70\%$ and doubling system goodput.

---

## 13. Native FP8 (E4M3 / E5M2) Tensor Cores & Delayed Scaling

### Q14: How does FP8 mixed-precision differ from FP16/INT8, and why are delayed dynamic scaling factors necessary?
**Deep Answer**:
* **The FP8 Formats (IEEE / NVIDIA Hopper)**:
  * **E4M3** (1 sign, 4 exponent, 3 mantissa bits): Range $[-448, 448]$, higher precision $\rightarrow$ Ideal for forward pass activations and weights.
  * **E5M2** (1 sign, 5 exponent, 2 mantissa bits): Range $[-57344, 57344]$, higher dynamic range $\rightarrow$ Ideal for backward pass gradients.
* **Why Static Scaling Fails**: Unlike INT8 which has uniform quantization bins, FP8 has non-uniform floating-point spacing. If tensors exceed $448$, values saturate to NaN/Inf; if too small, they underflow to zero.
* **Delayed Dynamic Scaling**:
  Instead of computing the exact maximum absolute value ($\text{amax}$) before every single layer (which causes GPU pipeline stalls), frameworks maintain a historical sliding window of $\text{amax}$ values across recent iterations. The scaling factor is computed as:
  $$S = \frac{\text{FP8\_MAX}}{\max(\text{history}(\text{amax}))}$$
  This unlocks **1,979 TFLOPS** on Hopper Tensor Cores ($1.86\text{x}$ speedup over FP16) with zero loss in validation perplexity.

---

## 14. NCCL Multi-GPU Collective Profiling & Straggler Detection

### Q15: How do you calculate NCCL Bus Bandwidth, and how do you diagnose straggler GPU ranks during distributed training?
**Deep Answer**:
* **Algorithmic vs. Bus Bandwidth**:
  * *Algorithmic Bandwidth*: $B_{alg} = \frac{\text{Message Size (Bytes)}}{\text{Elapsed Time (Seconds)}}$
  * *Bus Bandwidth Formula (Accounts for Multi-GPU Traffic Multiplying Factor)*:
    * For `All-Reduce`: $B_{bus} = \frac{2(N-1)}{N} \cdot B_{alg}$ (since each rank sends $(N-1)/N$ data during Reduce-Scatter and $(N-1)/N$ data during All-Gather).
    * For `All-Gather` / `Reduce-Scatter`: $B_{bus} = \frac{N-1}{N} \cdot B_{alg}$
* **Straggler Detection**:
  In distributed synchronous training, all $N$ GPUs must synchronize at the end of every forward/backward pass. If 7 GPUs finish in $1.0\text{ms}$ but 1 GPU takes $2.5\text{ms}$ due to thermal throttling or a PCIe bus degradation from $16\text{x}$ to $8\text{x}$, the entire cluster wastes $60\%$ of its compute waiting at the barrier.
  * *Detection*: Inject NVTX markers and profile per-rank kernel durations. Any rank with $>5\%$ variance from the cluster mean is flagged for hardware remediation.

---

## 15. Medusa Multi-Head Speculative Decoding & Tree Attention

### Q16: How does Medusa achieve speculative decoding without hosting a separate draft model?
**Deep Answer**:
* **The Draft Model Trade-Off**: Standard speculative decoding requires loading an auxiliary 1B/3B model in VRAM, consuming memory bandwidth and complex scheduler coordination.
* **The Medusa Architecture**:
  1. *Attached MLP Prediction Heads*: Directly attaches $K$ lightweight MLP heads (e.g. $K=4$) on top of the base model's final hidden states $h_t$.
  2. *Parallel Candidate Generation*: Head $k$ predicts the candidate token for position $t+k+1$ in parallel using residual projections:
     $$\hat{y}_{t+k+1} = \text{softmax}(W_k \cdot \text{SiLU}(V_k \cdot h_t))$$
  3. *2D Tree Attention Causal Masking*: Generates a tree of candidate token paths and constructs a custom 2D Tree Attention mask. The target model verifies all candidate paths in a **single forward pass**.
  4. *Speedup*: Accepts $2$ to $4$ tokens per forward pass, delivering **2.2x–2.85x latency speedup** with zero additional model footprint.
"""

# Update Table of Contents
if "10. [Data Governance" in content:
    toc_replacement = """10. [Data Governance, OpenLineage & Quality Contracts (Great Expectations)](#10-data-governance-openlineage--quality-contracts)
11. [Multi-LoRA Dynamic Adapter Hot-Swapping & Segmented GEMM](#11-multi-lora-dynamic-adapter-hot-swapping--segmented-gemm)
12. [Disaggregated Prefill vs. Decode & RDMA KV Pools](#12-disaggregated-prefill-vs-decode--rdma-kv-pools)
13. [Native FP8 (E4M3 / E5M2) Tensor Cores & Delayed Scaling](#13-native-fp8-e4m3--e5m2-tensor-cores--delayed-scaling)
14. [NCCL Multi-GPU Collective Profiling & Straggler Detection](#14-nccl-multi-gpu-collective-profiling--straggler-detection)
15. [Medusa Multi-Head Speculative Decoding & Tree Attention](#15-medusa-multi-head-speculative-decoding--tree-attention)"""
    content = content.replace("10. [Data Governance, OpenLineage & Quality Contracts (Great Expectations)](#10-data-governance-openlineage--quality-contracts)", toc_replacement)

# Append additional questions
if "## 11. Multi-LoRA" not in content:
    content = content.rstrip() + "\n" + additional_prep

with open(prep_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated INTERVIEW_PREP.md with deep Staff/Principal Q&A for Projects 21 to 25!")
