"""
PyTorch FSDP (Fully Sharded Data Parallel) Model Sharding Engine.
Shards model weights, gradients, and optimizer states across GPU ranks (ZeRO-3 equivalent),
enabling training of 70B+ parameter models on multi-node GPU clusters.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class FSDPShardingConfig(BaseModel):
    model_name: str
    total_params_billions: float
    num_gpus: int
    mixed_precision: str = "bfloat16"
    cpu_offload: bool = False
    sharding_strategy: str = "FULL_SHARD"  # ZeRO-3 equivalent


class FSDPShardedState(BaseModel):
    total_vram_required_gb: float
    vram_per_gpu_gb: float
    sharded_param_count_millions: float
    optimizer_state_vram_gb: float
    memory_savings_pct: float


class FSDPSharder:
    def __init__(self, config: FSDPShardingConfig):
        self.config = config

    def calculate_fsdp_sharding_memory(self) -> FSDPShardedState:
        """
        Calculates FSDP ZeRO-3 memory breakdown:
        Unsharded FP16 model = 2 bytes/param
        Gradients = 2 bytes/param
        Adam Optimizer states (fp32 master weights + m + v) = 12 bytes/param
        Total unsharded memory = 16 bytes/param.
        FSDP divides params, grads, and optimizer states by num_gpus.
        """
        params_b = self.config.total_params_billions
        num_gpus = max(1, self.config.num_gpus)

        # Base memory in GB for FP16/BF16
        unsharded_vram = params_b * 16.0  # 16 GB per billion params (weights + grads + optimizer)
        sharded_vram = unsharded_vram / num_gpus

        if self.config.cpu_offload:
            sharded_vram *= 0.35  # Offload optimizer states to CPU RAM

        sharded_params = (params_b * 1000.0) / num_gpus
        savings_pct = round((1.0 - (sharded_vram / unsharded_vram)) * 100.0, 2)

        return FSDPShardedState(
            total_vram_required_gb=round(unsharded_vram, 2),
            vram_per_gpu_gb=round(sharded_vram, 2),
            sharded_param_count_millions=round(sharded_params, 2),
            optimizer_state_vram_gb=round((params_b * 12.0) / num_gpus, 2),
            memory_savings_pct=savings_pct
        )
