"""
FastAPI REST Service for Project 18 - TensorRT-LLM Engine & ONNX Execution.
"""

from fastapi import FastAPI
from src.tensorrt_orchestrator import TensorRTExecutionOrchestrator

app = FastAPI(title="Project 18 - TensorRT-LLM & ONNX Engine", version="2.0")
orchestrator = TensorRTExecutionOrchestrator()


@app.get("/")
def health_check():
    return {"status": "HEALTHY", "service": "TensorRT-LLM & ONNX Engine"}


@app.post("/tensorrt/compile")
def compile_engine(model_name: str = "Llama-3.2-7B"):
    return orchestrator.export_and_compile_pipeline(model_name=model_name)
