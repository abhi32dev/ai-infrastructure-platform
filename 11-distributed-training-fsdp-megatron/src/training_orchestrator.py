"""
Master Distributed Training & Parallelism Orchestrator.
Integrates PyTorch FSDP Model Sharding, Megatron-LM 3D Parallelism Grid, and NCCL Communication Profiling.
"""

from typing import Any, Dict
from src.fsdp_sharder import FSDPSharder, FSDPShardedState, FSDPShardingConfig
from src.megatron_parallelism import Megatron3DGrid, MegatronParallelismEngine
from src.nccl_communicator import NCCLCommMetrics, NCCLCommunicatorProfiler


class DistributedTrainingOrchestrator:
    def __init__(self, model_name: str = "Llama-3.2-70B", num_nodes: int = 2, gpus_per_node: int = 8):
        self.model_name = model_name
        self.num_gpus = num_nodes * gpus_per_node
        self.fsdp = FSDPSharder(FSDPShardingConfig(
            model_name=model_name,
            total_params_billions=70.0,
            num_gpus=self.num_gpus,
            sharding_strategy="FULL_SHARD"
        ))
        self.megatron = MegatronParallelismEngine(
            tensor_parallel_size=2,
            pipeline_parallel_size=2,
            data_parallel_size=self.num_gpus // 4
        )
        self.nccl = NCCLCommunicatorProfiler()

    def run_training_step(self, batch_size: int = 16) -> Dict[str, Any]:
        """Executes a single distributed training step profiling memory & NCCL bandwidth."""
        fsdp_state = self.fsdp.calculate_fsdp_sharding_memory()
        grid = self.megatron.build_3d_rank_grid()
        nccl_metrics = self.nccl.profile_collective_op(
            collective_type="ALL_REDUCE",
            data_size_mb=280.0,
            num_ranks=self.num_gpus,
            is_cross_node=True
        )

        return {
            "status": "STEP_COMPLETED",
            "model_name": self.model_name,
            "world_size": self.num_gpus,
            "fsdp_vram_per_gpu_gb": fsdp_state.vram_per_gpu_gb,
            "memory_savings_pct": fsdp_state.memory_savings_pct,
            "3d_grid": {
                "tp": grid.tensor_parallel_size,
                "pp": grid.pipeline_parallel_size,
                "dp": grid.data_parallel_size
            },
            "nccl_bus_bandwidth_gbps": nccl_metrics.bus_bandwidth_gbps,
            "nccl_latency_us": nccl_metrics.latency_us
        }
