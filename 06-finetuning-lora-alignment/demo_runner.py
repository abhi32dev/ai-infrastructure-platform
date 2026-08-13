"""
Interactive CLI Runner for Project 6 - Fine-Tuning, LoRA & Dataset Alignment.
Reads real instruction dataset from data/sft_instruction_dataset.json, curates tokens,
executes LoRA rank r=8, alpha=16 training pass, logs loss/perplexity to data/loss_convergence_log.json,
and merges LoRA weights into compiled GGUF model artifact.
"""

import json
import os
from src.dataset_curator import DatasetCurator
from src.lora_trainer import LoRAConfig, LoRATrainer
from src.model_exporter import ModelExporter


def run_demo():
    print("==========================================================================")
    print("🎛️ STARTING FINE-TUNING, LORA & DATASET ALIGNMENT DEMO")
    print("==========================================================================\n")

    # -------------------------------------------------------------------------
    # SCENARIO 1: Ingesting Real SFT Instruction Dataset from data/
    # -------------------------------------------------------------------------
    print("--- [SCENARIO 1] Reading Real SFT Instruction Dataset from data/ ---")
    dataset_path = "data/sft_instruction_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        raw_dataset = json.load(f)

    curator = DatasetCurator(max_seq_length=500)
    train_set, val_set, stats = curator.curate_dataset(raw_dataset)

    print(f"Dataset Curation Statistics:")
    print(f"  └─ Total Raw Samples:      {stats['total_raw']}")
    print(f"  └─ Curated Train Samples:  {stats['train_samples']}")
    print(f"  └─ Curated Val Samples:    {stats['val_samples']}")
    print(f"  └─ Rejected Outliers:      {stats['rejected_outliers']}")
    print(f"  └─ Average Token Length:   {stats['avg_tokens']} tokens")

    # -------------------------------------------------------------------------
    # SCENARIO 2 & 3: LoRA Fine-Tuning Pass & Loss Logging
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIOS 2 & 3] LoRA Fine-Tuning Pass (r=8, Alpha=16) & Loss Logging ---")
    trainer = LoRATrainer(config=LoRAConfig(r=8, lora_alpha=16, num_epochs=3))
    training_res = trainer.train_lora_adapter(train_samples_count=stats['train_samples'], val_samples_count=stats['val_samples'])

    # Save loss convergence log to data/
    os.makedirs("data", exist_ok=True)
    log_path = "data/loss_convergence_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(training_res, f, indent=2)
    print(f"Saved Training Loss Log to: '{log_path}'")

    print(f"\nLoRA Training Configuration:")
    print(f"  └─ Target Modules:        {training_res['lora_config']['target_modules']}")
    print(f"  └─ LoRA Rank (r):         {training_res['lora_config']['r']}")
    print(f"  └─ Alpha Scaling (alpha): {training_res['lora_config']['lora_alpha']}")
    print(f"  └─ Trainable Parameters:  {training_res['trainable_lora_params']:,} (vs {training_res['base_model_params']:,} base params)")
    print(f"  └─ Parameter Reduction:   {training_res['param_reduction_pct']}% reduction!")

    print("\nLoss Convergence History:")
    for step in training_res['metrics_history']:
        print(f"  └─ Epoch {step['epoch']} (Step {step['step']}): Train Loss = {step['training_loss']} | Val Loss = {step['validation_loss']} | Perplexity = {step['perplexity']}")

    # -------------------------------------------------------------------------
    # SCENARIO 4: LoRA Weight Merging & GGUF Export
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 4] LoRA Weight Merging & GGUF Quantization Export ---")
    exporter = ModelExporter()
    export_res = exporter.merge_and_export_gguf(
        base_model_id="meta-llama/Llama-3.2-3B-Instruct",
        adapter_path="data/adapters/lora_config.json",
        quantization_type="Q4_K_M"
    )

    print(f"Model Export Result:")
    print(f"  └─ Base Model:       {export_res['base_model']}")
    print(f"  └─ Merged Model:      {export_res['merged_model_name']}")
    print(f"  └─ Quantization:      {export_res['quantization_format']}")
    print(f"  └─ Export File:       {export_res['export_file_path']}")

    print("\n==========================================================================")
    print("✅ DEMO COMPLETED SUCCESSFULLY! ALL ARTIFACTS PERSISTED IN data/")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_demo()
