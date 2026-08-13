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
