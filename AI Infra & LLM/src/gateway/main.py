import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from src.gateway.schemas import CandidateEvaluationRequest, CandidateEvaluation, CoverLetterRequest
from src.gateway.grammar import SchemaEnforcer
from src.gateway.tracer import performance_tracer
from src.retrieval.pipeline import RetrievalPipeline
from src.serving.client import LLMClient
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("gateway_main")

app = FastAPI(
    title="Nexus AI Infrastructure Gateway",
    description="Enterprise structured gateway and telemetry server.",
    version="1.0.0"
)

# Shared platform instances
pipeline = RetrievalPipeline()
client = LLMClient()

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI Gateway microservice successfully launched.")

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": settings.serving_engine}

@app.post("/v1/candidate/evaluate", response_model=CandidateEvaluation)
async def evaluate_candidate(req: CandidateEvaluationRequest):
    """
    Ingests resume data, queries the two-stage RAG retrieval pipeline,
    and returns a strictly enforced Pydantic structured output evaluation.
    """
    start_time = time.perf_counter()
    logger.info(f"Evaluating candidate ID: {req.candidate_id}")

    try:
        # Step 1: Ingest candidate resume into vector store
        pipeline.ingest_candidate_data(req.candidate_id, req.resume_text)
        
        # Step 2: Build compressed retrieval context
        context = pipeline.build_compressed_context(req.job_description, req.candidate_id)
        
        # Step 3: Call serving client using structural parameters
        prompt = (
            f"Resume Excerpts:\n{context}\n\n"
            f"Job Description:\n{req.job_description}\n\n"
            "Format the output strictly as a JSON object containing the fields:\n"
            "- candidate_id (string)\n"
            "- fit_score (float between 0.0 and 1.0)\n"
            "- key_strengths (list of strings)\n"
            "- growth_areas (list of strings)\n"
            "- source_citations (list of strings citing achievements)\n"
            "- confidence_score (float between 0.0 and 1.0)\n"
        )
        
        system_prompt = "You are an expert Candidate Evaluation Agent. Produce valid JSON conformant to the requested fields."

        response_chunks = []
        async for chunk in client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True
        ):
            content = chunk.get("content", "")
            if content:
                response_chunks.append(content)

        full_response = "".join(response_chunks)
        
        # Step 4: Schema enforcement & validation
        evaluation = SchemaEnforcer.enforce(full_response, CandidateEvaluation)
        
        # Override ID to match query to avoid misalignment
        evaluation.candidate_id = req.candidate_id

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Step 5: Telemetry Trace reporting
        performance_tracer.trace_span(
            name="candidate_evaluation",
            input_data={"candidate_id": req.candidate_id},
            output_data=evaluation.model_dump(),
            latency_ms=duration_ms,
            token_count=len(full_response.split()),
            model=settings.serving_model
        )

        return evaluation

    except Exception as e:
        logger.error(f"Failed to evaluate candidate {req.candidate_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/candidate/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest):
    """
    Streams a tailored markdown cover letter based on resume context.
    """
    logger.info(f"Generating cover letter for candidate {req.candidate_name}")

    async def event_generator():
        prompt = (
            f"Job Requirements:\n{req.job_description}\n\n"
            f"Candidate Accomplishments:\n{req.resume_context}\n\n"
            f"Generate a customized cover letter for candidate {req.candidate_name} "
            f"applying to the role of {req.job_title} at {req.company_name}."
        )
        
        async for chunk in client.generate_stream(
            prompt=prompt,
            system_prompt="You are an expert executive cover letter writer."
        ):
            content = chunk.get("content", "")
            if content:
                yield content

    return StreamingResponse(event_generator(), media_type="text/plain")
