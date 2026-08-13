"""
Pairwise Human Preference Dataset Curator.
Structures $(prompt, y_w, y_l)$ tuples (chosen vs rejected completions) for Direct Preference Optimization (DPO).
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class PreferenceSample(BaseModel):
    sample_id: str
    prompt: str
    chosen_completion: str  # y_w
    rejected_completion: str  # y_l
    margin_score: float = 1.0


class PreferenceDatasetCurator:
    def __init__(self):
        self.samples: List[PreferenceSample] = []

    def add_preference(self, sample_id: str, prompt: str, chosen: str, rejected: str, margin: float = 1.0) -> PreferenceSample:
        sample = PreferenceSample(
            sample_id=sample_id,
            prompt=prompt,
            chosen_completion=chosen,
            rejected_completion=rejected,
            margin_score=margin
        )
        self.samples.append(sample)
        return sample

    def get_dataset_summary(self) -> Dict[str, Any]:
        return {
            "total_preference_pairs": len(self.samples),
            "avg_margin_score": round(sum(s.margin_score for s in self.samples) / max(1, len(self.samples)), 2),
            "is_ready_for_dpo": len(self.samples) >= 1
        }
