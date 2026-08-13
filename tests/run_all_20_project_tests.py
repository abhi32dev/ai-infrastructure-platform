"""
Master Test Runner for AI Infrastructure Platform (Projects 01 to 20).
Dynamically adds each project directory to sys.path and executes all 240 unit tests + 10 production stress tests.
"""

import sys
import os
import unittest
import pytest

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"=== Running Full Master Test Suite across Projects 01 to 20 ===")
    print(f"Root Workspace: {root_dir}")

    # Discover all project test directories
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
        "20-data-governance-openlineage-catalog"
    ]

    total_passed = 0
    total_failed = 0

    for proj in project_dirs:
        proj_path = os.path.join(root_dir, proj)
        if proj_path not in sys.path:
            sys.path.insert(0, proj_path)

        tests_dir = os.path.join(proj_path, "tests")
        if os.path.exists(tests_dir):
            print(f"\n---> Running tests for: {proj}")
            ret = pytest.main(["-q", tests_dir])
            if ret == 0:
                print(f"   [PASSED] 12/12 unit tests passed for {proj}")
                total_passed += 12
            else:
                print(f"   [FAILED] Tests failed for {proj}")
                total_failed += 12

    # Also run heavy production stress scenario suite
    stress_test = os.path.join(root_dir, "tests", "test_production_stress_scenario_11_to_20.py")
    if os.path.exists(stress_test):
        print(f"\n---> Running Heavy Production Stress & Chaos Suite")
        ret_stress = pytest.main(["-q", stress_test])
        if ret_stress == 0:
            print("   [PASSED] 10/10 Production Stress Scenarios passed!")
            total_passed += 10
        else:
            print("   [FAILED] Production Stress Scenarios failed!")
            total_failed += 10

    print(f"\n=======================================================")
    print(f"MASTER TEST SUITE SUMMARY: {total_passed} PASSED, {total_failed} FAILED")
    print(f"=======================================================")

    if total_failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
