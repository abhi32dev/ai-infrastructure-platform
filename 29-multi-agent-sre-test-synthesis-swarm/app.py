"""
FastAPI Microservice for Multi-Agent SRE & Test Synthesis Swarm.
"""
from fastapi import FastAPI, HTTPException, status
from src.agents import MicroserviceSpec, SwarmReport
from src.swarm_orchestrator import SRESwarmOrchestrator

app = FastAPI(
    title="Multi-Agent SRE & Developer Velocity Swarm",
    version="1.0.0",
    description="Autonomous 4-agent swarm for automated OpenAPI analysis, Pytest matrix synthesis, IAM security audits, and release certification."
)

swarm = SRESwarmOrchestrator()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "swarm_engine": "Multi-Agent SRE Swarm",
        "active_agents": ["SpecAnalyst", "PytestSynthesis", "SecurityChaos", "QualityGatekeeper"]
    }

@app.post("/api/v1/swarm/synthesize-suite", response_model=SwarmReport, status_code=status.HTTP_200_OK)
async def synthesize_suite(spec: MicroserviceSpec):
    """
    Executes the 4-agent swarm to analyze microservice schemas, generate Pytest suites, and audit IAM security.
    """
    try:
        report = swarm.process_spec(spec)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Swarm orchestration failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
