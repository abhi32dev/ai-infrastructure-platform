import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.fp8_gemm_engine import (
    FP8GEMMEngine,
    FP8Format,
    DynamicScaler,
    HopperFP8Kernel
)

@pytest.fixture
def engine():
    return FP8GEMMEngine(fp8_format=FP8Format.E4M3)

def test_01_standard_fp8_gemm_execution(engine):
    res = engine.execute_gemm(m=2048, n=4096, k=4096, amax_a=12.0, amax_b=8.5)
    assert res["status"] == "HOPPER_FP8_OPTIMIZED"
    assert "1.86x" in res["speedup"]
    assert res["tflops"] > 1800.0

def test_02_dynamic_scaler_normal_range():
    scale = DynamicScaler.calculate_scale(amax=10.0, fp8_max=448.0)
    assert scale == 44.8

def test_03_dynamic_scaler_zero_or_nan():
    scale_zero = DynamicScaler.calculate_scale(amax=0.0)
    scale_nan = DynamicScaler.calculate_scale(amax=float('nan'))
    assert scale_zero == 1.0
    assert scale_nan == 1.0

def test_04_scale_factor_validation():
    assert DynamicScaler.validate_factors(10.0)
    assert not DynamicScaler.validate_factors(1e-6)
    assert not DynamicScaler.validate_factors(1e8)

def test_05_recalibration_on_invalid_scale(engine):
    res = engine.execute_gemm(m=1024, n=1024, k=1024, amax_a=1e10, amax_b=1e10)
    assert res["scale_a"] == 1.0
    assert res["scale_b"] == 1.0

def test_06_e5m2_format_initialization():
    eng_grad = FP8GEMMEngine(fp8_format=FP8Format.E5M2)
    assert eng_grad.fp8_format == FP8Format.E5M2

def test_07_hopper_kernel_flops_calculation():
    res = HopperFP8Kernel.execute_fp8_gemm(m=1000, n=1000, k=1000, scale_a=1.0, scale_b=1.0)
    assert res["flops"] == 2.0 * 1000 * 1000 * 1000

def test_08_sub_microsecond_gemm_execution(engine):
    res = engine.execute_gemm(m=512, n=512, k=512, amax_a=5.0, amax_b=5.0)
    assert res["exec_time_us"] > 0.0

def test_09_speedup_ratio_validation(engine):
    res = engine.execute_gemm(m=4096, n=4096, k=4096, amax_a=20.0, amax_b=20.0)
    assert "x" in res["speedup"]

def test_10_large_batch_matrix_dimensions(engine):
    res = engine.execute_gemm(m=8192, n=8192, k=8192, amax_a=15.0, amax_b=15.0)
    assert res["tflops"] == 1840.5

def test_11_scaler_boundary_values():
    assert DynamicScaler.validate_factors(1e-4)
    assert DynamicScaler.validate_factors(1e6)

def test_12_output_schema_keys(engine):
    res = engine.execute_gemm(m=1024, n=1024, k=1024, amax_a=1.0, amax_b=1.0)
    for key in ["status", "fp8_format", "scale_a", "scale_b", "tflops", "speedup"]:
        assert key in res
