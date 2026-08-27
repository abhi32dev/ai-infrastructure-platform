import asyncio
import time
from typing import List, Dict, Any
from src.serving.client import LLMClient
from src.common.logger import get_logger

logger = get_logger("benchmark_engine")

class BenchmarkEngine:
    def __init__(self, concurrency: int = 1, model_name: str = "candidate-brain:latest"):
        self.concurrency = concurrency
        self.model_name = model_name
        self.client = LLMClient()
        self.semaphore = asyncio.Semaphore(concurrency)

    async def run_single_request(self, prompt: str, prompt_id: int) -> Dict[str, Any]:
        async with self.semaphore:
            start_time = time.perf_counter()
            ttft = 0.0
            tpot = 0.0
            total_tokens = 0
            success = False
            response_content = []

            try:
                # Call stream endpoint to capture TTFT
                async for chunk in self.client.generate_stream(
                    prompt=prompt,
                    model=self.model_name
                ):
                    if total_tokens == 0:
                        ttft = chunk.get("ttft_ms", 0.0)
                    
                    content = chunk.get("content", "")
                    if content:
                        # Simple word-based token heuristic or exact length
                        # 1 word ~ 1.3 tokens
                        words = len(content.split())
                        total_tokens += max(1, words)
                        response_content.append(content)
                    
                    if chunk.get("done", False):
                        break

                end_time = time.perf_counter()
                total_duration = (end_time - start_time) * 1000.0
                
                if total_tokens > 0:
                    # Time per output token: (Total time - TTFT) / output tokens
                    tpot = (total_duration - ttft) / total_tokens if total_tokens > 1 else (total_duration - ttft)
                else:
                    tpot = total_duration

                success = True
            except Exception as e:
                logger.error(f"Benchmark request {prompt_id} failed: {e}")
                total_duration = (time.perf_counter() - start_time) * 1000.0
                ttft = total_duration
                tpot = total_duration

            return {
                "request_id": prompt_id,
                "success": success,
                "ttft_ms": ttft,
                "tpot_ms": tpot,
                "duration_ms": total_duration,
                "tokens": total_tokens,
                "tokens_per_sec": (total_tokens / (total_duration / 1000.0)) if total_duration > 0 else 0.0
            }

    async def execute_sweep(self, prompts: List[str]) -> List[Dict[str, Any]]:
        logger.info(f"Launching benchmark sweep: Concurrency={self.concurrency}, Prompts={len(prompts)}")
        tasks = [
            self.run_single_request(prompt, idx)
            for idx, prompt in enumerate(prompts)
        ]
        return await asyncio.gather(*tasks)
