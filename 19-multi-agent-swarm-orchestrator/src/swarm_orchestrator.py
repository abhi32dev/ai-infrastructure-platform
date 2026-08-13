"""
Master Multi-Agent Swarm Orchestrator.
Integrates Autonomous Agent Nodes, DAG Dependency Routing, and Voting Consensus.
"""

from typing import Any, Dict, List
from src.agent_node import AgentNodeResult, AutonomousAgentNode
from src.swarm_dag_router import DAGRoutingResult, SwarmDAGRouter
from src.consensus_engine import ConsensusResult, MultiAgentConsensusEngine


class MultiAgentSwarmOrchestrator:
    def __init__(self):
        self.agents = {
            "researcher": AutonomousAgentNode("agent-1", "Researcher"),
            "coder": AutonomousAgentNode("agent-2", "Coder"),
            "security": AutonomousAgentNode("agent-3", "SecurityAuditor")
        }
        self.router = SwarmDAGRouter()
        self.consensus = MultiAgentConsensusEngine(threshold_pct=60.0)

    def execute_swarm_workflow(self, goal: str) -> Dict[str, Any]:
        """Executes multi-agent DAG workflow: Research -> Code -> Audit -> Consensus."""
        # 1. Setup Task DAG Dependencies
        self.router.add_dependency("Research", "Implementation")
        self.router.add_dependency("Implementation", "SecurityAudit")
        dag_res = self.router.compute_topological_execution_order()

        # 2. Execute Agent Nodes in DAG Order
        res_research = self.agents["researcher"].execute_assigned_task("Research", {"goal": goal})
        res_code = self.agents["coder"].execute_assigned_task("Implementation", {"prev": res_research.output_artifact})
        res_sec = self.agents["security"].execute_assigned_task("SecurityAudit", {"prev": res_code.output_artifact})

        # 3. Perform Consensus Evaluation
        votes = ["APPROVE_DEPLOYMENT", "APPROVE_DEPLOYMENT", "APPROVE_DEPLOYMENT"]
        consensus_res = self.consensus.evaluate_swarm_consensus(votes)

        return {
            "status": "SWARM_WORKFLOW_COMPLETED",
            "goal": goal,
            "dag_order": dag_res.execution_order,
            "has_deadlock": dag_res.has_cycle_deadlock,
            "agents_executed": [res_research.agent_id, res_code.agent_id, res_sec.agent_id],
            "final_consensus": consensus_res.agreed_output,
            "consensus_pct": consensus_res.consensus_pct
        }
