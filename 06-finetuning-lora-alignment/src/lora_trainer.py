"""
LoRA Parameter-Efficient Fine-Tuning (PEFT) Simulator.
Simulates low-rank adaptation matrix injection (W = W0 + (alpha/r)*B*A) into attention projections,
tracking training loss, perplexity convergence, and GPU parameter memory optimization.
"""

import math
import time
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class LoRAConfig(BaseModel):
    r: int = 8               # LoRA rank dimension
    lora_alpha: int = 16     # Scaling factor alpha
    target_modules: List[str] = Field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout: float = 0.05
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 4


class TrainingStepMetric(BaseModel):
    epoch: int
    step: int
    training_loss: float
    validation_loss: float
    perplexity: float
    elapsed_sec: float


class LoRATrainer:
    def __init__(self, config: LoRAConfig = LoRAConfig()):
        self.config = config

    def train_lora_adapter(
        self, 
        train_samples_count: int, 
        val_samples_count: int
    ) -> Dict[str, Any]:
        """
        Simulates LoRA training loop over SFT dataset, logging loss and perplexity.
        """
        start_time = time.time()
        scaling_factor = self.config.lora_alpha / self.config.r
        
        # Calculate trainable parameter reduction %
        base_params = 7_000_000_000  # 7B base model
        trainable_lora_params = 4_194_304  # ~4.2M params for rank r=8
        param_reduction_pct = round((1 - (trainable_lora_params / base_params)) * 100.0, 4)

        metrics_history: List[TrainingStepMetric] = []
        current_loss = 2.45

        total_steps = math.ceil(train_samples_count / self.config.batch_size) * self.config.num_epochs

        step_counter = 0
        for epoch in range(1, self.config.num_epochs + 1):
            steps_in_epoch = math.ceil(train_samples_count / self.config.batch_size)
            for step in range(1, steps_in_epoch + 1):
                step_counter += 1
                # Loss convergence decay formula
                decay = math.exp(-0.4 * (step_counter / total_steps * 5.0))
                current_loss = round(0.45 + (1.95 * decay), 4)
                val_loss = round(current_loss + 0.08, 4)
                perplexity = round(math.exp(val_loss), 2)

                metrics_history.append(TrainingStepMetric(
                    epoch=epoch,
                    step=step_counter,
                    training_loss=current_loss,
                    validation_loss=val_loss,
                    perplexity=perplexity,
                    elapsed_sec=round(time.time() - start_time, 2)
                ))

        return {
            "status": "COMPLETED",
            "lora_config": self.config.dict(),
            "scaling_factor": scaling_factor,
            "base_model_params": base_params,
            "trainable_lora_params": trainable_lora_params,
            "param_reduction_pct": param_reduction_pct,
            "final_training_loss": current_loss,
            "final_perplexity": round(math.exp(current_loss), 2),
            "total_epochs": self.config.num_epochs,
            "total_steps": total_steps,
            "metrics_history": [m.dict() for m in metrics_history]
        }
