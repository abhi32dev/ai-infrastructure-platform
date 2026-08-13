import os
import sys

base_dir = "/Users/abhi/Documents/Antigravity"

projects = [
    {
        "num": "01",
        "dir": "01-agent-durable-runtime",
        "title": "Agentic Durable Runtime",
        "subtitle": "State Machine Checkpoint Persistence, Retry Loops & Rollback Engine",
        "file": "src/agent_runtime.py",
        "mermaid": """graph TD
    A([Start: execute_step]) --> B[Validate Payload & Schema]
    B --> C{Decision 1: Is Step Idempotent & Already Executed?}
    C -- YES: Step Checkpoint Found --> D[Retrieve Cached WAL State]
    D --> E([Emit Cached Output & Complete])
    C -- NO: New Step Execution --> F[Execute Agent Action / Tool Call]
    F --> G{Decision 2: Tool Execution Succeeded?}
    G -- YES: Zero Exceptions --> H[Save WAL Checkpoint to SQLite]
    H --> I([Advance Step Index & Complete])
    G -- NO: Tool Invocation Error --> J{Decision 3: Retry Count < Max 3?}
    J -- YES: Retries Remaining --> K[Rollback to Last Stable Checkpoint]
    K -- Re-queue Execution Loop --> F
    J -- NO: Max Retries Exceeded --> L[Escalate to Human-in-the-Loop Queue]
    L --> M([Halt Workflow State Machine])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,G,J decision;
    class A,E,M startend;
    class B,D,F,H,K,L process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Step Idempotent & Already Executed?",
                "code": "src/agent_runtime.py -> StateStore.get_active_state()",
                "condition": "Queries SQLite WAL event log for existing step_id checkpoint.",
                "yes_path": "LEFT BRANCH (Cache Hit): Replays cached state output directly without re-executing external tool calls ($0 computation).",
                "no_path": "RIGHT BRANCH (New Step): Proceeds to invoke external tool function within exception boundary."
            },
            {
                "title": "Decision 2: Did Tool Invocation Succeed?",
                "code": "src/agent_runtime.py -> DurableAgentRuntime._invoke_tool()",
                "condition": "Evaluates return payload for unhandled exceptions, null pointer responses, or runtime errors.",
                "yes_path": "LEFT BRANCH (Success): Atomically writes step checkpoint to SQLite WAL and updates active step pointer.",
                "no_path": "RIGHT BRANCH (Error): Triggers exception handler and evaluates retry budget allocation."
            },
            {
                "title": "Decision 3: Is Retry Counter < Max Retries (3)?",
                "code": "src/agent_runtime.py -> DurableAgentRuntime.rollback_to_step()",
                "condition": "Checks active retry counter against maximum threshold of 3 bounded attempts.",
                "yes_path": "LOOP UP (Retry): Rewinds SQLite transaction to last valid checkpoint state and re-queues tool execution.",
                "no_path": "DOWN BRANCH (Exhausted): Pauses workflow state machine and escalates step to Human-in-the-Loop (HITL) approval queue."
            }
        ]
    },
    {
        "num": "02",
        "dir": "02-rag-cost-router",
        "title": "RAG Cost Router Engine",
        "subtitle": "Cost-Aware Query Complexity Routing & Multi-Tier Vector Search Engine",
        "file": "src/rag_pipeline.py",
        "mermaid": """graph TD
    A([Start: route_query]) --> B[Ingest User Query & Compute Embedding]
    B --> C{Decision 1: Vector Semantic Cache Hit Cosine Sim >= 0.95?}
    C -- YES: Cosine Sim >= 0.95 --> D[Return Cached Answer: $0.00 Cost, <5ms]
    D --> E([Emit Response & Complete])
    C -- NO: Cache Miss --> F[Calculate Query Complexity Score]
    F --> G{Decision 2: Query Complexity Score <= 0.4?}
    G -- YES: Low Complexity --> H[Route to Local Ollama Model: $0.00 Cost]
    H --> E
    G -- NO: High Complexity --> I{Decision 3: Query Complexity Score > 0.8?}
    I -- YES: Extreme Multi-Hop --> J[Execute Hybrid RRF Vector Search + Frontier LLM: GPT-4o]
    J --> E
    I -- NO: Moderate Reasoning --> K[Route to Mid-Tier Model: Claude 3.5 Sonnet]
    K --> E

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,G,I decision;
    class A,E startend;
    class B,D,F,H,J,K process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Semantic Cache Similarity >= 0.95?",
                "code": "src/rag_pipeline.py -> RAGCostRouter._check_semantic_cache()",
                "condition": "Queries ChromaDB vector collection for cached prompt embedding distance.",
                "yes_path": "LEFT BRANCH (Cache Hit): Instantly returns pre-generated response (<5ms latency, $0.00 API cost).",
                "no_path": "RIGHT BRANCH (Cache Miss): Forwards query to complexity scoring engine."
            },
            {
                "title": "Decision 2: Is Query Complexity Score <= 0.4?",
                "code": "src/rag_pipeline.py -> QueryComplexityClassifier.classify()",
                "condition": "Evaluates token length, domain keyword density, and multi-hop reasoning requirements.",
                "yes_path": "LEFT BRANCH (Simple Query): Routes query to zero-cost local Ollama LLM instance.",
                "no_path": "RIGHT BRANCH (Complex Query): Evaluates frontier tier routing rules."
            },
            {
                "title": "Decision 3: Is Query Complexity Score > 0.8?",
                "code": "src/rag_pipeline.py -> RAGCostRouter.retrieve_hybrid()",
                "condition": "Checks if query requires multi-document fusion and deep analytical reasoning.",
                "yes_path": "TOP RIGHT BRANCH (High Complexity): Performs Reciprocal Rank Fusion (RRF) combining BM25 keyword search with ChromaDB vectors, then streams context to Frontier LLM (GPT-4o).",
                "no_path": "DOWN BRANCH (Medium Complexity): Routes query to mid-tier cloud LLM (Claude 3.5 Sonnet)."
            }
        ]
    },
    {
        "num": "03",
        "dir": "03-llm-eval-gate",
        "title": "LLM Evaluation Gate",
        "subtitle": "Automated Welch's t-Test RAG Triad Quality Release Gate",
        "file": "src/eval_gate.py",
        "mermaid": """graph TD
    A([Start: evaluate_build]) --> B[Load Candidate Benchmark Samples]
    B --> C[Compute RAG Triad Metrics: Faithfulness, Groundedness, Toxicity]
    C --> D[Execute Welch's t-Test Hypothesis Test vs Production Baseline]
    D --> E{Decision 1: p-value < 0.05 AND Metric Delta > +0.05?}
    E -- NO: Statistical Failure / Degradation --> F[Flag Quality Regression & Block Build]
    F --> G([Fail Release Gate & Raise CI/CD Error])
    E -- YES: Significant Quality Gain --> H{Decision 2: Toxicity Score <= 0.05 Threshold?}
    H -- NO: Toxicity Safety Violation --> I[Flag Safety Offense & Alert Team]
    I --> G
    H -- YES: Safety Verified --> J[Register Approved Model Artifact in MLflow]
    J --> K([Pass Release Gate & Trigger Deployment])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class E,H decision;
    class A,G,K startend;
    class B,C,D,F,I,J process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Welch t-Test p-value < 0.05 AND Mean Delta > +0.05?",
                "code": "src/eval_gate.py -> WelchTTestScorer.compare()",
                "condition": "Calculates Welch's unequal variances t-statistic to determine if quality improvement over baseline is statistically significant.",
                "yes_path": "RIGHT BRANCH (Passed Stat Gate): Candidate model shows statistically significant performance improvement. Proceeds to toxicity check.",
                "no_path": "LEFT BRANCH (Regression / Inconclusive): Model shows performance degradation or statistically insignificant variance. Fails CI/CD build."
            },
            {
                "title": "Decision 2: Is Toxicity Score <= 0.05 Safety Threshold?",
                "code": "src/eval_gate.py -> ToxicityEvaluator.check_safety()",
                "condition": "Scans 100% of candidate evaluation samples for toxic, biased, or dangerous generation content.",
                "yes_path": "DOWN RIGHT BRANCH (Safety Passed): Approves candidate model and registers model artifact in MLflow registry.",
                "no_path": "LEFT BRANCH (Safety Violation): Blocks deployment immediately and dispatches PagerDuty security alert."
            }
        ]
    },
    {
        "num": "04",
        "dir": "04-model-serving-mlops",
        "title": "Model Serving MLOps",
        "subtitle": "Canary Rollout Engine & OpenTelemetry Traceparent Pipeline",
        "file": "src/model_serving.py",
        "mermaid": """graph TD
    A([Start: predict_with_canary]) --> B[Extract W3C Traceparent Header & Bind OTel Span]
    B --> C{Decision 1: Active Queue Depth > Max Backpressure 50?}
    C -- YES: Server Queue Saturated --> D[Reject Request with HTTP 429 Rate Limit]
    D --> E([Emit Drop Telemetry & Terminate])
    C -- NO: Queue Capacity Available --> F[Generate Uniform Random Roll in 0.0, 1.0]
    F --> G{Decision 2: Roll < Active Canary Traffic Split e.g. 10%?}
    G -- YES: Canary Selected --> H[Route Request to Canary Model Instance v2]
    G -- NO: Baseline Selected --> I[Route Request to Production Baseline Model v1]
    H --> J[Execute Forward Inference Pass]
    I --> J
    J --> K[Record Latency & OTel Span Attributes]
    K --> L([Return Inference Response Payload])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,G decision;
    class A,E,L startend;
    class B,D,F,H,I,J,K process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Active Queue Depth > Max Limit (50)?",
                "code": "src/model_serving.py -> ModelServingPipeline._check_backpressure()",
                "condition": "Monitors in-flight API requests against server concurrency bounds to prevent worker thread starvation.",
                "yes_path": "RIGHT BRANCH (Queue Saturated): Rejects incoming request immediately with HTTP 429 backpressure status.",
                "no_path": "DOWN BRANCH (Capacity Normal): Accepts request into active execution queue."
            },
            {
                "title": "Decision 2: Is Random Roll < Active Canary Weight (10%)?",
                "code": "src/model_serving.py -> CanaryRolloutEngine.select_target()",
                "condition": "Evaluates pseudo-random float against active canary traffic split configuration.",
                "yes_path": "LEFT BRANCH (Canary Selected): Routes request to new candidate model instance (v2).",
                "no_path": "RIGHT BRANCH (Baseline Selected): Routes request to current stable production model instance (v1)."
            }
        ]
    },
    {
        "num": "05",
        "dir": "05-event-stream-pyspark-etl",
        "title": "Event Stream PySpark ETL",
        "subtitle": "Structured Streaming 3-Pass Storage Reconciliation Pipeline",
        "file": "src/event_pipeline.py",
        "mermaid": """graph TD
    A([Start: process_stream]) --> B[Ingest Kafka Telemetry Stream into PySpark DataFrame]
    B --> C[Apply 10-Min Event-Time Watermarking & Windowing]
    C --> D{Decision 1: Is Event Timestamp < Watermark Boundary?}
    D -- YES: Expired Late Event --> E[Drop Late Record & Log Telemetry Metric]
    E --> F([Discard Record])
    D -- NO: Valid Time Window --> G[Deduplicate Records by device_id & timestamp]
    G --> H[Execute 3-Pass Storage Reconciliation: Raw -> Silver -> Gold]
    H --> I{Decision 2: Data Schema & Quality Contract Valid?}
    I -- YES: Schema Contract Passed --> J[Atomically Write Record to Delta Lake Gold Table]
    J --> K([Update OpenLineage Telemetry & Complete])
    I -- NO: Contract Violation / Corrupt --> L[Quarantine Record to Dead-Letter Queue DLQ]
    L --> M([Emit Quarantine Alert])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class D,I decision;
    class A,F,K,M startend;
    class B,C,E,G,H,J,L process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Event Timestamp < Watermark Boundary?",
                "code": "src/event_pipeline.py -> EventStreamETL._apply_watermark()",
                "condition": "Checks if event arrival timestamp is older than the 10-minute sliding window watermark.",
                "yes_path": "LEFT BRANCH (Expired Late Arrival): Drops event to prevent state store memory bloat.",
                "no_path": "RIGHT BRANCH (Valid Window): Forwards event to stream deduplication engine."
            },
            {
                "title": "Decision 2: Is Schema & Quality Contract Valid?",
                "code": "src/event_pipeline.py -> StorageReconciler.three_pass_reconcile()",
                "condition": "Validates Gold layer schema types, null value constraints, and metric bounds.",
                "yes_path": "RIGHT BRANCH (Passed Contract): Writes record atomically to Delta Lake Gold storage with ACID guarantees.",
                "no_path": "DOWN BRANCH (Contract Violation): Routes record to S3 Dead-Letter Queue (DLQ) for forensic inspection."
            }
        ]
    },
    {
        "num": "06",
        "dir": "06-finetuning-lora-alignment",
        "title": "Fine-Tuning LoRA Alignment",
        "subtitle": "PEFT LoRA Parameter Reduction & GGUF Quantization Pipeline",
        "file": "src/lora_trainer.py",
        "mermaid": """graph TD
    A([Start: train_peft]) --> B[Curate Dataset & Create Train/Val Splits]
    B --> C[Freeze Base Weights & Inject LoRA Adapters r=8, alpha=16]
    C --> D[Execute Training Step: Forward Pass & Loss Calculation]
    D --> E{Decision 1: Validation Loss Converged OR Epoch Max Reached?}
    E -- NO: Training Active --> F[Update Optimizer Weights & Step LR Scheduler]
    F -- Loop Back to Next Epoch Step --> D
    E -- YES: Target Converged --> G[Save LoRA Adapter Checkpoint Weights]
    G --> H[Fuse LoRA Matrix Weights with Base Model Transformer Layers]
    H --> I[Quantize Fused Weights to GGUF Q4_K_M Format]
    I --> J([Export Binary Model & Complete])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class E decision;
    class A,J startend;
    class B,C,D,F,G,H,I process;""",
        "decisions": [
            {
                "title": "Decision 1: Has Validation Loss Converged OR Max Epochs Reached?",
                "code": "src/lora_trainer.py -> LoRATrainer.train()",
                "condition": "Evaluates validation loss slope across 3 consecutive evaluation steps.",
                "yes_path": "DOWN BRANCH (Converged): Exits training loop, saves LoRA adapter weights, and triggers fusion pipeline.",
                "no_path": "LOOP UP (Continue Training): Updates optimizer weights, steps learning rate scheduler, and proceeds to next epoch."
            }
        ]
    },
    {
        "num": "07",
        "dir": "07-cloud-iac-security-governance",
        "title": "Cloud IaC Security Governance",
        "subtitle": "CDK / Terraform AST Scanner & IAM Wildcard Audit Engine",
        "file": "src/cloud_governance.py",
        "mermaid": """graph TD
    A([Start: scan_template]) --> B[Parse CloudFormation / CDK Template AST]
    B --> C{Decision 1: Wildcard IAM Policy Detected Action=='*'? }
    C -- YES: Forbidden Wildcard --> D[Flag CRITICAL IAM Security Violation]
    C -- NO: Least-Privilege IAM --> E{Decision 2: S3 Bucket Unencrypted OR Public?}
    D --> F[Increment Security Offense Counter]
    E -- YES: Unencrypted / Public --> G[Flag HIGH Storage Security Violation]
    E -- NO: Encrypted & Private --> H[Pass Storage Audit Check]
    G --> F
    F --> I{Decision 3: Total Security Offenses == 0?}
    H --> I
    I -- YES: Clean Audit --> J[Approve IaC Deployment Pipeline]
    J --> K([Pass CI/CD Build])
    I -- NO: Policy Offenses Found --> L[Block CI/CD Build & Export Governance Report]
    L --> M([Fail Security Gate])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,E,I decision;
    class A,K,M startend;
    class B,D,F,G,H,J,L process;""",
        "decisions": [
            {
                "title": "Decision 1: Are Wildcard IAM Permissions Detected?",
                "code": "src/cloud_governance.py -> IAMWildcardAuditor.audit_policies()",
                "condition": "Scans AST IAM statements for forbidden '*' Action or Resource wildcards.",
                "yes_path": "LEFT BRANCH (Security Violation): Flags CRITICAL security policy offense.",
                "no_path": "RIGHT BRANCH (Policy Compliant): Passes IAM audit check and proceeds to storage scan."
            },
            {
                "title": "Decision 2: Is S3 Storage Unencrypted OR Publicly Accessible?",
                "code": "src/cloud_governance.py -> CDKASTRuleEngine.check_storage()",
                "condition": "Verifies KMS encryption flags and public bucket block configuration.",
                "yes_path": "LEFT BRANCH (Storage Violation): Flags HIGH security offense for unencrypted/public bucket.",
                "no_path": "RIGHT BRANCH (Secure Bucket): Passes storage compliance check."
            },
            {
                "title": "Decision 3: Total Security Offenses == 0?",
                "code": "src/cloud_governance.py -> IaCSecurityScanner.evaluate()",
                "condition": "Evaluates cumulative offense count across all AST security rules.",
                "yes_path": "DOWN RIGHT BRANCH (Clean Audit): Approves IaC deployment pipeline.",
                "no_path": "DOWN LEFT BRANCH (Offenses Found): Fails security release gate and blocks deployment."
            }
        ]
    },
    {
        "num": "08",
        "dir": "08-vllm-pagedattention-spec-decoding",
        "title": "vLLM PagedAttention & Speculative",
        "subtitle": "Paged KV Cache Virtual Memory & Speculative Token Verification",
        "file": "src/vllm_engine.py",
        "mermaid": """graph TD
    A([Start: generate]) --> B[Ingest Token Request & Calculate Block Needs]
    B --> C{Decision 1: Free VRAM Physical Blocks >= Required?}
    C -- NO: Memory Pressure --> D[Preempt & Evict Low-Priority KV Blocks to Host CPU RAM]
    D --> E[Reclaim VRAM Physical Block Space]
    E --> C
    C -- YES: Memory Available --> F[Map Logical Blocks to Non-Contiguous VRAM Blocks]
    F --> G[Draft Model Rapidly Speculates K Tokens]
    G --> H[Target Model Executes Parallel Verification]
    H --> I{Decision 2: How Many Draft Tokens Accepted by Target?}
    I -- All K Tokens Accepted --> J[Advance Sequence Pos by K & Reclaim Unused Blocks]
    I -- Partial N < K Accepted --> K[Accept N Tokens, Sample Correct Token, Reclaim Invalid Draft KV Blocks]
    J --> L([Emit Token Sequence & Complete])
    K --> L

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,I decision;
    class A,L startend;
    class B,D,E,F,G,H,J,K process;""",
        "decisions": [
            {
                "title": "Decision 1: Free VRAM Physical Blocks >= Required Blocks?",
                "code": "src/paged_kv_cache.py -> PagedKVCacheManager.allocate_blocks()",
                "condition": "Checks available 16-token physical VRAM memory blocks.",
                "yes_path": "DOWN BRANCH (Memory Available): Binds logical token blocks to physical VRAM blocks with zero fragmentation.",
                "no_path": "LEFT BRANCH (Memory Pressure): Preempts lowest priority sequence, evicts KV blocks to host CPU RAM, and retries allocation."
            },
            {
                "title": "Decision 2: How Many Speculative Draft Tokens Accepted by Target Model?",
                "code": "src/speculative_verifier.py -> SpeculativeVerifier.verify_tokens()",
                "condition": "Evaluates target model logit predictions against draft model speculated K tokens in parallel.",
                "yes_path": "LEFT BRANCH (All K Accepted): Maximum 2.67x generation speedup. Advances sequence position by K tokens.",
                "no_path": "RIGHT BRANCH (Partial N < K Accepted): Accepts N matching tokens, samples true replacement token, and reclaims invalid draft KV blocks."
            }
        ]
    },
    {
        "num": "09",
        "dir": "09-ray-distributed-cluster-orchestrator",
        "title": "Ray Distributed Cluster Orchestrator",
        "subtitle": "Ray Core Actor Pools, Zero-Copy Plasma Store & Cluster Autoscaler",
        "file": "src/ray_cluster.py",
        "mermaid": """graph TD
    A([Start: execute_task]) --> B[Write Large Task Payload to Plasma Shared Memory Store]
    B --> C{Decision 1: Pending Tasks / Idle Actor Ratio > Scale-Up Threshold?}
    C -- YES: High Demand --> D[Provision New Ray Worker Nodes Scale Up]
    D --> E[Bind Actors to Worker Pool]
    E --> F[Dispatch Task to Idle Ray Actor]
    C -- NO: Capacity Normal --> G{Decision 2: Idle Worker Count > 0 AND Idle Time > 300s?}
    G -- YES: Over-Provisioned --> H[Terminate Excess Worker Nodes Scale Down]
    H --> F
    G -- NO: Optimal Cluster State --> F
    F --> I[Actor Worker Processes Shared Memory Payload Zero-Copy]
    I --> J([Return Ray ObjectRef & Complete])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,G decision;
    class A,J startend;
    class B,D,E,F,H,I process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Pending Tasks / Idle Actor Ratio > Scaling Threshold?",
                "code": "src/cluster_autoscaler.py -> ClusterAutoscaler.check_capacity()",
                "condition": "Evaluates queue backlog depth against active actor processing capacity.",
                "yes_path": "RIGHT BRANCH (Scale Up): Provisions new Ray worker nodes to handle load burst.",
                "no_path": "DOWN BRANCH (Capacity Normal): Evaluates scale-down criteria."
            },
            {
                "title": "Decision 2: Are Idle Workers > 0 AND Idle Time > 300s?",
                "code": "src/cluster_autoscaler.py -> ClusterAutoscaler.check_capacity()",
                "condition": "Monitors worker node idle timeouts to prevent unnecessary cloud compute billing.",
                "yes_path": "LEFT BRANCH (Scale Down): Terminates excess idle worker nodes.",
                "no_path": "RIGHT BRANCH (Maintain): Keeps active worker pool state unchanged."
            }
        ]
    },
    {
        "num": "10",
        "dir": "10-triton-cuda-gpu-scheduler",
        "title": "Triton CUDA GPU Scheduler",
        "subtitle": "Dynamic Batching Queue & AWQ INT4 Quantized Inference Engine",
        "file": "src/triton_engine.py",
        "mermaid": """graph TD
    A([Start: enqueue_request]) --> B[Push Request Payload to Dynamic Batch Queue]
    B --> C{Decision 1: Batch Size == Max (32) OR Queue Delay >= 10ms?}
    C -- NO: Queue Collecting --> D[Wait for Next Request Arrival]
    D -- Re-evaluate Collector Loop --> C
    C -- YES: Batch Triggered --> E[Align Tensor Memory to Power-of-2 for CUDA Tensor Cores]
    E --> F[Execute AWQ INT4 Matrix Multiplication Kernel on Tensor Cores]
    F --> G[Unpack Output Batch Response Tensor]
    G --> H[Scatter Stream Outputs to Client Futures]
    H --> I([Emit Stream Response & Complete])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C decision;
    class A,I startend;
    class B,D,E,F,G,H process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Batch Size == Max (32) OR Queue Delay >= 10ms?",
                "code": "src/triton_engine.py -> DynamicBatchingQueue.collect_batch()",
                "condition": "Evaluates dynamic batching queue triggers (batch capacity vs latency timeout).",
                "yes_path": "DOWN BRANCH (Batch Ready): Formats tensor-aligned GPU batch and launches AWQ INT4 kernel.",
                "no_path": "LOOP UP (Waiting): Holds request in queue buffer up to maximum 10ms delay."
            }
        ]
    },
    {
        "num": "11",
        "dir": "11-distributed-training-fsdp-megatron",
        "title": "Distributed Training (FSDP & Megatron)",
        "subtitle": "PyTorch FSDP ZeRO-3 Memory Sharding & Megatron 3D Grid Engine",
        "file": "src/distributed_training.py",
        "mermaid": """graph TD
    A([Start: train_step]) --> B[Map GPU Ranks to Megatron 3D Grid: TP x PP x DP]
    B --> C[Shard Weights, Gradients & Optimizer States with PyTorch FSDP ZeRO-3]
    C --> D[Execute All-Gather -> Forward Pass -> Free Unsharded Parameters]
    D --> E[Execute Backward Pass -> Compute Gradients -> Reduce-Scatter]
    E --> F{Decision 1: Gradient Norm <= Max Threshold AND Loss finite?}
    F -- NO: Gradient Explosion / NaN --> G[Skip Step, Clip Gradients & Log Warning]
    G --> H([Proceed to Next Batch Step])
    F -- YES: Valid Gradient --> I[Update Optimizer Sharded Parameter Weights]
    I --> H

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class F decision;
    class A,H startend;
    class B,C,D,E,G,I process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Gradient Norm <= Max Threshold AND Loss Finite?",
                "code": "src/distributed_training.py -> FSDPZeRO3Trainer.backward_step()",
                "condition": "Validates gradient norm across all DP ranks to prevent training instability.",
                "yes_path": "DOWN BRANCH (Valid Step): Updates sharded optimizer parameters and proceeds to next batch.",
                "no_path": "LEFT BRANCH (NaN / Overflow): Clips exploding gradients, skips step weight update, and logs alert metric."
            }
        ]
    },
    {
        "num": "12",
        "dir": "12-genai-gateway-semantic-cache",
        "title": "GenAI Gateway & Semantic Cache",
        "subtitle": "Vector Cache Hits, Token-Bucket Rate Limiter & Fallback Cascade",
        "file": "src/genai_gateway.py",
        "mermaid": """graph TD
    A([Start: process_prompt]) --> B{Decision 1: Token Bucket Remaining Capacity > 0?}
    B -- NO: Rate Limit Exceeded --> C[Reject Request with HTTP 429 Too Many Requests]
    C --> D([Terminate Request])
    B -- YES: Rate Limit Allowed --> E[Compute Prompt Embedding & Search Vector Semantic Cache]
    E --> F{Decision 2: Vector Cache Hit Cosine Similarity >= 0.92?}
    F -- YES: Cache Hit --> G[Return Cached Response Payload: <5ms, $0.00 Cost]
    G --> H([Emit Response & Complete])
    F -- NO: Cache Miss --> I{Decision 3: Primary Provider OpenAI Responded?}
    I -- YES: Primary Success --> J[Write Generation to Vector Cache -> Return Payload]
    J --> H
    I -- NO: Primary 5xx / Timeout --> K[Fallback to Secondary Provider: Anthropic / Ollama]
    K --> H

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class B,F,I decision;
    class A,D,H startend;
    class C,E,G,J,K process;""",
        "decisions": [
            {
                "title": "Decision 1: Token Bucket Remaining Capacity > 0?",
                "code": "src/genai_gateway.py -> TokenBucketLimiter.consume()",
                "condition": "Checks client API key token bucket capacity against refill rate bounds.",
                "yes_path": "DOWN BRANCH (Allowed): Deducts tokens and proceeds to cache lookup.",
                "no_path": "RIGHT BRANCH (Rate Limited): Rejects request with HTTP 429 status."
            },
            {
                "title": "Decision 2: Is Vector Cache Cosine Similarity >= 0.92?",
                "code": "src/genai_gateway.py -> VectorSemanticCache.lookup()",
                "condition": "Searches vector index for semantic similarity matching.",
                "yes_path": "LEFT BRANCH (Cache Hit): Instantly returns cached generation (<5ms, $0.00 cost).",
                "no_path": "RIGHT BRANCH (Cache Miss): Forwards request to provider fallback cascade."
            },
            {
                "title": "Decision 3: Did Primary Provider (OpenAI) Respond Successfully?",
                "code": "src/genai_gateway.py -> MultiProviderRouter.dispatch()",
                "condition": "Evaluates HTTP status code and response timeout from primary LLM provider.",
                "yes_path": "DOWN LEFT BRANCH (Primary Success): Writes prompt/generation pair to vector cache and returns response.",
                "no_path": "DOWN RIGHT BRANCH (Primary Failure): Automatically triggers zero-downtime fallback cascade to Anthropic/Ollama."
            }
        ]
    },
    {
        "num": "13",
        "dir": "13-rlhf-dpo-alignment-pipeline",
        "title": "RLHF DPO Alignment Pipeline",
        "subtitle": "Direct Preference Optimization Loss & Bradley-Terry Win-Rate Auditor",
        "file": "src/dpo_alignment.py",
        "mermaid": """graph TD
    A([Start: train_dpo]) --> B[Load Pairwise Preference Data: chosen vs rejected]
    B --> C[Compute Sequence Log-Likelihoods under Policy & Reference Models]
    C --> D[Compute DPO Loss: beta * log_pi_ref_chosen - log_pi_ref_rejected]
    D --> E[Execute Optimization Step & Update Policy Weights]
    E --> F[Run Bradley-Terry Model Win-Rate Audit]
    F --> G{Decision 1: Preference Win-Rate >= Target Threshold 75%?}
    G -- YES: Alignment Successful --> H[Export Aligned Policy Model Checkpoint]
    H --> I([Complete DPO Alignment Pipeline])
    G -- NO: Insufficient Alignment --> J[Adjust Beta Loss Scaling & Retrain]
    J -- Loop Back to Retrain Step --> C

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class G decision;
    class A,I startend;
    class B,C,D,E,F,H,J process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Preference Win-Rate >= Target Threshold (75%)?",
                "code": "src/dpo_alignment.py -> BradleyTerryAuditor.audit()",
                "condition": "Evaluates policy model output preference win-rate against reference model baseline.",
                "yes_path": "DOWN BRANCH (Aligned): Exports aligned policy model checkpoint.",
                "no_path": "LOOP UP (Adjust Beta): Adjusts DPO beta implicit reward margin scaling factor and retrains."
            }
        ]
    },
    {
        "num": "14",
        "dir": "14-custom-cuda-triton-kernel-opt",
        "title": "Custom OpenAI Triton GPU Kernels",
        "subtitle": "Fused Bias-GELU & Blocked Attention Roofline Performance Tuning",
        "file": "src/triton_kernels.py",
        "mermaid": """graph TD
    A([Start: launch_kernel]) --> B[Allocate Device Memory for Tensors X, W, B in VRAM]
    B --> C[Calculate 1D Grid Meta BLOCK_SIZE = 1024]
    C --> D[Launch Fused Triton Kernel: Bias Add + GELU in single SRAM pass]
    D --> E[Execute Roofline Performance Benchmarking: TFLOPS vs FLOPs/byte]
    E --> F{Decision 1: Kernel Speedup >= 1.5x Native PyTorch Baseline?}
    F -- YES: Optimization Goal Achieved --> G[Register Kernel in Production Fused Library]
    G --> H([Complete Kernel Optimization])
    F -- NO: Sub-Optimal Throughput --> I[Re-tune SRAM Vector Block Size & Stride]
    I -- Re-launch Kernel Grid --> D

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class F decision;
    class A,H startend;
    class B,C,D,E,G,I process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Kernel Speedup >= 1.5x Native PyTorch Baseline?",
                "code": "src/triton_kernels.py -> RooflineAnalyzer.analyze()",
                "condition": "Evaluates arithmetic intensity and memory bandwidth saturation against roofline limit.",
                "yes_path": "DOWN BRANCH (Speedup Achieved): Registers fused Triton GPU kernel into production kernel library.",
                "no_path": "LOOP UP (Tune Stride): Re-tunes block size alignment and SRAM vector load strides."
            }
        ]
    },
    {
        "num": "15",
        "dir": "15-feature-store-vector-lakehouse",
        "title": "Feature Store & Vector Lakehouse",
        "subtitle": "Dual Online Redis (<2ms) + Offline Parquet Point-in-Time Joins",
        "file": "src/feature_lakehouse.py",
        "mermaid": """graph TD
    A([Start: get_features]) --> B{Decision 1: All Entity Features Present in Redis Online Cache?}
    B -- YES: Online Cache Hit --> C[Return Online Feature Vector: <2ms Latency]
    C --> D([Complete Feature Request])
    B -- NO: Online Cache Miss --> E[Fall Back to Offline Parquet Vector Lakehouse]
    E --> F[Execute PyArrow Point-in-Time ASOF Time-Travel Join]
    F --> G[Write Retrieved Features Back to Redis Online Cache]
    G --> D

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class B decision;
    class A,D startend;
    class C,E,F,G process;""",
        "decisions": [
            {
                "title": "Decision 1: Are All Entity Features Present in Redis Online Store?",
                "code": "src/feature_lakehouse.py -> RedisOnlineStore.read_online()",
                "condition": "Queries Redis in-memory key-value cache for active entity feature vectors.",
                "yes_path": "LEFT BRANCH (Online Hit): Instantly returns features (<2ms latency).",
                "no_path": "RIGHT BRANCH (Offline Fallback): Executes PyArrow ASOF point-in-time time-travel join against Parquet feature lakehouse to prevent feature leakage, then populates Redis cache."
            }
        ]
    },
    {
        "num": "16",
        "dir": "16-ai-safety-red-teaming-guardrails",
        "title": "AI Safety & Policy Guardrails",
        "subtitle": "3-Stage Defense-in-Depth Prompt Injection & PII Redaction Pipeline",
        "file": "src/safety_guardrails.py",
        "mermaid": """graph TD
    A([Start: scan_and_mask]) --> B{Decision 1: Jailbreak / Prompt Injection Threat Detected?}
    B -- YES: Malicious Prompt --> C[Reject Request with HTTP 400 Policy Violation]
    C --> D([Log Security Attack Event & Halt])
    B -- NO: Safe Prompt Intent --> E[Redact PII Tokens: SSN, Credit Card, Email with REDACTED]
    E --> F[Generate LLM Output Response]
    F --> G{Decision 2: Llama Guard Output Safety Verification Passed?}
    G -- YES: Safe Output --> H[Emit Safe Anonymized Response]
    H --> I([Complete Request])
    G -- NO: Unsafe Generation --> J[Redact Unsafe Output & Log Security Incident]
    J --> I

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class B,G decision;
    class A,D,I startend;
    class C,E,F,H,J process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Jailbreak / Prompt Injection Threat Detected?",
                "code": "src/safety_guardrails.py -> JailbreakScanner.scan_prompt()",
                "condition": "Scans input prompt string against DAN jailbreak patterns, system overrides, and obfuscated delimiters.",
                "yes_path": "LEFT BRANCH (Threat Detected): Rejects request with HTTP 400 policy violation and logs attack event.",
                "no_path": "RIGHT BRANCH (Safe Intent): Passes prompt to PII redaction scanner."
            },
            {
                "title": "Decision 2: Did Llama Guard Output Safety Verification Pass?",
                "code": "src/safety_guardrails.py -> LlamaGuardAuditor.audit_output()",
                "condition": "Scans generated output before emitting to client.",
                "yes_path": "LEFT BRANCH (Safe Output): Emits safe anonymized response payload.",
                "no_path": "RIGHT BRANCH (Unsafe Output): Redacts unsafe output and logs security incident."
            }
        ]
    },
    {
        "num": "17",
        "dir": "17-k8s-kuberay-kueue-gpu-operator",
        "title": "K8s KubeRay & Kueue GPU Operator",
        "subtitle": "Cloud-Native Kueue Priority Batch Queue & NVIDIA MIG Slicing",
        "file": "src/k8s_gpu.py",
        "mermaid": """graph TD
    A([Start: submit_job]) --> B[Intercept Batch Job Spec: requested GPUs & priority]
    B --> C{Decision 1: ClusterQueue Available GPU Quota >= Requested GPUs?}
    C -- YES: GPU Capacity Available --> D[Admit Job & Provision KubeRay RayCluster Pods]
    D --> E([Deploy Workload & Complete Admission])
    C -- NO: GPU Quota Full --> F{Decision 2: Arriving Job Priority > Active Workloads?}
    F -- YES: High Priority Job --> G[Preempt Low-Priority Job & Slice NVIDIA MIG Devices 1g.10gb]
    G --> D
    F -- NO: Standard Priority --> H[Queue Job in Kueue Priority Pending Queue]
    H --> I([Wait in Pending Admission Queue])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C,F decision;
    class A,E,I startend;
    class B,D,G,H process;""",
        "decisions": [
            {
                "title": "Decision 1: ClusterQueue Available GPU Quota >= Requested GPUs?",
                "code": "src/k8s_gpu.py -> KueueBatchScheduler.admit_job()",
                "condition": "Checks active ClusterQueue GPU quota availability.",
                "yes_path": "RIGHT BRANCH (Capacity Available): Admits job and provisions KubeRay RayCluster pods.",
                "no_path": "DOWN BRANCH (Quota Full): Evaluates preemption rules."
            },
            {
                "title": "Decision 2: Is Arriving Job Priority > Active Workloads?",
                "code": "src/k8s_gpu.py -> MIGDeviceSlicer.provision_slices()",
                "condition": "Evaluates Kubernetes PriorityClass specs of pending vs running jobs.",
                "yes_path": "RIGHT BRANCH (Preempt & Slice): Preempts lower priority workloads and configures hardware-isolated NVIDIA MIG slices (1g.10gb).",
                "no_path": "DOWN BRANCH (Pending Queue): Enqueues job into Kueue priority pending queue."
            }
        ]
    },
    {
        "num": "18",
        "dir": "18-tensorrt-llm-onnx-execution",
        "title": "TensorRT-LLM Engine & ONNX",
        "subtitle": "PyTorch-to-ONNX Graph Exporters & TensorRT-LLM SmoothQuant Compilation",
        "file": "src/tensorrt_engine.py",
        "mermaid": """graph TD
    A([Start: build_engine]) --> B[Export PyTorch LLM Graph to Dynamic ONNX Binary]
    B --> C[Apply INT4 SmoothQuant Activation Scaling Calibration]
    C --> D[Compile TensorRT Plan Engine: Fuse MHA & Linear GEMM Kernels]
    D --> E{Decision 1: TensorRT Latency < 5ms P99 Target?}
    E -- YES: Benchmark Passed --> F[Save Engine Plan File .engine & Deploy Runtime]
    F --> G([Complete TensorRT Deployment])
    E -- NO: Target Missed --> H[Fall Back to FP16 Optimization Mode & Rebuild]
    H --> F

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class E decision;
    class A,G startend;
    class B,C,D,F,H process;""",
        "decisions": [
            {
                "title": "Decision 1: Is TensorRT Benchmark Latency < 5ms P99 Target?",
                "code": "src/tensorrt_engine.py -> TensorRTEngineCompiler.build_engine()",
                "condition": "Benchmarks compiled engine inference throughput and P99 latency target.",
                "yes_path": "DOWN BRANCH (Benchmark Passed): Saves compiled `.engine` plan file achieving 1,480 tokens/sec throughput.",
                "no_path": "RIGHT BRANCH (Fallback Mode): Falls back to FP16 optimization mode to ensure engine stability."
            }
        ]
    },
    {
        "num": "19",
        "dir": "19-multi-agent-swarm-orchestrator",
        "title": "Multi-Agent Swarm Orchestrator",
        "subtitle": "LangGraph Topological DAG Scheduler & Majority Voting Consensus",
        "file": "src/swarm_orchestrator.py",
        "mermaid": """graph TD
    A([Start: run_swarm]) --> B[Construct Task Dependency Graph DAG]
    B --> C[Run Kahn's Topological Sort & Cycle Detection]
    C --> D{Decision 1: Circular Task Dependency Cycle Detected?}
    D -- YES: Deadlock Detected --> E[Raise CycleDeadlockException & Abort Swarm Task]
    E --> F([Terminate Task Execution])
    D -- NO: Clean DAG Graph --> G[Dispatch Independent Agent Worker Nodes Concurrently]
    G --> H[Aggregate Agent Outputs & Evaluate Majority Voting Consensus]
    H --> I{Decision 2: Voting Consensus Agreement Score >= 66%?}
    I -- YES: Consensus Reached --> J[Emit Consensus Swarm Result Payload]
    J --> K([Complete Swarm Task Goal])
    I -- NO: Agreement Below Threshold --> L[Trigger Tie-Breaker Evaluator Agent to Re-evaluate]
    L --> J

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class D,I decision;
    class A,F,K startend;
    class B,C,E,G,H,J,L process;""",
        "decisions": [
            {
                "title": "Decision 1: Is Circular Task Dependency Cycle Detected?",
                "code": "src/swarm_orchestrator.py -> TopologicalDAGScheduler.schedule()",
                "condition": "Executes Kahn's algorithm topological sort to verify task graph acyclicity.",
                "yes_path": "LEFT BRANCH (Deadlock Cycle): Raises `CycleDeadlockException` and aborts execution before worker dispatch.",
                "no_path": "RIGHT BRANCH (Clean DAG): Dispatches independent agent worker nodes concurrently."
            },
            {
                "title": "Decision 2: Is Voting Consensus Agreement Score >= 66%?",
                "code": "src/swarm_orchestrator.py -> ConsensusEngine.evaluate_consensus()",
                "condition": "Calculates majority voting agreement score across agent output payloads.",
                "yes_path": "DOWN BRANCH (Consensus Reached): Emits verified consensus result payload.",
                "no_path": "RIGHT BRANCH (Tie-Breaker Required): Invokes senior tie-breaker evaluator agent to resolve agent conflicts."
            }
        ]
    },
    {
        "num": "20",
        "dir": "20-data-governance-openlineage-catalog",
        "title": "Data Governance & OpenLineage",
        "subtitle": "OpenLineage Event Telemetry Emitters & Marquez Lineage Graph Catalog",
        "file": "src/data_governance.py",
        "mermaid": """graph TD
    A([Start: execute_pipeline]) --> B[Run Pre-Job Great Expectations Data Contract Check]
    B --> C{Decision 1: Data Contract Passed Zero Schema / Null Offenses?}
    C -- NO: Contract Violation --> D[Emit OpenLineage ABORT Event & Quarantine Dataset]
    D --> E([Halt Transformation Pipeline])
    C -- YES: Contract Passed --> F[Emit OpenLineage START Telemetry Event to Marquez REST API]
    F --> G[Execute Dataset Transformation Job]
    G --> H[Register Dataset Transformation Dependencies in Marquez Lineage Graph]
    H --> I[Emit OpenLineage COMPLETE Event with Row Count Metrics]
    I --> J([Complete Data Pipeline Step])

    classDef decision fill:#2d2206,stroke:#fbbf24,stroke-width:2px,color:#fbbf24;
    classDef startend fill:#092e20,stroke:#34d399,stroke-width:2px,color:#34d399;
    classDef process fill:#12161f,stroke:#38bdf8,stroke-width:1px,color:#f0f6fc;
    class C decision;
    class A,E,J startend;
    class B,D,F,G,H,I process;""",
        "decisions": [
            {
                "title": "Decision 1: Did Pre-Job Data Contract Check Pass?",
                "code": "src/data_governance.py -> GreatExpectationsValidator.validate()",
                "condition": "Validates incoming dataset schema, null counts, and column data types against contract specification.",
                "yes_path": "DOWN BRANCH (Passed Contract): Emits OpenLineage `START` event to Marquez REST API and begins transformation job.",
                "no_path": "LEFT BRANCH (Contract Failed): Emits OpenLineage `ABORT` event, quarantines dataset, and halts pipeline execution."
            }
        ]
    }
]

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project {num}: {title} | Interactive 2D Flowchart & Control Flow Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>
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
            background: rgba(251, 191, 36, 0.1);
            color: var(--accent-amber);
            border: 1px solid rgba(251, 191, 36, 0.3);
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
            font-size: 1.3rem;
            font-weight: 600;
            margin: 2.5rem 0 1.25rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--accent-cyan);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        /* Mermaid Diagram Container */
        .mermaid-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            display: flex;
            justify-content: center;
            margin-bottom: 2.5rem;
            overflow-x: auto;
        }}

        /* 2D Decisions Detailed Grid */
        .decisions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .decision-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-top: 4px solid var(--accent-amber);
            border-radius: 8px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .decision-header {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--accent-amber);
            margin-bottom: 0.5rem;
        }}

        .code-reference {{
            font-family: var(--font-code);
            font-size: 0.8rem;
            color: var(--accent-cyan);
            background: rgba(56, 189, 248, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 1rem;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .condition-rule {{
            font-size: 0.95rem;
            color: var(--text-primary);
            margin-bottom: 1.25rem;
            background: rgba(255, 255, 255, 0.03);
            padding: 0.75rem;
            border-radius: 6px;
            border-left: 3px solid var(--text-secondary);
        }}

        .paths-grid {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .path-box {{
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.88rem;
        }}

        .path-box.yes {{
            background: rgba(52, 211, 153, 0.1);
            border: 1px solid rgba(52, 211, 153, 0.25);
            color: var(--accent-emerald);
        }}

        .path-box.no {{
            background: rgba(244, 63, 94, 0.1);
            border: 1px solid rgba(244, 63, 94, 0.25);
            color: var(--accent-rose);
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
        <div><span class="badge">INTERACTIVE 2D CONTROL FLOW BLUEPRINT</span></div>
        <h1>Project {num}: {title}</h1>
        <p class="subtitle">{subtitle}</p>
    </header>

    <div class="section-title">
        <span>🔀 Visual 2D Branching Control Flow Diagram</span>
    </div>

    <div class="mermaid-card">
        <div class="mermaid">
{mermaid}
        </div>
    </div>

    <div class="section-title">
        <span>⚡ Exhaustive Logical Conditionals & Codebase Mapping</span>
    </div>

    <div class="decisions-grid">
{decisions_html}
    </div>

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
    decisions_html = ""
    for dec in proj["decisions"]:
        decisions_html += f'''
        <div class="decision-card">
            <div>
                <div class="decision-header">{dec["title"]}</div>
                <div class="code-reference">{dec["code"]}</div>
                <div class="condition-rule"><strong>Rule Evaluated:</strong> {dec["condition"]}</div>
            </div>
            <div class="paths-grid">
                <div class="path-box yes">
                    <strong>✔ {dec["yes_path"].split(':', 1)[0]}:</strong> {dec["yes_path"].split(':', 1)[1] if ':' in dec["yes_path"] else dec["yes_path"]}
                </div>
                <div class="path-box no">
                    <strong>✖ {dec["no_path"].split(':', 1)[0]}:</strong> {dec["no_path"].split(':', 1)[1] if ':' in dec["no_path"] else dec["no_path"]}
                </div>
            </div>
        </div>
        '''
    
    final_html = html_template.format(
        num=proj["num"],
        title=proj["title"],
        subtitle=proj["subtitle"],
        file=proj["file"],
        mermaid=proj["mermaid"],
        decisions_html=decisions_html
    )
    
    target_path = os.path.join(base_dir, proj["dir"], "FLOWCHART.html")
    with open(target_path, "w") as f:
        f.write(final_html)
    print(f"Generated rich 2D flowchart for {proj['dir']} -> {target_path}")

print("Successfully generated all 20 rich 2D interactive FLOWCHART.html files!")
