"""
Master TensorRT-LLM & ONNX Execution Orchestrator.
Integrates PyTorch-to-ONNX Graph Export and TensorRT Engine Compilation.
"""

from typing import Any, Dict
from src.onnx_exporter import ONNXExportResult, PyTorchONNXExporter
from src.tensorrt_compiler import TensorRTCompilerEngine, TensorRTEnginePlan


class TensorRTExecutionOrchestrator:
    def __init__(self, precision: str = "INT4_SMOOTHQUANT"):
        self.onnx_exporter = PyTorchONNXExporter(target_opset=18)
        self.trt_compiler = TensorRTCompilerEngine(target_precision=precision)

    def export_and_compile_pipeline(self, model_name: str = "Llama-3.2-7B") -> Dict[str, Any]:
        """Runs PyTorch -> ONNX Export -> TensorRT Compilation pipeline."""
        onnx_res = self.onnx_exporter.export_pytorch_to_onnx(model_name, [1, 512])
        trt_res = self.trt_compiler.compile_tensorrt_engine(model_name)

        return {
            "status": "TENSORRT_PIPELINE_SUCCESS",
            "model_name": model_name,
            "onnx_path": onnx_res.onnx_file_path,
            "engine_file": trt_res.engine_name,
            "precision": trt_res.target_precision,
            "throughput_tokens_per_sec": trt_res.throughput_tokens_per_sec,
            "latency_p99_ms": trt_res.latency_p99_ms,
            "vram_gb": trt_res.gpu_memory_gb
        }
