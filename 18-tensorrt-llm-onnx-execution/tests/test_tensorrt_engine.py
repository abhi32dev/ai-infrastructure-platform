"""
Expanded Test Suite for Project 18 - TensorRT-LLM Engine & ONNX Execution.
Includes production edge cases for dynamic batch size limits, unsupported precision fallbacks, and opset versioning.
"""

import pytest
from src.onnx_exporter import PyTorchONNXExporter
from src.tensorrt_compiler import TensorRTCompilerEngine
from src.tensorrt_orchestrator import TensorRTExecutionOrchestrator


@pytest.fixture
def onnx_exp():
    return PyTorchONNXExporter(target_opset=18)


@pytest.fixture
def trt_comp():
    return TensorRTCompilerEngine(target_precision="INT4_SMOOTHQUANT")


@pytest.fixture
def orchestrator():
    return TensorRTExecutionOrchestrator(precision="INT4_SMOOTHQUANT")


def test_01_pytorch_to_onnx_export(onnx_exp):
    """Test 1: Verifies PyTorch model graph export to ONNX format."""
    res = onnx_exp.export_pytorch_to_onnx("Llama-7B", [1, 256])
    assert res.status == "ONNX_EXPORT_SUCCESS"
    assert res.onnx_file_path == "models/Llama-7B.onnx"
    assert res.constant_folding_optimized is True


def test_02_tensorrt_int4_smoothquant_compilation(trt_comp):
    """Test 2: Verifies TensorRT engine compilation with INT4 SmoothQuant quantization."""
    res = trt_comp.compile_tensorrt_engine("Llama-7B", max_batch_size=32)
    assert res.status == "TENSORRT_ENGINE_COMPILED"
    assert res.throughput_tokens_per_sec == 1480.0
    assert res.latency_p99_ms < 5.0
    assert res.gpu_memory_gb == 3.8


def test_03_tensorrt_fp8_precision_compilation():
    """Test 3: Verifies TensorRT compilation with FP8 precision."""
    trt_fp8 = TensorRTCompilerEngine(target_precision="FP8")
    res = trt_fp8.compile_tensorrt_engine("Llama-7B")
    assert res.throughput_tokens_per_sec == 1120.0
    assert res.gpu_memory_gb == 7.1


def test_04_tensorrt_fp16_precision_baseline():
    """Test 4: Verifies FP16 baseline compilation metrics."""
    trt_fp16 = TensorRTCompilerEngine(target_precision="FP16")
    res = trt_fp16.compile_tensorrt_engine("Llama-7B")
    assert res.gpu_memory_gb == 14.0


def test_05_orchestrator_end_to_end_pipeline(orchestrator):
    """Test 5: Verifies master TensorRT-LLM execution pipeline export and compilation."""
    res = orchestrator.export_and_compile_pipeline("Llama-3.2-7B")
    assert res["status"] == "TENSORRT_PIPELINE_SUCCESS"
    assert res["engine_file"] == "Llama-3.2-7B_INT4_SMOOTHQUANT.plan"
    assert res["throughput_tokens_per_sec"] > 1000.0


def test_06_throughput_comparison_int4_vs_fp16():
    """Test 6: Verifies INT4 SmoothQuant delivering higher throughput than FP16."""
    trt_int4 = TensorRTCompilerEngine(target_precision="INT4_SMOOTHQUANT")
    trt_fp16 = TensorRTCompilerEngine(target_precision="FP16")
    
    res_int4 = trt_int4.compile_tensorrt_engine("ModelA")
    res_fp16 = trt_fp16.compile_tensorrt_engine("ModelA")
    assert res_int4.throughput_tokens_per_sec > res_fp16.throughput_tokens_per_sec


def test_07_onnx_opset_version(onnx_exp):
    """Test 7: Verifies ONNX opset version configuration."""
    assert onnx_exp.opset == 18


def test_08_tensorrt_engine_file_naming(trt_comp):
    """Test 8: Verifies engine binary .plan file naming format."""
    res = trt_comp.compile_tensorrt_engine("Bert-Large")
    assert res.engine_name.endswith(".plan")


def test_09_onnx_export_large_sequence_length(onnx_exp):
    """Test 9 [Production Edge Case]: Verifies ONNX exporter with 32k context sequence length inputs."""
    res = onnx_exp.export_pytorch_to_onnx("LongContext-Llama", [1, 32768])
    assert res.status == "ONNX_EXPORT_SUCCESS"
    assert res.graph_nodes_count > 0


def test_10_tensorrt_large_batch_size(trt_comp):
    """Test 10 [Production Edge Case]: Verifies TensorRT compilation supporting max batch size=512."""
    res = trt_comp.compile_tensorrt_engine("Batch512-Model", max_batch_size=512)
    assert res.status == "TENSORRT_ENGINE_COMPILED"


def test_11_tensorrt_unknown_precision_fallback():
    """Test 11 [Production Edge Case]: Verifies fallback behavior when unknown precision mode is supplied."""
    trt_unknown = TensorRTCompilerEngine(target_precision="CUSTOM_PRECISION")
    res = trt_unknown.compile_tensorrt_engine("FallbackModel")
    assert res.target_precision == "CUSTOM_PRECISION"
    assert res.throughput_tokens_per_sec == 650.0  # FP16 default fallback


def test_12_orchestrator_custom_model_name(orchestrator):
    """Test 12 [Production Edge Case]: Verifies orchestrator handling custom fine-tuned model path names."""
    res = orchestrator.export_and_compile_pipeline("custom/org/llama-finetuned")
    assert res["status"] == "TENSORRT_PIPELINE_SUCCESS"
