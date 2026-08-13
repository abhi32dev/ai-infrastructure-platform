"""
Multi-Agent Voting Consensus & Verification Engine.
Aggregates outputs from multiple agent nodes, performing majority voting and threshold verification.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ConsensusResult(BaseModel):
    agreed_output: str
    consensus_pct: float
    total_votes: int
    is_consensus_reached: bool


class MultiAgentConsensusEngine:
    def __init__(self, threshold_pct: float = 60.0):
        self.threshold = threshold_pct

    def evaluate_swarm_consensus(self, agent_votes: List[str]) -> ConsensusResult:
        """Evaluates majority vote among swarm agent outputs."""
        if not agent_votes:
            return ConsensusResult(agreed_output="", consensus_pct=0.0, total_votes=0, is_consensus_reached=False)

        counts: Dict[str, int] = {}
        for vote in agent_votes:
            counts[vote] = counts.get(vote, 0) + 1

        top_vote = max(counts, key=counts.get)
        top_count = counts[top_vote]
        pct = round((top_count / float(len(agent_votes))) * 100.0, 2)

        return ConsensusResult(
            agreed_output=top_vote,
            consensus_pct=pct,
            total_votes=len(agent_votes),
            is_consensus_reached=pct >= self.threshold
        )
