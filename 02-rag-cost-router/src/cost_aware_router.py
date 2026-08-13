"""
Token & Context-Cost-Aware Dynamic Model Router.
Analyzes query intent, token complexity, and context window requirements to route queries
between fast local models (Ollama llama3.2/qwen2.5) and frontier API models, tracking cost ($) per query.
"""

from enum import Enum
import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ModelTier(str, Enum):
    LOCAL_OLLAMA = "LOCAL_OLLAMA"        # $0.00 / 1M tokens (e.g. llama3.2:1b, qwen2.5:3b)
    SMALL_FRONTIER = "SMALL_FRONTIER"    # $0.15 / 1M input tokens (e.g. gpt-4o-mini, claude-3-haiku)
    LARGE_FRONTIER = "LARGE_FRONTIER"    # $5.00 / 1M input tokens (e.g. gpt-4o, claude-3.5-sonnet)


class RoutingDecision(BaseModel):
    query: str
    tier: ModelTier
    assigned_model: str
    intent_category: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    routing_reason: str
    context_length_chars: int


class CostAwareRouter:
    # Model Pricing Per 1M Tokens (Input, Output)
    PRICING_CATALOG = {
        ModelTier.LOCAL_OLLAMA: {"input": 0.00, "output": 0.00, "default_model": "ollama/llama3.2:1b"},
        ModelTier.SMALL_FRONTIER: {"input": 0.15, "output": 0.60, "default_model": "gpt-4o-mini"},
        ModelTier.LARGE_FRONTIER: {"input": 5.00, "output": 15.00, "default_model": "gpt-4o"}
    }

    def __init__(self, max_local_context_tokens: int = 2048):
        self.max_local_context_tokens = max_local_context_tokens

    @staticmethod
    def estimate_token_count(text: str) -> int:
        """Rough token estimation (approx 4 chars per token)."""
        return max(1, len(text) // 4)

    def classify_intent(self, query: str) -> str:
        """Classifies query intent into factual lookup vs complex reasoning."""
        q_lower = query.lower()

        complex_keywords = [
            "compare", "analyze", "tradeoff", "trade-off", "architecture", 
            "explain why", "evaluate", "synthesize", "root cause", "design"
        ]
        
        for kw in complex_keywords:
            if kw in q_lower:
                return "ANALYTICAL_REASONING"

        if len(query.split()) > 25:
            return "COMPLEX_LONG_FORM"

        return "SIMPLE_FACTUAL_LOOKUP"

    def route_query(
        self, 
        query: str, 
        retrieved_context: str = "",
        force_tier: Optional[ModelTier] = None
    ) -> RoutingDecision:
        """
        Calculates token length and classifies intent to make an optimal routing decision.
        """
        intent = self.classify_intent(query)
        prompt_tokens = self.estimate_token_count(query)
        context_tokens = self.estimate_token_count(retrieved_context)
        total_input_tokens = prompt_tokens + context_tokens
        
        # Estimate expected output tokens based on intent
        output_tokens = 500 if intent == "ANALYTICAL_REASONING" else 150

        if force_tier:
            tier = force_tier
            reason = f"Forced override to {force_tier.value}."
        elif intent == "SIMPLE_FACTUAL_LOOKUP" and total_input_tokens <= self.max_local_context_tokens:
            tier = ModelTier.LOCAL_OLLAMA
            reason = "Simple factual query with small context; routed to zero-cost local Ollama model."
        elif intent == "ANALYTICAL_REASONING" or total_input_tokens > 4000:
            tier = ModelTier.LARGE_FRONTIER
            reason = "Complex analytical reasoning or high context window required; routed to Large Frontier model."
        else:
            tier = ModelTier.SMALL_FRONTIER
            reason = "Moderate complexity query; routed to Small Frontier API for optimal cost-quality balance."

        pricing = self.PRICING_CATALOG[tier]
        cost_in = (total_input_tokens / 1_000_000) * pricing["input"]
        cost_out = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = round(cost_in + cost_out, 6)

        return RoutingDecision(
            query=query,
            tier=tier,
            assigned_model=pricing["default_model"],
            intent_category=intent,
            estimated_input_tokens=total_input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_cost_usd=total_cost,
            routing_reason=reason,
            context_length_chars=len(retrieved_context)
        )
