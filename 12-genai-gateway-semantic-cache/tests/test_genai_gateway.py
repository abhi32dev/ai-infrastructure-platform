"""
Expanded Test Suite for Project 12 - GenAI Gateway, Semantic Cache & Rate Limiter.
Tests Vector Semantic Caching (< 5ms hits), Token Bucket TPM rate limiting, multi-provider fallback cascades,
and API cost governance.
"""

import pytest
from src.semantic_cache import SemanticCacheManager
from src.rate_limiter import TokenBucketRateLimiter
from src.fallback_router import GatewayRequest, GenAIFallbackRouter
from src.gateway_orchestrator import GenAIGatewayOrchestrator


@pytest.fixture
def cache():
    return SemanticCacheManager(similarity_threshold=0.8)


@pytest.fixture
def limiter():
    return TokenBucketRateLimiter(default_tpm_limit=100, refill_rate_per_sec=10.0)


@pytest.fixture
def router():
    return GenAIFallbackRouter()


@pytest.fixture
def gateway():
    return GenAIGatewayOrchestrator(default_tpm_limit=50000)


def test_01_semantic_cache_miss_and_put(cache):
    """Test 1: Verifies initial cache miss and subsequent entry insertion."""
    assert cache.lookup_semantic_cache("What is PagedAttention?") is None
    cache.put_cache_entry("What is PagedAttention?", "PagedAttention allocates GPU memory in blocks.", "gpt-4o", 50)
    
    hit = cache.lookup_semantic_cache("What is PagedAttention?")
    assert hit["cache_hit"] is True
    assert hit["latency_ms"] < 5.0


def test_02_semantic_cache_similarity_matching(cache):
    """Test 2: Verifies semantically similar query matching threshold."""
    cache.put_cache_entry("Explain PyTorch FSDP ZeRO-3 sharding", "FSDP shards weights and grads.", "gpt-4o", 60)
    hit = cache.lookup_semantic_cache("Explain PyTorch FSDP ZeRO-3 sharding pipeline")
    assert hit is not None
    assert hit["similarity_score"] >= 0.80


def test_03_token_bucket_rate_limiter_consume(limiter):
    """Test 3: Verifies token consumption from bucket."""
    status = limiter.consume_tokens(client_id="client-101", requested_tokens=50)
    assert status.is_allowed is True
    assert status.tokens_remaining == 50.0


def test_04_token_bucket_rate_limiter_exceeded(limiter):
    """Test 4: Verifies rate limiter blocking requests exceeding bucket capacity."""
    limiter.consume_tokens("client-exceeded", 90)
    status = limiter.consume_tokens("client-exceeded", 50)  # Exceeds remaining 10!
    assert status.is_allowed is False
    assert status.retry_after_sec > 0.0


def test_05_fallback_router_primary_success(router):
    """Test 5: Verifies primary provider (OpenAI) routing when online."""
    req = GatewayRequest(client_id="client-1", prompt="Hello LLM")
    res = router.dispatch_with_fallback(req, simulate_primary_down=False)
    assert res.successful_provider == "OpenAI"
    assert res.attempts_made == ["OpenAI"]


def test_06_fallback_router_secondary_fallback(router):
    """Test 6: Verifies fallback to Anthropic when primary OpenAI provider fails."""
    req = GatewayRequest(client_id="client-1", prompt="Hello LLM")
    res = router.dispatch_with_fallback(req, simulate_primary_down=True)
    assert res.successful_provider == "Anthropic"
    assert res.attempts_made == ["OpenAI", "Anthropic"]


def test_07_gateway_orchestrator_end_to_end(gateway):
    """Test 7: Verifies end-to-end Gateway request processing and cache populate."""
    res1 = gateway.process_request(client_id="tenant-A", prompt="How does Ray cluster autoscaler work?")
    assert res1["status"] == "SUCCESS"
    assert res1["provider"] == "OpenAI"

    # Second identical query should be a CACHE_HIT
    res2 = gateway.process_request(client_id="tenant-A", prompt="How does Ray cluster autoscaler work?")
    assert res2["status"] == "CACHE_HIT"
    assert res2["cost_usd"] == 0.0


def test_08_gateway_rate_limit_blocking(gateway):
    """Test 8: Verifies gateway blocking when tenant rate limit is exceeded."""
    res = gateway.process_request(client_id="tenant-over-limit", prompt="Query", max_tokens=90000)
    assert res["status"] == "RATE_LIMITED"
