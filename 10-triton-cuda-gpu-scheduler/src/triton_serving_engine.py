"""
Master NVIDIA Triton & CUDA Serving Engine Orchestrator.
Integrates Hardware-Aligned Dynamic Batching Queues with AWQ FP8/INT8 Model Quantization.
"""

from typing import Any, Dict, List
from src.awq_quantizer import AWQQuantizationEngine, AWQQuantizationResult
from src.dynamic_batch_queue import DynamicBatchQueueManager, DynamicBatchResult


class TritonCUDAServingEngine:
    def __init__(self, max_batch_size: int = 16):
        print("[TRITON ENGINE] Initializing NVIDIA Triton & CUDA GPU Platform...")
        self.batch_queue = DynamicBatchQueueManager(max_batch_size=max_batch_size)
        self.quantizer = AWQQuantizationEngine()

    def submit_triton_request(self, request_id: str, shape: List[int]) -> None:
        """Enqueues inference request into Triton dynamic batcher."""
        self.batch_queue.enqueue_request(request_id, shape)

    def execute_dynamic_batch_step(self) -> DynamicBatchResult:
        """Flushes dynamic batch to CUDA Tensor Cores."""
        return self.batch_queue.flush_batch()

    def audit_model_quantization(self, model_id: str, fmt: str) -> AWQQuantizationResult:
        """Runs AWQ quantization loss audit."""
        return self.quantizer.quantize_model_weights(model_id, target_format=fmt)
