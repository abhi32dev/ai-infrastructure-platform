# 🎤 Staff AI Platform Interview Guide: GenAI Gateway & Redis Semantic Cache

This guide bridges **Project 12 (`12-genai-gateway-semantic-cache`)** to Staff/Principal-level questions on enterprise API gateways and rate limiting.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you implement distributed token-bucket rate limiters in Redis?"
> **Staff Engineer Answer**:
> "In `src/gateway_proxy.py`, we execute atomic Redis Lua scripts computing token replenishment based on timestamp deltas, enforcing per-API-key requests-per-minute (RPM) quotas."

### Q2: "How does multi-provider failover cascade prevent customer-facing outages?"
> **Staff Engineer Answer**:
> "If primary provider OpenAI returns 5xx errors or timeouts, the gateway automatically cascades to Anthropic Claude 3.5 Sonnet, and then to local Ollama instances."

### Q3: "How does semantic vector caching reduce downstream API billing?"
> **Staff Engineer Answer**:
> "Prompts with cosine similarity $\ge 0.92$ return cached completions from ChromaDB in $<5\text{ms}$ at $\$0$ cost."
