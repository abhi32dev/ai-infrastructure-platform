import os
import sys

projects = [
    {
        "num": "01",
        "dir": "01-agent-durable-runtime",
        "title": "Agentic Durable Runtime",
        "subtitle": "State Machine Checkpoint Persistence & Rollback Engine",
        "file": "src/agent_runtime.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Input Payload Validation", "code": "src/agent_runtime.py -> DurableAgentRuntime.execute_step()", "desc": "Validates state payload, step_id, and schema parameters before execution."},
            {"id": "N2", "title": "Step 2: Check Active State Store", "code": "src/agent_runtime.py -> StateStore.get_active_state()", "desc": "Queries SQLite WAL engine for current step checkpoint or initializes genesis state."},
            {"id": "N3", "title": "Decision 1: Is Step Idempotent & Already Executed?", "type": "decision", "desc": "Checks if step_id exists in SQLite WAL event log to prevent double execution.", "yes": "Return cached step checkpoint output", "no": "Proceed to Tool Execution Boundary"},
            {"id": "N4", "title": "Step 4: Execute Agent Action / Tool Call", "code": "src/agent_runtime.py -> DurableAgentRuntime._invoke_tool()", "desc": "Runs isolated tool function within exception boundary and captures return value."},
            {"id": "N5", "title": "Decision 2: Did Tool Invocation Succeed?", "type": "decision", "desc": "Verifies tool response for exception or unhandled error state.", "yes": "Persist WAL Snapshot", "no": "Trigger Error Recovery Routine"},
            {"id": "N6", "title": "Step 6: Write WAL Checkpoint & Event Delta", "code": "src/agent_runtime.py -> CheckpointManager.save_checkpoint()", "desc": "Atomically inserts checkpoint record into SQLite WAL database and updates step index."},
            {"id": "N7", "title": "Step 7: Rollback / Retry Subroutine", "code": "src/agent_runtime.py -> DurableAgentRuntime.rollback_to_step()", "desc": "Rolls back SQLite transaction, restores last stable checkpoint state, and increments retry counter."}
        ]
    },
    {
        "num": "02",
        "dir": "02-rag-cost-router",
        "title": "RAG Cost Router Engine",
        "subtitle": "Cost-Aware Query Complexity Routing & Vector Search Engine",
        "file": "src/rag_pipeline.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Prompt Ingestion & Normalization", "code": "src/rag_pipeline.py -> RAGCostRouter.route_query()", "desc": "Receives user query, strips whitespace, and computes token length & embedding vector."},
            {"id": "N2", "title": "Step 2: Semantic Cache Lookup", "code": "src/rag_pipeline.py -> RAGCostRouter._check_semantic_cache()", "desc": "Queries ChromaDB for cached vector similarity > 0.95."},
            {"id": "N3", "title": "Decision 1: Cache Hit Found (Similarity >= 0.95)?", "type": "decision", "desc": "Evaluates cosine distance threshold of vector store cache.", "yes": "Return Cache Answer ($0.00 Cost)", "no": "Proceed to Complexity Classifier"},
            {"id": "N4", "title": "Step 4: Calculate Query Complexity Score", "code": "src/rag_pipeline.py -> QueryComplexityClassifier.classify()", "desc": "Evaluates query length, domain keywords, and multi-hop reasoning requirements."},
            {"id": "N5", "title": "Decision 2: Complexity Tier Assessment", "type": "decision", "desc": "Routes query based on computed complexity score threshold.", "yes": "LOW -> Local Ollama Model", "no": "HIGH -> Hybrid RRF BM25 + Frontier LLM"},
            {"id": "N6", "title": "Step 6: Execute Hybrid RRF Vector Retrieval", "code": "src/rag_pipeline.py -> RAGCostRouter.retrieve_hybrid()", "desc": "Fuses BM25 keyword search with ChromaDB dense vector embeddings using Reciprocal Rank Fusion."},
            {"id": "N7", "title": "Step 7: Frontier LLM Response Synthesis", "code": "src/rag_pipeline.py -> FrontierLLMAdapter.generate()", "desc": "Streams context-augmented prompt to frontier model and records token billing metrics."}
        ]
    },
    {
        "num": "03",
        "dir": "03-llm-eval-gate",
        "title": "LLM Evaluation Gate",
        "subtitle": "Automated Welch's t-Test RAG Triad Quality Release Gate",
        "file": "src/eval_gate.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Ingest Candidate Benchmark Dataset", "code": "src/eval_gate.py -> LLMEvalGate.evaluate_build()", "desc": "Loads test set questions, candidate outputs, and ground-truth reference answers."},
            {"id": "N2", "title": "Step 2: Compute Metric Scores (Faithfulness, Groundedness, Toxicity)", "code": "src/eval_gate.py -> FaithfulnessEvaluator.score()", "desc": "Calculates LLM-as-a-Judge numerical metric scores across candidate output samples."},
            {"id": "N3", "title": "Step 3: Execute Welch's t-Test Hypothesis Testing", "code": "src/eval_gate.py -> WelchTTestScorer.compare()", "desc": "Computes Welch's unequal variances t-statistic and p-value against production baseline scores."},
            {"id": "N4", "title": "Decision 1: Is p-value < 0.05 AND Mean Delta > Minimum Threshold?", "type": "decision", "desc": "Validates statistical significance of quality improvement.", "yes": "Pass Metric Gate", "no": "Fail Release Gate"},
            {"id": "N5", "title": "Step 5: Check Toxicity Policy Enforcement", "code": "src/eval_gate.py -> ToxicityEvaluator.check_safety()", "desc": "Ensures zero samples exceed toxicity threshold score of 0.05."},
            {"id": "N6", "title": "Decision 2: All Metrics Passed Gate?", "type": "decision", "desc": "Final CI/CD gate evaluation rule.", "yes": "APPROVED -> Register MLflow Model Artifact", "no": "REJECTED -> Trigger CI/CD Build Fail & Alert"}
        ]
    },
    {
        "num": "04",
        "dir": "04-model-serving-mlops",
        "title": "Model Serving MLOps",
        "subtitle": "Canary Rollout Engine & OpenTelemetry Traceparent Pipeline",
        "file": "src/model_serving.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: API Request Arrival & Trace Isolation", "code": "src/model_serving.py -> ModelServingPipeline.predict_with_canary()", "desc": "Parses incoming request, extracts or generates W3C traceparent header, and binds span context."},
            {"id": "N2", "title": "Step 2: Queue Depth & Backpressure Check", "code": "src/model_serving.py -> ModelServingPipeline._check_backpressure()", "desc": "Verifies active request queue length does not exceed max threshold (50 requests)."},
            {"id": "N3", "title": "Decision 1: Queue Depth > Backpressure Limit?", "type": "decision", "desc": "Evaluates server queue saturation state.", "yes": "Return HTTP 429 Rate Limit Exceeded", "no": "Proceed to Canary Shift Evaluator"},
            {"id": "N4", "title": "Step 4: Evaluate Canary Traffic Split", "code": "src/model_serving.py -> CanaryRolloutEngine.select_target()", "desc": "Generates uniform pseudo-random roll [0.0, 1.0) and compares against active canary weight."},
            {"id": "N5", "title": "Decision 2: Roll < Canary Weight (e.g. 10%)?", "type": "decision", "desc": "Determines model target instance routing.", "yes": "Route to Canary v2 Model Instance", "no": "Route to Baseline v1 Model Instance"},
            {"id": "N6", "title": "Step 6: Model Inference Execution & Telemetry Emission", "code": "src/model_serving.py -> ModelServingPipeline._execute_inference()", "desc": "Runs model forward pass, measures latency, records OpenTelemetry metrics, and returns payload."}
        ]
    },
    {
        "num": "05",
        "dir": "05-event-stream-pyspark-etl",
        "title": "Event Stream PySpark ETL",
        "subtitle": "Structured Streaming 3-Pass Storage Reconciliation Pipeline",
        "file": "src/event_pipeline.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Ingest Kafka / Edge Telemetry Stream", "code": "src/event_pipeline.py -> EventStreamETL.process_stream()", "desc": "Reads raw JSON SNMP traps and device metrics from stream source into PySpark DataFrame."},
            {"id": "N2", "title": "Step 2: Apply Event-Time Watermarking & Windowing", "code": "src/event_pipeline.py -> EventStreamETL._apply_watermark()", "desc": "Defines 10-minute event-time watermark to bound late-arriving edge data."},
            {"id": "N3", "title": "Step 3: Deduplicate Stream Events", "code": "src/event_pipeline.py -> TelemetryDeduplicator.dedupe()", "desc": "Deduplicates records based on device_id and event_timestamp unique keys."},
            {"id": "N4", "title": "Step 4: 3-Pass Storage Reconciliation", "code": "src/event_pipeline.py -> StorageReconciler.three_pass_reconcile()", "desc": "Pass 1: Raw Landing, Pass 2: Silver De-duplication, Pass 3: Gold Delta Lake ACID Write."},
            {"id": "N5", "title": "Decision 1: Is Reconciled Schema Valid?", "type": "decision", "desc": "Validates Schema Contract compliance.", "yes": "Write to Delta Lake Table", "no": "Quarantine to Dead-Letter Queue (DLQ)"}
        ]
    },
    {
        "num": "06",
        "dir": "06-finetuning-lora-alignment",
        "title": "Fine-Tuning LoRA Alignment",
        "subtitle": "PEFT LoRA Parameter Reduction & GGUF Quantization Pipeline",
        "file": "src/lora_trainer.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Dataset Curation & Tokenization", "code": "src/dataset_curator.py -> DatasetCurator.prepare_splits()", "desc": "Validates prompt-response pairs, filters samples, and creates train/val splits."},
            {"id": "N2", "title": "Step 2: Inject LoRA Adapter Layers", "code": "src/lora_trainer.py -> LoRATrainer.inject_adapters()", "desc": "Freezes base transformer weights and injects low-rank matrix pairs (r=8, alpha=16)."},
            {"id": "N3", "title": "Step 3: Fine-Tuning Training Loop", "code": "src/lora_trainer.py -> LoRATrainer.train()", "desc": "Executes forward/backward passes, calculates cross-entropy loss, and updates adapter weights."},
            {"id": "N4", "title": "Decision 1: Has Loss Converged OR Epoch Max Reached?", "type": "decision", "desc": "Evaluates training loop exit criteria.", "yes": "Save LoRA Weights Checkpoint", "no": "Continue Training Steps"},
            {"id": "N5", "title": "Step 5: Merge Adapters & Export GGUF", "code": "src/gguf_exporter.py -> GGUFExporter.export()", "desc": "Fuses adapter weights into base model and quantizes weights to GGUF Q4_K_M format."}
        ]
    },
    {
        "num": "07",
        "dir": "07-cloud-iac-security-governance",
        "title": "Cloud IaC Security Governance",
        "subtitle": "CDK / Terraform AST Scanner & IAM Wildcard Audit Engine",
        "file": "src/cloud_governance.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Parse CloudFormation / CDK AST", "code": "src/cloud_governance.py -> IaCSecurityScanner.scan_template()", "desc": "Loads IaC template JSON/YAML and parses Abstract Syntax Tree (AST) nodes."},
            {"id": "N2", "title": "Step 2: Scan IAM Policy Definitions", "code": "src/cloud_governance.py -> IAMWildcardAuditor.audit_policies()", "desc": "Inspects Action and Resource fields for forbidden '*' wildcard permissions."},
            {"id": "N3", "title": "Decision 1: Are Wildcard IAM Permissions Detected?", "type": "decision", "desc": "Checks policy rules against least-privilege principles.", "yes": "Flag CRITICAL Security Violation", "no": "Pass IAM Audit Check"},
            {"id": "N4", "title": "Step 4: Check S3 / Storage Encryption & Public Access", "code": "src/cloud_governance.py -> CDKASTRuleEngine.check_storage()", "desc": "Verifies KMS encryption flags and public bucket block configuration."},
            {"id": "N5", "title": "Decision 2: Total Security Violations == 0?", "type": "decision", "desc": "Final policy compliance gate.", "yes": "PASS -> Approve Deployment Pipeline", "no": "FAIL -> Block CI/CD Build & Export Governance Report"}
        ]
    },
    {
        "num": "08",
        "dir": "08-vllm-pagedattention-spec-decoding",
        "title": "vLLM PagedAttention & Speculative",
        "subtitle": "Paged KV Cache Virtual Memory & Speculative Token Verification",
        "file": "src/vllm_engine.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Ingest Token Sequence Generation Request", "code": "src/vllm_engine.py -> VLLMEngine.generate()", "desc": "Receives prompt tokens and target output length requirement."},
            {"id": "N2", "title": "Step 2: Allocate Virtual KV Cache Blocks", "code": "src/paged_kv_cache.py -> PagedKVCacheManager.allocate_blocks()", "desc": "Maps logical token sequence blocks to non-contiguous physical VRAM memory blocks (16 tokens/block)."},
            {"id": "N3", "title": "Decision 1: Free VRAM Block Capacity Available?", "type": "decision", "desc": "Checks physical GPU memory block availability.", "yes": "Bind Virtual Memory Block Mapping", "no": "Preempt & Evict Low-Priority KV Blocks to Host CPU RAM"},
            {"id": "N4", "title": "Step 4: Draft Model K-Token Speculative Generation", "code": "src/speculative_verifier.py -> SpeculativeVerifier.generate_draft()", "desc": "Small draft model rapidly speculates K tokens ahead."},
            {"id": "N5", "title": "Step 5: Target Model Parallel Speculative Verification", "code": "src/speculative_verifier.py -> SpeculativeVerifier.verify_tokens()", "desc": "Target model evaluates draft tokens in parallel and accepts valid matching prefixes."}
        ]
    },
    {
        "num": "09",
        "dir": "09-ray-distributed-cluster-orchestrator",
        "title": "Ray Distributed Cluster Orchestrator",
        "subtitle": "Ray Core Actor Pools, Zero-Copy Plasma Store & Cluster Autoscaler",
        "file": "src/ray_cluster.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Task Submission to Cluster Orchestrator", "code": "src/ray_cluster.py -> RayClusterOrchestrator.execute_task()", "desc": "Submits task payload to stateful Ray Actor pool."},
            {"id": "N2", "title": "Step 2: Zero-Copy Shared Memory Write", "code": "src/plasma_store.py -> PlasmaStoreManager.put()", "desc": "Writes large numpy/tensor object payloads to Ray Plasma Shared Memory Store."},
            {"id": "N3", "title": "Step 3: Evaluate Worker Task Queue Depth", "code": "src/cluster_autoscaler.py -> ClusterAutoscaler.check_capacity()", "desc": "Monitors pending tasks vs idle actor count."},
            {"id": "N4", "title": "Decision 1: Queue Depth > Scaling Threshold?", "type": "decision", "desc": "Determines cluster scaling decision.", "yes": "SCALE_UP -> Provision New Ray Worker Nodes", "no": "MAINTAIN -> Dispatch to Idle Actor Pool"},
            {"id": "N5", "title": "Step 5: Execute Actor Worker Task & Return ObjectRef", "code": "src/ray_cluster.py -> RayActor.compute()", "desc": "Worker processes shared memory payload zero-copy and emits result ObjectRef."}
        ]
    },
    {
        "num": "10",
        "dir": "10-triton-cuda-gpu-scheduler",
        "title": "Triton CUDA GPU Scheduler",
        "subtitle": "Dynamic Batching Queue & AWQ INT4 Quantized Inference Engine",
        "file": "src/triton_engine.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Inference Request Arrival", "code": "src/triton_engine.py -> TritonGPUScheduler.enqueue_request()", "desc": "Pushes incoming request payload into Dynamic Batching Queue."},
            {"id": "N2", "title": "Step 2: Dynamic Batch Collector & Delay Evaluation", "code": "src/triton_engine.py -> DynamicBatchingQueue.collect_batch()", "desc": "Waits up to max_queue_delay_ms (10ms) or until batch size reaches max_batch_size (32)."},
            {"id": "N3", "title": "Decision 1: Batch Ready OR Max Delay Expired?", "type": "decision", "desc": "Evaluates batch forming trigger.", "yes": "Form Tensor-Aligned GPU Batch", "no": "Wait for Next Request Arrival"},
            {"id": "N4", "title": "Step 4: Execute AWQ INT4 Matrix Multiplication Kernel", "code": "src/triton_engine.py -> AWQQuantizer.matmul_int4()", "desc": "Executes INT4 weight unpack and GEMM on CUDA Tensor Cores."},
            {"id": "N5", "title": "Step 5: Scatter Outputs to Client Streams", "code": "src/triton_engine.py -> TritonGPUScheduler.dispatch_results()", "desc": "Unpacks batch response tensor and streams results back to individual client futures."}
        ]
    },
    {
        "num": "11",
        "dir": "11-distributed-training-fsdp-megatron",
        "title": "Distributed Training (FSDP & Megatron)",
        "subtitle": "PyTorch FSDP ZeRO-3 Memory Sharding & Megatron 3D Grid Engine",
        "file": "src/distributed_training.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: World Initialization & 3D Grid Rank Mapping", "code": "src/distributed_training.py -> Megatron3DGrid.init_mesh()", "desc": "Initializes Process Group and maps GPU ranks to Tensor (TP), Pipeline (PP), and Data Parallel (DP) dimensions."},
            {"id": "N2", "title": "Step 2: FSDP ZeRO-3 Parameter Sharding", "code": "src/distributed_training.py -> FSDPZeRO3Trainer.shard_parameters()", "desc": "Shards model weights, gradients, and optimizer states evenly across all DP ranks (93.75% memory savings)."},
            {"id": "N3", "title": "Step 3: All-Gather Forward Pass Execution", "code": "src/distributed_training.py -> FSDPZeRO3Trainer.forward_step()", "desc": "Executes NCCL All-Gather to collect layer weights, performs forward GEMM, and frees unsharded parameters."},
            {"id": "N4", "title": "Step 4: Reduce-Scatter Backward Pass", "code": "src/distributed_training.py -> FSDPZeRO3Trainer.backward_step()", "desc": "Computes gradients, performs Reduce-Scatter across ranks, and updates sharded optimizer states."},
            {"id": "N5", "title": "Decision 1: Checkpoint Epoch Reached?", "type": "decision", "desc": "Checks epoch index for model snapshot export.", "yes": "Consolidate Distributed Checkpoint to Disk", "no": "Proceed to Next Mini-Batch"}
        ]
    },
    {
        "num": "12",
        "dir": "12-genai-gateway-semantic-cache",
        "title": "GenAI Gateway & Semantic Cache",
        "subtitle": "Vector Cache Hits, Token-Bucket Rate Limiter & Fallback Cascade",
        "file": "src/genai_gateway.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Client API Key & Token Bucket Check", "code": "src/genai_gateway.py -> TokenBucketLimiter.consume()", "desc": "Verifies client token bucket refill rate and capacity before accepting request."},
            {"id": "N2", "title": "Decision 1: Token Bucket Remaining > 0?", "type": "decision", "desc": "Evaluates API key rate limit capacity.", "yes": "Deduct Tokens & Proceed", "no": "Reject with HTTP 429 Too Many Requests"},
            {"id": "N3", "title": "Step 3: Vector Semantic Cache Search", "code": "src/genai_gateway.py -> VectorSemanticCache.lookup()", "desc": "Computes prompt embedding and searches vector index for cosine similarity > 0.92."},
            {"id": "N4", "title": "Decision 2: Semantic Cache Hit (Similarity >= 0.92)?", "type": "decision", "desc": "Evaluates semantic similarity threshold.", "yes": "Return Cached Generation (<5ms)", "no": "Cascade to Provider Router"},
            {"id": "N5", "title": "Step 5: Multi-Provider Fallback Routing (OpenAI -> Anthropic -> Ollama)", "code": "src/genai_gateway.py -> MultiProviderRouter.dispatch()", "desc": "Tries Primary Provider (OpenAI). If 5xx error or timeout occurs, fails over to Secondary (Anthropic), then Fallback (Ollama)."}
        ]
    },
    {
        "num": "13",
        "dir": "13-rlhf-dpo-alignment-pipeline",
        "title": "RLHF DPO Alignment Pipeline",
        "subtitle": "Direct Preference Optimization Loss & Bradley-Terry Win-Rate Auditor",
        "file": "src/dpo_alignment.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Load Pairwise Preference Dataset", "code": "src/dpo_alignment.py -> PreferencePairCurator.load()", "desc": "Loads (prompt, chosen_response, rejected_response) data tuples."},
            {"id": "N2", "title": "Step 2: Log-Likelihood Evaluation Across Policy & Reference Models", "code": "src/dpo_alignment.py -> DPOLossEngine.evaluate_logps()", "desc": "Calculates sequence log probabilities for chosen and rejected responses under policy and reference models."},
            {"id": "N3", "title": "Step 3: Compute Numerically Stable DPO Loss", "code": "src/dpo_alignment.py -> DPOLossEngine.compute_loss()", "desc": "Computes Implicit Reward Margin: beta * (log(pi/ref)_chosen - log(pi/ref)_rejected) with log-sigmoid stabilization."},
            {"id": "N4", "title": "Step 4: Bradley-Terry Win-Rate Audit", "code": "src/dpo_alignment.py -> BradleyTerryAuditor.audit()", "desc": "Evaluates policy alignment win-rate against reference model baseline."},
            {"id": "N5", "title": "Decision 1: Accuracy Win-Rate >= Target Threshold (e.g. 75%)?", "type": "decision", "desc": "Evaluates model preference alignment quality.", "yes": "PASS -> Export Aligned Model Checkpoint", "no": "FAIL -> Adjust Beta Hyperparameter & Retrain"}
        ]
    },
    {
        "num": "14",
        "dir": "14-custom-cuda-triton-kernel-opt",
        "title": "Custom OpenAI Triton GPU Kernels",
        "subtitle": "Fused Bias-GELU & Blocked Attention Roofline Performance Tuning",
        "file": "src/triton_kernels.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Prepare Input GPU Tensors in VRAM", "code": "src/triton_kernels.py -> TritonFusedKernels.launch_kernel()", "desc": "Allocates contiguous CUDA device memory for input X, Weight W, and Bias B."},
            {"id": "N2", "title": "Step 2: Grid 1D Block Launcher Configuration", "code": "src/triton_kernels.py -> FusedBiasGELU.grid_meta()", "desc": "Calculates grid dimensions BLOCK_SIZE = 1024 to maximize SM occupancy."},
            {"id": "N3", "title": "Step 3: Execute Fused Triton GPU Kernel", "code": "src/triton_kernels.py -> FusedBiasGELU.kernel_fn()", "desc": "Loads vector blocks into SRAM, executes fused add_bias + gelu in a single memory pass without VRAM round-trips."},
            {"id": "N4", "title": "Step 4: Roofline Performance Benchmarking", "code": "src/triton_kernels.py -> RooflineAnalyzer.analyze()", "desc": "Measures TFLOPS vs Arithmetic Intensity (FLOPs/byte) to verify memory bandwidth saturation."},
            {"id": "N5", "title": "Decision 1: Is Speedup >= PyTorch Native Baseline (e.g. 1.5x)?", "type": "decision", "desc": "Evaluates kernel optimization gain.", "yes": "PASS -> Register Optimized Kernel", "no": "FAIL -> Tune BLOCK_SIZE and Vector Load Alignment"}
        ]
    },
    {
        "num": "15",
        "dir": "15-feature-store-vector-lakehouse",
        "title": "Feature Store & Vector Lakehouse",
        "subtitle": "Dual Online Redis (<2ms) + Offline Parquet Point-in-Time Joins",
        "file": "src/feature_lakehouse.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Feature Retrieval Request", "code": "src/feature_lakehouse.py -> FeatureStoreOrchestrator.get_features()", "desc": "Receives entity IDs, feature names, and evaluation timestamp."},
            {"id": "N2", "title": "Step 2: Online Redis Store Lookup", "code": "src/feature_lakehouse.py -> RedisOnlineStore.read_online()", "desc": "Queries Redis in-memory cache for ultra-low latency feature vectors."},
            {"id": "N3", "title": "Decision 1: All Required Entity Features Present in Redis?", "type": "decision", "desc": "Evaluates online cache hit state.", "yes": "Return Online Features (<2ms Latency)", "no": "Fall Back to Offline Vector Lakehouse"},
            {"id": "N4", "title": "Step 4: PyArrow Point-in-Time Time-Travel Join", "code": "src/feature_lakehouse.py -> PyArrowVectorScanner.time_travel_join()", "desc": "Executes point-in-time ASOF join against Parquet dataset to prevent feature leakage."},
            {"id": "N5", "title": "Step 5: Write-Back Cache Update", "code": "src/feature_lakehouse.py -> RedisOnlineStore.write_online()", "desc": "Populates Redis online cache with retrieved offline features for future requests."}
        ]
    },
    {
        "num": "16",
        "dir": "16-ai-safety-red-teaming-guardrails",
        "title": "AI Safety & Policy Guardrails",
        "subtitle": "3-Stage Defense-in-Depth Prompt Injection & PII Redaction Pipeline",
        "file": "src/safety_guardrails.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Ingest User Prompt", "code": "src/safety_guardrails.py -> AISafetyGuardrails.scan_and_mask()", "desc": "Receives raw input prompt string for real-time safety inspection."},
            {"id": "N2", "title": "Step 2: Jailbreak & Prompt Injection Scan", "code": "src/safety_guardrails.py -> JailbreakScanner.scan_prompt()", "desc": "Evaluates prompt against DAN jailbreak patterns, system prompt overrides, and obfuscated delimiters."},
            {"id": "N3", "title": "Decision 1: Jailbreak / Malicious Intent Detected?", "type": "decision", "desc": "Evaluates prompt safety threat score.", "yes": "BLOCK -> Return HTTP 400 Policy Violation Exception", "no": "Proceed to PII Anonymizer"},
            {"id": "N4", "title": "Step 4: PII Data Redaction & Masking", "code": "src/safety_guardrails.py -> PIIAnonymizer.anonymize()", "desc": "Regex & NER scanner redacts SSNs, credit cards, emails, and phone numbers with [REDACTED] tokens."},
            {"id": "N5", "title": "Step 5: Llama Guard Output Policy Verification", "code": "src/safety_guardrails.py -> LlamaGuardAuditor.audit_output()", "desc": "Inspects generated LLM output before emitting to user."}
        ]
    },
    {
        "num": "17",
        "dir": "17-k8s-kuberay-kueue-gpu-operator",
        "title": "K8s KubeRay & Kueue GPU Operator",
        "subtitle": "Cloud-Native Kueue Priority Batch Queue & NVIDIA MIG Slicing",
        "file": "src/k8s_gpu.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Submit Batch GPU Workload (RayJob / PyTorchJob)", "code": "src/k8s_gpu.py -> KueueBatchScheduler.submit_job()", "desc": "Intercepts Job spec with requested GPU count, priority class, and resource quotas."},
            {"id": "N2", "title": "Step 2: Kueue LocalQueue & ClusterQueue Admission Check", "code": "src/k8s_gpu.py -> KueueBatchScheduler.admit_job()", "desc": "Checks ClusterQueue available GPU quotas and active running workloads."},
            {"id": "N3", "title": "Decision 1: Cluster GPU Quota Available?", "type": "decision", "desc": "Evaluates Kubernetes GPU cluster capacity.", "yes": "ADMIT -> Allocate GPU Nodes / MIG Slices", "no": "PENDING -> Queue Job in Priority Order"},
            {"id": "N4", "title": "Step 4: Preemption & Resource Slicing Engine", "code": "src/k8s_gpu.py -> MIGDeviceSlicer.provision_slices()", "desc": "If high-priority job arrives, preempts low-priority workloads and configures NVIDIA MIG slices (e.g. 1g.10gb)."},
            {"id": "N5", "title": "Step 5: KubeRay RayCluster Deployment", "code": "src/k8s_gpu.py -> KubeRayOperator.deploy_cluster()", "desc": "Provisions Ray Head Pod and Ray Worker Pods to execute distributed GPU training job."}
        ]
    },
    {
        "num": "18",
        "dir": "18-tensorrt-llm-onnx-execution",
        "title": "TensorRT-LLM Engine & ONNX",
        "subtitle": "PyTorch-to-ONNX Graph Exporters & TensorRT-LLM SmoothQuant Compilation",
        "file": "src/tensorrt_engine.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: PyTorch Model Graph Export to ONNX", "code": "src/tensorrt_engine.py -> ONNXExporter.export()", "desc": "Traces PyTorch LLM graph and exports dynamic-axes ONNX model binary."},
            {"id": "N2", "title": "Step 2: INT4 SmoothQuant Calibration", "code": "src/tensorrt_engine.py -> SmoothQuantFusion.calibrate()", "desc": "Applies activation scaling factors to migrate quantization difficulty from activations to weights."},
            {"id": "N3", "title": "Step 3: TensorRT Engine Building & Layer Fusion", "code": "src/tensorrt_engine.py -> TensorRTEngineCompiler.build_engine()", "desc": "Fuses MHA attention kernels, linear projections, and GEMM operations into a optimized TensorRT plan."},
            {"id": "N4", "title": "Decision 1: Did Engine Compilation Pass Benchmarks?", "type": "decision", "desc": "Evaluates compiled engine performance target.", "yes": "Save Plan File (.engine)", "no": "Fall Back to FP16 Optimization Mode"},
            {"id": "N5", "title": "Step 5: High-Throughput Engine Execution", "code": "src/tensorrt_engine.py -> TensorRTEngineCompiler.execute()", "desc": "Runs TensorRT engine achieving 1,480 tokens/sec throughput at <5ms P99 latency."}
        ]
    },
    {
        "num": "19",
        "dir": "19-multi-agent-swarm-orchestrator",
        "title": "Multi-Agent Swarm Orchestrator",
        "subtitle": "LangGraph Topological DAG Scheduler & Majority Voting Consensus",
        "file": "src/swarm_orchestrator.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Swarm Task Goal Ingestion", "code": "src/swarm_orchestrator.py -> SwarmOrchestrator.run_swarm()", "desc": "Parses complex user goal into dependent sub-task nodes."},
            {"id": "N2", "title": "Step 2: Topological DAG Dependency Sort & Cycle Detection", "code": "src/swarm_orchestrator.py -> TopologicalDAGScheduler.schedule()", "desc": "Performs Kahn's algorithm topological sort on task graph and verifies no circular dependencies exist."},
            {"id": "N3", "title": "Decision 1: Cycle Deadlock Detected?", "type": "decision", "desc": "Validates task dependency graph for circular cycles.", "yes": "Raise CycleDeadlockException & Abort", "no": "Dispatch Parallel Agent Workers"},
            {"id": "N4", "title": "Step 4: Multi-Agent Parallel Worker Execution", "code": "src/swarm_orchestrator.py -> SwarmOrchestrator._execute_agent_nodes()", "desc": "Executes independent agent nodes concurrently with shared DAG state context."},
            {"id": "N5", "title": "Step 5: Majority Voting Consensus Engine", "code": "src/swarm_orchestrator.py -> ConsensusEngine.evaluate_consensus()", "desc": "Aggregates agent outputs and computes majority voting consensus threshold (>66% agreement)."}
        ]
    },
    {
        "num": "20",
        "dir": "20-data-governance-openlineage-catalog",
        "title": "Data Governance & OpenLineage",
        "subtitle": "OpenLineage Event Telemetry Emitters & Marquez Lineage Graph Catalog",
        "file": "src/data_governance.py",
        "nodes": [
            {"id": "N1", "title": "Step 1: Pre-Job Data Contract Validation", "code": "src/data_governance.py -> GreatExpectationsValidator.validate()", "desc": "Checks incoming dataset schema, null counts, and column types against contract spec."},
            {"id": "N2", "title": "Decision 1: Data Contract Passed?", "type": "decision", "desc": "Evaluates schema and data quality rules.", "yes": "Emit OpenLineage START Event", "no": "Emit OpenLineage ABORT Event & Stop Pipeline"},
            {"id": "N3", "title": "Step 3: OpenLineage START Event Telemetry Emitter", "code": "src/data_governance.py -> OpenLineageCatalog.emit_event()", "desc": "Constructs standard OpenLineage JSON payload (job, inputs, run_id) and sends to Marquez REST API."},
            {"id": "N4", "title": "Step 4: Execute Transformation Job & Record Lineage Graph", "code": "src/data_governance.py -> MarquezGraphTracker.update_lineage()", "desc": "Registers dataset transformation dependencies into Marquez DAG visual catalog."},
            {"id": "N5", "title": "Step 5: Emit OpenLineage COMPLETE Event", "code": "src/data_governance.py -> OpenLineageCatalog.emit_event()", "desc": "Emits job completion status and row count metrics to lineage catalog."}
        ]
    }
]

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project {num}: {title} | Flowchart & Control Flow Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0c10;
            --bg-card: #12161f;
            --bg-card-hover: #1a202c;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-cyan: #38bdf8;
            --accent-emerald: #34d399;
            --accent-purple: #c084fc;
            --accent-amber: #fbbf24;
            --accent-rose: #f43f5e;
            --border-color: #21262d;
            --font-main: 'Inter', -apple-system, sans-serif;
            --font-code: 'JetBrains Mono', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-main);
            line-height: 1.6;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
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
        }}

        .nav-back:hover {{
            text-decoration: underline;
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            background: rgba(192, 132, 252, 0.1);
            color: var(--accent-purple);
            border: 1px solid rgba(192, 132, 252, 0.3);
            margin-bottom: 0.75rem;
        }}

        h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #f0f6fc 0%, #8b949e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        p.subtitle {{
            color: var(--text-secondary);
            font-size: 1.05rem;
        }}

        .section-title {{
            font-size: 1.4rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--accent-cyan);
        }}

        /* Flowchart Visual Grid */
        .flow-container {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            margin-bottom: 3rem;
        }}

        .flow-node {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-cyan);
            border-radius: 8px;
            padding: 1.25rem;
            position: relative;
            transition: all 0.2s ease;
        }}

        .flow-node:hover {{
            border-color: var(--accent-cyan);
            transform: translateX(4px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}

        .flow-node.decision {{
            border-left-color: var(--accent-amber);
            background: rgba(251, 191, 36, 0.03);
        }}

        .flow-node-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}

        .flow-node-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .code-tag {{
            font-family: var(--font-code);
            font-size: 0.8rem;
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-cyan);
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .flow-node.decision .code-tag {{
            background: rgba(251, 191, 36, 0.1);
            color: var(--accent-amber);
            border-color: rgba(251, 191, 36, 0.2);
        }}

        .flow-node-desc {{
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}

        .branches {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px dashed var(--border-color);
        }}

        .branch {{
            font-size: 0.85rem;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-family: var(--font-code);
        }}

        .branch.yes {{
            background: rgba(52, 211, 153, 0.1);
            color: var(--accent-emerald);
            border: 1px solid rgba(52, 211, 153, 0.2);
        }}

        .branch.no {{
            background: rgba(244, 63, 94, 0.1);
            color: var(--accent-rose);
            border: 1px solid rgba(244, 63, 94, 0.2);
        }}

        .flow-connector {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 1.2rem;
            margin: -0.5rem 0;
        }}

        /* Table Tutorial */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background: var(--bg-card);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}

        th, td {{
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.9rem;
        }}

        th {{
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-primary);
            font-weight: 600;
        }}

        td {{
            color: var(--text-secondary);
        }}

        td.code-cell {{
            font-family: var(--font-code);
            color: var(--accent-cyan);
            font-size: 0.82rem;
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
    </style>
</head>
<body>

    <header>
        <a href="../index.html" class="nav-back">&larr; Back to Main Platform Showcase</a>
        <div><span class="badge">PROJECT {num} TUTORIAL BLUEPRINT</span></div>
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
    </header>

    <div class="section-title">
        <span>🔀 Visual Logic & Control Flow Blueprint</span>
    </div>

    <div class="flow-container">
{nodes_html}
    </div>

    <div class="section-title">
        <span>📚 Codebase Mapping & Execution Reference Table</span>
    </div>

    <table>
        <thead>
            <tr>
                <th>Step / Phase</th>
                <th>Source Code Reference</th>
                <th>Description & Logic Purpose</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
{table_html}
        </tbody>
    </table>

    <footer>
        <p>&copy; 2026 Abhishek Singh • Staff & Principal AI Platform Architect</p>
        <p style="margin-top: 0.5rem;">
            <a href="PROD_ARCHITECTURE_REASONING.md" target="_blank">Architecture Reasoning</a> • 
            <a href="{file}" target="_blank">Source Code ({file})</a> • 
            <a href="../index.html">Main Platform Showcase</a>
        </p>
    </footer>

</body>
</html>
"""

for proj in projects:
    nodes_html = ""
    table_html = ""
    
    for idx, node in enumerate(proj["nodes"]):
        is_decision = node.get("type") == "decision"
        node_class = "flow-node decision" if is_decision else "flow-node"
        node_desc = node.get("desc", f"Evaluates control flow branch rule: {node.get('title')}")
        
        branches_markup = ""
        if is_decision:
            branches_markup = f'''
            <div class="branches">
                <div class="branch yes">✔ CONDITION TRUE: {node.get("yes", "Proceed")}</div>
                <div class="branch no">✖ CONDITION FALSE: {node.get("no", "Fallback")}</div>
            </div>
            '''
        
        code_tag_markup = f'<div class="code-tag">{node["code"]}</div>' if "code" in node else '<div class="code-tag">Condition Branch</div>'
        
        nodes_html += f'''
        <div class="{node_class}">
            <div class="flow-node-header">
                <div class="flow-node-title">{node["title"]}</div>
                {code_tag_markup}
            </div>
            <div class="flow-node-desc">{node_desc}</div>
            {branches_markup}
        </div>
        '''
        
        if idx < len(proj["nodes"]) - 1:
            nodes_html += '<div class="flow-connector">&darr;</div>'
            
        code_ref = node.get("code", "Branch Rule")
        node_type = "Conditional Decision" if is_decision else "Execution Action"
        
        table_html += f'''
        <tr>
            <td><strong>{node["title"]}</strong></td>
            <td class="code-cell">{code_ref}</td>
            <td>{node_desc}</td>
            <td>{node_type}</td>
        </tr>
        '''
    
    final_html = html_template.format(
        num=proj["num"],
        title=proj["title"],
        subtitle=proj["subtitle"],
        file=proj["file"],
        nodes_html=nodes_html,
        table_html=table_html
    )
    
    target_path = os.path.join("/Users/abhi/Documents/Antigravity", proj["dir"], "FLOWCHART.html")
    with open(target_path, "w") as f:
        f.write(final_html)
    print(f"Generated flowchart HTML for {proj['dir']} -> {target_path}")

print("All 20 FLOWCHART.html files generated successfully!")
