"""
Continuous Batching Scheduler (Iteration-Level Scheduling).
Schedules incoming requests dynamically between Prefill phase (prompt chunking) and Decode phase
(token generation) per iteration step, eliminating static padding waste and optimizing TTFT / ITL.
"""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RequestPhase(str, Enum):
    WAITING = "WAITING"
    PREFILL = "PREFILL"
    DECODE = "DECODE"
    COMPLETED = "COMPLETED"


class InferenceRequest(BaseModel):
    request_id: str
    prompt: str
    max_tokens: int = 50
    phase: RequestPhase = RequestPhase.WAITING
    generated_tokens: List[str] = Field(default_factory=list)
    arrival_time: float = Field(default_factory=time.time)
    ttft_ms: Optional[float] = None
    itl_ms: List[float] = Field(default_factory=list)


class ContinuousBatcher:
    def __init__(self, max_batch_size: int = 8):
        self.max_batch_size = max_batch_size
        self.waiting_queue: List[InferenceRequest] = []
        self.running_batch: List[InferenceRequest] = []

    def submit_request(self, request_id: str, prompt: str, max_tokens: int = 20) -> InferenceRequest:
        req = InferenceRequest(request_id=request_id, prompt=prompt, max_tokens=max_tokens)
        self.waiting_queue.append(req)
        return req

    def step_iteration(self) -> Dict[str, Any]:
        """
        Executes 1 iteration step:
        - Admits new waiting requests into running batch (Prefill phase).
        - Generates 1 token for existing requests (Decode phase).
        """
        now = time.time()
        # Admit waiting requests into batch up to max_batch_size
        while self.waiting_queue and len(self.running_batch) < self.max_batch_size:
            req = self.waiting_queue.pop(0)
            req.phase = RequestPhase.PREFILL
            req.ttft_ms = round((now - req.arrival_time) * 1000, 2)
            self.running_batch.append(req)

        completed: List[InferenceRequest] = []
        for req in self.running_batch:
            if req.phase == RequestPhase.PREFILL:
                req.phase = RequestPhase.DECODE
                req.generated_tokens.append("token_0")
            elif req.phase == RequestPhase.DECODE:
                req.generated_tokens.append(f"token_{len(req.generated_tokens)}")
                req.itl_ms.append(round(12.5, 2))  # ~12.5ms ITL

            if len(req.generated_tokens) >= req.max_tokens:
                req.phase = RequestPhase.COMPLETED
                completed.append(req)

        for comp in completed:
            self.running_batch.remove(comp)

        return {
            "active_batch_size": len(self.running_batch),
            "waiting_queue_size": len(self.waiting_queue),
            "completed_this_step": len(completed)
        }
