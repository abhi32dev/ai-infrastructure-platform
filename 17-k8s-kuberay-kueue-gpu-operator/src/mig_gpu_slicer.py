"""
NVIDIA MIG (Multi-Instance GPU) Fractional GPU Slicing Engine.
Partitions A100/H100 physical GPUs into hardware-isolated instances (1g.10gb, 2g.20gb, 3g.40gb, 7g.80gb).
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class MIGInstance(BaseModel):
    mig_profile: str  # 1g.10gb, 2g.20gb, 3g.40gb, 7g.80gb
    vram_gb: int
    compute_slices: int
    is_allocated: bool = False


class MIGGPUSlicer:
    PROFILES = {
        "1g.10gb": {"vram": 10, "slices": 1},
        "2g.20gb": {"vram": 20, "slices": 2},
        "3g.40gb": {"vram": 40, "slices": 3},
        "7g.80gb": {"vram": 80, "slices": 7}
    }

    def __init__(self, physical_gpu_model: str = "A100-SXM4-80GB"):
        self.gpu_model = physical_gpu_model
        self.active_slices: List[MIGInstance] = []

    def partition_gpu(self, profile_name: str) -> MIGInstance:
        """Partitions physical GPU into specified MIG slice profile."""
        if profile_name not in self.PROFILES:
            raise ValueError(f"Invalid MIG profile '{profile_name}'. Choose from {list(self.PROFILES.keys())}")

        spec = self.PROFILES[profile_name]
        instance = MIGInstance(
            mig_profile=profile_name,
            vram_gb=spec["vram"],
            compute_slices=spec["slices"],
            is_allocated=True
        )
        self.active_slices.append(instance)
        return instance
