"""
Expanded Test Suite for Project 14 - Custom OpenAI Triton & CUDA GPU Kernel Optimization.
Includes production edge cases for extreme tensor dimensions, zero FLOPs roofline checks, and multi-span timeline tracing.
"""

import pytest
from src.triton_fused_kernel import TritonFusedKernelEngine
from src.roofline_analyzer import RooflineAnalyzer
from src.nvtx_profiler import NVTXProfiler
from src.kernel_orchestrator import CustomKernelOptimizationOrchestrator


@pytest.fixture
def triton_engine():
    return TritonFusedKernelEngine(block_size=128)


@pytest.fixture
def roofline():
    return RooflineAnalyzer(peak_bandwidth_gbps=900.0, peak_tensor_tflops=312.0)


@pytest.fixture
def nvtx():
    return NVTXProfiler()


@pytest.fixture
def orchestrator():
    return CustomKernelOptimizationOrchestrator(block_size=128)


def test_01_triton_kernel_launch_grid(triton_engine):
    """Test 1: Verifies Triton kernel launch grid allocation for 1,048,576 elements."""
    res = triton_engine.launch_fused_bias_gelu_kernel(num_elements=1048576)
    assert res.grid_size == 8192  # ceil(1048576 / 128) = 8192 blocks
    assert res.fusion_speedup_factor >= 2.0
    assert res.status == "KERNEL_LAUNCH_SUCCESS"


def test_02_roofline_memory_bound_detection(roofline):
    """Test 2: Verifies Roofline model identifying memory-bound elementwise fused kernels."""
    # 8 FLOPs / 6 bytes = 1.33 FLOPs/Byte (far below A100 ridge point 346.6!)
    res = roofline.analyze_kernel_performance(flops=1048576 * 8.0, bytes_transferred=1048576 * 6.0, execution_time_us=1.35)
    assert res.bottleneck_type == "MEMORY_BOUND"
    assert res.operational_intensity_flops_per_byte == 1.33


def test_03_roofline_compute_bound_detection(roofline):
    """Test 3: Verifies Roofline model identifying compute-bound matrix GEMM kernels."""
    # 500 FLOPs/Byte (exceeds ridge point 346.6!)
    res = roofline.analyze_kernel_performance(flops=500000.0, bytes_transferred=1000.0, execution_time_us=2.0)
    assert res.bottleneck_type == "COMPUTE_BOUND"


def test_04_roofline_invalid_inputs(roofline):
    """Test 4: Verifies exception handling for non-positive Roofline metrics."""
    with pytest.raises(ValueError):
        roofline.analyze_kernel_performance(flops=100.0, bytes_transferred=0.0, execution_time_us=1.0)


def test_05_nvtx_trace_kernel_range(nvtx):
    """Test 5: Verifies NVTX range tracing and span recording."""
    span = nvtx.trace_kernel_range("fused_bias_gelu", "CUDA_KERNEL", 1.35)
    assert span.range_name == "fused_bias_gelu"
    summary = nvtx.get_timeline_summary()
    assert summary["total_spans_traced"] == 1


def test_06_kernel_orchestrator_profiling(orchestrator):
    """Test 6: Verifies end-to-end custom GPU kernel profiling orchestrator."""
    res = orchestrator.benchmark_and_profile_kernel(num_elements=1048576)
    assert res["status"] == "PROFILING_COMPLETED"
    assert res["bottleneck_type"] == "MEMORY_BOUND"
    assert res["fusion_speedup_factor"] > 2.0


def test_07_triton_different_block_sizes():
    """Test 7: Verifies Triton engine with custom block size=256."""
    eng_256 = TritonFusedKernelEngine(block_size=256)
    res = eng_256.launch_fused_bias_gelu_kernel(num_elements=1048576)
    assert res.grid_size == 4096  # ceil(1048576 / 256) = 4096 blocks


def test_08_nvtx_multiple_spans(nvtx):
    """Test 8: Verifies NVTX profiler tracking multiple sequential kernel passes."""
    nvtx.trace_kernel_range("attn_forward", "ATTENTION", 10.5)
    nvtx.trace_kernel_range("bias_gelu", "ACTIVATION", 1.5)
    summary = nvtx.get_timeline_summary()
    assert summary["total_spans_traced"] == 2
    assert summary["total_gpu_time_us"] == 12.0


def test_09_triton_small_tensor_elements(triton_engine):
    """Test 9 [Production Edge Case]: Verifies Triton kernel grid allocation on small tensor (1 element)."""
    res = triton_engine.launch_fused_bias_gelu_kernel(num_elements=1)
    assert res.grid_size == 1
    assert res.status == "KERNEL_LAUNCH_SUCCESS"


def test_10_roofline_h100_peak_specs():
    """Test 10 [Production Edge Case]: Verifies Roofline analyzer with NVIDIA H100 GPU specs (2000 GB/s, 989 TFLOPS)."""
    roofline_h100 = RooflineAnalyzer(peak_bandwidth_gbps=2000.0, peak_tensor_tflops=989.0)
    res = roofline_h100.analyze_kernel_performance(flops=100000.0, bytes_transferred=50000.0, execution_time_us=5.0)
    assert res.operational_intensity_flops_per_byte == 2.0
    assert res.bottleneck_type == "MEMORY_BOUND"


def test_11_nvtx_empty_timeline_summary(nvtx):
    """Test 11 [Production Edge Case]: Verifies NVTX profiler handling timeline summary with zero recorded spans."""
    summary = nvtx.get_timeline_summary()
    assert summary["total_spans_traced"] == 0
    assert summary["total_gpu_time_us"] == 0.0


def test_12_triton_block_size_512():
    """Test 12 [Production Edge Case]: Verifies Triton kernel launch with block size=512."""
    eng_512 = TritonFusedKernelEngine(block_size=512)
    res = eng_512.launch_fused_bias_gelu_kernel(num_elements=10000)
    assert res.grid_size == 20  # ceil(10000 / 512) = 20
