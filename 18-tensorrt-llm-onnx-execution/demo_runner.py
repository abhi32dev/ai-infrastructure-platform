"""
CLI Demo Runner for Project 18 - TensorRT-LLM Engine & ONNX Execution.
"""

from src.tensorrt_orchestrator import TensorRTExecutionOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 18: NVIDIA TensorRT-LLM Engine & ONNX High-Throughput")
    print("==================================================================")
    orch = TensorRTExecutionOrchestrator(precision="INT4_SMOOTHQUANT")
    res = orch.export_and_compile_pipeline("Llama-3.2-7B")
    print(f"Status: {res['status']} | Model: {res['model_name']}")
    print(f"Engine Plan: {res['engine_file']} ({res['precision']})")
    print(f"Throughput: {res['throughput_tokens_per_sec']} tokens/sec | P99 Latency: {res['latency_p99_ms']} ms")
    print(f"VRAM Memory: {res['vram_gb']} GB")
    print("==================================================================")
