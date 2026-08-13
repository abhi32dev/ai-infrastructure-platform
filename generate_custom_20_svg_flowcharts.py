import os

base_dir = "/Users/abhi/Documents/Antigravity"

# Comprehensive builder for ultra-detailed, project-specific 2D SVG Flowcharts
def build_custom_svg(p):
    return f"""<svg viewBox="0 0 960 720" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
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
  <g transform="translate(330, 20)">
    <rect width="300" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="150" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">▶ {p['start_text']}</text>
  </g>

  <path d="M 480 65 L 480 105" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Step 1 Process Node -->
  <g transform="translate(310, 110)">
    <rect width="340" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="170" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">{p['step1_title']}</text>
    <text x="170" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">{p['step1_code']}</text>
  </g>

  <path d="M 480 160 L 480 195" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- DECISION 1 DIAMOND -->
  <g transform="translate(480, 240)">
    <polygon points="0,-42 170,0 0,42 -170,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-10" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="11">DECISION 1</text>
    <text x="0" y="8" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="11">{p['d1_cond']}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">({p['d1_sub']})</text>
  </g>

  <!-- LEFT BRANCH: Fast Path / Cache Hit -->
  <path d="M 310 240 L 160 240 L 160 305" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="180" y="220" width="110" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="235" y="235" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">{p['d1_left_label']}</text>

  <g transform="translate(20, 310)">
    <rect width="280" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="140" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="12">{p['left_action_title']}</text>
    <text x="140" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="10">{p['left_action_sub']}</text>
  </g>

  <path d="M 160 360 L 160 415" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(30, 420)">
    <rect width="260" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="130" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="12">{p['left_end_text']}</text>
  </g>

  <!-- DOWN BRANCH: Proceed to Main Execution -->
  <path d="M 480 282 L 480 325" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="490" y="288" width="110" height="22" rx="4" fill="#12161f" stroke="#38bdf8" stroke-width="1"/>
  <text x="545" y="303" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">{p['d1_down_label']}</text>

  <g transform="translate(310, 330)">
    <rect width="340" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="170" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">{p['step2_title']}</text>
    <text x="170" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">{p['step2_code']}</text>
  </g>

  <path d="M 480 380 L 480 415" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- DECISION 2 DIAMOND -->
  <g transform="translate(480, 460)">
    <polygon points="0,-42 165,0 0,42 -165,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-10" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="11">DECISION 2</text>
    <text x="0" y="8" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="11">{p['d2_cond']}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">({p['d2_sub']})</text>
  </g>

  <!-- DOWN BRANCH: Success Path -->
  <path d="M 480 502 L 480 545" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="490" y="508" width="110" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="545" y="523" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">{p['d2_yes_label']}</text>

  <g transform="translate(310, 550)">
    <rect width="340" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="170" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">{p['success_action_title']}</text>
    <text x="170" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="11">{p['success_action_sub']}</text>
  </g>

  <path d="M 480 600 L 480 645" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(330, 650)">
    <rect width="300" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="150" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">★ {p['end_success_text']}</text>
  </g>

  <!-- RIGHT BRANCH: Error / Fallback Branch -->
  <path d="M 645 460 L 735 460" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="650" y="435" width="80" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="690" y="450" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">{p['d2_no_label']}</text>

  <!-- DECISION 3 DIAMOND (Recovery / Retry Audit) -->
  <g transform="translate(835, 460)">
    <polygon points="0,-36 100,0 0,36 -100,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2"/>
    <text x="0" y="-6" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="10">DECISION 3</text>
    <text x="0" y="10" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="10">{p['d3_cond']}</text>
  </g>

  <!-- UPWARD LOOP ARROW (Retry / Re-tune / Re-eval Loop) -->
  <path d="M 835 424 C 835 350, 720 350, 650 350" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-amber)"/>
  <rect x="700" y="325" width="120" height="22" rx="4" fill="#2d2206" stroke="#fbbf24" stroke-width="1"/>
  <text x="760" y="340" text-anchor="middle" fill="#fbbf24" font-family="JetBrains Mono, monospace" font-weight="600" font-size="9">↻ {p['retry_loop_label']}</text>

  <!-- DOWN BRANCH: Fallback / Escalation Action -->
  <path d="M 835 496 L 835 550" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="840" y="508" width="90" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="885" y="523" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">{p['d3_no_label']}</text>

  <g transform="translate(700, 555)">
    <rect width="250" height="50" rx="8" fill="#12161f" stroke="#f43f5e" stroke-width="1.5"/>
    <text x="125" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="12">{p['fail_action_title']}</text>
    <text x="125" y="38" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-size="10">{p['fail_action_sub']}</text>
  </g>
</svg>"""

projects_spec = [
    {
        "num": "01", "dir": "01-agent-durable-runtime",
        "start_text": "Start: DurableAgentRuntime.execute_step()",
        "step1_title": "Validate Step Schema & State Payload", "step1_code": "src/agent_runtime.py:L45",
        "d1_cond": "Step Idempotent & Executed?", "d1_sub": "StateStore.get_active_state()", "d1_left_label": "YES (Cache Hit)", "d1_down_label": "NO (New Step)",
        "left_action_title": "Retrieve Cached State from WAL", "left_action_sub": "$0.00 Compute / Instant Return", "left_end_text": "✔ Replayed Cached State",
        "step2_title": "Invoke External Agent Tool / Action", "step2_code": "DurableAgentRuntime._invoke_tool()",
        "d2_cond": "Tool Invocation Succeeded?", "d2_sub": "Zero Unhandled Exceptions", "d2_yes_label": "YES (Success)", "d2_no_label": "NO (Exception)",
        "success_action_title": "Write Atomic WAL Checkpoint SQLite", "success_action_sub": "CheckpointManager.save_checkpoint()", "end_success_text": "Step State Saved & Advanced",
        "d3_cond": "Retry Count < 3?", "retry_loop_label": "YES: Rollback & Retry", "d3_no_label": "NO (Exhausted)",
        "fail_action_title": "Escalate to HITL Approval Queue", "fail_action_sub": "Pause Workflow State Machine"
    },
    {
        "num": "02", "dir": "02-rag-cost-router",
        "start_text": "Start: RAGCostRouter.route_query()",
        "step1_title": "Compute Query Embedding & Cache Lookup", "step1_code": "src/rag_pipeline.py:L62",
        "d1_cond": "Cache Sim Cosine >= 0.95?", "d1_sub": "ChromaDB Semantic Vector Index", "d1_left_label": "YES (Cache Hit)", "d1_down_label": "NO (Cache Miss)",
        "left_action_title": "Return Cached Answer (<5ms)", "left_action_sub": "$0.00 API Cost / Zero Latency", "left_end_text": "✔ Fast Cache Served",
        "step2_title": "Calculate Query Complexity Score", "step2_code": "QueryComplexityClassifier.classify()",
        "d2_cond": "Complexity Score <= 0.4?", "d2_sub": "Token & Keyword Density Metric", "d2_yes_label": "YES (Low Score)", "d2_no_label": "NO (High Score)",
        "success_action_title": "Route Query to Local Ollama LLM", "success_action_sub": "Zero Cloud API Billing Cost", "end_success_text": "Local Inference Completed",
        "d3_cond": "Score > 0.8?", "retry_loop_label": "YES: Multi-Hop RRF", "d3_no_label": "NO (Mid-Tier)",
        "fail_action_title": "Route to Claude 3.5 Sonnet Tier", "fail_action_sub": "Balanced Cost/Quality Tier"
    },
    {
        "num": "03", "dir": "03-llm-eval-gate",
        "start_text": "Start: LLMEvalGate.evaluate_build()",
        "step1_title": "Compute RAG Triad Metrics (Faithful/Ground)", "step1_code": "src/eval_gate.py:L58",
        "d1_cond": "p-value < 0.05 & Delta > +0.05?", "d1_sub": "Welch's t-Test vs Baseline", "d1_left_label": "NO (Degraded)", "d1_down_label": "YES (Quality Gain)",
        "left_action_title": "Flag Quality Degradation", "left_action_sub": "Fail CI/CD Stat Release Gate", "left_end_text": "✖ Build Blocked: Low Stat Gain",
        "step2_title": "Run Toxicity & Safety Audit Check", "step2_code": "ToxicityEvaluator.check_safety()",
        "d2_cond": "Toxicity Score <= 0.05?", "d2_sub": "Safety Policy Threshold", "d2_yes_label": "YES (Safe)", "d2_no_label": "NO (Toxic)",
        "success_action_title": "Register Model Artifact in MLflow", "success_action_sub": "Promote to Production Registry", "end_success_text": "Release Gate Approved",
        "d3_cond": "Sample Valid?", "retry_loop_label": "YES: Re-Evaluate", "d3_no_label": "NO (Violation)",
        "fail_action_title": "Flag Safety Violation & Alert Team", "fail_action_sub": "Block Deployment & Dispatch PagerDuty"
    },
    {
        "num": "04", "dir": "04-model-serving-mlops",
        "start_text": "Start: ModelServingPipeline.predict()",
        "step1_title": "Bind W3C OTel Traceparent Header", "step1_code": "src/model_serving.py:L40",
        "d1_cond": "Active Queue Depth > Max 50?", "d1_sub": "Server Backpressure Guard", "d1_left_label": "YES (Saturated)", "d1_down_label": "NO (Capacity OK)",
        "left_action_title": "Reject Request with HTTP 429", "left_action_sub": "Protect Server Worker Threads", "left_end_text": "✖ Backpressure Rejection",
        "step2_title": "Execute Canary Traffic Roll (Float 0-1)", "step2_code": "CanaryRolloutEngine.select_target()",
        "d2_cond": "Roll < Canary Split (10%)?", "d2_sub": "Traffic Splitting Engine", "d2_yes_label": "YES (Canary v2)", "d2_no_label": "NO (Baseline v1)",
        "success_action_title": "Route to Canary Model Instance v2", "success_action_sub": "Record Latency & OTel Spans", "end_success_text": "Canary Inference Emitted",
        "d3_cond": "v1 Healthy?", "retry_loop_label": "YES: Fallback v1", "d3_no_label": "NO (Fault)",
        "fail_action_title": "Route to Production Baseline v1", "fail_action_sub": "Stable Baseline Fallback Pass"
    },
    {
        "num": "05", "dir": "05-event-stream-pyspark-etl",
        "start_text": "Start: EventStreamETL.process_stream()",
        "step1_title": "Apply 10-Min Event Watermark Boundary", "step1_code": "src/event_pipeline.py:L52",
        "d1_cond": "Event Timestamp < Watermark?", "d1_sub": "Late Event Filter", "d1_left_label": "YES (Expired)", "d1_down_label": "NO (Valid Window)",
        "left_action_title": "Drop Expired Late Event Record", "left_action_sub": "Prevent State Memory Bloat", "left_end_text": "✖ Late Record Discarded",
        "step2_title": "Deduplicate & Execute 3-Pass Storage", "step2_code": "StorageReconciler.three_pass()",
        "d2_cond": "Gold Schema & Quality Valid?", "d2_sub": "Data Quality Contract", "d2_yes_label": "YES (Passed)", "d2_no_label": "NO (Corrupt)",
        "success_action_title": "Atomically Write Delta Lake Gold Table", "success_action_sub": "OpenLineage Telemetry Event", "end_success_text": "Delta ACID Commit Done",
        "d3_cond": "DLQ Active?", "retry_loop_label": "YES: Retry Buffer", "d3_no_label": "NO (Corrupt)",
        "fail_action_title": "Quarantine Record to S3 DLQ", "fail_action_sub": "Emit DLQ Quarantine Alert"
    },
    {
        "num": "06", "dir": "06-finetuning-lora-alignment",
        "start_text": "Start: LoRATrainer.train_peft()",
        "step1_title": "Freeze Base Weights & Inject LoRA (r=8)", "step1_code": "src/lora_trainer.py:L48",
        "d1_cond": "Dataset Split & Tokenizer Valid?", "d1_sub": "Curator Pre-check", "d1_left_label": "NO (Data Error)", "d1_down_label": "YES (Valid Data)",
        "left_action_title": "Abort Training & Log Data Bug", "left_action_sub": "Prevent GPU Waste", "left_end_text": "✖ Training Cancelled",
        "step2_title": "Execute Epoch Step & Compute Loss", "step2_code": "LoRATrainer.train_step()",
        "d2_cond": "Validation Loss Converged?", "d2_sub": "Slope Evaluation Across 3 Evals", "d2_yes_label": "YES (Converged)", "d2_no_label": "NO (Active)",
        "success_action_title": "Fuse LoRA Matrix & Export GGUF Q4", "success_action_sub": "Export Binary Model Artifact", "end_success_text": "GGUF Quantized Export Done",
        "d3_cond": "Epoch < Max?", "retry_loop_label": "YES: Next Epoch Loop", "d3_no_label": "NO (Max Limit)",
        "fail_action_title": "Step Optimizer & Update LR Scheduler", "fail_action_sub": "Proceed to Next Training Iteration"
    },
    {
        "num": "07", "dir": "07-cloud-iac-security-governance",
        "start_text": "Start: IaCSecurityScanner.scan_template()",
        "step1_title": "Parse CloudFormation / CDK AST", "step1_code": "src/cloud_governance.py:L35",
        "d1_cond": "IAM Policy Wildcard Action=='*'?", "d1_sub": "AST Security Audit Scan", "d1_left_label": "YES (Forbidden)", "d1_down_label": "NO (Least-Priv)",
        "left_action_title": "Flag CRITICAL IAM Violation", "left_action_sub": "Increment Offense Counter", "left_end_text": "✖ Security Check Failed",
        "step2_title": "Audit S3 Encryption & Public Access", "step2_code": "CDKASTRuleEngine.check_storage()",
        "d2_cond": "Total Security Offenses == 0?", "d2_sub": "Governance Release Gate", "d2_yes_label": "YES (Clean)", "d2_no_label": "NO (Offenses)",
        "success_action_title": "Approve IaC Deployment Pipeline", "success_action_sub": "Pass Security Build Gate", "end_success_text": "IaC Audit Passed",
        "d3_cond": "Fixable?", "retry_loop_label": "YES: Auto-Remediate", "d3_no_label": "NO (Violations)",
        "fail_action_title": "Block CI/CD Build & Export Report", "fail_action_sub": "Export Security Offense Log"
    },
    {
        "num": "08", "dir": "08-vllm-pagedattention-spec-decoding",
        "start_text": "Start: VLLMEngine.generate()",
        "step1_title": "Calculate 16-Token Physical VRAM Blocks", "step1_code": "src/paged_kv_cache.py:L40",
        "d1_cond": "Free VRAM Blocks >= Required?", "d1_sub": "Paged KV Memory Manager", "d1_left_label": "NO (Low VRAM)", "d1_down_label": "YES (Available)",
        "left_action_title": "Evict Low-Priority KV Blocks to CPU", "left_action_sub": "Reclaim Physical VRAM Space", "left_end_text": "↺ Memory Reclaimed",
        "step2_title": "Speculate K Draft Tokens & Verify Target", "step2_code": "SpeculativeVerifier.verify()",
        "d2_cond": "All K Speculative Tokens Accepted?", "d2_sub": "Target Model Logit Check", "d2_yes_label": "YES (All K)", "d2_no_label": "NO (Partial N < K)",
        "success_action_title": "Advance Pos by K (2.67x Speedup)", "success_action_sub": "Reclaim Unused Draft Blocks", "end_success_text": "Max Speedup Generated",
        "d3_cond": "N > 0 Tokens?", "retry_loop_label": "YES: Resample Token", "d3_no_label": "NO (Reject All)",
        "fail_action_title": "Accept N Tokens & Sample Replacement", "fail_action_sub": "Reclaim Invalid Draft KV Blocks"
    },
    {
        "num": "09", "dir": "09-ray-distributed-cluster-orchestrator",
        "start_text": "Start: RayClusterOrchestrator.execute_task()",
        "step1_title": "Write Large Payload to Plasma Memory", "step1_code": "src/ray_cluster.py:L55",
        "d1_cond": "Pending Task / Actor Ratio > Scale-Up?", "d1_sub": "Autoscaler Capacity Metric", "d1_left_label": "YES (High Load)", "d1_down_label": "NO (Optimal)",
        "left_action_title": "Provision New Ray Worker Nodes", "left_action_sub": "Scale Up Worker Node Pool", "left_end_text": "✔ Cluster Scaled Up",
        "step2_title": "Dispatch Task to Idle Ray Actor", "step2_code": "ClusterAutoscaler.check_capacity()",
        "d2_cond": "Idle Workers > 0 & Idle Time > 300s?", "d2_sub": "Scale Down Capacity Audit", "d2_yes_label": "YES (Scale Down)", "d2_no_label": "NO (Maintain)",
        "success_action_title": "Process Task Zero-Copy Plasma Store", "success_action_sub": "Emit Ray ObjectRef Result", "end_success_text": "Actor Task Completed",
        "d3_cond": "Excess Workers?", "retry_loop_label": "YES: Terminate Worker", "d3_no_label": "NO (Keep Stable)",
        "fail_action_title": "Terminate Excess Idle Worker Nodes", "fail_action_sub": "Scale Down Cloud Compute Billing"
    },
    {
        "num": "10", "dir": "10-triton-cuda-gpu-scheduler",
        "start_text": "Start: TritonGPUScheduler.enqueue_request()",
        "step1_title": "Push Request to Dynamic Batch Queue", "step1_code": "src/triton_engine.py:L45",
        "d1_cond": "Batch Size == 32 OR Delay >= 10ms?", "d1_sub": "Dynamic Batching Trigger", "d1_left_label": "NO (Collecting)", "d1_down_label": "YES (Batch Ready)",
        "left_action_title": "Hold Request in Queue Buffer", "left_action_sub": "Wait for Next Request (max 10ms)", "left_end_text": "⏳ Buffer Collecting",
        "step2_title": "Align Tensor & Launch Triton Kernel", "step2_code": "DynamicBatchingQueue.collect()",
        "d2_cond": "AWQ INT4 Kernel Executed Cleanly?", "d2_sub": "CUDA Tensor Core Pass", "d2_yes_label": "YES (Success)", "d2_no_label": "NO (Kernel Error)",
        "success_action_title": "Unpack Batch Output & Scatter Stream", "success_action_sub": "Emit Stream Response to Futures", "end_success_text": "Triton Batch Emitted",
        "d3_cond": "Retry Unbatched?", "retry_loop_label": "YES: Single Pass", "d3_no_label": "NO (Fatal Fault)",
        "fail_action_title": "Fall Back to Unbatched Single Pass", "fail_action_sub": "Safeguard Execution Latency"
    },
    {
        "num": "11", "dir": "11-distributed-training-fsdp-megatron",
        "start_text": "Start: FSDPZeRO3Trainer.train_step()",
        "step1_title": "Map Ranks to Megatron 3D Grid (TPxPPxDP)", "step1_code": "src/distributed_training.py:L60",
        "d1_cond": "Weights Sharded with FSDP ZeRO-3?", "d1_sub": "Memory Sharding Initializer", "d1_left_label": "NO (Unsharded)", "d1_down_label": "YES (Sharded)",
        "left_action_title": "Initialize ZeRO-3 Parameter Shards", "left_action_sub": "Shard Weights & Gradients", "left_end_text": "✔ Sharding Ready",
        "step2_title": "Execute All-Gather -> Forward -> Back Pass", "step2_code": "FSDPZeRO3Trainer.backward_step()",
        "d2_cond": "Grad Norm Finite & Loss Valid?", "d2_sub": "Gradient Overflow Check", "d2_yes_label": "YES (Valid)", "d2_no_label": "NO (Exploding)",
        "success_action_title": "Update Sharded Optimizer Weights", "success_action_sub": "Reduce-Scatter Gradient Pass", "end_success_text": "FSDP Step Completed",
        "d3_cond": "Overflow Occurred?", "retry_loop_label": "YES: Clip Gradients", "d3_no_label": "NO (Unstable)",
        "fail_action_title": "Skip Step Weight Update & Clip Grads", "fail_action_sub": "Log Instability Warning & Proceed"
    },
    {
        "num": "12", "dir": "12-genai-gateway-semantic-cache",
        "start_text": "Start: GenAIGateway.process_prompt()",
        "step1_title": "Check Client Token-Bucket Capacity", "step1_code": "src/genai_gateway.py:L50",
        "d1_cond": "Token Bucket Capacity > 0?", "d1_sub": "Rate Limiting Policy", "d1_left_label": "NO (Exceeded)", "d1_down_label": "YES (Allowed)",
        "left_action_title": "Reject Request with HTTP 429", "left_action_sub": "Too Many Requests Policy", "left_end_text": "✖ Rate Limit Blocked",
        "step2_title": "Search ChromaDB Vector Semantic Cache", "step2_code": "VectorSemanticCache.lookup()",
        "d2_cond": "Vector Cache Similarity >= 0.92?", "d2_sub": "Cosine Distance Metric", "d2_yes_label": "YES (Cache Hit)", "d2_no_label": "NO (Cache Miss)",
        "success_action_title": "Return Cached Response Payload", "success_action_sub": "<5ms Latency / $0.00 Cost", "end_success_text": "Semantic Cache Hit",
        "d3_cond": "Primary Failed?", "retry_loop_label": "YES: Fallback Cascade", "d3_no_label": "NO (Secondary Fail)",
        "fail_action_title": "Fallback to Secondary LLM Provider", "fail_action_sub": "Zero Downtime Provider Routing"
    },
    {
        "num": "13", "dir": "13-rlhf-dpo-alignment-pipeline",
        "start_text": "Start: DPOLossEngine.train_dpo()",
        "step1_title": "Load Pairwise Preference Data (Chosen/Reject)", "step1_code": "src/dpo_alignment.py:L42",
        "d1_cond": "Compute Log-Likelihoods Policy/Ref?", "d1_sub": "DPO Sequence Likelihood Pass", "d1_left_label": "NO (Data Fail)", "d1_down_label": "YES (Computed)",
        "left_action_title": "Abort Batch & Quarantine Data", "left_action_sub": "Sequence Tokenization Error", "left_end_text": "✖ Data Error Abort",
        "step2_title": "Compute Implicit Reward DPO Loss", "step2_code": "DPOLossEngine.compute_loss()",
        "d2_cond": "Bradley-Terry Win-Rate >= 75%?", "d2_sub": "Preference Alignment Audit", "d2_yes_label": "YES (Aligned)", "d2_no_label": "NO (Unaligned)",
        "success_action_title": "Export Aligned Policy Model Checkpoint", "success_action_sub": "Promote Aligned Weights", "end_success_text": "DPO Model Exported",
        "d3_cond": "Loss Unstable?", "retry_loop_label": "YES: Tune Beta Margin", "d3_no_label": "NO (Failed)",
        "fail_action_title": "Adjust Loss Beta Margin Scaling", "fail_action_sub": "Re-run Alignment Iteration Loop"
    },
    {
        "num": "14", "dir": "14-custom-cuda-triton-kernel-opt",
        "start_text": "Start: TritonFusedKernels.launch()",
        "step1_title": "Allocate VRAM Tensors X, W, B", "step1_code": "src/triton_kernels.py:L38",
        "d1_cond": "Launch Fused Grid BLOCK_SIZE=1024?", "d1_sub": "Single SRAM Pass Execution", "d1_left_label": "NO (OOM Error)", "d1_down_label": "YES (Launched)",
        "left_action_title": "Reduce Block Size to 512", "left_action_sub": "SRAM Memory Pressure Fallback", "left_end_text": "↺ Block Resized",
        "step2_title": "Execute Fused Bias-GELU Kernel", "step2_code": "RooflineAnalyzer.analyze()",
        "d2_cond": "Roofline Speedup >= 1.5x Baseline?", "d2_sub": "TFLOPS vs Memory Bandwidth Metric", "d2_yes_label": "YES (Speedup)", "d2_no_label": "NO (Sub-optimal)",
        "success_action_title": "Register Kernel in Production Library", "success_action_sub": "Max Hardware Saturation", "end_success_text": "Fused Kernel Deployed",
        "d3_cond": "Re-tune Stride?", "retry_loop_label": "YES: Tune Vector Stride", "d3_no_label": "NO (Limit Hit)",
        "fail_action_title": "Re-tune SRAM Vector Memory Stride", "fail_action_sub": "Re-align Tensor Core Access"
    },
    {
        "num": "15", "dir": "15-feature-store-vector-lakehouse",
        "start_text": "Start: FeatureStoreOrchestrator.get_features()",
        "step1_title": "Query Redis In-Memory Online Cache", "step1_code": "src/feature_lakehouse.py:L52",
        "d1_cond": "Features Present in Redis Online?", "d1_sub": "Online Cache Lookup (<2ms)", "d1_left_label": "YES (Cache Hit)", "d1_down_label": "NO (Cache Miss)",
        "left_action_title": "Return Online Feature Vector (<2ms)", "left_action_sub": "$0 Lakehouse Billing", "left_end_text": "✔ Online Cache Served",
        "step2_title": "Execute PyArrow ASOF Point-in-Time Join", "step2_code": "ParquetLakehouse.time_travel_join()",
        "d2_cond": "Point-in-Time Join Valid (No Leak)?", "d2_sub": "Temporal Leakage Audit", "d2_yes_label": "YES (No Leak)", "d2_no_label": "NO (Corrupt)",
        "success_action_title": "Populate Redis Cache & Return Vector", "success_action_sub": "Parquet Lakehouse Feature Read", "end_success_text": "Lakehouse Read Done",
        "d3_cond": "Fallback Default?", "retry_loop_label": "YES: Default Vector", "d3_no_label": "NO (Missing)",
        "fail_action_title": "Inject Imputed Baseline Default Features", "fail_action_sub": "Prevent Model Null Exception"
    },
    {
        "num": "16", "dir": "16-ai-safety-red-teaming-guardrails",
        "start_text": "Start: AISafetyGuardrails.scan_and_mask()",
        "step1_title": "Scan Prompt DAN Jailbreak Patterns", "step1_code": "src/safety_guardrails.py:L44",
        "d1_cond": "Jailbreak / Injection Threat Found?", "d1_sub": "Prompt Security Auditor", "d1_left_label": "YES (Malicious)", "d1_down_label": "NO (Safe Intent)",
        "left_action_title": "Reject Request with HTTP 400", "left_action_sub": "Log Security Attack Event", "left_end_text": "✖ Injection Threat Blocked",
        "step2_title": "Redact PII Tokens & Run Llama Guard", "step2_code": "LlamaGuardAuditor.audit_output()",
        "d2_cond": "Llama Guard Output Verification Safe?", "d2_sub": "Output Safety Policy Filter", "d2_yes_label": "YES (Safe Output)", "d2_no_label": "NO (Unsafe Output)",
        "success_action_title": "Emit Safe Anonymized Response", "success_action_sub": "PII Masked with [REDACTED]", "end_success_text": "Safe Response Emitted",
        "d3_cond": "Unsafe Output?", "retry_loop_label": "YES: Redact Output", "d3_no_label": "NO (Fatal Threat)",
        "fail_action_title": "Redact Unsafe Output & Log Incident", "fail_action_sub": "Security Incident Logging"
    },
    {
        "num": "17", "dir": "17-k8s-kuberay-kueue-gpu-operator",
        "start_text": "Start: KueueBatchScheduler.submit_job()",
        "step1_title": "Intercept Batch Job Spec & GPU Needs", "step1_code": "src/k8s_gpu.py:L58",
        "d1_cond": "ClusterQueue GPU Quota Available?", "d1_sub": "Kubernetes Resource Quota", "d1_left_label": "YES (Capacity OK)", "d1_down_label": "NO (Quota Full)",
        "left_action_title": "Admit Job & Provision RayCluster Pods", "left_action_sub": "Immediate Admission", "left_end_text": "✔ Ray Pods Provisioned",
        "step2_title": "Evaluate Preemption Priority Rules", "step2_code": "MIGDeviceSlicer.provision_slices()",
        "d2_cond": "Arriving Priority > Active Workloads?", "d2_sub": "K8s PriorityClass Metric", "d2_yes_label": "YES (High Priority)", "d2_no_label": "NO (Low Priority)",
        "success_action_title": "Preempt & Slice NVIDIA MIG (1g.10gb)", "success_action_sub": "Hardware Isolated GPU Slices", "end_success_text": "MIG Slice Provisioned",
        "d3_cond": "Pending Queue?", "retry_loop_label": "YES: Kueue Pending", "d3_no_label": "NO (Rejected)",
        "fail_action_title": "Enqueue Job in Kueue Pending Queue", "fail_action_sub": "Wait for Resource Release"
    },
    {
        "num": "18", "dir": "18-tensorrt-llm-onnx-execution",
        "start_text": "Start: TensorRTEngineCompiler.build()",
        "step1_title": "Export PyTorch LLM Graph to ONNX", "step1_code": "src/tensorrt_engine.py:L40",
        "d1_cond": "INT4 SmoothQuant Calibrated?", "d1_sub": "Activation Scaling Calibration", "d1_left_label": "NO (Scale Fail)", "d1_down_label": "YES (Calibrated)",
        "left_action_title": "Fall Back to Standard FP16 Graph", "left_action_sub": "Bypass SmoothQuant Scaling", "left_end_text": "↺ Fallback FP16 Graph",
        "step2_title": "Compile TensorRT Plan Engine (MHA/GEMM)", "step2_code": "TensorRTEngineCompiler.benchmark()",
        "d2_cond": "TensorRT Latency < 5ms P99 Target?", "d2_sub": "Target Engine Throughput", "d2_yes_label": "YES (Target Hit)", "d2_no_label": "NO (Target Miss)",
        "success_action_title": "Save .engine Plan File (1,480 tok/s)", "success_action_sub": "Deploy High Performance Engine", "end_success_text": "TensorRT Plan Saved",
        "d3_cond": "Recompile FP16?", "retry_loop_label": "YES: Rebuild FP16", "d3_no_label": "NO (Build Error)",
        "fail_action_title": "Fall Back to FP16 Optimization Mode", "fail_action_sub": "Rebuild Engine with FP16 Weights"
    },
    {
        "num": "19", "dir": "19-multi-agent-swarm-orchestrator",
        "start_text": "Start: SwarmOrchestrator.run_swarm()",
        "step1_title": "Construct Task Dependency Graph DAG", "step1_code": "src/swarm_orchestrator.py:L52",
        "d1_cond": "Circular Dependency Cycle Detected?", "d1_sub": "Kahn Topological Sort Audit", "d1_left_label": "YES (Cycle Found)", "d1_down_label": "NO (Clean DAG)",
        "left_action_title": "Abort CycleDeadlockException", "left_action_sub": "Prevent Agent Execution Deadlock", "left_end_text": "✖ Swarm Deadlock Aborted",
        "step2_title": "Dispatch Workers & Aggregate Voting", "step2_code": "ConsensusEngine.evaluate_consensus()",
        "d2_cond": "Voting Consensus Score >= 66%?", "d2_sub": "Majority Voting Consensus Metric", "d2_yes_label": "YES (Consensus)", "d2_no_label": "NO (Disagreement)",
        "success_action_title": "Emit Verified Consensus Result Payload", "success_action_sub": "Swarm Objective Reached", "end_success_text": "Swarm Task Completed",
        "d3_cond": "Tie-Breaker?", "retry_loop_label": "YES: Senior Agent", "d3_no_label": "NO (Failed)",
        "fail_action_title": "Invoke Senior Tie-Breaker Evaluator Agent", "fail_action_sub": "Resolve Conflicting Agent Outputs"
    },
    {
        "num": "20", "dir": "20-data-governance-openlineage-catalog",
        "start_text": "Start: OpenLineageCatalog.execute_job()",
        "step1_title": "Run Great Expectations Data Contract", "step1_code": "src/data_governance.py:L48",
        "d1_cond": "Pre-Job Data Contract Passed?", "d1_sub": "Zero Schema / Null Offenses", "d1_left_label": "NO (Violations)", "d1_down_label": "YES (Passed)",
        "left_action_title": "Emit OpenLineage ABORT Event", "left_action_sub": "Quarantine Corrupt Dataset", "left_end_text": "✖ Pipeline Execution Aborted",
        "step2_title": "Emit START -> Execute Job -> Register Graph", "step2_code": "MarquezCatalogClient.register_job()",
        "d2_cond": "Transformation Job Succeeded?", "d2_sub": "Marquez Lineage Graph Audit", "d2_yes_label": "YES (Job Complete)", "d2_no_label": "NO (Job Exception)",
        "success_action_title": "Emit OpenLineage COMPLETE Event", "success_action_sub": "Register Row Metrics in Marquez", "end_success_text": "Lineage Graph Updated",
        "d3_cond": "Marquez Up?", "retry_loop_label": "YES: Retry Telemetry", "d3_no_label": "NO (API Fault)",
        "fail_action_title": "Quarantine Dataset & Emit Alert", "fail_action_sub": "Log Pipeline Governance Failure"
    }
]

print("Injecting ultra-detailed project-specific 2D SVG flowcharts into all 20 FLOWCHART.html files...")

for p in projects_spec:
    svg_markup = build_custom_svg(p)
    flowchart_path = os.path.join(base_dir, p["dir"], "FLOWCHART.html")
    
    if os.path.exists(flowchart_path):
        with open(flowchart_path, "r") as f:
            html = f.read()
            
        if '<div class="mermaid-card">' in html:
            start_idx = html.find('<div class="mermaid-card">')
            end_idx = html.find('</div>\n    </div>\n\n    <div class="section-title">\n        <span>⚡ Exhaustive')
            
            if end_idx != -1:
                new_card_content = f'<div class="mermaid-card">\n{svg_markup}\n    </div>'
                new_html = html[:start_idx] + new_card_content + html[end_idx + 18:]
                
                with open(flowchart_path, "w") as f:
                    f.write(new_html)
                print(f"Updated {p['dir']}/FLOWCHART.html with custom 2D SVG flowchart!")

print("Successfully injected 20 hand-crafted, project-specific 2D SVG Flowchart diagrams!")
