"""
FastAPI Application & Interactive Playground for Advanced RAG & Cost Router.
Provides REST endpoints for document ingestion, hybrid vector/BM25 retrieval,
cross-encoder reranking, and dynamic model routing with cost visualization.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
import json
import os
from typing import Any, Dict, List, Optional
import uvicorn

from src.document_loader import ChunkingStrategy
from src.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Advanced RAG, Hybrid Search & Cost-Aware Model Router",
    version="1.0.0",
    description="7-Stage RAG Pipeline with Hybrid BM25/Vector Search, Cross-Encoder Reranking, and Token Cost Routing."
)

pipeline = RAGPipeline()

# Automatically ingest sample docs on startup
sample_path = "data/sample_docs/enterprise_infra_spec.json"
if os.path.exists(sample_path):
    with open(sample_path, "r") as f:
        sample_docs = json.load(f)
        pipeline.ingest_documents(sample_docs, strategy=ChunkingStrategy.PARENT_CHILD)


@app.post("/ingest")
async def ingest_documents(payload: Dict[str, Any] = Body(...)):
    docs = payload.get("documents", [])
    strategy_str = payload.get("strategy", "PARENT_CHILD")
    strategy = ChunkingStrategy(strategy_str)
    num_chunks = pipeline.ingest_documents(docs, strategy=strategy)
    return {"status": "SUCCESS", "chunks_indexed": num_chunks, "strategy": strategy.value}


@app.post("/rag/query")
async def execute_rag_query(payload: Dict[str, Any] = Body(...)):
    query = payload.get("query", "Why was ALB selected over API Gateway for HTTP ingestion?")
    top_k = payload.get("top_k", 3)
    use_hyde = payload.get("use_hyde", True)
    use_reranker = payload.get("use_reranker", True)

    result = pipeline.execute_rag(
        user_query=query, 
        top_k=top_k, 
        use_hyde=use_hyde, 
        use_reranker=use_reranker
    )
    return result


@app.post("/router/evaluate")
async def evaluate_router(payload: Dict[str, Any] = Body(...)):
    query = payload.get("query", "Compare ALB and API Gateway cost profiles")
    context = payload.get("context", "")
    decision = pipeline.router.route_query(query, retrieved_context=context)
    return decision.dict()


@app.get("/", response_class=HTMLResponse)
async def serve_playground():
    """
    Embedded Single-Page Interactive Playground for RAG & Cost Router Visualization.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced RAG & Cost Router Playground</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0b0f19;
                --card: #151c2c;
                --accent: #38bdf8;
                --text: #f8fafc;
                --muted: #94a3b8;
                --border: #232d42;
                --success: #22c55e;
                --warning: #f59e0b;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
            .header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
            h1 { color: var(--accent); font-size: 1.5rem; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
            .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; }
            textarea, input, select { width: 100%; padding: 0.75rem; background: #090d16; border: 1px solid var(--border); color: #fff; border-radius: 6px; margin-bottom: 1rem; font-family: inherit; }
            .btn { background: var(--accent); color: #000; border: none; padding: 0.75rem 1.5rem; font-weight: 600; border-radius: 6px; cursor: pointer; width: 100%; }
            .btn:hover { opacity: 0.9; }
            .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
            .badge-LOCAL_OLLAMA { background: rgba(34, 197, 94, 0.2); color: var(--success); }
            .badge-SMALL_FRONTIER { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
            .badge-LARGE_FRONTIER { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
            pre { background: #070a10; padding: 1rem; border-radius: 6px; font-size: 0.85rem; color: #a5f3fc; overflow-x: auto; margin-top: 0.5rem; }
            .source-box { background: #0f172a; border-left: 3px solid var(--accent); padding: 0.75rem; margin-bottom: 0.75rem; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>🔍 Advanced 7-Stage RAG & Cost-Aware Model Router</h1>
                <div style="color:var(--muted); font-size:0.9rem;">Hybrid Vector/BM25 Search • Cross-Encoder Reranking • HyDE • Dynamic Model Cost Routing</div>
            </div>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <div class="card-title">💬 RAG & Router Query Tester</div>
                    <label>Enter Technical Query:</label>
                    <input type="text" id="queryInput" value="Why was ALB chosen over API Gateway for HTTP ingestion?">

                    <label>Retrieved Top-K Count:</label>
                    <select id="topKInput">
                        <option value="3" selected>Top 3 Reranked Context Chunks</option>
                        <option value="5">Top 5 Reranked Context Chunks</option>
                    </select>

                    <button class="btn" onclick="runRAG()">Execute 7-Stage RAG Pipeline</button>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">💰 Dynamic Model Router Decision</div>
                    <div id="routerOutput" style="color:var(--muted); font-size:0.9rem;">Submit query to evaluate token cost & routing decision...</div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title">📚 Retrieved Sources & Cross-Encoder Scores</div>
                    <div id="sourcesOutput" style="color:var(--muted); font-size:0.9rem;">No query executed yet.</div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">🤖 Generated Response & Assembled Context</div>
                    <div id="responseOutput" style="color:var(--muted); font-size:0.9rem;">Execution output will display here.</div>
                </div>
            </div>
        </div>

        <script>
            async function runRAG() {
                const query = document.getElementById('queryInput').value;
                const top_k = parseInt(document.getElementById('topKInput').value);

                const res = await fetch('/rag/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: query, top_k: top_k, use_hyde: true, use_reranker: true })
                });

                const data = await res.json();
                renderResults(data);
            }

            function renderResults(data) {
                // Router output
                const rd = data.routing_decision;
                document.getElementById('routerOutput').innerHTML = `
                    <div style="margin-bottom: 0.5rem;">
                        <strong>Assigned Model:</strong> ${rd.assigned_model} 
                        <span class="badge badge-${rd.tier}">${rd.tier}</span>
                    </div>
                    <div><strong>Intent Category:</strong> ${rd.intent_category}</div>
                    <div><strong>Est. Tokens:</strong> ${rd.estimated_input_tokens} Input / ${rd.estimated_output_tokens} Output</div>
                    <div><strong>Est. Query Cost:</strong> <span style="color:var(--success); font-weight:700;">$${rd.estimated_cost_usd}</span></div>
                    <div style="font-size:0.8rem; color:var(--muted); margin-top:0.5rem;"><em>${rd.routing_reason}</em></div>
                `;

                // Retrieved Sources
                const sources = data.retrieved_sources;
                document.getElementById('sourcesOutput').innerHTML = sources.map(s => `
                    <div class="source-box">
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.25rem;">
                            <strong>${s.doc_id}</strong>
                            <span style="color:var(--accent);">Rerank Score: ${s.rerank_score}</span>
                        </div>
                        <div style="font-size:0.8rem; color:var(--muted);">${s.text_snippet}</div>
                    </div>
                `).join('');

                // Generated response
                document.getElementById('responseOutput').innerHTML = `
                    <div style="font-weight:600; margin-bottom:0.5rem;">Generated Output:</div>
                    <div style="background:#090d16; padding:0.75rem; border-radius:6px; font-size:0.9rem;">${data.generated_response}</div>
                    <div style="font-weight:600; margin-top:1rem; margin-bottom:0.5rem;">Rewritten Search Query (HyDE):</div>
                    <div style="color:var(--muted); font-size:0.85rem;">${data.rewritten_query}</div>
                `;
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
