import os

base_dir = "/Users/abhi/Documents/Antigravity"

# Template generator for crisp, 100% self-contained, responsive 2D SVG Flowchart diagrams
def create_svg(num, title, file_path, d1_title, d1_sub, d1_left_text, d1_right_text, d2_title, d2_sub, d2_yes_text, d2_no_text, d3_title, d3_sub):
    return f"""<svg viewBox="0 0 960 700" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#34d399"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#fbbf24"/>
    </marker>
    <marker id="arrow-rose" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#f43f5e"/>
    </marker>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161c27" stroke-width="1"/>
  </pattern>
  <rect width="100%" height="100%" fill="url(#grid)" />

  <!-- Start Node -->
  <g transform="translate(360, 20)">
    <rect width="240" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="14">▶ Start: Project {num} Entry</text>
  </g>

  <path d="M 480 65 L 480 105" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Ingest & Validate -->
  <g transform="translate(330, 110)">
    <rect width="300" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="150" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">Ingest &amp; Validate Input Payload</text>
    <text x="150" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">{file_path}</text>
  </g>

  <path d="M 480 160 L 480 195" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- DECISION 1 DIAMOND -->
  <g transform="translate(480, 240)">
    <polygon points="0,-40 160,0 0,40 -160,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-8" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="12">DECISION 1</text>
    <text x="0" y="10" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="11">{d1_title}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">({d1_sub})</text>
  </g>

  <!-- LEFT BRANCH: Fast Path / Cache / Pass -->
  <path d="M 320 240 L 160 240 L 160 305" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="190" y="220" width="100" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="240" y="235" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">YES (Fast-Path)</text>

  <g transform="translate(40, 310)">
    <rect width="240" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="120" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="12">{d1_left_text}</text>
    <text x="120" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="10">Optimized Execution</text>
  </g>

  <path d="M 160 360 L 160 415" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(40, 420)">
    <rect width="240" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">✔ Fast Complete ($0.00)</text>
  </g>

  <!-- RIGHT / DOWN BRANCH: Processing Path -->
  <path d="M 480 280 L 480 325" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="490" y="288" width="110" height="22" rx="4" fill="#12161f" stroke="#38bdf8" stroke-width="1"/>
  <text x="545" y="303" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">NO (Proceed)</text>

  <g transform="translate(330, 330)">
    <rect width="300" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="150" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">{d1_right_text}</text>
    <text x="150" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">Core Transformation Engine</text>
  </g>

  <path d="M 480 380 L 480 415" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- DECISION 2 DIAMOND -->
  <g transform="translate(480, 460)">
    <polygon points="0,-40 150,0 0,40 -150,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-8" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="12">DECISION 2</text>
    <text x="0" y="10" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="11">{d2_title}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">({d2_sub})</text>
  </g>

  <!-- DOWN BRANCH: Success -->
  <path d="M 480 500 L 480 545" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="490" y="508" width="100" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="540" y="523" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">YES (Passed)</text>

  <g transform="translate(330, 550)">
    <rect width="300" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="150" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">{d2_yes_text}</text>
    <text x="150" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="11">State Persisted / Artifact Exported</text>
  </g>

  <path d="M 480 600 L 480 635" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(360, 640)">
    <rect width="240" height="40" rx="20" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="25" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">★ Execution Verified</text>
  </g>

  <!-- RIGHT BRANCH: Fail / Fallback -->
  <path d="M 630 460 L 730 460" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="640" y="435" width="80" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="680" y="450" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">NO (Fallback)</text>

  <!-- DECISION 3 DIAMOND (Error / Recovery) -->
  <g transform="translate(830, 460)">
    <polygon points="0,-35 100,0 0,35 -100,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2"/>
    <text x="0" y="-5" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="11">DECISION 3</text>
    <text x="0" y="12" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="10">{d3_title}</text>
  </g>

  <!-- UPWARD LOOP ARROW (Retry / Loop Up) -->
  <path d="M 830 425 C 830 350, 720 350, 630 350" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-amber)"/>
  <rect x="700" y="325" width="110" height="22" rx="4" fill="#2d2206" stroke="#fbbf24" stroke-width="1"/>
  <text x="755" y="340" text-anchor="middle" fill="#fbbf24" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">↻ YES (Loop Up)</text>

  <!-- DOWN BRANCH: Fallback Execution -->
  <path d="M 830 495 L 830 550" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="840" y="508" width="90" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="885" y="523" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">NO (Fallback)</text>

  <g transform="translate(710, 555)">
    <rect width="240" height="50" rx="8" fill="#12161f" stroke="#f43f5e" stroke-width="1.5"/>
    <text x="120" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="12">{d2_no_text}</text>
    <text x="120" y="38" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-size="11">Fallback Routine Active</text>
  </g>
</svg>"""

projects = [
    {
        "num": "01", "dir": "01-agent-durable-runtime", "title": "Agentic Durable Runtime",
        "file": "src/agent_runtime.py",
        "d1_title": "Step Already Executed?", "d1_sub": "SQLite WAL Lookup", "d1_left_text": "Retrieve Cached State", "d1_right_text": "Execute Agent Tool Call",
        "d2_title": "Tool Execution Succeeded?", "d2_sub": "Zero Exceptions", "d2_yes_text": "Write WAL Checkpoint to SQLite", "d2_no_text": "Escalate to HITL Queue",
        "d3_title": "Retry Count < 3?", "d3_sub": "Bounded Retries"
    },
    {
        "num": "02", "dir": "02-rag-cost-router", "title": "RAG Cost Router Engine",
        "file": "src/rag_pipeline.py",
        "d1_title": "Vector Cache Hit (Sim >= 0.95)?", "d1_sub": "ChromaDB Embedding", "d1_left_text": "Return Cached Answer ($0.00)", "d1_right_text": "Calculate Query Complexity",
        "d2_title": "Query Complexity <= 0.4?", "d2_sub": "Simple Lookup Tier", "d2_yes_text": "Route to Local Ollama Model", "d2_no_text": "Route to Frontier GPT-4o",
        "d3_title": "Score > 0.8?", "d3_sub": "Multi-Hop Tier"
    },
    {
        "num": "03", "dir": "03-llm-eval-gate", "title": "LLM Evaluation Gate",
        "file": "src/eval_gate.py",
        "d1_title": "p-value < 0.05 & Delta > 0.05?", "d1_sub": "Welch t-Test Gate", "d1_left_text": "Pass Statistical Gate", "d1_right_text": "Evaluate Toxicity Safety",
        "d2_title": "Toxicity Score <= 0.05?", "d2_sub": "Safety Threshold", "d2_yes_text": "Register Artifact in MLflow", "d2_no_text": "Block Release & Alert",
        "d3_title": "Re-eval Iteration?", "d3_sub": "Sample Check"
    },
    {
        "num": "04", "dir": "04-model-serving-mlops", "title": "Model Serving MLOps",
        "file": "src/model_serving.py",
        "d1_title": "Queue Depth > Max 50?", "d1_sub": "Backpressure Check", "d1_left_text": "Reject with HTTP 429", "d1_right_text": "Evaluate Canary Roll Split",
        "d2_title": "Roll < Canary Weight 10%?", "d2_sub": "Canary Traffic Split", "d2_yes_text": "Route to Canary v2 Model", "d2_no_text": "Route to Production v1",
        "d3_title": "Node Healthy?", "d3_sub": "Health Audit"
    },
    {
        "num": "05", "dir": "05-event-stream-pyspark-etl", "title": "Event Stream PySpark ETL",
        "file": "src/event_pipeline.py",
        "d1_title": "Event < Watermark Boundary?", "d1_sub": "10-Min Watermark", "d1_left_text": "Drop Expired Late Event", "d1_right_text": "Deduplicate & 3-Pass Reconcile",
        "d2_title": "Schema Contract Valid?", "d2_sub": "Gold Layer Contract", "d2_yes_text": "Atomically Write Delta Lake", "d2_no_text": "Quarantine to DLQ S3",
        "d3_title": "Retry Stream?", "d3_sub": "Checkpoint Reset"
    },
    {
        "num": "06", "dir": "06-finetuning-lora-alignment", "title": "Fine-Tuning LoRA Alignment",
        "file": "src/lora_trainer.py",
        "d1_title": "Dataset Split Verified?", "d1_sub": "Curator Check", "d1_left_text": "Fast Validation Pass", "d1_right_text": "Inject LoRA Matrix Layers",
        "d2_title": "Validation Loss Converged?", "d2_sub": "Epoch Loss Curve", "d2_yes_text": "Fuse LoRA & Export GGUF", "d2_no_text": "Adjust Learning Rate",
        "d3_title": "Epoch Max Reached?", "d3_sub": "Loop Limit"
    },
    {
        "num": "07", "dir": "07-cloud-iac-security-governance", "title": "Cloud IaC Security Governance",
        "file": "src/cloud_governance.py",
        "d1_title": "Wildcard IAM Action=='*'?", "d1_sub": "IAM Policy AST Scan", "d1_left_text": "Flag CRITICAL Offense", "d1_right_text": "Audit Storage Encryption",
        "d2_title": "Total Offenses == 0?", "d2_sub": "Policy Gate", "d2_yes_text": "Approve IaC Deployment", "d2_no_text": "Fail Security Build Gate",
        "d3_title": "KMS Key Active?", "d3_sub": "KMS Audit"
    },
    {
        "num": "08", "dir": "08-vllm-pagedattention-spec-decoding", "title": "vLLM PagedAttention & Speculative Decoding",
        "file": "src/vllm_engine.py",
        "d1_title": "Free VRAM Blocks >= Needed?", "d1_sub": "Paged KV Memory", "d1_left_text": "Bind Logical Block Map", "d1_right_text": "Draft K-Token Speculation",
        "d2_title": "All K Draft Tokens Accepted?", "d2_sub": "Target Verification", "d2_yes_text": "Advance Sequence by K Pos", "d2_no_text": "Reclaim Invalid KV Blocks",
        "d3_title": "Host RAM Available?", "d3_sub": "CPU Eviction"
    },
    {
        "num": "09", "dir": "09-ray-distributed-cluster-orchestrator", "title": "Ray Distributed Cluster Orchestrator",
        "file": "src/ray_cluster.py",
        "d1_title": "Queue Depth > Scale Threshold?", "d1_sub": "Autoscaler Check", "d1_left_text": "SCALE UP New Ray Nodes", "d1_right_text": "Plasma Shared Memory Write",
        "d2_title": "Worker Idle Time > 300s?", "d2_sub": "Capacity Audit", "d2_yes_text": "Dispatch Task to Actor Pool", "d2_no_text": "SCALE DOWN Idle Nodes",
        "d3_title": "Actor Active?", "d3_sub": "Health Check"
    },
    {
        "num": "10", "dir": "10-triton-cuda-gpu-scheduler", "title": "Triton CUDA GPU Scheduler",
        "file": "src/triton_engine.py",
        "d1_title": "Batch == 32 OR Delay >= 10ms?", "d1_sub": "Dynamic Batching Queue", "d1_left_text": "Execute AWQ INT4 Kernel", "d1_right_text": "Align Tensor Tensor Cores",
        "d2_title": "Kernel Execution Passed?", "d2_sub": "CUDA Execution", "d2_yes_text": "Scatter Outputs to Futures", "d2_no_text": "Fallback Unbatched Pass",
        "d3_title": "Queue Overflow?", "d3_sub": "Buffer Check"
    },
    {
        "num": "11", "dir": "11-distributed-training-fsdp-megatron", "title": "Distributed Training (FSDP & Megatron)",
        "file": "src/distributed_training.py",
        "d1_title": "FSDP ZeRO-3 Sharding Complete?", "d1_sub": "3D Grid Mesh", "d1_left_text": "Execute All-Gather Forward", "d1_right_text": "Execute Reduce-Scatter Back",
        "d2_title": "Gradient Norm Normal?", "d2_sub": "Gradient Stability", "d2_yes_text": "Update Sharded Optimizer", "d2_no_text": "Skip Step & Clip Gradients",
        "d3_title": "Epoch End?", "d3_sub": "Checkpoint Save"
    },
    {
        "num": "12", "dir": "12-genai-gateway-semantic-cache", "title": "GenAI Gateway & Semantic Cache",
        "file": "src/genai_gateway.py",
        "d1_title": "Token Bucket Capacity > 0?", "d1_sub": "Rate Limiter Check", "d1_left_text": "Return Cached Hit (<5ms)", "d1_right_text": "Vector Semantic Cache Search",
        "d2_title": "Primary OpenAI Succeeded?", "d2_sub": "Provider Cascade", "d2_yes_text": "Write Cache & Return Result", "d2_no_text": "Fallback to Anthropic/Ollama",
        "d3_title": "Retry Fallback?", "d3_sub": "Timeout Cascade"
    },
    {
        "num": "13", "dir": "13-rlhf-dpo-alignment-pipeline", "title": "RLHF DPO Alignment Pipeline",
        "file": "src/dpo_alignment.py",
        "d1_title": "Preference Data Pairs Loaded?", "d1_sub": "Dataset Curator", "d1_left_text": "Evaluate Policy Logps", "d1_right_text": "Compute DPO Loss Beta",
        "d2_title": "Win-Rate Audit >= 75%?", "d2_sub": "Bradley-Terry Audit", "d2_yes_text": "Export Aligned Checkpoint", "d2_no_text": "Adjust Beta & Retrain",
        "d3_title": "Loss Converged?", "d3_sub": "Loss Check"
    },
    {
        "num": "14", "dir": "14-custom-cuda-triton-kernel-opt", "title": "Custom OpenAI Triton GPU Kernels",
        "file": "src/triton_kernels.py",
        "d1_title": "VRAM Tensors Allocated?", "d1_sub": "Memory Stride", "d1_left_text": "Launch Grid BLOCK_1024", "d1_right_text": "Execute Fused Bias-GELU",
        "d2_title": "Roofline Speedup >= 1.5x?", "d2_sub": "Roofline TFLOPS", "d2_yes_text": "Register Fused GPU Kernel", "d2_no_text": "Re-tune Vector Stride",
        "d3_title": "Occupancy Max?", "d3_sub": "SRAM Audit"
    },
    {
        "num": "15", "dir": "15-feature-store-vector-lakehouse", "title": "Feature Store & Vector Lakehouse",
        "file": "src/feature_lakehouse.py",
        "d1_title": "Features Present in Redis?", "d1_sub": "Online Cache Check", "d1_left_text": "Return Online Features (<2ms)", "d1_right_text": "PyArrow Time-Travel ASOF",
        "d2_title": "Point-in-Time Join Valid?", "d2_sub": "No Feature Leakage", "d2_yes_text": "Populate Redis Cache & Return", "d2_no_text": "Fallback Default Features",
        "d3_title": "Redis Connected?", "d3_sub": "Health Check"
    },
    {
        "num": "16", "dir": "16-ai-safety-red-teaming-guardrails", "title": "AI Safety & Policy Guardrails",
        "file": "src/safety_guardrails.py",
        "d1_title": "Jailbreak / Injection Detected?", "d1_sub": "DAN Pattern Scanner", "d1_left_text": "Reject HTTP 400 Violation", "d1_right_text": "Redact Sensitive PII Tokens",
        "d2_title": "Llama Guard Output Safe?", "d2_sub": "Output Policy Verification", "d2_yes_text": "Emit Safe Anonymized Output", "d2_no_text": "Redact Unsafe Response",
        "d3_title": "NER Active?", "d3_sub": "PII Rule Scan"
    },
    {
        "num": "17", "dir": "17-k8s-kuberay-kueue-gpu-operator", "title": "K8s KubeRay & Kueue GPU Operator",
        "file": "src/k8s_gpu.py",
        "d1_title": "ClusterQueue GPU Quota Available?", "d1_sub": "Kueue Batch Scheduler", "d1_left_text": "Admit Job & Deploy KubeRay", "d1_right_text": "Evaluate Preemption Priority",
        "d2_title": "Job Priority > Running?", "d2_sub": "Preemption Rule", "d2_yes_text": "Preempt & Slice MIG 1g.10gb", "d2_no_text": "Queue in Pending Queue",
        "d3_title": "MIG Sliced?", "d3_sub": "Device Check"
    },
    {
        "num": "18", "dir": "18-tensorrt-llm-onnx-execution", "title": "TensorRT-LLM Engine & ONNX",
        "file": "src/tensorrt_engine.py",
        "d1_title": "Dynamic ONNX Export Success?", "d1_sub": "Graph Trace", "d1_left_text": "INT4 SmoothQuant Scale", "d1_right_text": "Compile TensorRT Plan Engine",
        "d2_title": "Latency < 5ms P99 Target?", "d2_sub": "Engine Throughput Target", "d2_yes_text": "Save .engine Plan File", "d2_no_text": "Fallback to FP16 Mode",
        "d3_title": "SmoothQuant Passed?", "d3_sub": "Scale Check"
    },
    {
        "num": "19", "dir": "19-multi-agent-swarm-orchestrator", "title": "Multi-Agent Swarm Orchestrator",
        "file": "src/swarm_orchestrator.py",
        "d1_title": "Circular Dependency Cycle Detected?", "d1_sub": "Kahn Topological Sort", "d1_left_text": "Abort CycleDeadlockException", "d1_right_text": "Dispatch Agent Workers Parallel",
        "d2_title": "Voting Consensus Score >= 66%?", "d2_sub": "Consensus Engine", "d2_yes_text": "Emit Verified Result Payload", "d2_no_text": "Invoke Tie-Breaker Agent",
        "d3_title": "Workers Free?", "d3_sub": "Worker Pool"
    },
    {
        "num": "20", "dir": "20-data-governance-openlineage-catalog", "title": "Data Governance & OpenLineage",
        "file": "src/data_governance.py",
        "d1_title": "Data Contract Check Passed?", "d1_sub": "Great Expectations Validator", "d1_left_text": "Emit OpenLineage ABORT", "d1_right_text": "Emit OpenLineage START Event",
        "d2_title": "Transformation Job Succeeded?", "d2_sub": "Marquez Lineage Graph", "d2_yes_text": "Emit COMPLETE Event & Rows", "d2_no_text": "Quarantine Dataset & Alert",
        "d3_title": "Marquez Up?", "d3_sub": "API Check"
    }
]

print("Injecting pure SVG vector 2D flowcharts into all 20 FLOWCHART.html files...")

for proj in projects:
    svg_content = create_svg(
        num=proj["num"],
        title=proj["title"],
        file_path=proj["file"],
        d1_title=proj["d1_title"],
        d1_sub=proj["d1_sub"],
        d1_left_text=proj["d1_left_text"],
        d1_right_text=proj["d1_right_text"],
        d2_title=proj["d2_title"],
        d2_sub=proj["d2_sub"],
        d2_yes_text=proj["d2_yes_text"],
        d2_no_text=proj["d2_no_text"],
        d3_title=proj["d3_title"],
        d3_sub=proj["d3_sub"]
    )
    
    flowchart_path = os.path.join(base_dir, proj["dir"], "FLOWCHART.html")
    if os.path.exists(flowchart_path):
        with open(flowchart_path, "r") as f:
            html = f.read()
            
        # Replace the mermaid div container with our self-contained inline SVG graphic
        if '<div class="mermaid-card">' in html:
            start_idx = html.find('<div class="mermaid-card">')
            end_idx = html.find('</div>\n    </div>\n\n    <div class="section-title">\n        <span>⚡ Exhaustive')
            
            if end_idx != -1:
                new_card_content = f'<div class="mermaid-card">\n{svg_content}\n    </div>'
                new_html = html[:start_idx] + new_card_content + html[end_idx + 18:]
                
                with open(flowchart_path, "w") as f:
                    f.write(new_html)
                print(f"Injected SVG 2D flowchart into {proj['dir']}/FLOWCHART.html")

print("All 20 FLOWCHART.html files updated with pure 2D Inline SVG Vector Graphic Flowcharts!")
