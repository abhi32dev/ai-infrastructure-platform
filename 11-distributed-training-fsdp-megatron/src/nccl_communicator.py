"""
NCCL Inter-GPU All-Reduce & Communication Bandwidth Profiler.
Simulates NVLink intra-node and InfiniBand / RoCE inter-node collective communication
bandwidth saturation (GB/s) and All-Reduce latency during FSDP / Megatron training.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class NCCLCommMetrics(BaseModel):
    collective_type: str  # ALL_REDUCE, ALL_GATHER, REDUCE_SCATTER
    data_size_mb: float
    bus_bandwidth_gbps: float
    latency_us: float
    network_interconnect: str  # NVLink (900 GB/s) vs InfiniBand (400 Gbps)
    is_network_bottleneck: bool


class NCCLCommunicatorProfiler:
    def __init__(self, nvlink_bandwidth_gbps: float = 900.0, infiniband_gbps: float = 50.0):
        self.nvlink_bandwidth = nvlink_bandwidth_gbps
        self.infiniband_bandwidth = infiniband_gbps

    def profile_collective_op(
        self, 
        collective_type: str, 
        data_size_mb: float, 
        num_ranks: int, 
        is_cross_node: bool = False
    ) -> NCCLCommMetrics:
        """
        Profiles NCCL collective bandwidth:
        All-Reduce bus bandwidth = (2 * (N - 1) / N) * (data_size / time)
        """
        effective_bw = self.infiniband_bandwidth if is_cross_node else self.nvlink_bandwidth
        
        # Algorithmic factor for All-Reduce ring
        factor = (2.0 * (num_ranks - 1)) / num_ranks if num_ranks > 1 else 1.0
        data_gb = data_size_mb / 1024.0
        
        # Latency in microseconds
        time_sec = (data_gb * factor) / effective_bw
        latency_us = round(time_sec * 1_000_000, 2)
        bus_bw = round(effective_bw * 0.92, 1)  # 92% hardware efficiency

        return NCCLCommMetrics(
            collective_type=collective_type,
            data_size_mb=data_size_mb,
            bus_bandwidth_gbps=bus_bw,
            latency_us=latency_us,
            network_interconnect="InfiniBand_400G" if is_cross_node else "NVLink_4",
            is_network_bottleneck=is_cross_node and (data_size_mb > 500.0)
        )
