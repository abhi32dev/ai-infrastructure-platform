"""
FastAPI Production Microservice for AWS Bedrock RAG Telemetry Triage
and Multi-Agent Developer Velocity Swarm.
"""
from fastapi import FastAPI, HTTPException, status
from src.models import TelemetryTrapPayload, TriageDiagnosis, AgenticReviewTask
from src.bedrock_client import BedrockTriageEngine
from src.multi_agent_orchestrator import MultiAgentVelocitySwarm

app = FastAPI(
    title="Comcast CONDOR AI Telemetry Triage & Agentic Engine",
    version="3.3.0",
    description="High-scale edge telemetry classification, AWS Bedrock RAG runbook triage, and multi-agent test synthesis."
)

triage_engine = BedrockTriageEngine()
agent_swarm = MultiAgentVelocitySwarm()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "platform": "CONDOR-Edge-AI",
        "bedrock_model": triage_engine.model_id,
        "vector_retriever": "PGVector-RDS-Postgres"
    }

@app.post("/api/v1/triage/telemetry", response_model=TriageDiagnosis, status_code=status.HTTP_200_OK)
async def triage_edge_telemetry(payload: TelemetryTrapPayload):
    """
    Ingests raw edge SNMP/UDP or REST telemetry, retrieves matching runbooks from PGVector,
    and returns a structured root-cause diagnosis via AWS Bedrock (Claude 3.5 Sonnet).
    """
    try:
        diagnosis = triage_engine.triage_alarm(payload)
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage pipeline failure: {str(e)}")

@app.post("/api/v1/agentic/synthesize-tests", status_code=status.HTTP_200_OK)
async def synthesize_endpoint_tests(task: AgenticReviewTask):
    """
    Multi-Agent orchestration endpoint for automated Pytest synthesis and Pydantic validation.
    """
    result = agent_swarm.run_review_and_test_synthesis(task)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
