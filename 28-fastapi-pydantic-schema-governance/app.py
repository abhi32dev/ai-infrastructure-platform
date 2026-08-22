"""
FastAPI Schema Governance Service.
Enforces Pydantic v2 strict type validation and OpenAPI 3.1 contracts.
"""
from fastapi import FastAPI, HTTPException, status, Body
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.schemas import (
    PolymorphicEdgePayload,
    IngestionBatchRequest,
    IngestionBatchResponse,
    GoogleSASTelemetryPayload,
    NokiaTelemetryPayload,
    SamsungTelemetryPayload
)

app = FastAPI(
    title="Comcast CONDOR Schema Governance Service",
    version="2.0.0",
    description="Strict Pydantic v2 schema governance, polymorphic discriminated unions, and high-concurrency microservice APIs on ECS/Fargate."
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "error_type": "SchemaValidationError",
            "detail": [
                {
                    "loc": err["loc"],
                    "msg": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        })
    )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "engine": "FastAPI + Pydantic v2",
        "pydantic_mode": "strict",
        "supported_vendors": ["GOOGLE_SAS", "NOKIA", "SAMSUNG"]
    }

@app.post("/api/v1/telemetry/ingest-single", status_code=status.HTTP_200_OK)
async def ingest_single_telemetry(payload: PolymorphicEdgePayload = Body(..., discriminator="vendor_type")):
    """
    Polymorphic endpoint: Automatically discriminates Google SAS, Nokia, and Samsung payloads using Pydantic v2.
    """
    return {
        "status": "accepted",
        "vendor": payload.vendor_type,
        "event_id": payload.event_id,
        "node_id": payload.node_id
    }

@app.post("/api/v1/telemetry/ingest-batch", response_model=IngestionBatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_batch_telemetry(batch: IngestionBatchRequest):
    """
    Batch ingestion endpoint validating batch-level invariants and deduplication tokens.
    """
    return IngestionBatchResponse(
        batch_id=batch.batch_id,
        processed_count=len(batch.items),
        status="ACCEPTED"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
