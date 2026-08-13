import os

projects = [
    {"num": "01", "dir": "01-agent-durable-runtime", "title": "Agentic Durable Runtime"},
    {"num": "02", "dir": "02-rag-cost-router", "title": "RAG Cost Router Engine"},
    {"num": "03", "dir": "03-llm-eval-gate", "title": "LLM Evaluation Gate"},
    {"num": "04", "dir": "04-model-serving-mlops", "title": "Model Serving MLOps"},
    {"num": "05", "dir": "05-event-stream-pyspark-etl", "title": "Event Stream PySpark ETL"},
    {"num": "06", "dir": "06-finetuning-lora-alignment", "title": "Fine-Tuning LoRA Alignment"},
    {"num": "07", "dir": "07-cloud-iac-security-governance", "title": "Cloud IaC Security Governance"},
    {"num": "08", "dir": "08-vllm-pagedattention-spec-decoding", "title": "vLLM PagedAttention & Speculative Decoding"},
    {"num": "09", "dir": "09-ray-distributed-cluster-orchestrator", "title": "Ray Distributed Cluster Orchestrator"},
    {"num": "10", "dir": "10-triton-cuda-gpu-scheduler", "title": "Triton CUDA GPU Scheduler"},
    {"num": "11", "dir": "11-distributed-training-fsdp-megatron", "title": "Distributed Training (FSDP & Megatron)"},
    {"num": "12", "dir": "12-genai-gateway-semantic-cache", "title": "GenAI Gateway & Semantic Cache"},
    {"num": "13", "dir": "13-rlhf-dpo-alignment-pipeline", "title": "RLHF DPO Alignment Pipeline"},
    {"num": "14", "dir": "14-custom-cuda-triton-kernel-opt", "title": "Custom OpenAI Triton GPU Kernels"},
    {"num": "15", "dir": "15-feature-store-vector-lakehouse", "title": "Feature Store & Vector Lakehouse"},
    {"num": "16", "dir": "16-ai-safety-red-teaming-guardrails", "title": "AI Safety & Policy Guardrails"},
    {"num": "17", "dir": "17-k8s-kuberay-kueue-gpu-operator", "title": "K8s KubeRay & Kueue GPU Operator"},
    {"num": "18", "dir": "18-tensorrt-llm-onnx-execution", "title": "TensorRT-LLM Engine & ONNX"},
    {"num": "19", "dir": "19-multi-agent-swarm-orchestrator", "title": "Multi-Agent Swarm Orchestrator"},
    {"num": "20", "dir": "20-data-governance-openlineage-catalog", "title": "Data Governance & OpenLineage"}
]

base_dir = "/Users/abhi/Documents/Antigravity"

banner_template = """
> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/{dir}/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**

---
"""

for proj in projects:
    proj_path = os.path.join(base_dir, proj["dir"])
    readme_path = os.path.join(proj_path, "README.md")
    
    banner = banner_template.format(dir=proj["dir"])
    
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
            
        # Avoid duplicate banners
        if "CLICK HERE TO VIEW LIVE RENDERED FLOWCHART" not in content:
            lines = content.splitlines()
            # Insert banner after title line
            if lines and lines[0].startswith("#"):
                new_content = lines[0] + "\n" + banner + "\n".join(lines[1:])
            else:
                new_content = banner + content
                
            with open(readme_path, "w") as f:
                f.write(new_content)
            print(f"Updated README.md for {proj['dir']}")
    else:
        # Create a new README.md
        new_content = f"# Project {proj['num']}: {proj['title']}\n\n" + banner + f"\n\nProduction AI Infrastructure module for {proj['title']}.\n"
        with open(readme_path, "w") as f:
            f.write(new_content)
        print(f"Created README.md for {proj['dir']}")

print("Successfully injected live flowchart links into all project README files!")
