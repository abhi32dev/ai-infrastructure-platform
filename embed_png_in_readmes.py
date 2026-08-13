import os

base_dir = "/Users/abhi/Documents/Antigravity"

dirs = [
    "01-agent-durable-runtime",
    "02-rag-cost-router", "02-agentic-workflow-engine",
    "03-llm-eval-gate", "03-high-throughput-rag-engine",
    "04-model-serving-mlops", "04-realtime-stream-feature-pipeline",
    "05-event-stream-pyspark-etl", "05-ml-observability-monitoring-stack",
    "06-finetuning-lora-alignment", "06-auto-scaling-inference-gateway",
    "07-cloud-iac-security-governance",
    "08-vllm-pagedattention-spec-decoding",
    "09-ray-distributed-cluster-orchestrator",
    "10-triton-cuda-gpu-scheduler",
    "11-distributed-training-fsdp-megatron",
    "12-genai-gateway-semantic-cache",
    "13-rlhf-dpo-alignment-pipeline",
    "14-custom-cuda-triton-kernel-opt",
    "15-feature-store-vector-lakehouse",
    "16-ai-safety-red-teaming-guardrails",
    "17-k8s-kuberay-kueue-gpu-operator",
    "18-tensorrt-llm-onnx-execution",
    "19-multi-agent-swarm-orchestrator",
    "20-data-governance-openlineage-catalog"
]

print("Embedding FLOWCHART.png into README.md files...")

for d in dirs:
    readme_path = os.path.join(base_dir, d, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
            
        img_md = "\n\n![2D Control Flow Diagram](FLOWCHART.png)\n\n"
        if "![2D Control Flow Diagram](FLOWCHART.png)" not in content:
            if "\n---\n" in content:
                content = content.replace("\n---\n", img_md + "---\n", 1)
            else:
                content = img_md + content
                
            with open(readme_path, "w") as f:
                f.write(content)
            print(f"Embedded FLOWCHART.png image into {d}/README.md")

print("Successfully embedded FLOWCHART.png images into all README.md files!")
