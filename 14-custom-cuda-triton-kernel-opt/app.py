"""
FastAPI REST Service for Project 14 - Custom OpenAI Triton & CUDA GPU Kernel Optimization.
"""

from fastapi import FastAPI
from src.kernel_orchestrator import CustomKernelOptimizationOrchestrator

app = FastAPI(title="Project 14 - Custom OpenAI Triton GPU Kernel Engine", version="2.0")
orchestrator = CustomKernelOptimizationOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "Custom OpenAI Triton GPU Kernel Engine"}


@app.post("/kernel/benchmark")
def benchmark_kernel(num_elements: int = 1048576):
    return orchestrator.benchmark_and_profile_kernel(num_elements=num_elements)
