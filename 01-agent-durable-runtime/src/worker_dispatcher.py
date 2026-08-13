"""
Fan-Out / Fan-In Async Worker Dispatcher.
Implements parallel task execution, worker concurrency scheduling, and deterministic result aggregation.
Emulates master-worker dynamic batching and sub-agent dispatch from Comcast CONDOR / Agent platform architecture.
"""

import asyncio
import time
from typing import Any, Callable, Dict, List


class WorkerDispatcher:
    def __init__(self, max_concurrency: int = 5):
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_subtask(
        self, 
        subtask_id: str, 
        subtask_fn: Callable[..., Any], 
        *args, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes a single subtask with concurrency bounding via Semaphore.
        """
        async with self.semaphore:
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(subtask_fn):
                    result = await subtask_fn(*args, **kwargs)
                else:
                    # Run sync function in thread pool to prevent blocking main event loop
                    loop = asyncio.get_running_loop()
                    result = await loop.run_in_executor(None, lambda: subtask_fn(*args, **kwargs))
                
                return {
                    "subtask_id": subtask_id,
                    "status": "SUCCESS",
                    "result": result,
                    "execution_time_sec": round(time.time() - start_time, 4)
                }
            except Exception as e:
                return {
                    "subtask_id": subtask_id,
                    "status": "FAILED",
                    "error": str(e),
                    "execution_time_sec": round(time.time() - start_time, 4)
                }

    async def fan_out_fan_in(
        self, 
        tasks_batch: List[Dict[str, Any]], 
        worker_fn: Callable[..., Any]
    ) -> List[Dict[str, Any]]:
        """
        Fans out processing across worker_fn for all tasks in tasks_batch in parallel,
        and fans in (gathers) all results deterministically.
        """
        futures = []
        for idx, task_info in enumerate(tasks_batch):
            subtask_id = task_info.get("id", f"subtask-{idx}")
            params = task_info.get("params", {})
            futures.append(self.execute_subtask(subtask_id, worker_fn, **params))

        # Fan-in via asyncio.gather
        results = await asyncio.gather(*futures)
        return results
