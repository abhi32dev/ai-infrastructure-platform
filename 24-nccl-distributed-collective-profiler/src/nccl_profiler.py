import math
import statistics
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class CollectiveType:
    ALL_REDUCE = "ALL_REDUCE"
    ALL_GATHER = "ALL_GATHER"
    REDUCE_SCATTER = "REDUCE_SCATTER"

class BandwidthAnalyzer:
    """Calculates algorithmic and bus bandwidth for multi-GPU collectives."""
    @staticmethod
    def calculate_bus_bw(collective: str, size_bytes: float, latency_sec: float, world_size: int) -> float:
        if latency_sec <= 0.0:
            return 0.0
        alg_bw = (size_bytes / latency_sec) / 1e9  # GB/s
        if collective == CollectiveType.ALL_REDUCE:
            bus_factor = (2.0 * (world_size - 1)) / world_size
        else:
            bus_factor = (world_size - 1) / world_size
        return alg_bw * bus_factor

class StragglerDetector:
    """Detects straggler GPU ranks and thermal throttling imbalances."""
    @staticmethod
    def detect_stragglers(per_rank_latencies_ms: List[float], max_variance_pct: float = 5.0) -> Dict[str, Any]:
        if not per_rank_latencies_ms:
            return {"straggler_detected": False, "straggler_ranks": []}
        
        mean_lat = statistics.mean(per_rank_latencies_ms)
        stragglers = []
        for rank, lat in enumerate(per_rank_latencies_ms):
            pct_diff = ((lat - mean_lat) / mean_lat) * 100.0
            if pct_diff > max_variance_pct:
                stragglers.append(rank)

        return {
            "straggler_detected": len(stragglers) > 0,
            "straggler_ranks": stragglers,
            "mean_latency_ms": round(mean_lat, 3),
            "max_latency_ms": round(max(per_rank_latencies_ms), 3)
        }

class NCCLProfiler:
    """NCCL Distributed Collective Communication & Topology Profiler."""
    def __init__(self, world_size: int = 8, nvlink_peak_gb: float = 900.0):
        self.world_size = world_size
        self.nvlink_peak_gb = nvlink_peak_gb

    def profile_collectives(self, collective: str, message_size_mb: float, per_rank_latencies_ms: List[float]) -> Dict[str, Any]:
        size_bytes = message_size_mb * 1024 * 1024
        mean_latency_sec = statistics.mean(per_rank_latencies_ms) / 1000.0

        # Step 1: Bus Bandwidth Calculation
        bus_bw = BandwidthAnalyzer.calculate_bus_bw(collective, size_bytes, mean_latency_sec, self.world_size)
        saturation_pct = (bus_bw / self.nvlink_peak_gb) * 100.0

        # Step 2: Straggler Detection
        straggler_report = StragglerDetector.detect_stragglers(per_rank_latencies_ms)

        # Decision Gate
        if saturation_pct >= 80.0 and not straggler_report["straggler_detected"]:
            status = "OPTIMAL_COMMUNICATION"
        elif straggler_report["straggler_detected"]:
            status = "STRAGGLER_RANK_DETECTED"
        else:
            status = "BANDWIDTH_BOTTLENECK"

        return {
            "status": status,
            "collective": collective,
            "world_size": self.world_size,
            "bus_bandwidth_gbs": round(bus_bw, 2),
            "nvlink_saturation_pct": round(saturation_pct, 2),
            "straggler_ranks": straggler_report["straggler_ranks"],
            "mean_latency_ms": straggler_report["mean_latency_ms"]
        }
