"""
GPU Memory Bandwidth vs Compute TFLOPS Roofline Analyzer.
Calculates Operational Intensity (FLOPs / Byte) and determines whether a kernel is
Memory-Bound (VRAM bandwidth limited) or Compute-Bound (Tensor Core TFLOPS limited).
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class RooflineAnalysis(BaseModel):
    operational_intensity_flops_per_byte: float
    attainable_performance_tflops: float
    bottleneck_type: str  # MEMORY_BOUND or COMPUTE_BOUND
    peak_vram_bandwidth_pct: float
    peak_tensor_tflops_pct: float


class RooflineAnalyzer:
    def __init__(self, peak_bandwidth_gbps: float = 900.0, peak_tensor_tflops: float = 312.0):
        self.peak_bw = peak_bandwidth_gbps      # e.g., A100 SXM 900 GB/s
        self.peak_tflops = peak_tensor_tflops  # e.g., A100 FP16 Tensor Core 312 TFLOPS

    def analyze_kernel_performance(self, flops: float, bytes_transferred: float, execution_time_us: float) -> RooflineAnalysis:
        """
        Calculates Roofline model metrics:
        Operational Intensity I = FLOPs / Bytes
        Ridge Point I_ridge = Peak_TFLOPS / Peak_Bandwidth = 312 / 0.9 = 346.6 FLOPs/Byte
        """
        if bytes_transferred <= 0 or execution_time_us <= 0:
            raise ValueError("Bytes and time must be positive numbers")

        op_intensity = round(flops / bytes_transferred, 2)
        achieved_tflops = round((flops / (execution_time_us * 1e-6)) / 1e12, 2)
        achieved_bw = round((bytes_transferred / (execution_time_us * 1e-6)) / 1e9, 2)

        ridge_point = (self.peak_tflops * 1e12) / (self.peak_bw * 1e9)
        bottleneck = "MEMORY_BOUND" if op_intensity < ridge_point else "COMPUTE_BOUND"

        bw_pct = round((achieved_bw / self.peak_bw) * 100.0, 2)
        tflops_pct = round((achieved_tflops / self.peak_tflops) * 100.0, 2)

        return RooflineAnalysis(
            operational_intensity_flops_per_byte=op_intensity,
            attainable_performance_tflops=achieved_tflops,
            bottleneck_type=bottleneck,
            peak_vram_bandwidth_pct=min(100.0, bw_pct),
            peak_tensor_tflops_pct=min(100.0, tflops_pct)
        )
