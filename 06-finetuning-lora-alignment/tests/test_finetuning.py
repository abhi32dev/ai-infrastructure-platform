"""
Expanded Test Suite for Project 6 - Fine-Tuning, LoRA & Dataset Alignment.
Tests SFT instruction dataset curation, token outlier filtering, LoRA PEFT rank matrix configuration (r=8, alpha=16),
parameter reduction calculations, loss convergence history logging, and GGUF quantization model weight export.
"""

import pytest
from src.dataset_curator import DatasetCurator
from src.lora_trainer import LoRAConfig, LoRATrainer
from src.model_exporter import ModelExporter


@pytest.fixture
def curator():
    return DatasetCurator(max_seq_length=100)


@pytest.fixture
def sample_raw_dataset():
    return [
        {"instruction": "Query node 108 status", "input_context": "Edge node 108", "output_response": "Node 108 memory normal."},
        {"instruction": "Restart socket daemon", "input_context": "UDP port 162", "output_response": "Socket restarted successfully."},
        {"instruction": "Clear alarm", "input_context": "Alarm CRITICAL", "output_response": "Alarm cleared."},
        {"instruction": "Long token outlier " * 50, "input_context": "Outlier", "output_response": "Reject this."}
    ]


def test_01_dataset_curation_outlier_rejection(curator, sample_raw_dataset):
    """Test 1: Verifies outlier token sequence length rejection."""
    train_set, val_set, stats = curator.curate_dataset(sample_raw_dataset)
    assert stats["total_raw"] == 4
    assert stats["rejected_outliers"] == 1
    assert stats["train_samples"] + stats["val_samples"] == 3


def test_02_train_val_split_proportions(curator, sample_raw_dataset):
    """Test 2: Verifies dataset train/validation split proportions."""
    train_set, val_set, _ = curator.curate_dataset(sample_raw_dataset, val_ratio=0.33)
    assert len(train_set) == 2
    assert len(val_set) == 1


def test_03_lora_rank_matrix_adapter_configuration():
    """Test 3: Verifies LoRA PEFT rank matrix adapter configuration parameters."""
    config = LoRAConfig(r=8, lora_alpha=16, lora_dropout=0.05, num_epochs=3)
    assert config.r == 8
    assert config.lora_alpha == 16
    assert "q_proj" in config.target_modules
    assert "v_proj" in config.target_modules


def test_04_parameter_reduction_calculation():
    """Test 4: Verifies 99.94% trainable parameter memory reduction calculation."""
    trainer = LoRATrainer(config=LoRAConfig(r=8, lora_alpha=16))
    res = trainer.train_lora_adapter(train_samples_count=10, val_samples_count=2)
    assert res["param_reduction_pct"] > 99.90
    assert res["trainable_lora_params"] == 4_194_304


def test_05_loss_convergence_logging_history():
    """Test 5: Verifies training loss decay and perplexity convergence history logging."""
    trainer = LoRATrainer(config=LoRAConfig(r=8, num_epochs=3))
    res = trainer.train_lora_adapter(train_samples_count=10, val_samples_count=2)
    metrics = res["metrics_history"]
    assert len(metrics) >= 3
    assert metrics[0]["training_loss"] > metrics[-1]["training_loss"]  # Loss decreased across epochs!


def test_06_model_exporter_gguf_quantization_format():
    """Test 6: Verifies GGUF Q4_K_M quantization format export compilation."""
    exporter = ModelExporter()
    export_res = exporter.merge_and_export_gguf(
        base_model_id="meta-llama/Llama-3.2-3B-Instruct",
        adapter_path="data/adapters/lora_config.json",
        quantization_type="Q4_K_M"
    )
    assert export_res["quantization_format"] == "Q4_K_M"
    assert export_res["export_file_path"].endswith(".gguf")


def test_07_empty_dataset_handling(curator):
    """Test 7: Verifies dataset curator handling empty inputs safely without crashing."""
    train_set, val_set, stats = curator.curate_dataset([])
    assert stats["total_raw"] == 0
    assert len(train_set) == 0


def test_08_tokenizer_max_length_truncation(curator):
    """Test 8: Verifies token truncation bounds on maximum sequence length."""
    long_raw = [{"instruction": "Word " * 200, "input_context": "Context", "output_response": "Ans"}]
    _, _, stats = curator.curate_dataset(long_raw)
    assert stats["rejected_outliers"] == 1
