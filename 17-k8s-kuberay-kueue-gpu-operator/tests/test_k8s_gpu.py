"""
Expanded Test Suite for Project 17 - K8s Cloud-Native GPU Operator (KubeRay, Kueue & NVIDIA MIG).
Tests KubeRay RayCluster CRD YAML spec generation, Kueue priority queueing, BATCH job preemption,
NVIDIA MIG GPU slicing, and cloud-native workload deployment.
"""

import pytest
from src.kuberay_crd import KubeRayCRDManager
from src.kueue_job_scheduler import KueueJobScheduler
from src.mig_gpu_slicer import MIGGPUSlicer
from src.k8s_gpu_orchestrator import K8sGPUCloudNativeOrchestrator


@pytest.fixture
def kuberay():
    return KubeRayCRDManager(namespace="ai-platform")


@pytest.fixture
def kueue():
    return KueueJobScheduler(cluster_gpu_capacity=32)


@pytest.fixture
def mig():
    return MIGGPUSlicer(physical_gpu_model="A100-SXM4-80GB")


@pytest.fixture
def orchestrator():
    return K8sGPUCloudNativeOrchestrator()


def test_01_kuberay_crd_yaml_synthesis(kuberay):
    """Test 1: Verifies KubeRay RayCluster CRD spec generation and YAML dictionary schema."""
    crd = kuberay.generate_raycluster_crd_spec("ray-llm-cluster", replicas=4, gpus_per_worker=8)
    yaml_dict = kuberay.to_yaml_dict(crd)
    assert yaml_dict["kind"] == "RayCluster"
    assert yaml_dict["spec"]["workerGroupSpecs"][0]["replicas"] == 4
    assert yaml_dict["spec"]["workerGroupSpecs"][0]["template"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] == 8


def test_02_kueue_job_admissions_success(kueue):
    """Test 2: Verifies Kueue admitting GPU job within cluster quota capacity."""
    status = kueue.submit_kueue_job("job-1", priority_class="HIGH_PRIORITY", gpus_requested=16)
    assert status.status == "ADMITTED"
    assert status.gpus_allocated == 16


def test_03_kueue_job_queueing_when_full(kueue):
    """Test 3: Verifies Kueue queueing job when cluster capacity is full."""
    kueue.submit_kueue_job("job-1", "HIGH_PRIORITY", 32)  # Fills 32 GPUs
    status2 = kueue.submit_kueue_job("job-2", "MEDIUM", 8)
    assert status2.status == "QUEUED"
    assert status2.gpus_allocated == 0


def test_04_kueue_batch_job_preemption(kueue):
    """Test 4: Verifies HIGH_PRIORITY job preempting BATCH jobs when capacity saturates."""
    kueue.submit_kueue_job("batch-job-1", priority_class="BATCH", gpus_requested=16)
    kueue.submit_kueue_job("batch-job-2", priority_class="BATCH", gpus_requested=16)
    assert kueue.allocated_gpus == 32

    # High priority job requires 16 GPUs -> should preempt batch-job-1!
    hp_status = kueue.submit_kueue_job("prod-job-1", priority_class="HIGH_PRIORITY", gpus_requested=16)
    assert hp_status.status == "ADMITTED"
    assert kueue.active_jobs["batch-job-1"].status == "PREEMPTED"


def test_05_nvidia_mig_gpu_slicing(mig):
    """Test 5: Verifies NVIDIA MIG GPU partitioning into 2g.20gb slice."""
    slice_inst = mig.partition_gpu("2g.20gb")
    assert slice_inst.mig_profile == "2g.20gb"
    assert slice_inst.vram_gb == 20
    assert slice_inst.compute_slices == 2


def test_06_mig_invalid_profile_error(mig):
    """Test 6: Verifies exception handling for invalid MIG slice profile."""
    with pytest.raises(ValueError):
        mig.partition_gpu("invalid_profile")


def test_07_orchestrator_k8s_ai_workload_deploy(orchestrator):
    """Test 7: Verifies master K8s GPU cloud-native workload deployment orchestrator."""
    res = orchestrator.deploy_k8s_ai_workload("finetune-k8s-cluster")
    assert res["status"] == "WORKLOAD_DEPLOYED"
    assert res["crd_kind"] == "RayCluster"
    assert res["kueue_status"] == "ADMITTED"
    assert res["mig_profile"] == "2g.20gb"


def test_08_kuberay_crd_head_node_limits(kuberay):
    """Test 8: Verifies KubeRay head node CPU and memory limits."""
    crd = kuberay.generate_raycluster_crd_spec("head-spec-test")
    yaml_dict = kuberay.to_yaml_dict(crd)
    limits = yaml_dict["spec"]["headGroupSpec"]["template"]["spec"]["containers"][0]["resources"]["limits"]
    assert limits["cpu"] == 4
    assert limits["memory"] == "16Gi"
