import os
from PIL import Image, ImageDraw, ImageFont

base_dir = "/Users/abhi/Documents/Antigravity"
artifact_dir = "/Users/abhi/.gemini/antigravity/brain/3c431721-b2f2-4621-b3fe-4b12e98501d5"

# Load clean fonts or default PIL font
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    font_badge = ImageFont.truetype("/System/Library/Fonts/Monaco.dfont", 11)
except Exception:
    font_title = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()

def draw_diamond(draw, center_x, center_y, width, height, fill_color, stroke_color):
    half_w = width // 2
    half_h = height // 2
    points = [
        (center_x, center_y - half_h),
        (center_x + half_w, center_y),
        (center_x, center_y + half_h),
        (center_x - half_w, center_y)
    ]
    draw.polygon(points, fill=fill_color, outline=stroke_color, width=2)
    return points

def draw_stadium(draw, x, y, width, height, fill_color, stroke_color):
    draw.rounded_rectangle([x, y, x + width, y + height], radius=height//2, fill=fill_color, outline=stroke_color, width=2)

def draw_box(draw, x, y, width, height, fill_color, stroke_color):
    draw.rounded_rectangle([x, y, x + width, y + height], radius=8, fill=fill_color, outline=stroke_color, width=2)

def draw_arrow(draw, start_pos, end_pos, color, width=2):
    draw.line([start_pos, end_pos], fill=color, width=width)
    # Simple arrowhead
    x1, y1 = start_pos
    x2, y2 = end_pos
    if x1 == x2: # Vertical arrow
        if y2 > y1: # Down
            draw.polygon([(x2-5, y2-8), (x2+5, y2-8), (x2, y2)], fill=color)
        else: # Up
            draw.polygon([(x2-5, y2+8), (x2+5, y2+8), (x2, y2)], fill=color)
    elif y1 == y2: # Horizontal arrow
        if x2 > x1: # Right
            draw.polygon([(x2-8, y2-5), (x2-8, y2+5), (x2, y2)], fill=color)
        else: # Left
            draw.polygon([(x2+8, y2-5), (x2+8, y2+5), (x2, y2)], fill=color)

def generate_png_diagram(proj_data, out_path):
    W, H = 1000, 760
    img = Image.new("RGB", (W, H), color="#0a0c10")
    draw = ImageDraw.Draw(img)

    # Header Title
    draw.text((W//2, 25), f"Project {proj_data['num']}: {proj_data['title']}", fill="#f0f6fc", font=font_title, anchor="mm")
    draw.text((W//2, 50), "2D Branching Control Flow & Decision Architecture", fill="#8b949e", font=font_sub, anchor="mm")

    # Colors
    c_bg_card = "#12161f"
    c_cyan = "#38bdf8"
    c_green = "#34d399"
    c_green_bg = "#092e20"
    c_gold = "#fbbf24"
    c_gold_bg = "#2d2206"
    c_rose = "#f43f5e"
    c_rose_bg = "#3b1219"

    # 1. Start Node (Center Top)
    draw_stadium(draw, 350, 75, 300, 45, c_green_bg, c_green)
    draw.text((500, 97), f"▶ {proj_data['start_text']}", fill=c_green, font=font_bold, anchor="mm")

    draw_arrow(draw, (500, 120), (500, 150), c_cyan)

    # 2. Step 1 Box
    draw_box(draw, 330, 150, 340, 50, c_bg_card, c_cyan)
    draw.text((500, 166), proj_data['step1_title'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((500, 184), proj_data['step1_code'], fill=c_cyan, font=font_badge, anchor="mm")

    draw_arrow(draw, (500, 200), (500, 235), c_cyan)

    # 3. Decision 1 Diamond (Center)
    draw_diamond(draw, 500, 275, 340, 80, c_gold_bg, c_gold)
    draw.text((500, 260), "DECISION 1", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((500, 276), proj_data['d1_cond'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((500, 292), f"({proj_data['d1_sub']})", fill="#8b949e", font=font_badge, anchor="mm")

    # LEFT BRANCH (Fast-Path / Cache Hit)
    # Line left to 170, then down to 350
    draw.line([(330, 275), (170, 275)], fill=c_green, width=2)
    draw_arrow(draw, (170, 275), (170, 350), c_green)

    # Left Badge
    draw_box(draw, 195, 255, 110, 22, c_green_bg, c_green)
    draw.text((250, 266), proj_data['d1_left_label'], fill=c_green, font=font_badge, anchor="mm")

    # Left Action Box
    draw_box(draw, 30, 350, 280, 50, c_bg_card, c_green)
    draw.text((170, 366), proj_data['left_action_title'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((170, 384), proj_data['left_action_sub'], fill=c_green, font=font_badge, anchor="mm")

    draw_arrow(draw, (170, 400), (170, 445), c_green)
    draw_stadium(draw, 40, 445, 260, 45, c_green_bg, c_green)
    draw.text((170, 467), proj_data['left_end_text'], fill=c_green, font=font_bold, anchor="mm")

    # DOWN BRANCH (Proceed Execution)
    draw_arrow(draw, (500, 315), (500, 360), c_cyan)
    draw_box(draw, 510, 322, 110, 22, c_bg_card, c_cyan)
    draw.text((565, 333), proj_data['d1_down_label'], fill=c_cyan, font=font_badge, anchor="mm")

    # Step 2 Box
    draw_box(draw, 330, 360, 340, 50, c_bg_card, c_cyan)
    draw.text((500, 376), proj_data['step2_title'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((500, 394), proj_data['step2_code'], fill=c_cyan, font=font_badge, anchor="mm")

    draw_arrow(draw, (500, 410), (500, 445), c_cyan)

    # 4. Decision 2 Diamond
    draw_diamond(draw, 500, 485, 340, 80, c_gold_bg, c_gold)
    draw.text((500, 470), "DECISION 2", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((500, 486), proj_data['d2_cond'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((500, 502), f"({proj_data['d2_sub']})", fill="#8b949e", font=font_badge, anchor="mm")

    # DOWN BRANCH (Success)
    draw_arrow(draw, (500, 525), (500, 575), c_green)
    draw_box(draw, 510, 535, 110, 22, c_green_bg, c_green)
    draw.text((565, 546), proj_data['d2_yes_label'], fill=c_green, font=font_badge, anchor="mm")

    # Success Box
    draw_box(draw, 330, 575, 340, 50, c_bg_card, c_green)
    draw.text((500, 591), proj_data['success_action_title'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((500, 609), proj_data['success_action_sub'], fill=c_green, font=font_badge, anchor="mm")

    draw_arrow(draw, (500, 625), (500, 665), c_green)
    draw_stadium(draw, 350, 665, 300, 45, c_green_bg, c_green)
    draw.text((500, 687), f"★ {proj_data['end_success_text']}", fill=c_green, font=font_bold, anchor="mm")

    # RIGHT BRANCH (Error / Retry Branch)
    draw.line([(670, 485), (850, 485)], fill=c_rose, width=2)
    draw_arrow(draw, (850, 485), (850, 525), c_rose)
    draw_box(draw, 685, 465, 80, 22, c_rose_bg, c_rose)
    draw.text((725, 476), proj_data['d2_no_label'], fill=c_rose, font=font_badge, anchor="mm")

    # Decision 3 Diamond (Right Side)
    draw_diamond(draw, 850, 555, 200, 60, c_gold_bg, c_gold)
    draw.text((850, 547), "DECISION 3", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((850, 563), proj_data['d3_cond'], fill="#f0f6fc", font=font_badge, anchor="mm")

    # UPWARD RETRY LOOP ARROW (Curving from Decision 3 back up to Step 2 Box)
    draw.line([(850, 525), (850, 385)], fill=c_gold, width=2)
    draw_arrow(draw, (850, 385), (670, 385), c_gold)

    draw_box(draw, 730, 360, 130, 22, c_gold_bg, c_gold)
    draw.text((795, 371), f"↻ {proj_data['retry_loop_label']}", fill=c_gold, font=font_badge, anchor="mm")

    # DOWN BRANCH (Exhausted / Fail Action)
    draw_arrow(draw, (850, 585), (850, 630), c_rose)
    draw_box(draw, 855, 595, 90, 22, c_rose_bg, c_rose)
    draw.text((900, 606), proj_data['d3_no_label'], fill=c_rose, font=font_badge, anchor="mm")

    draw_box(draw, 720, 630, 260, 50, c_bg_card, c_rose)
    draw.text((850, 646), proj_data['fail_action_title'], fill="#f0f6fc", font=font_bold, anchor="mm")
    draw.text((850, 664), proj_data['fail_action_sub'], fill=c_rose, font=font_badge, anchor="mm")

    img.save(out_path, "PNG")
    print(f"Generated PNG Flowchart: {out_path}")

projects_spec = [
    {
        "num": "01", "dir": "01-agent-durable-runtime", "title": "Agentic Durable Runtime",
        "start_text": "DurableAgentRuntime.execute_step()",
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
        "num": "02", "dir": "02-rag-cost-router", "title": "RAG Cost Router Engine",
        "start_text": "RAGCostRouter.route_query()",
        "step1_title": "Compute Query Embedding & Vector Search", "step1_code": "src/rag_pipeline.py:L62",
        "d1_cond": "Cache Sim Cosine >= 0.95?", "d1_sub": "ChromaDB Vector Index", "d1_left_label": "YES (Cache Hit)", "d1_down_label": "NO (Cache Miss)",
        "left_action_title": "Return Cached Answer (<5ms)", "left_action_sub": "$0.00 API Cost / Zero Latency", "left_end_text": "✔ Fast Cache Served",
        "step2_title": "Calculate Query Complexity Score", "step2_code": "QueryComplexityClassifier.classify()",
        "d2_cond": "Complexity Score <= 0.4?", "d2_sub": "Token & Keyword Density Metric", "d2_yes_label": "YES (Low Score)", "d2_no_label": "NO (High Score)",
        "success_action_title": "Route Query to Local Ollama LLM", "success_action_sub": "Zero Cloud API Billing Cost", "end_success_text": "Local Inference Done",
        "d3_cond": "Score > 0.8?", "retry_loop_label": "YES: Multi-Hop RRF", "d3_no_label": "NO (Mid-Tier)",
        "fail_action_title": "Route to Claude 3.5 Sonnet Tier", "fail_action_sub": "Balanced Cost/Quality Tier"
    },
    {
        "num": "03", "dir": "03-llm-eval-gate", "title": "LLM Evaluation Gate",
        "start_text": "LLMEvalGate.evaluate_build()",
        "step1_title": "Compute RAG Triad Metrics (Faithful/Ground)", "step1_code": "src/eval_gate.py:L58",
        "d1_cond": "p-value < 0.05 & Delta > +0.05?", "d1_sub": "Welch t-Test vs Baseline", "d1_left_label": "NO (Degraded)", "d1_down_label": "YES (Quality Gain)",
        "left_action_title": "Flag Quality Degradation", "left_action_sub": "Fail CI/CD Stat Release Gate", "left_end_text": "✖ Build Blocked: Stat Gain Low",
        "step2_title": "Run Toxicity & Safety Audit Check", "step2_code": "ToxicityEvaluator.check_safety()",
        "d2_cond": "Toxicity Score <= 0.05?", "d2_sub": "Safety Policy Threshold", "d2_yes_label": "YES (Safe)", "d2_no_label": "NO (Toxic)",
        "success_action_title": "Register Model Artifact in MLflow", "success_action_sub": "Promote to Production Registry", "end_success_text": "Release Gate Approved",
        "d3_cond": "Sample Valid?", "retry_loop_label": "YES: Re-Evaluate", "d3_no_label": "NO (Violation)",
        "fail_action_title": "Flag Safety Violation & Alert Team", "fail_action_sub": "Block Deployment & Alert PagerDuty"
    },
    {
        "num": "04", "dir": "04-model-serving-mlops", "title": "Model Serving MLOps",
        "start_text": "ModelServingPipeline.predict()",
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
        "num": "05", "dir": "05-event-stream-pyspark-etl", "title": "Event Stream PySpark ETL",
        "start_text": "EventStreamETL.process_stream()",
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
        "num": "06", "dir": "06-finetuning-lora-alignment", "title": "Fine-Tuning LoRA Alignment",
        "start_text": "LoRATrainer.train_peft()",
        "step1_title": "Freeze Base Weights & Inject LoRA (r=8)", "step1_code": "src/lora_trainer.py:L48",
        "d1_cond": "Dataset Split & Tokenizer Valid?", "d1_sub": "Curator Pre-check", "d1_left_label": "NO (Data Error)", "d1_down_label": "YES (Valid Data)",
        "left_action_title": "Abort Training & Log Data Bug", "left_action_sub": "Prevent GPU Waste", "left_end_text": "✖ Training Cancelled",
        "step2_title": "Execute Epoch Step & Compute Loss", "step2_code": "LoRATrainer.train_step()",
        "d2_cond": "Validation Loss Converged?", "d2_sub": "Slope Eval Across 3 Evals", "d2_yes_label": "YES (Converged)", "d2_no_label": "NO (Active)",
        "success_action_title": "Fuse LoRA Matrix & Export GGUF Q4", "success_action_sub": "Export Binary Model Artifact", "end_success_text": "GGUF Quantized Export Done",
        "d3_cond": "Epoch < Max?", "retry_loop_label": "YES: Next Epoch Loop", "d3_no_label": "NO (Max Limit)",
        "fail_action_title": "Step Optimizer & Update LR Scheduler", "fail_action_sub": "Proceed to Next Training Step"
    },
    {
        "num": "07", "dir": "07-cloud-iac-security-governance", "title": "Cloud IaC Security Governance",
        "start_text": "IaCSecurityScanner.scan_template()",
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
        "num": "08", "dir": "08-vllm-pagedattention-spec-decoding", "title": "vLLM PagedAttention & Speculative Decoding",
        "start_text": "VLLMEngine.generate()",
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
        "num": "09", "dir": "09-ray-distributed-cluster-orchestrator", "title": "Ray Distributed Cluster Orchestrator",
        "start_text": "RayClusterOrchestrator.execute_task()",
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
        "num": "10", "dir": "10-triton-cuda-gpu-scheduler", "title": "Triton CUDA GPU Scheduler",
        "start_text": "TritonGPUScheduler.enqueue_request()",
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
        "num": "11", "dir": "11-distributed-training-fsdp-megatron", "title": "Distributed Training (FSDP & Megatron)",
        "start_text": "FSDPZeRO3Trainer.train_step()",
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
        "num": "12", "dir": "12-genai-gateway-semantic-cache", "title": "GenAI Gateway & Semantic Cache",
        "start_text": "GenAIGateway.process_prompt()",
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
        "num": "13", "dir": "13-rlhf-dpo-alignment-pipeline", "title": "RLHF DPO Alignment Pipeline",
        "start_text": "DPOLossEngine.train_dpo()",
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
        "num": "14", "dir": "14-custom-cuda-triton-kernel-opt", "title": "Custom OpenAI Triton GPU Kernels",
        "start_text": "TritonFusedKernels.launch()",
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
        "num": "15", "dir": "15-feature-store-vector-lakehouse", "title": "Feature Store & Vector Lakehouse",
        "start_text": "FeatureStoreOrchestrator.get_features()",
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
        "num": "16", "dir": "16-ai-safety-red-teaming-guardrails", "title": "AI Safety & Policy Guardrails",
        "start_text": "AISafetyGuardrails.scan_and_mask()",
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
        "num": "17", "dir": "17-k8s-kuberay-kueue-gpu-operator", "title": "K8s KubeRay & Kueue GPU Operator",
        "start_text": "KueueBatchScheduler.submit_job()",
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
        "num": "18", "dir": "18-tensorrt-llm-onnx-execution", "title": "TensorRT-LLM Engine & ONNX Execution",
        "start_text": "TensorRTEngineCompiler.build()",
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
        "num": "19", "dir": "19-multi-agent-swarm-orchestrator", "title": "Multi-Agent Swarm Orchestrator",
        "start_text": "SwarmOrchestrator.run_swarm()",
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
        "num": "20", "dir": "20-data-governance-openlineage-catalog", "title": "Data Governance & OpenLineage Catalog",
        "start_text": "OpenLineageCatalog.execute_job()",
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

print("Rendering high-res 2D PNG flowchart image diagrams for all 20 projects...")
for p in projects_spec:
    png_path = os.path.join(base_dir, p["dir"], "FLOWCHART.png")
    generate_png_diagram(p, png_path)

    # Also copy Project 01 image to conversation artifact folder so it renders directly in chat
    if p["num"] == "01":
        artifact_png = os.path.join(artifact_dir, "flowchart_01.png")
        generate_png_diagram(p, artifact_png)

print("Successfully generated high-resolution 2D PNG flowchart images!")
