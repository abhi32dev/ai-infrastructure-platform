"""
FastAPI REST Application & MLOps Dashboard for Model Serving & RecSys.
Provides endpoints for personalized recommendation A/B testing, SSE streaming tokens,
Prometheus metrics export, and real-time P95/P99 latency SLA monitoring.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse
from typing import Any, Dict, Optional
import uvicorn

from src.serving_orchestrator import ServingOrchestrator

app = FastAPI(
    title="Production Model Serving, RecSys & MLOps Observability Platform",
    version="1.0.0",
    description="High-throughput model serving proxy with SSE streaming, backpressure control, RecSys A/B testing, and OpenTelemetry/Prometheus metrics."
)

orchestrator = ServingOrchestrator()


@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, top_k: int = 5):
    res = orchestrator.get_user_recommendations(user_id, top_k=top_k)
    return res


@app.get("/stream")
async def stream_tokens(prompt: str = "Explain CONDOR high availability architecture"):
    async def event_generator():
        async for chunk in orchestrator.streaming_proxy.stream_tokens(prompt):
            yield chunk

    # Record metrics sample for demo
    orchestrator.record_simulated_inference(ttft_ms=120.5, tokens=17, duration_sec=0.51, cost=0.00015)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/metrics/snapshot")
async def get_metrics_snapshot():
    snapshot = orchestrator.get_platform_telemetry()
    return snapshot.dict()


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    return orchestrator.metrics.export_prometheus_metrics()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Embedded Single-Page Dashboard for RecSys A/B Testing & MLOps Observability.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Production Model Serving & MLOps Dashboard</title>
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
                --purple: #a855f7;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
            .header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
            h1 { color: var(--accent); font-size: 1.5rem; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
            .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; }
            input, button { width: 100%; padding: 0.75rem; background: #090d16; border: 1px solid var(--border); color: #fff; border-radius: 6px; margin-bottom: 1rem; font-family: inherit; }
            .btn { background: var(--accent); color: #000; font-weight: 600; border: none; cursor: pointer; }
            .btn:hover { opacity: 0.9; }
            .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
            .badge-VARIANT_ML_EMBEDDINGS { background: rgba(168, 85, 247, 0.2); color: var(--purple); }
            .badge-CONTROL_POPULARITY { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
            .metric-card { background: #090d16; padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 3px solid var(--accent); }
            .metric-val { font-size: 1.25rem; font-weight: 700; color: var(--success); }
            pre { background: #070a10; padding: 1rem; border-radius: 6px; font-size: 0.85rem; color: #a5f3fc; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>📊 Model Serving, RecSys & MLOps Observability Platform</h1>
                <div style="color:var(--muted); font-size:0.9rem;">Matrix Factorization RecSys • SSE Streaming • Backpressure Isolation • OpenTelemetry & Prometheus Metrics</div>
            </div>
            <button class="btn" style="width:auto; padding:0.5rem 1rem;" onclick="refreshMetrics()">🔄 Refresh MLOps Telemetry</button>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <div class="card-title">🎯 RecSys Personalized Recommendation Engine</div>
                    <label>Enter User ID (A/B Test Variant Assignment):</label>
                    <input type="text" id="userIdInput" value="user-1048">
                    <button class="btn" onclick="fetchRecs()">Fetch Personal Recommendations</button>
                    <div id="recsOutput" style="font-size:0.9rem; color:var(--muted);">Click fetch to test variant assignment...</div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">⚡ SSE Token Streaming Endpoint</div>
                    <button class="btn" style="background:var(--purple); color:#fff;" onclick="testStream()">Trigger Live Token Stream (/stream)</button>
                    <div id="streamOutput" style="margin-top:1rem; font-size:0.9rem; background:#090d16; padding:1rem; border-radius:6px;">Stream tokens will render here...</div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title">📈 Real-Time MLOps Telemetry Snapshot</div>
                    <div id="telemetryOutput">
                        <div class="metric-card">
                            <div style="font-size:0.85rem; color:var(--muted);">Time-To-First-Token (P95 TTFT)</div>
                            <div class="metric-val" id="p95Val">-- ms</div>
                        </div>
                        <div class="metric-card">
                            <div style="font-size:0.85rem; color:var(--muted);">Serving Throughput (Avg TPS)</div>
                            <div class="metric-val" id="tpsVal">-- tokens/sec</div>
                        </div>
                        <div class="metric-card">
                            <div style="font-size:0.85rem; color:var(--muted);">SLA Compliance (TTFT &le; 500ms)</div>
                            <div class="metric-val" id="sloVal" style="color:var(--accent);">-- %</div>
                        </div>
                    </div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">🔥 Prometheus Export Format (/metrics/prometheus)</div>
                    <pre id="promOutput">Loading Prometheus metrics...</pre>
                </div>
            </div>
        </div>

        <script>
            async function fetchRecs() {
                const uid = document.getElementById('userIdInput').value;
                const res = await fetch(`/recommendations/${uid}`);
                const data = await res.json();

                document.getElementById('recsOutput').innerHTML = `
                    <div style="margin-bottom:0.5rem;">
                        Assigned Variant: <span class="badge badge-${data.assigned_variant}">${data.assigned_variant}</span>
                    </div>
                    ${data.recommendations.map(r => `
                        <div style="background:#090d16; padding:0.5rem 0.75rem; margin-bottom:0.4rem; border-radius:4px; font-size:0.85rem;">
                            <strong>${r.title}</strong> (${r.category}) - Score: ${r.relevance_score}
                        </div>
                    `).join('')}
                `;
            }

            async function testStream() {
                const out = document.getElementById('streamOutput');
                out.innerText = "Connecting to SSE stream...\n";
                const eventSource = new EventSource('/stream');

                eventSource.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.error) {
                        out.innerText += `\n⚠️ [BACKPRESSURE] ${data.message}`;
                        eventSource.close();
                    } else {
                        out.innerText += data.token;
                    }
                };

                eventSource.onerror = function() {
                    eventSource.close();
                    refreshMetrics();
                };
            }

            async function refreshMetrics() {
                const res = await fetch('/metrics/snapshot');
                const m = await res.json();

                document.getElementById('p95Val').innerText = `${m.p95_ttft_ms} ms`;
                document.getElementById('tpsVal').innerText = `${m.avg_tps} TPS`;
                document.getElementById('sloVal').innerText = `${m.slo_compliance_pct}%`;

                const pRes = await fetch('/metrics/prometheus');
                const pText = await pRes.text();
                document.getElementById('promOutput').innerText = pText;
            }

            refreshMetrics();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
