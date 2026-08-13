"""
CLI Demo Runner for Project 13 - RLHF & Direct Preference Optimization (DPO).
"""

from src.alignment_orchestrator import RLHFAlignmentOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 13: Direct Preference Optimization (DPO) & RLHF Alignment")
    print("==================================================================")
    orch = RLHFAlignmentOrchestrator(beta=0.1)
    res = orch.run_dpo_epoch()
    print(f"Status: {res['status']}")
    print(f"DPO Loss: {res['dpo_loss']} | Reward Margin: {res['reward_margin']}")
    print(f"Win Rate: {res['win_rate_pct']}% | Alignment Status: {res['alignment_status']}")
    print("==================================================================")
