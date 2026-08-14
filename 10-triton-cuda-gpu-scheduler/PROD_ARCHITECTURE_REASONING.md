# Production Architecture & Design Trade-offs: Triton CUDA GPU Scheduler

## 1. Executive Context & Business Motivation
Serving quantized neural networks under production SLAs requires efficient GPU batching and low-precision execution. Running un-batched single inference requests on high-end GPUs (e.g. A100/H100) underutilizes Tensor Cores (< 10% GPU duty cycle).

This system implements a **Triton Inference Server Dynamic Batching Scheduler with AWQ 4-Bit Weight Quantization**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Dynamic Delay-Based Batching Queue vs Instant Un-batched Execution
- **Chosen Option**: **Dynamic Delay-Based Batching Queue (Max Batch Size + Max Delay Timeout)**.
- **Alternative Evaluated**: Instant un-batched inference execution.
- **Trade-Off Rationale**:
  - *Instant Execution*: Minimal latency for single queries, but abysmal hardware throughput under load.
  - *Dynamic Batching Queue*: Collects incoming requests into batches up to `max_batch_size` within a strict `max_queue_delay_microseconds` window, maximizing GPU memory bandwidth utilization.

### B. Activation-Aware Weight Quantization (AWQ) 4-Bit vs FP16
- **Chosen Option**: **AWQ INT4 Weight Quantization**.
- **Trade-Off Rationale**: AWQ protects the top 1% salient weight channels, compressing model memory footprint by 75% (e.g. 14GB $\rightarrow$ 3.8GB) with negligible accuracy degradation compared to FP16.

---

## 3. Best Practices & Production Design Principles

1. **Queue Flush Safeguards**:
   - Dual flush trigger: flushes immediately when `max_batch_size` is reached OR when `max_queue_delay_ms` timer expires.
2. **Quantization Reconstruction Integrity**:
   - De-quantizes 4-bit weights back to FP16 during inference steps using scaling and zero-point vectors.
3. **Multi-Model Instance Isolation**:
   - Allocates dedicated CUDA execution streams per model instance to eliminate inter-model resource contention.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Request Surge Queue Overflow** | Dropped client requests | Dynamic queue depth limits + immediate batch flush on capacity cap. |
| **Quantization Precision Drift** | Model accuracy drop | AWQ salient channel preservation protects top 1% critical weights. |
| **CUDA Stream Deadlock** | Inference pipeline freeze | Timeout-bounded CUDA stream synchronizations. |
---

## 5. End-to-End Operational Manual & Execution Guide

### A. Plain English Summary (What This Project Does)
Maximizes GPU Tensor Core compute utilization by grouping individual inference requests into dynamic batches (size 32 / 10ms timeout) and executing custom AWQ INT4 GEMM kernels on CUDA streams.

---

### B. Input Data Contract & Initiation Payload
To execute or trigger this component, pass the following structured JSON input payload:

```json
{
  "request_id": "req_88190",
  "input_tensor_shape": [1, 4096],
  "max_batch_size": 32,
  "max_queue_delay_ms": 10.0
}
```
**Input Parameter Specification**:
Individual incoming inference requests with 1D input tensors and caller response Futures.

---

### C. Step-by-Step Execution Walkthrough (Mapped to 2D Flowchart)
- **1. Enqueue Request in Batch Buffer**: Pushes incoming request to high-throughput asyncio dynamic batch queue.
- **2. Decision 1 (Batch Ready Trigger)**: Checks if batch size == 32 OR if queue delay timeout >= 10ms. If neither, holds request in buffer.
- **3. Launch Triton AWQ INT4 Kernel**: Stacks input tensors into unified 2D matrix batch and executes fused AWQ INT4 GEMM kernel across GPU Tensor Cores.
- **4. Decision 2 (Kernel Launch Verification)**: If kernel succeeds, unpacks output tensor batch and scatters results back to individual caller Futures.
- **5. Decision 3 (Unbatched Fallback Pass)**: If batched kernel launch experiences memory fault, falls back to unbatched single-pass PyTorch CUDA execution to safeguard SLAs.

---

### D. Expected Output & Return Values
Upon successful execution, the component returns the following structured result payload:

```json
{
  "batch_size_executed": 32,
  "kernel_type": "triton_awq_int4_gemm",
  "batch_latency_ms": 6.8,
  "individual_latency_ms": 7.1,
  "tflops_achieved": 242.5
}
```
**Output Specification**:
Batch execution throughput, individual latency per request, and Tensor Core utilization metric.

---

### E. How to Run & Verify Locally
Execute the automated test suite and benchmarks using the following command:

```bash
python3 -m pytest 10-triton-cuda-gpu-scheduler/tests/test_triton_engine.py -v
```

---

### F. Interactive Architecture Diagrams & Blueprints
- **Interactive 2D HTML Blueprint**: [Open `FLOWCHART.html`](file:///Users/abhi/Documents/Antigravity/10-triton-cuda-gpu-scheduler/FLOWCHART.html)
- **Standalone Vector SVG Diagram**: [Open `FLOWCHART.svg`](file:///Users/abhi/Documents/Antigravity/10-triton-cuda-gpu-scheduler/FLOWCHART.svg)
