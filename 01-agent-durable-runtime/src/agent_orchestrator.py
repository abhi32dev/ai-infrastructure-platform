"""
Master Agent Orchestrator & Durable Execution Engine.
Combines multi-step LLM task planning, state machine transitions, SQLite checkpointing,
MCP tool execution, deterministic step replay, and Human-in-the-Loop approval gates.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from src.checkpoint_store import CheckpointStore
from src.mcp_tool_registry import MCPToolRegistry
from src.state_models import StepCheckpoint, TaskState, TaskStatus, ToolPermissionLevel
from src.worker_dispatcher import WorkerDispatcher


class AgentOrchestrator:
    def __init__(self, db_path: str = "agent_state.db"):
        self.store = CheckpointStore(db_path=db_path)
        self.tool_registry = MCPToolRegistry()
        self.dispatcher = WorkerDispatcher(max_concurrency=4)

    def submit_task(self, goal: str, metadata: Optional[Dict[str, Any]] = None) -> TaskState:
        """
        Submits a new multi-step agent task and initializes durable state.
        """
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        state = TaskState(
            task_id=task_id,
            goal=goal,
            status=TaskStatus.PENDING,
            current_step_index=0,
            total_steps=4,  # Standard 4-step remediation agent pipeline
            metadata=metadata or {}
        )
        self.store.save_task_state(state)
        return state

    async def run_task(self, task_id: str, simulate_failure_at_step: Optional[int] = None) -> TaskState:
        """
        Executes a multi-step agent workflow step-by-step with checkpointing and state persistence.
        """
        state = self.store.load_task_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found.")

        if state.status == TaskStatus.COMPLETED:
            return state

        state.status = TaskStatus.RUNNING
        self.store.save_task_state(state)

        # Execution Workflow Steps:
        # Step 0: Plan & Search Runbook (Tool: search_knowledge_base)
        # Step 1: Query Telemetry (Tool: query_telemetry)
        # Step 2: Fan-out Sub-agent Node Diagnostic (Parallel Worker Dispatch)
        # Step 3: Execute Remediation Action (Tool: execute_system_remediation - REQUIRES HITL)

        steps_definition = [
            ("search_runbook", "Search Runbook & Guidelines", "search_knowledge_base", {"query": state.goal}),
            ("check_telemetry", "Query Edge Node Telemetry", "query_telemetry", {"node_id": "edge-node-108"}),
            ("diagnose_subnodes", "Fan-out Subnode Diagnostic", "FAN_OUT_DIAGNOSTICS", {}),
            ("apply_remediation", "Execute System Remediation", "execute_system_remediation", {"node_id": "edge-node-108", "remediation_action": "RESTART"})
        ]

        start_index = state.current_step_index

        for step_idx in range(start_index, len(steps_definition)):
            step_id, step_name, tool_name, params = steps_definition[step_idx]

            # Check if this step was already completed in a previous run (deterministic check)
            existing_cp = next((cp for cp in state.checkpoints if cp.step_index == step_idx and cp.status == TaskStatus.COMPLETED), None)
            if existing_cp:
                print(f"[REPLAY CACHE HIT] Step {step_idx} ({step_name}) already completed. Reusing checkpoint output.")
                state.current_step_index = step_idx + 1
                continue

            print(f"[ORCHESTRATOR] Executing Step {step_idx}: {step_name}...")

            # Simulated failure hook for testing deterministic replay
            if simulate_failure_at_step is not None and step_idx == simulate_failure_at_step:
                error_msg = f"Simulated Transient Outage / Failure at Step {step_idx} ({step_name})"
                failed_cp = StepCheckpoint(
                    step_id=step_id,
                    step_name=step_name,
                    step_index=step_idx,
                    status=TaskStatus.FAILED,
                    input_data=params,
                    error_message=error_msg,
                    timestamp=time.time()
                )
                state.checkpoints.append(failed_cp)
                state.status = TaskStatus.FAILED
                self.store.save_task_state(state)
                print(f"[ORCHESTRATOR ERROR] {error_msg}")
                return state

            # Handle Step Execution Logic
            if tool_name == "FAN_OUT_DIAGNOSTICS":
                # Special parallel fan-out sub-agent execution step
                subtask_batch = [
                    {"id": "subnode-1", "params": {"query": "Check container log stream 1"}},
                    {"id": "subnode-2", "params": {"query": "Check network buffer queue 2"}},
                    {"id": "subnode-3", "params": {"query": "Check CPU throttling metric 3"}}
                ]
                fan_out_results = await self.dispatcher.fan_out_fan_in(
                    subtask_batch, 
                    lambda query: {"diagnostic_finding": f"Resolved '{query}': Metric normal"}
                )
                step_output = {"fan_out_results": fan_out_results}
                is_success = True
            else:
                # Check tool permission level
                tool_def = self.tool_registry.get_tool(tool_name)
                is_approved = state.metadata.get(f"approved_step_{step_idx}", False)

                is_success, result_or_err = self.tool_registry.execute_tool(
                    tool_name, params, is_human_approved=is_approved
                )

                if not is_success and isinstance(result_or_err, dict) and result_or_err.get("error") == "REQUIRES_HUMAN_APPROVAL":
                    # Trigger Human-in-the-Loop pause gate!
                    hitl_cp = StepCheckpoint(
                        step_id=step_id,
                        step_name=step_name,
                        step_index=step_idx,
                        status=TaskStatus.HUMAN_APPROVAL_REQUIRED,
                        input_data=params,
                        error_message="Paused: Waiting for human approval for sensitive action.",
                        tool_calls=[{"tool_name": tool_name, "params": params}],
                        timestamp=time.time()
                    )
                    state.checkpoints.append(hitl_cp)
                    state.status = TaskStatus.HUMAN_APPROVAL_REQUIRED
                    self.store.save_task_state(state)
                    print(f"[HITL PAUSE] Task {task_id} paused at Step {step_idx} for Human Approval.")
                    return state
                elif not is_success:
                    step_output = {"error": str(result_or_err)}
                else:
                    step_output = result_or_err

            # Step execution completed successfully! Record step checkpoint
            checkpoint = StepCheckpoint(
                step_id=step_id,
                step_name=step_name,
                step_index=step_idx,
                status=TaskStatus.COMPLETED if is_success else TaskStatus.FAILED,
                input_data=params,
                output_data=step_output,
                tool_calls=[{"tool_name": tool_name, "params": params}],
                timestamp=time.time()
            )

            # Update state context with step output
            state.context_data[step_id] = step_output
            state.checkpoints.append(checkpoint)
            state.current_step_index = step_idx + 1
            state.status = TaskStatus.CHECKPOINTED
            self.store.save_task_state(state)

        # All steps completed!
        state.status = TaskStatus.COMPLETED
        self.store.save_task_state(state)
        print(f"[ORCHESTRATOR] Task {task_id} COMPLETED SUCCESSFULLY.")
        return state

    def approve_step(self, task_id: str, step_index: int) -> TaskState:
        """
        Approves a pending Human-in-the-Loop sensitive step, enabling task resumption.
        """
        state = self.store.load_task_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found.")

        state.metadata[f"approved_step_{step_index}"] = True
        state.status = TaskStatus.CHECKPOINTED
        self.store.save_task_state(state)
        print(f"[HITL APPROVAL] Step {step_index} approved for Task {task_id}.")
        return state

    async def replay_task_from_last_checkpoint(self, task_id: str) -> TaskState:
        """
        Deterministic Replay: Loads last valid checkpoint, rewinds failed/stale state, and resumes execution.
        """
        state = self.store.load_task_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found.")

        last_valid_cp = self.store.get_last_successful_checkpoint(task_id)
        resume_index = (last_valid_cp.step_index + 1) if last_valid_cp else 0

        print(f"[DURABLE REPLAY] Rewinding Task {task_id} to resume from Step Index {resume_index}...")

        # Truncate failed/stale checkpoints in database after resume point
        self.store.truncate_checkpoints_after(task_id, resume_index - 1 if last_valid_cp else -1)
        
        # Reload clean state
        state = self.store.load_task_state(task_id)
        state.current_step_index = resume_index
        state.status = TaskStatus.REPLAYING
        self.store.save_task_state(state)

        # Resume task execution without simulated failure
        return await self.run_task(task_id, simulate_failure_at_step=None)
