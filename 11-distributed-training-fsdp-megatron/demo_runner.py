"""
CLI Demo Runner for Project 11 - Distributed Training (PyTorch FSDP & Megatron).
"""

from src.training_orchestrator import DistributedTrainingOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 11: Distributed Training (PyTorch FSDP & Megatron-LM)")
    print("==================================================================")
    orch = DistributedTrainingOrchestrator(model_name="Llama-3.2-70B", num_nodes=2, gpus_per_node=8)
    res = orch.run_training_step(batch_size=16)
    print(f"Status: {res['status']}")
    print(f"Model: {res['model_name']}")
    print(f"World Size: {res['world_size']} GPUs")
    print(f"FSDP VRAM per GPU: {res['fsdp_vram_per_gpu_gb']} GB ({res['memory_savings_pct']}% savings)")
    print(f"Megatron 3D Grid: TP={res['3d_grid']['tp']}, PP={res['3d_grid']['pp']}, DP={res['3d_grid']['dp']}")
    print(f"NCCL Bus Bandwidth: {res['nccl_bus_bandwidth_gbps']} GB/s (Latency: {res['nccl_latency_us']} us)")
    print("==================================================================")
