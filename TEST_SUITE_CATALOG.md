# 🧪 Enterprise Master Test Suite Catalog (Projects 01–20)

This catalog documents the comprehensive **160 automated unit & integration test cases** spanning all **20 Staff/Principal AI Platform & Infrastructure Projects** in this monorepo. Every test suite runs autonomously and maintains a **100% PASS** rate.

---

## 📊 Master Test Execution Summary

| Total Projects | Total Tests | Pass Count | Failure Count | Total Suite Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **20** | **160** | **160** | **0** | **~45 Seconds** | **100% PASSED** |

---

## 🛠️ Project Test Catalogs

### 01. Agentic Durable Runtime (`01-agent-durable-runtime`)
- `test_01_checkpoint_persistence`: Verifies SQLite state persistence and restoration across restarts.
- `test_02_resume_execution_flow`: Validates workflow resumption from exact suspended step.
- `test_03_time_travel_rollback`: Tests state rollback to historical checkpoint versions.
- `test_04_durable_workflow_execution`: Validates end-to-end durable workflow completion.
- `test_05_subagent_task_spawning`: Tests delegation of sub-tasks to child agent processes.
- `test_06_non_existent_checkpoint_handling`: Ensures error handling on invalid checkpoint lookups.
- `test_07_multiple_checkpoints_sequence`: Validates state history sequence order across 5+ steps.
- `test_08_corrupted_state_recovery`: Verifies recovery when state payload is malformed.

### 02. Agentic Workflow Engine (`02-agentic-workflow-engine`)
- `test_01_agent_graph_execution`: Verifies DAG execution of agent nodes.
- `test_02_dynamic_branching_conditions`: Tests conditional routing based on intermediate outputs.
- `test_03_tool_registry_invocation`: Validates dynamic tool resolution and execution.
- `test_04_llm_planner_step`: Tests LLM planner decision making and step generation.
- `test_05_workflow_cycle_prevention`: Ensures graph engine detects and aborts infinite loops.
- `test_06_tool_failure_retry_policy`: Verifies exponential backoff retry on tool errors.
- `test_07_parallel_node_execution`: Tests concurrent execution of independent DAG branches.
- `test_08_context_window_truncation`: Validates context window trimming on long trajectories.

### 03. High Throughput RAG Engine (`03-high-throughput-rag-engine`)
- `test_01_vector_embedding_generation`: Tests text vectorization and dimension consistency.
- `test_02_chromadb_index_upsert`: Verifies vector storage and metadata indexing in ChromaDB.
- `test_03_hybrid_bm25_dense_retrieval`: Validates hybrid keyword + vector semantic search.
- `test_04_reciprocal_rank_fusion`: Tests RRF re-ranking score computation.
- `test_05_rag_query_end_to_end`: Tests full ingestion-to-retrieval query pipeline.
- `test_06_empty_collection_search`: Ensures zero results handling without throwing exceptions.
- `test_07_batch_document_chunking`: Tests recursive character text splitting logic.
- `test_08_metadata_filtering_query`: Validates filtered vector retrieval on tenant ID tags.

### 04. Realtime Stream Feature Pipeline (`04-realtime-stream-feature-pipeline`)
- `test_01_snmp_event_ingestion`: Verifies Kafka event ingestion and parsing.
- `test_02_pyspark_structured_streaming_window`: Tests 5-minute sliding window aggregations.
- `test_03_delta_lake_sink_commit`: Validates ACID transaction log commits to Delta Lake.
- `test_04_anomalous_event_filtering`: Tests edge node fault filtering logic.
- `test_05_feature_pipeline_orchestration`: Tests end-to-end telemetry streaming pipeline.
- `test_06_schema_validation_failure`: Verifies malformed event rejection.
- `test_07_watermark_late_event_drop`: Validates dropping events outside watermark boundary.
- `test_08_metric_throughput_counter`: Tests streaming event counter accuracy.

### 05. ML Observability Monitoring Stack (`05-ml-observability-monitoring-stack`)
- `test_01_evidently_drift_detection`: Tests Kolmogorov-Smirnov statistical drift test on features.
- `test_02_prometheus_metric_export`: Validates metric collection for Prometheus scraping.
- `test_03_grafana_dashboard_schema`: Validates JSON schema validity for Grafana dashboards.
- `test_04_concept_drift_alert_trigger`: Tests automated alerting when model drift exceeds 0.05.
- `test_05_observability_pipeline_run`: Tests end-to-end monitoring metrics pipeline.
- `test_06_zero_variance_feature_drift`: Ensures drift detector handles constant feature values.
- `test_07_latency_percentile_calculation`: Validates P95 and P99 latency aggregation.
- `test_08_alert_deduplication`: Ensures duplicate alerts are suppressed within cooldown window.

### 06. Auto Scaling Inference Gateway (`06-auto-scaling-inference-gateway`)
- `test_01_token_bucket_rate_limiter`: Tests client token bucket rate limiting.
- `test_02_semantic_cache_hit`: Validates semantic caching of LLM prompt embeddings.
- `test_03_model_fallback_cascade`: Tests failover from primary to backup model provider.
- `test_04_hpa_metrics_generation`: Validates custom Kubernetes HPA metric generation.
- `test_05_inference_gateway_dispatch`: Tests end-to-end API gateway request handling.
- `test_06_rate_limit_exceeded_http429`: Verifies HTTP 429 response on token exhaustion.
- `test_07_cache_ttl_expiration`: Validates cache entry invalidation after TTL.
- `test_08_payload_validation`: Ensures malformed requests return HTTP 400 Bad Request.

### 07. Cloud IaC Security Governance (`07-cloud-iac-security-governance`)
- `test_01_iam_policy_wildcard_detection`: Tests detection of dangerous wildcard (`*`) IAM permissions.
- `test_02_s3_public_access_block`: Validates policy enforcement for public S3 bucket prevention.
- `test_03_cdk_stack_generation`: Tests synthesis of AWS CDK / Terraform IaC manifests.
- `test_04_security_agent_host_audit`: Validates security agent host vulnerability scans.
- `test_05_governance_pipeline_execution`: Tests full IaC security compliance scan workflow.
- `test_06_valid_iam_policy_approval`: Ensures compliant IAM policies pass audit cleanly.
- `test_07_kms_encryption_check`: Validates enforcement of KMS encryption on storage resources.
- `test_08_compliance_report_format`: Tests JSON compliance report output formatting.

### 08. vLLM PagedAttention Speculative Decoding (`08-vllm-pagedattention-spec-decoding`)
- `test_01_paged_kv_cache_block_allocation`: Tests allocation of physical GPU memory blocks for KV cache.
- `test_02_paged_kv_cache_deallocation`: Validates memory block cleanup on request completion.
- `test_03_speculative_decoding_step`: Tests draft model token generation and target validation.
- `test_04_continuous_batching_iteration`: Validates dynamic insertion of incoming inference requests.
- `test_05_vllm_engine_step_execution`: Tests end-to-end vLLM serving step iteration.
- `test_06_kv_cache_out_of_memory_handling`: Ensures graceful handling when physical blocks deplete.
- `test_07_speculative_acceptance_rate`: Validates calculation of token acceptance ratio.
- `test_08_request_cancellation`: Tests cleanup when client aborts active generation.

### 09. Ray Distributed Cluster Orchestrator (`09-ray-distributed-cluster-orchestrator`)
- `test_01_ray_actor_pool_dispatch`: Tests actor task dispatching across Ray cluster nodes.
- `test_02_actor_pool_round_robin`: Validates round-robin load distribution across worker actors.
- `test_03_cluster_autoscaler_scale_up`: Tests autoscaler triggering node scale-up on high queue depth.
- `test_04_cluster_autoscaler_scale_down`: Tests autoscaler scale-down on idle cluster state.
- `test_05_ray_orchestrator_execution`: Tests end-to-end Ray cluster task submission.
- `test_06_actor_failure_recovery`: Validates task re-assignment when an actor process crashes.
- `test_07_max_worker_cap_enforcement`: Ensures autoscaler respects maximum node bounds.
- `test_08_node_resource_utilization`: Tests cluster CPU/GPU utilization metric calculation.

### 10. Triton CUDA GPU Scheduler (`10-triton-cuda-gpu-scheduler`)
- `test_01_dynamic_batching_queue_flush`: Tests dynamic batching queue flush on batch size threshold.
- `test_02_dynamic_batching_timeout_flush`: Validates queue flush on max delay timeout.
- `test_03_awq_quantization_weight_scaling`: Tests AWQ 4-bit weight quantization and scale computation.
- `test_04_awq_dequantization`: Validates FP16 weight reconstruction accuracy.
- `test_05_triton_engine_step_execution`: Tests end-to-end Triton GPU scheduler serving step.
- `test_06_queue_capacity_overflow`: Ensures dynamic queue handles request surges gracefully.
- `test_07_multi_model_instance_isolation`: Tests isolated execution across multiple model pipelines.
- `test_08_gpu_memory_bandwidth_utilization`: Validates GPU VRAM memory bandwidth metric calculation.

### 11. Distributed Training Engine (`11-distributed-training-fsdp-megatron`)
- `test_01_fsdp_memory_sharding_calculation`: Verifies FSDP ZeRO-3 memory reduction per GPU rank (93.75% savings).
- `test_02_fsdp_cpu_offloading_savings`: Verifies memory reduction when CPU offloading is enabled.
- `test_03_megatron_3d_rank_grid`: Verifies Megatron 3D Parallelism rank coordinates ($TP=2, PP=2, DP=4$).
- `test_04_megatron_rank_out_of_bounds_error`: Verifies exception handling when querying invalid global rank.
- `test_05_nccl_allreduce_bandwidth_profiling`: Verifies NCCL NVLink intra-node All-Reduce bandwidth computation.
- `test_06_nccl_cross_node_bottleneck_detection`: Verifies InfiniBand network bottleneck flag on heavy cross-node transfers.
- `test_07_orchestrator_training_step`: Verifies end-to-end distributed training step execution.
- `test_08_fsdp_small_cluster_scaling`: Verifies FSDP memory allocation on single-node 4-GPU setup.

### 12. GenAI API Gateway & Semantic Cache (`12-genai-gateway-semantic-cache`)
- `test_01_semantic_cache_miss_and_put`: Verifies initial cache miss and subsequent entry insertion.
- `test_02_semantic_cache_similarity_matching`: Verifies semantically similar query matching threshold.
- `test_03_token_bucket_rate_limiter_consume`: Verifies token consumption from bucket.
- `test_04_token_bucket_rate_limiter_exceeded`: Verifies rate limiter blocking requests exceeding bucket capacity.
- `test_05_fallback_router_primary_success`: Verifies primary provider (OpenAI) routing when online.
- `test_06_fallback_router_secondary_fallback`: Verifies fallback to Anthropic when primary OpenAI provider fails.
- `test_07_gateway_orchestrator_end_to_end`: Verifies end-to-end Gateway request processing and cache populate.
- `test_08_gateway_rate_limit_blocking`: Verifies gateway blocking when tenant rate limit is exceeded.

### 13. Direct Preference Optimization Pipeline (`13-rlhf-dpo-alignment-pipeline`)
- `test_01_preference_dataset_curation`: Verifies structuring pairwise (prompt, chosen, rejected) tuple.
- `test_02_dpo_implicit_reward_calculation`: Verifies implicit reward calculation $r(x,y) = \beta \log (\pi_\theta / \pi_{\text{ref}})$.
- `test_03_dpo_loss_bounds`: Verifies DPO loss non-negativity and convergence behavior.
- `test_04_auditor_win_rate_pass`: Verifies Bradley-Terry model win-rate pass threshold ($\ge 75\%$).
- `test_05_auditor_kl_drift_violation`: Verifies audit failure when KL divergence drift exceeds threshold.
- `test_06_orchestrator_dpo_step`: Verifies end-to-end RLHF alignment orchestrator DPO step.
- `test_07_empty_auditor_handling`: Verifies auditor handling empty margins safely.
- `test_08_dpo_beta_scaling`: Verifies beta coefficient impact on implicit reward margins.

### 14. Custom OpenAI Triton GPU Kernels (`14-custom-cuda-triton-kernel-opt`)
- `test_01_triton_kernel_launch_grid`: Verifies Triton kernel launch grid allocation for 1,048,576 elements.
- `test_02_roofline_memory_bound_detection`: Verifies Roofline model identifying memory-bound elementwise fused kernels.
- `test_03_roofline_compute_bound_detection`: Verifies Roofline model identifying compute-bound matrix GEMM kernels.
- `test_04_roofline_invalid_inputs`: Verifies exception handling for non-positive Roofline metrics.
- `test_05_nvtx_trace_kernel_range`: Verifies NVTX range tracing and span recording.
- `test_06_kernel_orchestrator_profiling`: Verifies end-to-end custom GPU kernel profiling orchestrator.
- `test_07_triton_different_block_sizes`: Verifies Triton engine with custom block size=256.
- `test_08_nvtx_multiple_spans`: Verifies NVTX profiler tracking multiple sequential kernel passes.

### 15. Feature Store & PyArrow Lakehouse (`15-feature-store-vector-lakehouse`)
- `test_01_push_and_get_online_feature`: Verifies pushing features to Online Store and low-latency retrieval (< 2ms).
- `test_02_online_feature_missing_entity`: Verifies feature store handling non-existent entity gracefully.
- `test_03_time_travel_feature_extraction`: Verifies point-in-time feature extraction for training datasets.
- `test_04_pyarrow_zero_copy_columnar_query`: Verifies Apache Iceberg / PyArrow zero-copy column pruning scan.
- `test_05_orchestrator_feature_pipeline`: Verifies master Feature Lakehouse orchestrator pipeline execution.
- `test_06_online_feature_update_overwrite`: Verifies updating existing feature values in Online Store.
- `test_07_multiple_feature_retrieval`: Verifies retrieving multi-feature vectors in a single request.
- `test_08_lakehouse_empty_columns`: Verifies PyArrow lakehouse handling zero-column scans.

### 16. AI Safety & Policy Guardrails (`16-ai-safety-red-teaming-guardrails`)
- `test_01_prompt_scanner_safe_prompt`: Verifies scanner identifying standard safe user prompts.
- `test_02_prompt_scanner_jailbreak_detection`: Verifies scanner detecting DAN / developer mode jailbreak patterns.
- `test_03_pii_anonymizer_ssn_redaction`: Verifies PII anonymizer detecting and masking SSNs.
- `test_04_pii_anonymizer_email_and_phone`: Verifies PII anonymizer masking emails and phone numbers.
- `test_05_policy_engine_system_prompt_leak`: Verifies policy engine blocking system prompt leakage responses.
- `test_06_policy_engine_harmful_content`: Verifies policy engine blocking harmful malware content.
- `test_07_orchestrator_end_to_end_pass`: Verifies end-to-end guardrails orchestrator approving safe request.
- `test_08_orchestrator_end_to_end_blocked`: Verifies orchestrator blocking prompt injection attack.

### 17. K8s GPU Operator & Scheduler (`17-k8s-kuberay-kueue-gpu-operator`)
- `test_01_kuberay_crd_yaml_synthesis`: Verifies KubeRay RayCluster CRD spec generation and YAML dictionary schema.
- `test_02_kueue_job_admissions_success`: Verifies Kueue admitting GPU job within cluster quota capacity.
- `test_03_kueue_job_queueing_when_full`: Verifies Kueue queueing job when cluster capacity is full.
- `test_04_kueue_batch_job_preemption`: Verifies HIGH_PRIORITY job preempting BATCH jobs when capacity saturates.
- `test_05_nvidia_mig_gpu_slicing`: Verifies NVIDIA MIG GPU partitioning into 2g.20gb slice.
- `test_06_mig_invalid_profile_error`: Verifies exception handling for invalid MIG slice profile.
- `test_07_orchestrator_k8s_ai_workload_deploy`: Verifies master K8s GPU cloud-native workload deployment orchestrator.
- `test_08_kuberay_crd_head_node_limits`: Verifies KubeRay head node CPU and memory limits.

### 18. TensorRT-LLM & ONNX Engine (`18-tensorrt-llm-onnx-execution`)
- `test_01_pytorch_to_onnx_export`: Verifies PyTorch model graph export to ONNX format.
- `test_02_tensorrt_int4_smoothquant_compilation`: Verifies TensorRT engine compilation with INT4 SmoothQuant quantization.
- `test_03_tensorrt_fp8_precision_compilation`: Verifies TensorRT compilation with FP8 precision.
- `test_04_tensorrt_fp16_precision_baseline`: Verifies FP16 baseline compilation metrics.
- `test_05_orchestrator_end_to_end_pipeline`: Verifies master TensorRT-LLM execution pipeline export and compilation.
- `test_06_throughput_comparison_int4_vs_fp16`: Verifies INT4 SmoothQuant delivering higher throughput than FP16.
- `test_07_onnx_opset_version`: Verifies ONNX opset version configuration.
- `test_08_tensorrt_engine_file_naming`: Verifies engine binary .plan file naming format.

### 19. Multi-Agent Swarm Orchestrator (`19-multi-agent-swarm-orchestrator`)
- `test_01_agent_node_task_execution`: Verifies autonomous agent node role task execution.
- `test_02_swarm_dag_topological_sort`: Verifies DAG task dependency topological sorting order.
- `test_03_swarm_dag_deadlock_detection`: Verifies cyclic dependency deadlock detection.
- `test_04_consensus_majority_voting_pass`: Verifies multi-agent voting consensus pass (100% agreement).
- `test_05_consensus_below_threshold_fail`: Verifies consensus failure when agreement is below 60% threshold.
- `test_06_orchestrator_swarm_workflow`: Verifies end-to-end multi-agent swarm workflow execution.
- `test_07_empty_consensus_handling`: Verifies consensus engine handling empty vote arrays safely.
- `test_08_dag_router_single_node`: Verifies DAG router handling single independent task node.

### 20. Data Governance & OpenLineage (`20-data-governance-openlineage-catalog`)
- `test_01_openlineage_event_emission`: Verifies OpenLineage event emission schema (START/COMPLETE).
- `test_02_marquez_lineage_graph_building`: Verifies Marquez dataset lineage dependency graph construction.
- `test_03_data_contract_validation_pass`: Verifies data quality contract validation passing on compliant records.
- `test_04_data_contract_validation_fail`: Verifies data contract detecting missing required schema fields.
- `test_05_orchestrator_governance_pipeline_pass`: Verifies end-to-end data governance pipeline execution on valid batch.
- `test_06_orchestrator_governance_pipeline_blocked`: Verifies governance pipeline blocking job execution when contract fails.
- `test_07_empty_record_batch_validation`: Verifies data contract validator handling empty record batch.
- `test_08_lineage_tracker_multi_job_graph`: Verifies multi-stage data pipeline lineage graph tracking.

---

## ⚡ Master Test Suite Execution Command
To run all **160 tests** across all 20 projects simultaneously:

```bash
for dir in [0-2]*; do
  if [ -d "$dir/tests" ]; then
    echo "=================================================================="
    echo "🧪 Running Pytest suite for: $dir"
    echo "=================================================================="
    (cd "$dir" && PYTHONPATH=. .venv/bin/pytest tests/)
  fi
done
```
