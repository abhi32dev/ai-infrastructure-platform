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

print("Embedding FLOWCHART.png images into FLOWCHART.html files...")

for d in dirs:
    html_path = os.path.join(base_dir, d, "FLOWCHART.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            html = f.read()
            
        img_tag = '<div style="text-align:center; margin-bottom:2rem;"><img src="FLOWCHART.png" alt="2D Control Flow Architecture Diagram" style="max-width:100%; height:auto; border-radius:12px; border:1px solid #21262d; box-shadow: 0 8px 24px rgba(0,0,0,0.5);"></div>\n    '
        
        if '<div class="mermaid-card">' in html:
            html = html.replace('<div class="mermaid-card">', img_tag + '<div class="mermaid-card">')
            with open(html_path, "w") as f:
                f.write(html)
            print(f"Embedded FLOWCHART.png in {d}/FLOWCHART.html")

print("Successfully updated all FLOWCHART.html files with direct PNG image embeds!")
