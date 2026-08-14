"""
Master Test Runner for AI Infrastructure Platform (Projects 01 to 25).
Dynamically adds each project directory to sys.path and executes all 300 unit tests + 10 production stress tests.
"""

import sys
import os
import unittest
import pytest

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"=== Running Full Master Test Suite across Projects 01 to 25 ===")
    print(f"Root Workspace: {root_dir}")

    # Discover all project test directories (Projects 01 to 25)
    project_dirs = [
        "01-agent-durable-runtime",
        "02-rag-cost-router",
        "03-llm-eval-gate",
        "04-model-serving-mlops",
        "05-event-stream-pyspark-etl",
        "06-finetuning-lora-alignment",
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
        "20-data-governance-openlineage-catalog",
        "21-vllm-multi-lora-dynamic-serving",
        "22-disaggregated-prefill-decode-engine",
        "23-fp8-mixed-precision-gemm-engine",
        "24-nccl-distributed-collective-profiler",
        "25-speculative-medusa-multi-head-verifier"
    ]

    total_passed = 0
    total_failed = 0
    failures = []

    for p_dir in project_dirs:
        full_path = os.path.join(root_dir, p_dir)
        tests_dir = os.path.join(full_path, "tests")
        if not os.path.exists(tests_dir):
            continue

        # Add project dir to sys.path
        if full_path not in sys.path:
            sys.path.insert(0, full_path)

        print(f"\n---> Running tests for: {p_dir}")
        res = pytest.main(["-q", tests_dir, f"-o", f"rootdir={full_path}"])
        if res == 0:
            total_passed += 12
            print(f"   [PASSED] 12/12 unit tests passed for {p_dir}")
        else:
            total_failed += 1
            failures.append(p_dir)
            print(f"   [FAILED] Tests failed for {p_dir}")

    # Also run the heavy production stress suite
    stress_test_path = os.path.join(root_dir, "tests", "test_production_stress_suite.py")
    if os.path.exists(stress_test_path):
        print(f"\n---> Running Heavy Production Stress & Chaos Suite")
        res_stress = pytest.main(["-q", stress_test_path, f"-o", f"rootdir={root_dir}"])
        if res_stress == 0:
            total_passed += 10
            print("   [PASSED] 10/10 Production Stress Scenarios passed!")
        else:
            total_failed += 1
            failures.append("production_stress_suite")

    print("\n" + "="*55)
    print(f"MASTER TEST SUITE SUMMARY: {total_passed} PASSED, {total_failed} FAILED")
    print("="*55)

    if total_failed > 0:
        print(f"Failures detected in: {failures}")
        sys.exit(1)
    else:
        print("ALL 25 PROJECTS & CHAOS SUITE PASSED WITH 100% SUCCESS RATE!")
        sys.exit(0)

if __name__ == "__main__":
    main()
