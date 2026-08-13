# 🎛️ Project 6: Fine-Tuning, LoRA & Dataset Alignment Platform

A production-grade **Supervised Fine-Tuning (SFT) & LoRA Parameter-Efficient Fine-Tuning (PEFT)** platform implementing instruction dataset curation, sequence outlier filtering, low-rank matrix adapter injection ($r=8, \alpha=16$), loss convergence tracking, and GGUF model weight export compilation.

---

## 🎯 System Capabilities

- **SFT Dataset Curator**: Token length distribution filtering and instruction validation.
- **LoRA PEFT Simulator**: Low-rank matrix adaptation ($W = W_0 + \frac{\alpha}{r} B \cdot A$), reducing trainable parameters by **99.93%**.
- **Model Weight Merger & GGUF Exporter**: Merges adapter weights into base model checkpoints and compiles quantized GGUF artifacts (`Q4_K_M`).

---

## 📁 Repository Structure

```text
06-finetuning-lora-alignment/
├── src/
│   ├── dataset_curator.py    # SFT instruction dataset validation & outlier filtering
│   ├── lora_trainer.py       # LoRA rank matrix injection, parameter reduction, and loss tracking
│   └── model_exporter.py     # LoRA weight merger & GGUF quantization exporter
├── tests/
│   └── test_finetuning.py    # Pytest test suite for curator, trainer, and exporter
├── app.py                    # FastAPI REST server & embedded Fine-Tuning Dashboard
├── demo_runner.py            # Interactive CLI script running 4 fine-tuning scenarios
├── requirements.txt          # Project dependencies
├── README.md                 # System documentation
└── INTERVIEW_PREP.md         # Staff AI Infra Interview Guide
```

---

## 🚦 Quick Start & Interactive Demo

```bash
python3 demo_runner.py  # Runs CLI demo
pytest tests/           # Runs test suite
python3 app.py          # Launches Fine-Tuning Dashboard at http://127.0.0.1:8005
```
