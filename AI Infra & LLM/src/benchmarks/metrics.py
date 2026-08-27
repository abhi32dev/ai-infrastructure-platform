import numpy as np
import psutil
from typing import List, Dict, Any

class MetricsCalculator:
    @staticmethod
    def get_system_memory_mb() -> float:
        # Returns current RAM usage of the python process in MB
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    @staticmethod
    def calculate(results: List[Dict[str, Any]], start_mem_mb: float, end_mem_mb: float) -> Dict[str, Any]:
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests

        ttfts = [r["ttft_ms"] for r in results if r["success"]]
        tpots = [r["tpot_ms"] for r in results if r["success"]]
        durations = [r["duration_ms"] for r in results if r["success"]]
        tokens = [r["tokens"] for r in results if r["success"]]

        if not ttfts:
            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "mean_ttft_ms": 0.0,
                "p95_ttft_ms": 0.0,
                "p99_ttft_ms": 0.0,
                "mean_tpot_ms": 0.0,
                "tokens_per_sec": 0.0,
                "memory_delta_mb": end_mem_mb - start_mem_mb
            }

        mean_ttft = float(np.mean(ttfts))
        p95_ttft = float(np.percentile(ttfts, 95))
        p99_ttft = float(np.percentile(ttfts, 99))
        mean_tpot = float(np.mean(tpots))

        total_tokens = sum(tokens)
        total_duration_sec = sum(durations) / 1000.0
        tokens_per_sec = total_tokens / total_duration_sec if total_duration_sec > 0 else 0.0

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "mean_ttft_ms": round(mean_ttft, 2),
            "p95_ttft_ms": round(p95_ttft, 2),
            "p99_ttft_ms": round(p99_ttft, 2),
            "mean_tpot_ms": round(mean_tpot, 2),
            "tokens_per_sec": round(tokens_per_sec, 2),
            "memory_delta_mb": round(end_mem_mb - start_mem_mb, 2)
        }
