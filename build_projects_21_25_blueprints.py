import os
import xml.etree.ElementTree as ET
import html

base_dir = "/Users/abhi/Documents/Antigravity"

# Projects 21 to 25 Metadata
new_projects_data = [
    {
        "num": "21", "dir": "21-vllm-multi-lora-dynamic-serving", "title": "vLLM Multi-LoRA Dynamic Serving",
        "subtitle": "Multi-Tenant LoRA Adapter Hot-Swapping, Segmented GEMM & Zero-Stall Batching",
        "src_file": "src/multi_lora_engine.py",
        "start_text": "MultiLoRAEngine.serve_batch()",
        "step1_title": "Resolve Adapter IDs & Check VRAM Cache", "step1_code": "src/multi_lora_engine.py:L45",
        "d1_title": "Decision 1: Are All Target LoRA Adapters Present in VRAM Cache?",
        "d1_cond": "All LoRA Adapters in VRAM Cache?", "d1_sub": "Adapter Memory Manager",
        "d1_code": "src/multi_lora_engine.py -> LoRACacheManager.check_adapters()",
        "d1_rule": "Checks dynamic LoRA adapter cache memory in GPU VRAM to determine if requested adapter weights are pre-loaded.",
        "d1_left_label": "NO (Cache Miss)", "d1_down_label": "YES (Cache Hit)",
        "left_action_title": "Async Fetch Adapter from Host RAM / S3", "left_action_sub": "Non-Blocking Dynamic Page In", "left_end_text": "[Adapter Loaded to VRAM]",
        "left_desc": "Fetches missing LoRA adapter weights (rank=8, 50MB) asynchronously from host CPU RAM via zero-copy pinned memory.",
        "step2_title": "Execute Segmented GEMM Forward Pass", "step2_code": "SegmentedGEMMKernel.launch()",
        "d2_title": "Decision 2: Did Segmented GEMM Batch Complete Within Latency Budget (< 25ms)?",
        "d2_cond": "Segmented GEMM Latency < 25ms?", "d2_sub": "Multi-Tenant Batch SLA",
        "d2_code": "src/multi_lora_engine.py -> SegmentedGEMMKernel.execute_batch()",
        "d2_rule": "Executes single unified matrix multiplication applying distinct LoRA adapter weights to different sequence segments in the batch.",
        "d2_yes_label": "YES (SLA Met)", "d2_no_label": "NO (SLA Breach)",
        "success_action_title": "Emit Multi-Tenant Token Streams", "success_action_sub": "Zero-Stall Token Stream Dispatch", "end_success_text": "[Multi-LoRA Batch Emitted]",
        "down_desc": "Emits distinct token streams customized for 32 different tenant LoRA adapters concurrently from a single base model pass.",
        "d3_title": "Decision 3: Is VRAM Adapter Capacity Exceeded?",
        "d3_cond": "VRAM Full?", "d3_code": "src/multi_lora_engine.py -> LoRACacheManager.is_full()",
        "d3_rule": "Checks if active adapter memory pool exceeds allocated VRAM budget threshold.",
        "retry_loop_label": "YES: Evict LRU Adapter", "d3_no_label": "NO (Fatal OOM)",
        "retry_desc": "Evicts least-recently-used (LRU) LoRA adapter weights from GPU VRAM back to host RAM buffer.",
        "fail_action_title": "Evict LRU Adapter & Fall Back to Base", "fail_action_sub": "Reclaim Adapter Memory Pool",
        "fail_desc": "Evicts inactive adapters from GPU memory pool and logs multi-tenant latency SLA warning."
    },
    {
        "num": "22", "dir": "22-disaggregated-prefill-decode-engine", "title": "Disaggregated Prefill vs. Decode",
        "subtitle": "Splitwise / Mooncake Architecture, Chunked Prefill & RDMA KV Cache Transfer",
        "src_file": "src/disaggregated_engine.py",
        "start_text": "DisaggregatedRouter.route_request()",
        "step1_title": "Classify Request Phase & Split Chunk", "step1_code": "src/disaggregated_engine.py:L40",
        "d1_title": "Decision 1: Is Incoming Request in Prefill Phase (Prompt Ingestion)?",
        "d1_cond": "Request Phase == PREFILL?", "d1_sub": "Compute vs Memory Classification",
        "d1_code": "src/disaggregated_engine.py -> DisaggregatedRouter.classify_phase()",
        "d1_rule": "Separates compute-bound prompt ingestion (prefill) from memory-bandwidth-bound token generation (decode).",
        "d1_left_label": "NO (Decode Phase)", "d1_down_label": "YES (Prefill Phase)",
        "left_action_title": "Route to Decode Worker GPU Pool", "left_action_sub": "Memory Bandwidth Optimized Pool", "left_end_text": "[Decode Stream Active]",
        "left_desc": "Dispatches active token generation directly to memory-bandwidth-optimized GPU decode worker pool.",
        "step2_title": "Execute Chunked Prefill & Build KV Cache", "step2_code": "PrefillWorkerPool.compute_kv()",
        "d2_title": "Decision 2: Did RDMA KV Cache Transfer to Decode Pool Succeed (< 3.0ms)?",
        "d2_cond": "RDMA KV Transfer < 3ms?", "d2_sub": "GPUDirect RDMA Network Pass",
        "d2_code": "src/disaggregated_engine.py -> KVCacheTransferClient.send_rdma()",
        "d2_rule": "Transfers computed KV cache memory tensors from prefill GPU pool to decode GPU pool using GPUDirect RDMA.",
        "d2_yes_label": "YES (Transfer OK)", "d2_no_label": "NO (Network Delay)",
        "success_action_title": "Handoff to Decode Pool (Zero Interference)", "success_action_sub": "TTFT SLA Met / Zero Jitter", "end_success_text": "[Disaggregated Handoff Complete]",
        "down_desc": "Hands off generation to decode worker pool, completely eliminating head-of-line interference between prompts and token generation.",
        "d3_title": "Decision 3: Is Direct TCP Network Fallback Available?",
        "d3_cond": "Fallback TCP?", "d3_code": "src/disaggregated_engine.py -> NetworkFallback.has_tcp()",
        "d3_rule": "Checks fallback TCP network link if RDMA transfer encounters network queue timeout.",
        "retry_loop_label": "YES: Fallback TCP Transfer", "d3_no_label": "NO (Fatal Drop)",
        "retry_desc": "Transfers KV cache via high-speed TCP socket stream to safeguard request continuity.",
        "fail_action_title": "Fallback to TCP Socket KV Transfer", "fail_action_sub": "Log Network Telemetry Warning",
        "fail_desc": "Transfers KV cache via TCP socket stream and logs GPUDirect RDMA latency alarm to Datadog."
    },
    {
        "num": "23", "dir": "23-fp8-mixed-precision-gemm-engine", "title": "Native FP8 Mixed-Precision GEMM",
        "subtitle": "NVIDIA Hopper H100 FP8 (E4M3 / E5M2) Tensor Core Acceleration & Dynamic Scaling",
        "src_file": "src/fp8_gemm_engine.py",
        "start_text": "FP8GEMMEngine.execute_gemm()",
        "step1_title": "Quantize Inputs to FP8 (E4M3/E5M2)", "step1_code": "src/fp8_gemm_engine.py:L48",
        "d1_title": "Decision 1: Are Dynamic Activation Scaling Factors Within Valid Numeric Range?",
        "d1_cond": "Scaling Factors Finite & Valid?", "d1_sub": "Delayed Scaling Factor Check",
        "d1_code": "src/fp8_gemm_engine.py -> DynamicScaler.validate_factors()",
        "d1_rule": "Audits delayed dynamic scaling factors across activation and weight tensors to prevent FP8 saturation underflow.",
        "d1_left_label": "NO (Scale Underflow)", "d1_down_label": "YES (Scale Valid)",
        "left_action_title": "Recalibrate Amax & Adjust Scale Factor", "left_action_sub": "Prevent Underflow Saturation", "left_end_text": "[Scaling Recalibrated]",
        "left_desc": "Recalibrates maximum absolute value (amax) tensor history and updates delayed scaling factors.",
        "step2_title": "Launch Hopper FP8 Tensor Core GEMM", "step2_code": "HopperFP8Kernel.launch()",
        "d2_title": "Decision 2: Does Kernel Achieve Target Speedup (Speedup >= 1.85x vs FP16)?",
        "d2_cond": "Speedup >= 1.85x vs FP16?", "d2_sub": "Hopper Tensor Core Throughput",
        "d2_code": "src/fp8_gemm_engine.py -> HopperFP8Kernel.benchmark()",
        "d2_rule": "Measures hardware TFLOPS execution throughput on NVIDIA Hopper H100 native FP8 Tensor Cores.",
        "d2_yes_label": "YES (Target Hit)", "d2_no_label": "NO (Sub-optimal)",
        "success_action_title": "Dequantize Output to FP16 Residual", "success_action_sub": "2x Throughput / Zero Perplexity Loss", "end_success_text": "[FP8 GEMM Complete]",
        "down_desc": "Dequantizes output matrix to FP16 residual stream, achieving 1,950 TFLOPS throughput with zero perplexity loss.",
        "d3_title": "Decision 3: Is Standard FP16 GEMM Fallback Configured?",
        "d3_cond": "Fallback FP16?", "d3_code": "src/fp8_gemm_engine.py -> FallbackConfig.supports_fp16()",
        "d3_rule": "Verifies fallback path to execute standard FP16 GEMM if hardware does not support native FP8.",
        "retry_loop_label": "YES: Fallback FP16", "d3_no_label": "NO (Fatal Fault)",
        "retry_desc": "Executes standard cuBLAS FP16 GEMM operation on legacy GPU architectures.",
        "fail_action_title": "Fall Back to cuBLAS FP16 GEMM", "fail_action_sub": "Legacy Hardware Execution Mode",
        "fail_desc": "Executes cuBLAS FP16 GEMM kernel and logs legacy hardware fallback event."
    },
    {
        "num": "24", "dir": "24-nccl-distributed-collective-profiler", "title": "NCCL Collective Communication Profiler",
        "subtitle": "Ring vs. Tree All-Reduce Profiling, Straggler Rank Detection & NVLink Saturation",
        "src_file": "src/nccl_profiler.py",
        "start_text": "NCCLProfiler.profile_collectives()",
        "step1_title": "Inject NVTX Markers & Measure Latency", "step1_code": "src/nccl_profiler.py:L52",
        "d1_title": "Decision 1: Does Measured Bus Bandwidth Meet Target (> 80% NVLink Peak)?",
        "d1_cond": "Bus Bandwidth > 80% Peak?", "d1_sub": "NVLink Bandwidth Saturation",
        "d1_code": "src/nccl_profiler.py -> BandwidthAnalyzer.calculate_bus_bw()",
        "d1_rule": "Calculates effective bus bandwidth using standard collective formula: B_bus = (2*(N-1)/N) * (Size / Time).",
        "d1_left_label": "NO (Bottleneck)", "d1_down_label": "YES (Saturated)",
        "left_action_title": "Switch from Ring to Tree Topology", "left_action_sub": "Optimize Inter-Node Latency", "left_end_text": "[Topology Optimized]",
        "left_desc": "Switches collective algorithm from Ring to 2D-Tree topology to reduce inter-node latency hops.",
        "step2_title": "Detect Straggler Ranks Across Cluster", "step2_code": "StragglerDetector.scan_ranks()",
        "d2_title": "Decision 2: Are All GPU Ranks Synchronized (Variance < 5.0% Across Ranks)?",
        "d2_cond": "Rank Variance < 5.0%?", "d2_sub": "Straggler Elimination Gate",
        "d2_code": "src/nccl_profiler.py -> StragglerDetector.detect_stragglers()",
        "d2_rule": "Measures per-GPU completion variance during All-Reduce to detect thermal throttling or PCIe link degradation.",
        "d2_yes_label": "YES (Balanced)", "d2_no_label": "NO (Straggler Found)",
        "success_action_title": "Export NCCL Telemetry & Performance Trace", "success_action_sub": "Zero Straggler Jitter Confirmed", "end_success_text": "[NCCL Profile Verified]",
        "down_desc": "Exports NCCL communication performance metrics, verifying 900 GB/s NVLink intra-node and 400 Gbps RoCE inter-node saturation.",
        "d3_title": "Decision 3: Is Auto-Thermal Throttling Mitigation Enabled?",
        "d3_cond": "Auto-Mitigate?", "d3_code": "src/nccl_profiler.py -> Mitigator.is_enabled()",
        "d3_rule": "Checks if automated workload re-balancing can drain and replace offending straggler GPU node.",
        "retry_loop_label": "YES: Drain Straggler", "d3_no_label": "NO (Alert Only)",
        "retry_desc": "Drains active GPU rank, reallocates distributed communication communicator, and resumes training.",
        "fail_action_title": "Flag Straggler GPU Rank & Alert On-Call", "fail_action_sub": "Isolate Degraded PCIe / Thermal Rank",
        "fail_desc": "Flags offending GPU rank, triggers PagerDuty hardware alert, and isolates degraded compute node."
    },
    {
        "num": "25", "dir": "25-speculative-medusa-multi-head-verifier", "title": "Medusa Multi-Head Speculative Verifier",
        "subtitle": "Medusa Attached Prediction Heads, Tree Attention Masking & Parallel Verification",
        "src_file": "src/medusa_verifier.py",
        "start_text": "MedusaVerifier.generate_speculative()",
        "step1_title": "Predict Multi-Token Candidates via MLP Heads", "step1_code": "src/medusa_verifier.py:L46",
        "d1_title": "Decision 1: Are Candidate Tokens Successfully Emitted by All 4 Medusa Heads?",
        "d1_cond": "All 4 Medusa Heads Emitted?", "d1_sub": "Attached MLP Head Predictor",
        "d1_code": "src/medusa_verifier.py -> MedusaHeadPredictor.predict_candidates()",
        "d1_rule": "Uses 4 lightweight MLP heads attached to the base model's final hidden states to predict tokens t+1, t+2, t+3, t+4 simultaneously.",
        "d1_left_label": "NO (Head Fail)", "d1_down_label": "YES (Emitted)",
        "left_action_title": "Fall Back to Single-Token Standard Pass", "left_action_sub": "Bypass Medusa Speculation", "left_end_text": "[Single Token Fallback]",
        "left_desc": "Bypasses Medusa prediction heads and falls back to standard single-token autoregressive generation pass.",
        "step2_title": "Construct Tree Attention Mask & Verify", "step2_code": "TreeAttentionVerifier.verify()",
        "d2_title": "Decision 2: Did Base Model Accept >= 3 Speculative Candidate Tokens?",
        "d2_cond": "Accepted Tokens >= 3?", "d2_sub": "Tree Attention Verification",
        "d2_code": "src/medusa_verifier.py -> TreeAttentionVerifier.verify_tree()",
        "d2_rule": "Evaluates candidate token tree in a single forward pass using custom 2D Tree Attention causal masks.",
        "d2_yes_label": "YES (>= 3 Tokens)", "d2_no_label": "NO (< 3 Tokens)",
        "success_action_title": "Advance Sequence Position by Accepted Count", "success_action_sub": "2.85x Speculative Speedup", "end_success_text": "[Medusa Speedup Achieved]",
        "down_desc": "Advances sequence position by 3 to 4 tokens in a single target model pass, achieving 2.85x speedup with zero extra model VRAM.",
        "d3_title": "Decision 3: Is At Least 1 Candidate Token Accepted?",
        "d3_cond": "Accepted >= 1?", "d3_code": "src/medusa_verifier.py -> TreeAttentionVerifier.has_partial_match()",
        "d3_rule": "Checks if at least one candidate token was verified to advance generation state.",
        "retry_loop_label": "YES: Accept Partial", "d3_no_label": "NO (Full Reject)",
        "retry_desc": "Accepts verified tokens, samples true replacement token, and loops to next Medusa prediction pass.",
        "fail_action_title": "Accept Verified Tokens & Resample True Logit", "fail_action_sub": "Advance by 1-2 Tokens & Loop",
        "fail_desc": "Accepts matching tokens, samples replacement token from true logits, and continues generation."
    }
]

def escape_xml(s):
    if not s:
        return ""
    return html.escape(str(s), quote=True)

def generate_valid_xml_svg(p):
    title = escape_xml(f"Project {p['num']}: {p['title']}")
    start_text = escape_xml(f"Start: {p['start_text']}")
    step1_title = escape_xml(p['step1_title'])
    step1_code = escape_xml(p['step1_code'])
    d1_cond = escape_xml(p['d1_cond'])
    d1_sub = escape_xml(p['d1_sub'])
    d1_left_label = escape_xml(p['d1_left_label'])
    left_action_title = escape_xml(p['left_action_title'])
    left_action_sub = escape_xml(p['left_action_sub'])
    left_end_text = escape_xml(p['left_end_text'])
    d1_down_label = escape_xml(p['d1_down_label'])
    step2_title = escape_xml(p['step2_title'])
    step2_code = escape_xml(p['step2_code'])
    d2_cond = escape_xml(p['d2_cond'])
    d2_sub = escape_xml(p['d2_sub'])
    d2_yes_label = escape_xml(p['d2_yes_label'])
    success_action_title = escape_xml(p['success_action_title'])
    success_action_sub = escape_xml(p['success_action_sub'])
    end_success_text = escape_xml(p['end_success_text'])
    d2_no_label = escape_xml(p['d2_no_label'])
    d3_cond = escape_xml(p['d3_cond'])
    retry_loop_label = escape_xml(p['retry_loop_label'])
    d3_no_label = escape_xml(p['d3_no_label'])
    fail_action_title = escape_xml(p['fail_action_title'])
    fail_action_sub = escape_xml(p['fail_action_sub'])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 750" width="1000" height="750" version="1.1">
  <defs>
    <marker id="arrow-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
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
  </defs>

  <!-- Clean, Solid Dark Background -->
  <rect width="1000" height="750" fill="#0d1117" rx="12"/>

  <!-- Header Text -->
  <text x="500" y="32" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="20">{title}</text>
  <text x="500" y="54" text-anchor="middle" fill="#8b949e" font-family="sans-serif" font-size="13">2D Control Flow Architecture Blueprint</text>

  <!-- 1. Start Node -->
  <g transform="translate(340, 75)">
    <rect width="320" height="42" rx="21" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="160" y="26" text-anchor="middle" fill="#34d399" font-family="sans-serif" font-weight="bold" font-size="13">{start_text}</text>
  </g>

  <path d="M 500 117 L 500 150" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-cyan)"/>

  <!-- Step 1 Process Node -->
  <g transform="translate(320, 150)">
    <rect width="360" height="50" rx="8" fill="#161b22" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="180" y="22" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="13">{step1_title}</text>
    <text x="180" y="38" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="11">{step1_code}</text>
  </g>

  <path d="M 500 200 L 500 235" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-cyan)"/>

  <!-- DECISION 1 DIAMOND -->
  <g transform="translate(500, 275)">
    <polygon points="0,-40 180,0 0,40 -180,0" fill="#1f1906" stroke="#fbbf24" stroke-width="2.5"/>
    <text x="0" y="-10" text-anchor="middle" fill="#fbbf24" font-family="sans-serif" font-weight="bold" font-size="11">DECISION 1</text>
    <text x="0" y="8" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="11">{d1_cond}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="9">({d1_sub})</text>
  </g>

  <!-- LEFT BRANCH: Fast Path / Cache Hit -->
  <path d="M 320 275 L 170 275 L 170 345" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="200" y="255" width="100" height="20" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="250" y="269" text-anchor="middle" fill="#34d399" font-family="monospace" font-weight="bold" font-size="10">{d1_left_label}</text>

  <!-- Left Action Box -->
  <g transform="translate(30, 350)">
    <rect width="280" height="50" rx="8" fill="#161b22" stroke="#34d399" stroke-width="1.5"/>
    <text x="140" y="22" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="12">{left_action_title}</text>
    <text x="140" y="38" text-anchor="middle" fill="#34d399" font-family="monospace" font-size="10">{left_action_sub}</text>
  </g>

  <path d="M 170 400 L 170 445" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(40, 445)">
    <rect width="260" height="40" rx="20" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="130" y="25" text-anchor="middle" fill="#34d399" font-family="sans-serif" font-weight="bold" font-size="12">{left_end_text}</text>
  </g>

  <!-- DOWN BRANCH: Proceed Execution -->
  <path d="M 500 315 L 500 350" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-cyan)"/>
  <rect x="510" y="320" width="100" height="20" rx="4" fill="#161b22" stroke="#38bdf8" stroke-width="1"/>
  <text x="560" y="334" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-weight="bold" font-size="10">{d1_down_label}</text>

  <!-- Step 2 Box -->
  <g transform="translate(320, 350)">
    <rect width="360" height="50" rx="8" fill="#161b22" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="180" y="22" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="13">{step2_title}</text>
    <text x="180" y="38" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="11">{step2_code}</text>
  </g>

  <path d="M 500 400 L 500 445" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-cyan)"/>

  <!-- DECISION 2 DIAMOND -->
  <g transform="translate(500, 485)">
    <polygon points="0,-40 180,0 0,40 -180,0" fill="#1f1906" stroke="#fbbf24" stroke-width="2.5"/>
    <text x="0" y="-10" text-anchor="middle" fill="#fbbf24" font-family="sans-serif" font-weight="bold" font-size="11">DECISION 2</text>
    <text x="0" y="8" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="11">{d2_cond}</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="9">({d2_sub})</text>
  </g>

  <!-- DOWN BRANCH: Success -->
  <path d="M 500 525 L 500 565" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="510" y="530" width="100" height="20" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="560" y="544" text-anchor="middle" fill="#34d399" font-family="monospace" font-weight="bold" font-size="10">{d2_yes_label}</text>

  <!-- Success Box -->
  <g transform="translate(320, 565)">
    <rect width="360" height="50" rx="8" fill="#161b22" stroke="#34d399" stroke-width="1.5"/>
    <text x="180" y="22" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="13">{success_action_title}</text>
    <text x="180" y="38" text-anchor="middle" fill="#34d399" font-family="monospace" font-size="11">{success_action_sub}</text>
  </g>

  <path d="M 500 615 L 500 655" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(340, 655)">
    <rect width="320" height="42" rx="21" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="160" y="26" text-anchor="middle" fill="#34d399" font-family="sans-serif" font-weight="bold" font-size="13">{end_success_text}</text>
  </g>

  <!-- RIGHT BRANCH: Error / Retry Branch -->
  <path d="M 680 485 L 840 485" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="695" y="465" width="80" height="20" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="735" y="479" text-anchor="middle" fill="#f43f5e" font-family="monospace" font-weight="bold" font-size="10">{d2_no_label}</text>

  <!-- Decision 3 Diamond (Right Side) -->
  <g transform="translate(840, 565)">
    <polygon points="0,-35 110,0 0,35 -110,0" fill="#1f1906" stroke="#fbbf24" stroke-width="2"/>
    <text x="0" y="-6" text-anchor="middle" fill="#fbbf24" font-family="sans-serif" font-weight="bold" font-size="10">DECISION 3</text>
    <text x="0" y="10" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-size="10">{d3_cond}</text>
  </g>

  <!-- UPWARD RETRY LOOP ARROW -->
  <path d="M 840 530 L 840 375 L 695 375" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-amber)"/>
  <rect x="710" y="355" width="120" height="20" rx="4" fill="#2d2206" stroke="#fbbf24" stroke-width="1"/>
  <text x="770" y="369" text-anchor="middle" fill="#fbbf24" font-family="monospace" font-weight="bold" font-size="9">{retry_loop_label}</text>

  <!-- DOWN BRANCH: Fallback Action -->
  <path d="M 840 600 L 840 645" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="850" y="610" width="80" height="20" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="890" y="624" text-anchor="middle" fill="#f43f5e" font-family="monospace" font-weight="bold" font-size="10">{d3_no_label}</text>

  <g transform="translate(710, 645)">
    <rect width="260" height="50" rx="8" fill="#161b22" stroke="#f43f5e" stroke-width="1.5"/>
    <text x="130" y="22" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="12">{fail_action_title}</text>
    <text x="130" y="38" text-anchor="middle" fill="#f43f5e" font-family="monospace" font-size="10">{fail_action_sub}</text>
  </g>
</svg>"""

def build_native_html(p):
    inline_svg_markup = generate_valid_xml_svg(p)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Project {p['num']}: {p['title']} — Interactive 2D Architecture Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0c10;
            --bg-card: #12161f;
            --bg-card-hover: #171d29;
            --border-color: #21262d;
            --border-highlight: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-cyan: #38bdf8;
            --accent-green: #34d399;
            --accent-gold: #fbbf24;
            --accent-rose: #f43f5e;
            --accent-purple: #a78bfa;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem 1.5rem;
            max-width: 1350px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 2.5rem;
            text-align: center;
        }}

        .nav-back {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--accent-cyan);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 1rem;
            transition: color 0.2s;
        }}

        .nav-back:hover {{
            color: #7dd3fc;
            text-decoration: underline;
        }}

        .badge {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }}

        h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.025em;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            max-width: 800px;
            margin: 0 auto;
        }}

        .section-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.3rem;
            font-weight: 700;
            margin: 2.5rem 0 1.25rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .diagram-container {{
            background: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 3rem;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
            overflow: hidden;
            text-align: center;
        }}

        /* Pure HTML5/CSS3 2D Flowchart Layout */
        .flow-layout-2d {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.25rem;
            padding: 1rem 0;
        }}

        .flow-pill {{
            padding: 0.6rem 1.75rem;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.02em;
        }}

        .flow-pill.green {{
            background: rgba(52, 211, 153, 0.12);
            color: var(--accent-green);
            border: 2px solid var(--accent-green);
        }}

        .flow-arrow-v {{
            font-size: 1.5rem;
            font-weight: 900;
            line-height: 1;
        }}

        .flow-arrow-v.cyan {{ color: var(--accent-cyan); }}
        .flow-arrow-v.green {{ color: var(--accent-green); }}

        .flow-proc-box {{
            background: #161b22;
            border: 2px solid var(--accent-cyan);
            border-radius: 10px;
            padding: 1rem 2rem;
            min-width: 380px;
            text-align: center;
        }}

        .flow-proc-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .flow-proc-code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--accent-cyan);
            margin-top: 0.25rem;
        }}

        .flow-diamond-node {{
            background: #1f1906;
            border: 2.5px solid var(--accent-gold);
            border-radius: 12px;
            padding: 1.25rem 2.5rem;
            min-width: 420px;
            text-align: center;
            box-shadow: 0 0 20px rgba(251, 191, 36, 0.15);
        }}

        .diamond-badge-text {{
            color: var(--accent-gold);
            font-weight: 800;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.1em;
        }}

        .diamond-title-text {{
            color: #ffffff;
            font-weight: 700;
            font-size: 1.05rem;
            margin-top: 0.2rem;
        }}

        .diamond-sub-text {{
            color: var(--text-secondary);
            font-size: 0.82rem;
            font-family: 'JetBrains Mono', monospace;
        }}

        .flow-branches-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            width: 100%;
            max-width: 1100px;
            margin-top: 0.5rem;
        }}

        .branch-col-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
        }}

        .exec-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(580px, 1fr));
            gap: 1.5rem;
        }}

        .exec-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            transition: border-color 0.2s, transform 0.2s;
        }}

        .exec-card:hover {{
            border-color: var(--border-highlight);
            transform: translateY(-2px);
        }}

        .card-header {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--accent-gold);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .code-badge {{
            display: inline-block;
            background: #161b22;
            color: var(--accent-cyan);
            border: 1px solid #30363d;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .rule-box {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid var(--accent-gold);
            padding: 0.75rem 1rem;
            border-radius: 0 6px 6px 0;
            font-size: 0.92rem;
            color: var(--text-primary);
        }}

        .routes-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .route-card {{
            border-radius: 10px;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            font-size: 0.88rem;
        }}

        .route-card.green {{
            background: rgba(52, 211, 153, 0.06);
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}

        .route-card.cyan {{
            background: rgba(56, 189, 248, 0.06);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}

        .route-card.rose {{
            background: rgba(244, 63, 94, 0.06);
            border: 1px solid rgba(244, 63, 94, 0.3);
        }}

        .route-card.amber {{
            background: rgba(251, 191, 36, 0.06);
            border: 1px solid rgba(251, 191, 36, 0.3);
        }}

        .route-header {{
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .route-card.green .route-header {{ color: var(--accent-green); }}
        .route-card.cyan .route-header {{ color: var(--accent-cyan); }}
        .route-card.rose .route-header {{ color: var(--accent-rose); }}
        .route-card.amber .route-header {{ color: var(--accent-gold); }}

        .route-desc {{
            color: var(--text-primary);
            line-height: 1.45;
        }}

        footer {{
            margin-top: 4rem;
            border-top: 1px solid var(--border-color);
            padding-top: 2rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        footer a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>

    <header>
        <a href="../index.html" class="nav-back">&larr; Back to Main Platform Showcase</a>
        <div><span class="badge">INTERACTIVE 2D CONTROL FLOW BLUEPRINT</span></div>
        <h1>Project {p['num']}: {p['title']}</h1>
        <p class="subtitle">{p['subtitle']}</p>
    </header>

    <div class="section-title">
        <span>🔀 Visual 2D Branching Control Flow Architecture Diagram</span>
    </div>

    <!-- 100% Native Inline Grid-Free Vector SVG Diagram -->
    <div class="diagram-container">
{inline_svg_markup}
    </div>

    <!-- 100% Native HTML5/CSS3 Interactive 2D Flowchart (Zero Image Dependency) -->
    <div class="diagram-container">
        <div class="flow-layout-2d">
            <div class="flow-pill green">▶ Start: {p['start_text']}</div>
            <div class="flow-arrow-v cyan">↓</div>

            <div class="flow-proc-box">
                <div class="flow-proc-title">{p['step1_title']}</div>
                <div class="flow-proc-code">{p['step1_code']}</div>
            </div>
            <div class="flow-arrow-v cyan">↓</div>

            <div class="flow-diamond-node">
                <div class="diamond-badge-text">◆ DECISION 1</div>
                <div class="diamond-title-text">{p['d1_cond']}</div>
                <div class="diamond-sub-text">({p['d1_sub']})</div>
            </div>

            <div class="flow-branches-grid">
                <div class="branch-col-card" style="border-color: var(--accent-green);">
                    <div class="route-header" style="color: var(--accent-green);">↙ {p['d1_left_label']}</div>
                    <div class="flow-proc-box" style="border-color: var(--accent-green); min-width: auto; width: 100%;">
                        <div class="flow-proc-title">{p['left_action_title']}</div>
                        <div class="flow-proc-code" style="color: var(--accent-green);">{p['left_action_sub']}</div>
                    </div>
                    <div class="flow-pill green" style="width: 100%; text-align: center;">{p['left_end_text']}</div>
                </div>

                <div class="branch-col-card" style="border-color: var(--accent-cyan);">
                    <div class="route-header" style="color: var(--accent-cyan);">↓ {p['d1_down_label']}</div>
                    <div class="flow-proc-box" style="min-width: auto; width: 100%;">
                        <div class="flow-proc-title">{p['step2_title']}</div>
                        <div class="flow-proc-code">{p['step2_code']}</div>
                    </div>

                    <div class="flow-diamond-node" style="min-width: auto; width: 100%; padding: 0.75rem;">
                        <div class="diamond-badge-text">◆ DECISION 2</div>
                        <div class="diamond-title-text" style="font-size: 0.95rem;">{p['d2_cond']}</div>
                    </div>

                    <div class="flow-proc-box" style="border-color: var(--accent-green); min-width: auto; width: 100%;">
                        <div class="flow-proc-title">{p['success_action_title']}</div>
                        <div class="flow-proc-code" style="color: var(--accent-green);">{p['success_action_sub']}</div>
                    </div>
                    <div class="flow-pill green" style="width: 100%; text-align: center;">{p['end_success_text']}</div>
                </div>
            </div>
        </div>
    </div>

    <div class="section-title">
        <span>⚡ Exhaustive Logical Conditionals & Codebase Mapping</span>
    </div>

    <div class="exec-grid">

        <!-- Decision 1 Card -->
        <div class="exec-card">
            <div class="card-header">
                <div class="card-title">◆ {p['d1_title']}</div>
                <div class="code-badge"><code>{p['d1_code']}</code></div>
            </div>
            <div class="rule-box">
                <strong>Condition Evaluated:</strong> {p['d1_rule']}
            </div>
            <div class="routes-container">
                <div class="route-card green">
                    <div class="route-header">↙ LEFT FAST-PATH: {p['d1_left_label']}</div>
                    <div class="route-desc">{p['left_desc']}</div>
                </div>
                <div class="route-card cyan">
                    <div class="route-header">↓ DOWN EXECUTION: {p['d1_down_label']}</div>
                    <div class="route-desc">Proceeds to step 2 execution: {p['step2_title']}.</div>
                </div>
            </div>
        </div>

        <!-- Decision 2 Card -->
        <div class="exec-card">
            <div class="card-header">
                <div class="card-title">◆ {p['d2_title']}</div>
                <div class="code-badge"><code>{p['d2_code']}</code></div>
            </div>
            <div class="rule-box">
                <strong>Condition Evaluated:</strong> {p['d2_rule']}
            </div>
            <div class="routes-container">
                <div class="route-card green">
                    <div class="route-header">↓ DOWN SUCCESS: {p['d2_yes_label']}</div>
                    <div class="route-desc">{p['down_desc']}</div>
                </div>
                <div class="route-card rose">
                    <div class="route-header">↘ RIGHT BRANCH: {p['d2_no_label']}</div>
                    <div class="route-desc">Triggers exception evaluation to check retry boundary limits.</div>
                </div>
            </div>
        </div>

        <!-- Decision 3 Card -->
        <div class="exec-card" style="grid-column: 1 / -1;">
            <div class="card-header">
                <div class="card-title">◆ {p['d3_title']}</div>
                <div class="code-badge"><code>{p['d3_code']}</code></div>
            </div>
            <div class="rule-box">
                <strong>Condition Evaluated:</strong> {p['d3_rule']}
            </div>
            <div class="routes-container">
                <div class="route-card amber">
                    <div class="route-header">↺ UPWARD RETRY LOOP: {p['retry_loop_label']}</div>
                    <div class="route-desc">{p['retry_desc']}</div>
                </div>
                <div class="route-card rose">
                    <div class="route-header">↓ EXHAUSTED FALLBACK: {p['d3_no_label']}</div>
                    <div class="route-desc">{p['fail_desc']}</div>
                </div>
            </div>
        </div>

    </div>

    <footer>
        <p>&copy; 2026 Abhishek Singh • Staff & Principal AI Platform Architect</p>
        <p style="margin-top: 0.5rem;">
            <a href="PROD_ARCHITECTURE_REASONING.md" target="_blank">Architecture Reasoning</a> • 
            <a href="{p['src_file']}" target="_blank">Source Code ({p['src_file']})</a> • 
            <a href="../index.html">Main Platform Showcase</a>
        </p>
    </footer>

</body>
</html>"""

print("Generating SVGs and HTMLs for Projects 21 to 25...")
for p in new_projects_data:
    p_dir = os.path.join(base_dir, p["dir"])
    os.makedirs(os.path.join(p_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(p_dir, "tests"), exist_ok=True)
    
    # SVG
    svg_content = generate_valid_xml_svg(p)
    svg_path = os.path.join(p_dir, "FLOWCHART.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    # Validate XML
    ET.parse(svg_path)
    print(f"Generated and validated SVG: {p['dir']}/FLOWCHART.svg")
    
    # HTML
    html_content = build_native_html(p)
    html_path = os.path.join(p_dir, "FLOWCHART.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated bulletproof HTML: {p['dir']}/FLOWCHART.html")

print("All Project 21-25 SVG and HTML files built and validated!")
