"""
Megatron-LM 3D Parallelism Grid Coordinator.
Calculates Tensor Parallelism (TP), Pipeline Parallelism (PP), and Data Parallelism (DP)
rank maps across multi-node GPU clusters (TP * PP * DP = Total GPUs).
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class Megatron3DGrid(BaseModel):
    world_size: int
    tensor_parallel_size: int
    pipeline_parallel_size: int
    data_parallel_size: int
    rank_assignments: Dict[int, Dict[str, int]]


class MegatronParallelismEngine:
    def __init__(self, tensor_parallel_size: int = 2, pipeline_parallel_size: int = 2, data_parallel_size: int = 2):
        self.tp = tensor_parallel_size
        self.pp = pipeline_parallel_size
        self.dp = data_parallel_size
        self.world_size = tensor_parallel_size * pipeline_parallel_size * data_parallel_size

    def build_3d_rank_grid(self) -> Megatron3DGrid:
        """
        Builds Megatron 3D Parallelism rank mapping grid.
        Rank ID = (dp_rank * tp * pp) + (pp_rank * tp) + tp_rank
        """
        grid: Dict[int, Dict[str, int]] = {}
        for global_rank in range(self.world_size):
            tp_rank = global_rank % self.tp
            pp_rank = (global_rank // self.tp) % self.pp
            dp_rank = global_rank // (self.tp * self.pp)
            
            grid[global_rank] = {
                "tp_rank": tp_rank,
                "pp_rank": pp_rank,
                "dp_rank": dp_rank
            }

        return Megatron3DGrid(
            world_size=self.world_size,
            tensor_parallel_size=self.tp,
            pipeline_parallel_size=self.pp,
            data_parallel_size=self.dp,
            rank_assignments=grid
        )

    def get_rank_coordinates(self, global_rank: int) -> Dict[str, int]:
        grid = self.build_3d_rank_grid()
        if global_rank not in grid.rank_assignments:
            raise ValueError(f"Invalid global rank {global_rank} for world size {self.world_size}")
        return grid.rank_assignments[global_rank]
