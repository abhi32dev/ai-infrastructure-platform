"""
Master Enterprise GenAI API Gateway Orchestrator.
Integrates Vector Semantic Caching, Token Bucket Rate Limiting, and Multi-Provider Fallback Routing.
"""

from typing import Any, Dict
from src.semantic_cache import SemanticCacheManager
from src.rate_limiter import TokenBucketRateLimiter, TokenBucketStatus
from src.fallback_router import FallbackRouteResult, GatewayRequest, GenAIFallbackRouter


class GenAIGatewayOrchestrator:
    def __init__(self, default_tpm_limit: int = 50000):
        self.cache = SemanticCacheManager(similarity_threshold=0.85)
        self.limiter = TokenBucketRateLimiter(default_tpm_limit=default_tpm_limit)
        self.router = GenAIFallbackRouter()

    def process_request(self, client_id: str, prompt: str, max_tokens: int = 100, force_primary_fail: bool = False) -> Dict[str, Any]:
        """Processes request through Rate Limiter -> Semantic Cache -> Provider Fallback Cascade."""
        # Step 1: Rate Limiter Check
        limiter_status = self.limiter.consume_tokens(client_id, max_tokens)
        if not limiter_status.is_allowed:
            return {
                "status": "RATE_LIMITED",
                "client_id": client_id,
                "retry_after_sec": limiter_status.retry_after_sec,
                "message": "Token bucket rate limit exceeded"
            }

        # Step 2: Semantic Cache Lookup
        cache_hit = self.cache.lookup_semantic_cache(prompt)
        if cache_hit:
            return {
                "status": "CACHE_HIT",
                "provider": "Semantic_Cache_Layer",
                "similarity_score": cache_hit["similarity_score"],
                "content": cache_hit["response"],
                "latency_ms": cache_hit["latency_ms"],
                "cost_usd": 0.0
            }

        # Step 3: Multi-Provider Fallback Cascade
        req = GatewayRequest(client_id=client_id, prompt=prompt, max_tokens=max_tokens)
        route_res = self.router.dispatch_with_fallback(req, simulate_primary_down=force_primary_fail)

        # Store response in Semantic Cache for future hits
        self.cache.put_cache_entry(prompt, route_res.content, route_res.model_name, max_tokens)

        return {
            "status": "SUCCESS",
            "provider": route_res.successful_provider,
            "model_name": route_res.model_name,
            "attempts_made": route_res.attempts_made,
            "content": route_res.content,
            "latency_ms": route_res.latency_ms,
            "cost_usd": route_res.cost_usd
        }
