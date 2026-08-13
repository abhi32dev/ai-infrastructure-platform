# 🧪 Master AI Infrastructure Test Suite Catalog & Verification Matrix

This document provides a comprehensive description of the **80 automated Pytest test cases** spanning all 10 AI/ML Infrastructure repositories in `/Users/abhi/Documents/Antigravity/`.

---

## 📊 Summary Execution Matrix (80 / 80 Tests PASSED)

| Project Folder | Core Architecture Tested | Total Tests | Status | Execution Time |
| :--- | :--- | :---: | :---: | :---: |
| **`01-agent-durable-runtime`** | State Machine, SQLite Checkpoints, Deterministic Replay, HITL Gate, MCP Protocol, PII & DAN Defenses | **8 / 8** | ✅ **PASSED** | 0.27s |
| **`02-rag-cost-router`** | Multi-Strategy Chunkers, ChromaDB Dense Vector DB, BM25, RRF Fusion, Cross-Encoder, FinOps Router | **8 / 8** | ✅ **PASSED** | 16.68s |
| **`03-llm-eval-gate`** | Groundedness, Relevance, Faithfulness Rubrics, RAG Triad, Welch's t-test Gate, MLflow Tracking | **8 / 8** | ✅ **PASSED** | 3.87s |
| **`04-model-serving-mlops`** | RecSys Matrix Factorization, MD5 A/B Routing, OpenTelemetry W3C Tracing, Prometheus Exporter | **8 / 8** | ✅ **PASSED** | 0.26s |
| **`05-event-stream-pyspark-etl`** | SNMP MIB OID Trap Decoder, DynamoDB TTL Deduplication, PySpark Feature ETL, 3-Pass Reconciliation | **8 / 8** | ✅ **PASSED** | 1.03s |
| **`06-finetuning-lora-alignment`** | SFT Dataset Curation, Outlier Filtering, LoRA PEFT ($r=8, \alpha=16$), Loss History, GGUF Export | **8 / 8** | ✅ **PASSED** | 0.10s |
| **`07-cloud-iac-security-governance`**| AWS CDK Multi-Account Stack, Tiered VPC Isolation, IAM Wildcard Audit, EC2 Agent Compliance | **8 / 8** | ✅ **PASSED** | 0.12s |
| **`08-vllm-pagedattention-spec-decoding`**| PagedAttention GPU Block Allocator, Page Tables, 0% Fragmentation, Speculative Decoding (~2.67x) | **8 / 8** | ✅ **PASSED** | 0.10s |
| **`09-ray-distributed-cluster-orchestrator`**| Stateful Ray Actor Pools, Plasma Zero-Copy Shared Memory, Queue-Depth Autoscaler, Fault Recovery | **8 / 8** | ✅ **PASSED** | 0.09s |
| **`10-triton-cuda-gpu-scheduler`** | Triton Dynamic Batching Queue, Power-of-2 CUDA Tensor Core Alignment, AWQ FP8/INT4 Quantization | **8 / 8** | ✅ **PASSED** | 0.09s |
| **TOTAL** | **Master Enterprise Test Suite** | **80 / 80** | ✅ **100% PASSED** | **22.61s** |

---

## 🛠️ Detailed Test Descriptions per Project

### Project 1: `01-agent-durable-runtime` (8 / 8 Passed)
1. **`test_01_submit_task_initial_state`**: Verifies UUID generation, goal recording, and `PENDING` initial state status.
2. **`test_02_run_task_successful_completion`**: Verifies end-to-end multi-step task execution through step checkpoints to `COMPLETED`.
3. **`test_03_step_checkpoint_persistence_and_reload`**: Verifies atomic SQLite database state save and reload across process boundaries.
4. **`test_04_simulated_failure_and_deterministic_replay`**: Injects simulated failure at Step 2 and verifies state rewind and replay from Step 1 checkpoint.
5. **`test_05_hitl_approval_gate_pause_and_resume`**: Verifies execution pauses at Step 3 (`sql_query_executor`) requiring human approval before resuming.
6. **`test_06_mcp_json_rpc_handshake_and_tool_discovery`**: Verifies Model Context Protocol (MCP) JSON-RPC 2.0 handshake and capability tool listing.
7. **`test_07_mcp_json_rpc_tool_execution`**: Verifies MCP `tools/call` remote tool execution over socket protocols.
8. **`test_08_enterprise_guardrails_pii_redaction_and_jailbreak_block`**: Verifies PII redaction (`[REDACTED_SSN]`, `[REDACTED_EMAIL]`) and DAN prompt injection jailbreak blocking.

### Project 2: `02-rag-cost-router` (8 / 8 Passed)
1. **`test_01_document_chunking_fixed_overlap`**: Verifies sliding character window and overlap boundaries.
2. **`test_02_document_chunking_parent_child`**: Verifies hierarchical parent-child chunk mapping and context retention.
3. **`test_03_document_chunking_sentence_window`**: Verifies regex sentence splitting and surrounding sentence context buffer.
4. **`test_04_dense_vector_search_chromadb`**: Verifies persistent ChromaDB vector indexing and `all-MiniLM-L6-v2` cosine similarity scoring.
5. **`test_05_sparse_bm25_keyword_search`**: Verifies Rank-BM25 TF-IDF token matching for exact keyword lookup.
6. **`test_06_reciprocal_rank_fusion`**: Verifies Reciprocal Rank Fusion ($k=60$) rank merging formula.
7. **`test_07_cross_encoder_reranking`**: Verifies `cross-encoder/ms-marco-MiniLM-L-6-v2` candidate rescoring.
8. **`test_08_cost_aware_router_decisions`**: Verifies FinOps model router classification (Ollama $0 vs Frontier API $$$).

### Project 3: `03-llm-eval-gate` (8 / 8 Passed)
1. **`test_01_groundedness_rubric_scoring`**: Verifies Groundedness rubric evaluation score bounds [0.0, 1.0].
2. **`test_02_relevance_rubric_scoring`**: Verifies Context Relevance rubric query-context term matching.
3. **`test_03_faithfulness_rubric_scoring`**: Verifies Answer Faithfulness rubric detecting ungrounded hallucinations.
4. **`test_04_ragas_triad_automated_eval`**: Verifies RAG Triad (Precision, Recall, Faithfulness) joint scoring.
5. **`test_05_welch_ttest_hypothesis_pass`**: Verifies Welch's t-test hypothesis gate approving candidate model ($p < 0.05$).
6. **`test_06_welch_ttest_hypothesis_fail`**: Verifies statistical gate blocking candidate model when regression occurs ($p \ge 0.05$).
7. **`test_07_mlflow_tracker_experiment_logging`**: Verifies MLflow experiment metric logging and run tracking.
8. **`test_08_multi_model_judge_cross_verification`**: Verifies multi-judge score aggregation and inter-judge variance.

### Project 4: `04-model-serving-mlops` (8 / 8 Passed)
1. **`test_01_recsys_matrix_factorization_inference`**: Verifies User-Item latent embedding dot product inference score.
2. **`test_02_ab_testing_variant_hash_assignment`**: Verifies deterministic MD5 hash user ID assignment to Control vs Variant.
3. **`test_03_recommendation_item_schema`**: Verifies recommendation item schema metadata attributes.
4. **`test_04_queue_backpressure_isolation`**: Verifies queue capacity thresholds and backpressure load shedding metrics.
5. **`test_05_opentelemetry_w3c_traceparent_header`**: Verifies OpenTelemetry W3C traceparent header creation and span generation.
6. **`test_06_prometheus_metrics_counter_increment`**: Verifies Prometheus metrics text format export.
7. **`test_07_model_serving_latency_sla_bounds`**: Verifies inference execution finishes within P99 SLA (< 50ms).
8. **`test_08_concurrent_serving_load_handling`**: Verifies parallel inference requests under concurrent load.

### Project 5: `05-event-stream-pyspark-etl` (8 / 8 Passed)
1. **`test_01_snmp_packet_decoder_oid_parsing`**: Verifies SNMP trap MIB OID parsing for enterprise edge node metrics.
2. **`test_02_dynamodb_ttl_deduplication`**: Verifies DynamoDB 300-second window event deduplication logic.
3. **`test_03_pyspark_feature_transformation_aggregations`**: Verifies PySpark feature transformation aggregations.
4. **`test_04_storage_reconciliation_pass_1_success`**: Verifies Pass 1 real-time streaming ingestion success.
5. **`test_05_storage_reconciliation_pass_2_diff_retry`**: Verifies Pass 2 storage listing diff & retry reconciliation.
6. **`test_06_storage_reconciliation_pass_3_raw_recovery`**: Verifies Pass 3 raw-file recovery pass during storage outages.
7. **`test_07_snmpv3_auth_failure`**: Verifies SNMPv3 authentication failure when security key is missing.
8. **`test_08_high_volume_event_burst_deduplication`**: Verifies deduplicator under high-volume event stream burst.

### Project 6: `06-finetuning-lora-alignment` (8 / 8 Passed)
1. **`test_01_dataset_curation_outlier_rejection`**: Verifies outlier token sequence length rejection.
2. **`test_02_train_val_split_proportions`**: Verifies dataset train/validation split proportions.
3. **`test_03_lora_rank_matrix_adapter_configuration`**: Verifies LoRA PEFT rank matrix adapter configuration parameters ($r=8, \alpha=16$).
4. **`test_04_parameter_reduction_calculation`**: Verifies 99.94% trainable parameter memory reduction calculation.
5. **`test_05_loss_convergence_logging_history`**: Verifies training loss decay and perplexity convergence history logging.
6. **`test_06_model_exporter_gguf_quantization_format`**: Verifies GGUF Q4_K_M quantization format export compilation.
7. **`test_07_empty_dataset_handling`**: Verifies dataset curator handling empty inputs safely.
8. **`test_08_tokenizer_max_length_truncation`**: Verifies token truncation bounds on maximum sequence length.

### Project 7: `07-cloud-iac-security-governance` (8 / 8 Passed)
1. **`test_01_cdk_vpc_subnet_isolation`**: Verifies AWS CDK Tiered VPC Subnet Isolation (Public, Private, Protected).
2. **`test_02_cdk_multi_account_golden_path`**: Verifies AWS CDK Golden Path Stack synthesis across Dev, QA, Stage, and Prod.
3. **`test_03_iam_policy_wildcard_permission_violation`**: Verifies IAM policy audit engine detecting dangerous wildcard permissions (`Action: "*"`).
4. **`test_04_iam_policy_least_privilege_audit`**: Verifies least-privilege policy validation passing for tightly scoped ARNs.
5. **`test_05_security_agent_status_tracking`**: Verifies EC2 security monitoring agent status tracking (CrowdStrike, Qualys).
6. **`test_06_unregistered_security_agent_alert`**: Verifies alert generation when an endpoint misses required agent software.
7. **`test_07_invalid_json_iam_policy_handling`**: Verifies IAM policy auditor handling empty policies safely.
8. **`test_08_security_agent_outdated_patch_pending`**: Verifies patch pending status when agent version is outdated.

### Project 8: `08-vllm-pagedattention-spec-decoding` (8 / 8 Passed)
1. **`test_01_paged_attention_physical_block_allocator`**: Verifies PagedAttention physical GPU block allocation (16 tokens/block).
2. **`test_02_logical_to_physical_page_mapping`**: Verifies logical sequence token mapping to physical block table indices.
3. **`test_03_zero_vram_fragmentation_guarantee`**: Verifies 0.0% VRAM memory fragmentation calculation.
4. **`test_04_speculative_decoding_speedup`**: Verifies Speculative Decoding (1B Draft + 70B Target parallel pass) ~2.67x speedup.
5. **`test_05_continuous_batching_scheduler`**: Verifies continuous batching scheduler iteration step and phase transitions.
6. **`test_06_paged_attention_free_blocks`**: Verifies freeing physical blocks upon sequence completion.
7. **`test_07_block_allocator_out_of_memory_handling`**: Verifies block allocator handling GPU VRAM saturation gracefully.
8. **`test_08_batch_concurrency_scaling`**: Verifies parallel block allocation across 10 concurrent sequences.

### Project 9: `09-ray-distributed-cluster-orchestrator` (8 / 8 Passed)
1. **`test_01_ray_actor_pool_initialization`**: Verifies multi-GPU worker actor pool initialization (4 nodes, 32 GPUs).
2. **`test_02_stateful_actor_task_dispatch`**: Verifies stateful Ray Actor worker task dispatching.
3. **`test_03_plasma_zero_copy_shared_memory`**: Verifies Plasma zero-copy shared memory object store tensor payload referencing.
4. **`test_04_cluster_autoscaler_scale_up`**: Verifies dynamic cluster autoscaling scale-up when queue depth exceeds threshold.
5. **`test_05_cluster_autoscaler_scale_down`**: Verifies cluster autoscaler scaling down idle worker nodes when queue is empty.
6. **`test_06_actor_failure_and_state_recovery`**: Verifies worker actor failure detection and state recovery on backup nodes.
7. **`test_07_cluster_orchestrator_execution`**: Verifies cluster orchestrator task submission and Plasma ref creation.
8. **`test_08_distributed_task_fan_out_throughput`**: Verifies distributed task fan-out execution across multiple actors.

### Project 10: `10-triton-cuda-gpu-scheduler` (8 / 8 Passed)
1. **`test_01_triton_dynamic_batching_queue`**: Verifies Triton dynamic batching queue enqueue and batch formation.
2. **`test_02_power_of_2_cuda_tensor_core_alignment`**: Verifies CUDA hardware Tensor Core power-of-2 alignment validation ($B=8, 16, 32$).
3. **`test_03_awq_quantization_vram_reduction`**: Verifies AWQ FP8/INT8 weight matrix quantization VRAM memory reduction (3.68x).
4. **`test_04_awq_accuracy_preservation_score`**: Verifies AWQ accuracy preservation (99.42% cosine similarity retention).
5. **`test_05_triton_orchestrator_dynamic_batching`**: Verifies Triton orchestrator dynamic batch submission and flush.
6. **`test_06_triton_orchestrator_awq_audit`**: Verifies Triton orchestrator AWQ quantization audit pass.
7. **`test_07_empty_batch_queue_handling`**: Verifies dynamic batching queue handling empty requests safely.
8. **`test_08_awq_fp8_vs_int4_tradeoffs`**: Verifies compression and accuracy tradeoffs between FP8 and AWQ INT4.

---

## 💻 Command to Run All 80 Tests Locally

```bash
cd /Users/abhi/Documents/Antigravity
for dir in 0*; do echo "=== TESTING $dir ==="; (cd "$dir" && PYTHONPATH=. .venv/bin/pytest tests/); done
```
