"""
CLI Demo Runner for Project 14 - Custom OpenAI Triton & CUDA GPU Kernel Optimization.
"""

from src.kernel_orchestrator import CustomKernelOptimizationOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 14: Custom OpenAI Triton & CUDA GPU Kernel Optimization")
    print("==================================================================")
    orch = CustomKernelOptimizationOrchestrator(block_size=128)
    res = orch.benchmark_and_profile_kernel(num_elements=1048576)
    print(f"Status: {res['status']}")
    print(f"Kernel: {res['kernel_name']} | Speedup: {res['fusion_speedup_factor']}x")
    print(f"Operational Intensity: {res['operational_intensity']} FLOPs/Byte")
    print(f"Roofline Bottleneck: {res['bottleneck_type']} (VRAM BW Util: {res['vram_bandwidth_utilization_pct']}%)")
    print("==================================================================")
