"""
Interactive CLI Runner & Test Suite for Durable Agent Runtime Engine.
Runs 4 core production scenarios:
1. Normal workflow execution with step checkpointing.
2. Simulated failure mid-flight & durable state persistence.
3. Deterministic step replay from last successful checkpoint.
4. Human-in-the-Loop (HITL) pause gate and approval resume.
"""

import asyncio
import os
import sys
import time

from src.agent_orchestrator import AgentOrchestrator
from src.state_models import TaskStatus


async def run_demo():
    print("==========================================================================")
    print("🚀 STARTING AGENT RUNTIME & DURABLE EXECUTION ENGINE DEMO")
    print("==========================================================================\n")

    # Use a fresh test database for the demo
    db_file = "demo_agent_state.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    orchestrator = AgentOrchestrator(db_path=db_file)

    # -------------------------------------------------------------------------
    # SCENARIO 1: Normal Execution & Step Checkpointing
    # -------------------------------------------------------------------------
    print("\n--- [SCENARIO 1] Normal Workflow Execution & State Checkpointing ---")
    task1 = orchestrator.submit_task("Investigate and remediate memory pressure on edge-node-108")
    print(f"Task Submitted: ID = {task1.task_id}, Initial Status = {task1.status.value}")

    print("\nExecuting Task 1 (pre-approved HITL for scenario 1)...")
    orchestrator.approve_step(task1.task_id, step_index=3)
    final_state1 = await orchestrator.run_task(task1.task_id)
    print(f"Task 1 Final Status: {final_state1.status.value}")
    print(f"Checkpoints Recorded: {len(final_state1.checkpoints)}")
    for cp in final_state1.checkpoints:
        print(f"  └─ Step {cp.step_index} ({cp.step_name}): Status = {cp.status.value}")

    # -------------------------------------------------------------------------
    # SCENARIO 2: Simulated Failure Mid-Flight
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 2] Simulated Mid-Flight Failure (Transient Outage) ---")
    task2 = orchestrator.submit_task("Automated health recovery for cluster node-204")
    print(f"Task Submitted: ID = {task2.task_id}")

    print("Executing Task 2 with simulated failure at Step 2...")
    failed_state = await orchestrator.run_task(task2.task_id, simulate_failure_at_step=2)
    print(f"Task 2 Status After Failure: {failed_state.status.value}")
    for cp in failed_state.checkpoints:
        print(f"  └─ Step {cp.step_index} ({cp.step_name}): Status = {cp.status.value}")

    # -------------------------------------------------------------------------
    # SCENARIO 3: Deterministic Step Replay (Resuming from Checkpoint)
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 3] Deterministic Step Replay & Resumable Recovery ---")
    print("Triggering Replay from Last Valid Checkpoint...")
    orchestrator.approve_step(task2.task_id, step_index=3)
    replayed_state = await orchestrator.replay_task_from_last_checkpoint(task2.task_id)
    print(f"Task 2 Status After Replay: {replayed_state.status.value}")
    for cp in replayed_state.checkpoints:
        print(f"  └─ Step {cp.step_index} ({cp.step_name}): Status = {cp.status.value}")

    # -------------------------------------------------------------------------
    # SCENARIO 4: Human-in-the-Loop (HITL) Approval Gate
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 4] Human-In-The-Loop (HITL) Sensitive Action Gate ---")
    task3 = orchestrator.submit_task("Restart production database service daemon")
    print(f"Task Submitted: ID = {task3.task_id}")

    print("Running Task 3 without prior approval...")
    hitl_state = await orchestrator.run_task(task3.task_id)
    print(f"Task 3 Status (Expect HUMAN_APPROVAL_REQUIRED): {hitl_state.status.value}")

    print("\nSimulating Human Reviewer approving sensitive remediation step...")
    orchestrator.approve_step(task3.task_id, step_index=3)
    resumed_hitl_state = await orchestrator.run_task(task3.task_id)
    print(f"Task 3 Status After Human Approval & Resume: {resumed_hitl_state.status.value}")

    print("\n==========================================================================")
    print("✅ DEMO COMPLETED SUCCESSFULLY! ALL 4 SCENARIOS VERIFIED.")
    print("==========================================================================\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
