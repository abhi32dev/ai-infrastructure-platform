"""
CLI Demo Runner for Project 12 - GenAI Gateway, Semantic Cache & Rate Limiter.
"""

from src.gateway_orchestrator import GenAIGatewayOrchestrator

if __name__ == "__main__":
    print("==================================================================")
    print("🚀 Project 12: GenAI API Gateway, Semantic Cache & Rate Limiter")
    print("==================================================================")
    gw = GenAIGatewayOrchestrator(default_tpm_limit=50000)
    
    # Request 1: Fresh prompt -> Routes to OpenAI
    res1 = gw.process_request(client_id="tenant-A", prompt="Explain GPU Memory Bandwidth Roofline model")
    print(f"Req 1 Status: {res1['status']} | Provider: {res1['provider']} | Latency: {res1['latency_ms']} ms")

    # Request 2: Duplicate prompt -> Semantic Cache Hit!
    res2 = gw.process_request(client_id="tenant-A", prompt="Explain GPU Memory Bandwidth Roofline model")
    print(f"Req 2 Status: {res2['status']} | Provider: {res2['provider']} | Cost: ${res2['cost_usd']}")
    print("==================================================================")
