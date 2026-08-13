"""
SFT Dataset Curation & Token Alignment Engine.
Validates instruction-tuning datasets, calculates token length distributions,
filters sequence length outliers, and formats datasets for Supervised Fine-Tuning (SFT).
"""

from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field


class SFTDatasetSample(BaseModel):
    instruction: str
    input_context: str = ""
    output_response: str
    estimated_token_length: int = 0


class DatasetCurator:
    def __init__(self, max_seq_length: int = 2048):
        self.max_seq_length = max_seq_length

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    def curate_dataset(
        self, 
        raw_samples: List[Dict[str, Any]], 
        val_ratio: float = 0.2
    ) -> Tuple[List[SFTDatasetSample], List[SFTDatasetSample], Dict[str, Any]]:
        """
        Validates, filters, and splits raw dataset samples into train and validation sets.
        """
        curated_samples: List[SFTDatasetSample] = []
        rejected_count = 0

        for raw in raw_samples:
            instruction = raw.get("instruction", "").strip()
            input_ctx = raw.get("input_context", "").strip()
            output = raw.get("output_response", "").strip()

            if not instruction or not output:
                rejected_count += 1
                continue

            full_text = f"{instruction} {input_ctx} {output}"
            token_len = self.estimate_tokens(full_text)

            if token_len > self.max_seq_length:
                rejected_count += 1  # Outlier sequence length
                continue

            curated_samples.append(SFTDatasetSample(
                instruction=instruction,
                input_context=input_ctx,
                output_response=output,
                estimated_token_length=token_len
            ))

        # Split into Train / Val
        num_val = max(1, int(len(curated_samples) * val_ratio))
        train_set = curated_samples[:-num_val] if num_val < len(curated_samples) else curated_samples
        val_set = curated_samples[-num_val:] if num_val < len(curated_samples) else []

        stats = {
            "total_raw": len(raw_samples),
            "curated_total": len(curated_samples),
            "train_samples": len(train_set),
            "val_samples": len(val_set),
            "rejected_outliers": rejected_count,
            "avg_tokens": round(sum(s.estimated_token_length for s in curated_samples) / len(curated_samples), 1) if curated_samples else 0
        }

        return train_set, val_set, stats
