"""
Checkpoint Store for Durable Task Execution & Deterministic Replay.
Provides atomic persistence of task states and step checkpoints using SQLite + JSON snapshotting.
Demonstrates S3/DynamoDB-style checkpointing and state consistency patterns.
"""

import json
import os
import sqlite3
import time
from typing import List, Optional
from src.state_models import StepCheckpoint, TaskState, TaskStatus


class CheckpointStore:
    def __init__(self, db_path: str = "agent_state.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_step_index INTEGER NOT NULL,
                    total_steps INTEGER NOT NULL,
                    context_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS step_checkpoints (
                    checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT,
                    error_message TEXT,
                    tool_calls TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def save_task_state(self, state: TaskState) -> None:
        state.updated_at = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (
                    task_id, goal, status, current_step_index, total_steps, context_data, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    status=excluded.status,
                    current_step_index=excluded.current_step_index,
                    total_steps=excluded.total_steps,
                    context_data=excluded.context_data,
                    updated_at=excluded.updated_at,
                    metadata=excluded.metadata
            """, (
                state.task_id,
                state.goal,
                state.status.value if isinstance(state.status, TaskStatus) else state.status,
                state.current_step_index,
                state.total_steps,
                json.dumps(state.context_data),
                state.created_at,
                state.updated_at,
                json.dumps(state.metadata)
            ))
            conn.commit()

        # Save individual checkpoints
        for cp in state.checkpoints:
            self.save_step_checkpoint(state.task_id, cp)

    def save_step_checkpoint(self, task_id: str, checkpoint: StepCheckpoint) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Check if checkpoint already exists for this task_id & step_index
            cursor.execute("""
                SELECT checkpoint_id FROM step_checkpoints 
                WHERE task_id = ? AND step_index = ?
            """, (task_id, checkpoint.step_index))
            existing = cursor.fetchone()

            status_val = checkpoint.status.value if isinstance(checkpoint.status, TaskStatus) else checkpoint.status
            input_json = json.dumps(checkpoint.input_data)
            output_json = json.dumps(checkpoint.output_data) if checkpoint.output_data is not None else None
            tool_calls_json = json.dumps(checkpoint.tool_calls)

            if existing:
                cursor.execute("""
                    UPDATE step_checkpoints SET
                        step_id = ?, step_name = ?, status = ?, input_data = ?, 
                        output_data = ?, error_message = ?, tool_calls = ?, timestamp = ?
                    WHERE task_id = ? AND step_index = ?
                """, (
                    checkpoint.step_id, checkpoint.step_name, status_val,
                    input_json, output_json, checkpoint.error_message,
                    tool_calls_json, checkpoint.timestamp, task_id, checkpoint.step_index
                ))
            else:
                cursor.execute("""
                    INSERT INTO step_checkpoints (
                        task_id, step_id, step_name, step_index, status, 
                        input_data, output_data, error_message, tool_calls, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, checkpoint.step_id, checkpoint.step_name, checkpoint.step_index,
                    status_val, input_json, output_json, checkpoint.error_message,
                    tool_calls_json, checkpoint.timestamp
                ))
            conn.commit()

    def load_task_state(self, task_id: str) -> Optional[TaskState]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None

            # Load checkpoints
            cursor.execute("""
                SELECT * FROM step_checkpoints 
                WHERE task_id = ? 
                ORDER BY step_index ASC
            """, (task_id,))
            cp_rows = cursor.fetchall()

            checkpoints = []
            for cp_row in cp_rows:
                checkpoints.append(StepCheckpoint(
                    step_id=cp_row["step_id"],
                    step_name=cp_row["step_name"],
                    step_index=cp_row["step_index"],
                    status=TaskStatus(cp_row["status"]),
                    input_data=json.loads(cp_row["input_data"]),
                    output_data=json.loads(cp_row["output_data"]) if cp_row["output_data"] else None,
                    error_message=cp_row["error_message"],
                    tool_calls=json.loads(cp_row["tool_calls"]),
                    timestamp=cp_row["timestamp"]
                ))

            return TaskState(
                task_id=row["task_id"],
                goal=row["goal"],
                status=TaskStatus(row["status"]),
                current_step_index=row["current_step_index"],
                total_steps=row["total_steps"],
                checkpoints=checkpoints,
                context_data=json.loads(row["context_data"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                metadata=json.loads(row["metadata"])
            )

    def get_last_successful_checkpoint(self, task_id: str) -> Optional[StepCheckpoint]:
        state = self.load_task_state(task_id)
        if not state:
            return None
        
        successful_cps = [cp for cp in state.checkpoints if cp.status in (TaskStatus.COMPLETED, TaskStatus.CHECKPOINTED)]
        if not successful_cps:
            return None
        return max(successful_cps, key=lambda cp: cp.step_index)

    def truncate_checkpoints_after(self, task_id: str, step_index: int) -> None:
        """Used during replay to delete stale checkpoints following a target resume point."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM step_checkpoints 
                WHERE task_id = ? AND step_index > ?
            """, (task_id, step_index))
            conn.commit()
