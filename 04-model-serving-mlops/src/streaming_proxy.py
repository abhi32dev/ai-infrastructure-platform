"""
High-Throughput Async SSE Streaming Proxy & Backpressure Controller.
Implements Server-Sent Events (SSE) token streaming, queue length bounding (Backpressure isolation),
and request concurrency rate limiting for model serving endpoints.
"""

import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Optional


class StreamingProxy:
    def __init__(self, max_queue_depth: int = 10, max_concurrency: int = 5):
        self.max_queue_depth = max_queue_depth
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.active_requests = 0

    async def stream_tokens(
        self, 
        prompt: str, 
        model_name: str = "ollama/llama3.2:1b"
    ) -> AsyncGenerator[str, None]:
        """
        Streams generated LLM tokens via Server-Sent Events (SSE) format.
        Enforces Backpressure Isolation if request queue depth is breached.
        """
        if self.active_requests >= self.max_queue_depth:
            # Backpressure Isolation! Reject excess load cleanly before downstream saturation
            yield f"data: {json.dumps({'error': 'BACKPRESSURE_QUEUE_FULL', 'message': 'System queue capacity reached. Please try again.'})}\n\n"
            return

        self.active_requests += 1
        start_time = time.time()
        first_token_sent = False

        try:
            async with self.semaphore:
                # Simulated streaming token chunks
                sample_tokens = [
                    "Based ", "on ", "your ", "query, ", "the ", "CONDOR ", "distributed ", "platform ", 
                    "maintains ", "a ", "verified ", "99.999% ", "availability ", "SLA ", "across ", "12,000+ ", "nodes."
                ]

                for idx, token in enumerate(sample_tokens):
                    await asyncio.sleep(0.03)  # Simulate model inference latency per token
                    
                    ttft = round(time.time() - start_time, 4) if not first_token_sent else None
                    first_token_sent = True

                    chunk_payload = {
                        "token": token,
                        "token_index": idx,
                        "ttft_sec": ttft,
                        "model": model_name
                    }
                    yield f"data: {json.dumps(chunk_payload)}\n\n"

        finally:
            self.active_requests -= 1
