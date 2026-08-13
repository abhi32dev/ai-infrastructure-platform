"""
CLI Demo Runner for Project 19 - Multi-Agent Swarm Orchestrator.
"""

from src.swarm_orchestrator import MultiAgentSwarmOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 19: Multi-Agent Swarm Orchestrator & DAG Execution Mesh")
    print("==================================================================")
    orch = MultiAgentSwarmOrchestrator()
    res = orch.execute_swarm_workflow("Deploy Autonomous Multi-Agent AI Infrastructure")
    print(f"Status: {res['status']} | Goal: {res['goal']}")
    print(f"DAG Execution Order: {res['dag_order']} (Deadlock: {res['has_deadlock']})")
    print(f"Agents Executed: {res['agents_executed']}")
    print(f"Swarm Consensus: {res['final_consensus']} ({res['consensus_pct']}% agreement)")
    print("==================================================================")
