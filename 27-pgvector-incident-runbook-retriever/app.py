"""
FastAPI Microservice for PGVector Incident Runbook Retriever.
"""
from fastapi import FastAPI, HTTPException, status
from src.models import RunbookEntry, SearchQuery, HybridSearchResponse
from src.pgvector_engine import PGVectorRunbookRetriever

app = FastAPI(
    title="PGVector Incident Runbook Retriever",
    version="1.0.0",
    description="Sub-millisecond hybrid vector + keyword search over incident post-mortems on Amazon RDS PostgreSQL (pgvector)."
)

retriever = PGVectorRunbookRetriever()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "engine": "PGVector-PostgreSQL-RDS",
        "index_type": "HNSW",
        "total_runbooks": len(retriever.runbooks)
    }

@app.post("/api/v1/runbooks/hybrid-search", response_model=HybridSearchResponse, status_code=status.HTTP_200_OK)
async def hybrid_search_runbooks(query: SearchQuery):
    """
    Executes hybrid dense vector (HNSW cosine) + sparse keyword search with metadata filtering.
    """
    try:
        response = retriever.hybrid_search(
            query=query.query_text,
            vendor=query.vendor,
            severity=query.severity,
            top_k=query.top_k,
            alpha=query.alpha
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/v1/runbooks/upsert", status_code=status.HTTP_201_CREATED)
async def upsert_runbook(runbook: RunbookEntry):
    """
    Upserts a runbook entry and updates the HNSW vector embedding index.
    """
    try:
        retriever.upsert_runbook(runbook)
        return {"status": "upserted", "runbook_id": runbook.runbook_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upsert failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
