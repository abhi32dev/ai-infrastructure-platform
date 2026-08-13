"""
Expanded Test Suite for Project 19 - Multi-Agent Swarm Orchestrator.
Includes production edge cases for empty vote arrays, complex multi-branch DAG topographies, and tied voting consensus.
"""

import pytest
from src.agent_node import AutonomousAgentNode
from src.swarm_dag_router import SwarmDAGRouter
from src.consensus_engine import MultiAgentConsensusEngine
from src.swarm_orchestrator import MultiAgentSwarmOrchestrator


@pytest.fixture
def agent():
    return AutonomousAgentNode("agent-01", "Coder")


@pytest.fixture
def router():
    return SwarmDAGRouter()


@pytest.fixture
def consensus():
    return MultiAgentConsensusEngine(threshold_pct=60.0)


@pytest.fixture
def orchestrator():
    return MultiAgentSwarmOrchestrator()


def test_01_agent_node_task_execution(agent):
    """Test 1: Verifies autonomous agent node role task execution."""
    res = agent.execute_assigned_task("Write PySpark Pipeline", {"context_key": "val"})
    assert res.status == "COMPLETED"
    assert res.agent_id == "agent-01"
    assert res.role == "Coder"
    assert "[CODER ARTIFACT]" in res.output_artifact


def test_02_swarm_dag_topological_sort(router):
    """Test 2: Verifies DAG task dependency topological sorting order."""
    router.add_dependency("TaskA", "TaskB")
    router.add_dependency("TaskB", "TaskC")
    res = router.compute_topological_execution_order()
    assert res.has_cycle_deadlock is False
    assert res.execution_order == ["TaskA", "TaskB", "TaskC"]


def test_03_swarm_dag_deadlock_detection(router):
    """Test 3: Verifies cyclic dependency deadlock detection."""
    router.add_dependency("Task1", "Task2")
    router.add_dependency("Task2", "Task1")  # Cycle!
    res = router.compute_topological_execution_order()
    assert res.has_cycle_deadlock is True


def test_04_consensus_majority_voting_pass(consensus):
    """Test 4: Verifies multi-agent voting consensus pass (100% agreement)."""
    res = consensus.evaluate_swarm_consensus(["APPROVE", "APPROVE", "APPROVE"])
    assert res.is_consensus_reached is True
    assert res.consensus_pct == 100.0
    assert res.agreed_output == "APPROVE"


def test_05_consensus_below_threshold_fail(consensus):
    """Test 5: Verifies consensus failure when agreement is below 60% threshold."""
    res = consensus.evaluate_swarm_consensus(["APPROVE", "REJECT", "REVISE"])
    assert res.is_consensus_reached is False
    assert res.consensus_pct < 60.0


def test_06_orchestrator_swarm_workflow(orchestrator):
    """Test 6: Verifies end-to-end multi-agent swarm workflow execution."""
    res = orchestrator.execute_swarm_workflow("Deploy FSDP Model Serving Pipeline")
    assert res["status"] == "SWARM_WORKFLOW_COMPLETED"
    assert res["has_deadlock"] is False
    assert len(res["agents_executed"]) == 3
    assert res["final_consensus"] == "APPROVE_DEPLOYMENT"


def test_07_empty_consensus_handling(consensus):
    """Test 7: Verifies consensus engine handling empty vote arrays safely."""
    res = consensus.evaluate_swarm_consensus([])
    assert res.is_consensus_reached is False
    assert res.total_votes == 0


def test_08_dag_router_single_node(router):
    """Test 8: Verifies DAG router handling single independent task node."""
    router.add_dependency("SingleTask", "SingleTask")
    res = router.compute_topological_execution_order()
    assert res.total_nodes == 1


def test_09_consensus_tied_vote_evaluation(consensus):
    """Test 9 [Production Edge Case]: Verifies consensus behavior on 50/50 tied vote split."""
    res = consensus.evaluate_swarm_consensus(["APPROVE", "REJECT"])
    assert res.consensus_pct == 50.0
    assert res.is_consensus_reached is False  # 50% < 60% threshold!


def test_10_agent_node_empty_context(agent):
    """Test 10 [Production Edge Case]: Verifies agent node executing task with empty context dict."""
    res = agent.execute_assigned_task("EmptyContextTask", {})
    assert res.status == "COMPLETED"
    assert "[]" in res.output_artifact


def test_11_dag_multi_parent_convergence(router):
    """Test 11 [Production Edge Case]: Verifies DAG sorting with multiple parallel parents converging to single child."""
    router.add_dependency("BranchA", "Merge")
    router.add_dependency("BranchB", "Merge")
    res = router.compute_topological_execution_order()
    assert res.has_cycle_deadlock is False
    assert res.execution_order[-1] == "Merge"


def test_12_orchestrator_long_goal_description(orchestrator):
    """Test 12 [Production Edge Case]: Verifies swarm orchestrator processing complex multi-sentence goals."""
    goal_str = "Design and deploy a multi-node Ray cluster with automated Kueue preemption and OpenLineage monitoring."
    res = orchestrator.execute_swarm_workflow(goal_str)
    assert res["goal"] == goal_str
    assert res["status"] == "SWARM_WORKFLOW_COMPLETED"
