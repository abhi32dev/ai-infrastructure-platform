# Project 11: Distributed Training Engine (PyTorch FSDP & Megatron 3D Parallelism)

High-performance multi-node multi-GPU training platform supporting **PyTorch FSDP ZeRO-3** memory sharding, **Megatron-LM 3D Parallelism Grid** ($TP \times PP \times DP$), and **NCCL Collective Communication Profiling**.

---

## 🛠️ Architecture Components
- **FSDP Sharder**: Shards model weights, gradients, and Adam optimizer states (16 GB/billion params $\rightarrow$ sharded by GPU count).
- **Megatron 3D Grid**: Dynamically computes Tensor Parallelism ($TP$), Pipeline Parallelism ($PP$), and Data Parallelism ($DP$) rank maps.
- **NCCL Communicator**: Profiles NVLink intra-node and InfiniBand 400G inter-node All-Reduce bus bandwidth saturation.

---

## 🚦 Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest tests/
python demo_runner.py
```
