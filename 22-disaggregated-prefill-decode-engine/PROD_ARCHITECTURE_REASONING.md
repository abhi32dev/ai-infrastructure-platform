# Production Architecture & Design Trade-offs: Disaggregated Prefill vs. Decode Serving & Handoff Engine

## 1. Executive Context & Business Motivation
Eliminates head-of-line interference and latency jitter by separating compute-bound prompt ingestion (Prefill) from memory-bandwidth-bound token generation (Decode) across distinct GPU worker pools with GPUDirect RDMA KV cache transfer.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Core Strategy & Trade-Off Rationale
- **Chosen Option**: Production-grade modular architecture with deterministic fallback paths and high-throughput batching.
- **Alternative Evaluated**: Unoptimized naive execution.
- **Trade-Off Rationale**: Eliminates latency jitter, optimizes hardware utilization, and ensures continuous SLA compliance under high load.

---

## 3. Best Practices & Production Design Principles
1. **Defensive Schema Parsing**: Validates all input arguments and tensor shapes before GPU kernel execution.
2. **Deterministic Fallbacks**: Automatic graceful degradation to safe baselines upon hardware fault or SLA breach.
3. **Zero-Copy Memory Efficiency**: Optimized data structures to minimize memory bandwidth saturation.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **SLA Latency Breach** | P99 latency spike | Dynamic batch sizing and fast-path caching. |
| **Hardware Memory Exhaustion** | Worker OOM fault | LRU memory eviction and quota circuit breaking. |
| **Network Queue Timeout** | Inter-node stall | Automatic fallback to secondary high-speed protocol. |

---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Eliminates head-of-line interference and latency jitter by separating compute-bound prompt ingestion (Prefill) from memory-bandwidth-bound token generation (Decode) across distinct GPU worker pools with GPUDirect RDMA KV cache transfer.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "prompt": "Analyze quarterly balance sheet and compute EBITDA margin.",
  "tokens": [101, 2841, 3912, 102],
  "phase": "PREFILL"
}
```
**Input Parameter Specification**:
Inference request containing prompt text, tokenized sequence array, and current request phase (`PREFILL` vs `DECODE`).

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Classify Request Phase**: Inspects request metadata to route compute-heavy prompt processing to the Prefill GPU worker pool.
- **2. Decision 1 (Phase Classification Gate)**: If request is in PREFILL phase, executes chunked prefill compute. If in DECODE phase, routes directly to decode worker pool.
- **3. Compute KV Tensors & GPUDirect RDMA Transfer**: Computes initial Key-Value cache memory tensors on Prefill GPU and transfers tensors to Decode GPU pool via GPUDirect RDMA.
- **4. Decision 2 (RDMA Latency SLA Check)**: If RDMA transfer succeeds in < 3.0ms, commits KV cache to decode memory pool and begins autoregressive generation.
- **5. Decision 3 (Network Timeout Fallback)**: If RDMA queue encounters network timeout, falls back automatically to high-speed TCP socket stream.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "request_id": "req_8a7f12b0",
  "prefill_gpu_id": "gpu-prefill-01",
  "decode_gpu_id": "gpu-decode-01",
  "kv_cache_size_bytes": 65536,
  "rdma_latency_ms": 0.85,
  "ttft_ms": 10.2,
  "status": "RDMA_OK"
}
```
**Output Specification**:
Disaggregated handoff result containing prefill node ID, decode node ID, KV cache size in bytes, RDMA latency, and Time to First Token (TTFT).

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 22-disaggregated-prefill-decode-engine/tests/test_disaggregated.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/22-disaggregated-prefill-decode-engine/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/22-disaggregated-prefill-decode-engine/FLOWCHART.svg)
