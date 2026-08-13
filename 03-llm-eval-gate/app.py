"""
FastAPI REST Application & Web UI for AI Evaluation Gate Engine.
Provides endpoints for dataset evaluation, LLM-as-a-Judge cross-verification,
MLflow tracking, and statistical p-value release gates.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
import json
import os
from typing import Any, Dict, Optional
import uvicorn

from src.eval_pipeline import EvalPipeline

app = FastAPI(
    title="Multi-Model AI Evaluation Gate & MLflow Release Verification",
    version="1.0.0",
    description="Multi-model LLM-as-a-Judge framework with MLflow tracking and p-value statistical release gates."
)

pipeline = EvalPipeline()

# Load sample evaluation dataset
dataset_path = "data/eval_datasets/sample_eval_set.json"
sample_dataset = []
if os.path.exists(dataset_path):
    with open(dataset_path, "r") as f:
        sample_dataset = json.load(f)


@app.post("/evaluate")
async def run_evaluation(payload: Dict[str, Any] = Body(...)):
    run_name = payload.get("run_name", "eval-prompt-v2")
    prompt_version = payload.get("prompt_version", "v2.0")
    dataset = payload.get("dataset", sample_dataset)

    results = await pipeline.evaluate_dataset(
        eval_run_name=run_name,
        prompt_version=prompt_version,
        test_dataset=dataset
    )
    return results


@app.post("/release-gate")
async def evaluate_release_gate(payload: Dict[str, Any] = Body(...)):
    baseline_run = payload.get("baseline_run", {
        "prompt_version": "v1.0",
        "groundedness_scores": [0.65, 0.70, 0.60, 0.75, 0.68]
    })
    candidate_run = payload.get("candidate_run", {
        "prompt_version": "v2.0",
        "groundedness_scores": [0.95, 0.90, 0.92, 0.88, 0.94]
    })

    decision = pipeline.evaluate_release_gate(baseline_run, candidate_run)
    return decision.dict()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Embedded Single-Page Interactive Visualizer for AI Evaluation Gate & Release Gates.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Evaluation Gate & MLflow Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0f172a;
                --card: #1e293b;
                --accent: #38bdf8;
                --text: #f8fafc;
                --muted: #94a3b8;
                --border: #334155;
                --success: #22c55e;
                --warning: #f59e0b;
                --danger: #ef4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
            .header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
            h1 { color: var(--accent); font-size: 1.5rem; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
            .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; }
            .btn { background: var(--accent); color: #000; border: none; padding: 0.75rem 1.5rem; font-weight: 600; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 1rem; }
            .btn:hover { opacity: 0.9; }
            .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
            .badge-APPROVED { background: rgba(34, 197, 94, 0.2); color: var(--success); }
            .badge-REJECTED { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
            pre { background: #090d16; padding: 1rem; border-radius: 6px; font-size: 0.85rem; color: #a5f3fc; overflow-x: auto; margin-top: 0.5rem; }
            .metric-box { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>⚖️ Multi-Model AI Evaluation Gate & MLflow Dashboard</h1>
                <div style="color:var(--muted); font-size:0.9rem;">LLM-as-a-Judge • Rubric Evaluation • MLflow Experiment Tracking • P-Value Release Gate</div>
            </div>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <div class="card-title">🧪 Run Dataset Evaluation</div>
                    <label>Prompt / Model Version:</label>
                    <input type="text" id="promptVersion" value="v2.0-enhanced-prompt" style="width:100%; padding:0.75rem; background:#090d16; border:1px solid var(--border); color:#fff; border-radius:6px; margin-bottom:1rem;">
                    
                    <button class="btn" onclick="runEval()">Run Batch Evaluation & Log to MLflow</button>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">📊 Statistical P-Value Release Gate</div>
                    <button class="btn" style="background:var(--warning); color:#000;" onclick="testReleaseGate()">Test A/B Statistical Significance (Welch's t-test)</button>
                    <div id="gateOutput" style="margin-top:1rem; font-size:0.9rem; color:var(--muted);">Click above to run release gate...</div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title">📈 MLflow Experiment Summary & Rubric Metrics</div>
                    <div id="evalMetrics" style="font-size:0.9rem; color:var(--muted);">Run evaluation to populate metrics...</div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">🤖 LLM-as-a-Judge Detailed Results</div>
                    <div id="judgeResults" style="font-size:0.85rem; color:var(--muted);">Output will appear here.</div>
                </div>
            </div>
        </div>

        <script>
            async function runEval() {
                const version = document.getElementById('promptVersion').value;
                const res = await fetch('/evaluate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ run_name: `eval-${Date.now()}`, prompt_version: version })
                });

                const data = await res.json();

                // Render metrics
                const m = data.metrics;
                document.getElementById('evalMetrics').innerHTML = `
                    <div class="metric-box"><span>MLflow Run ID:</span> <strong>${data.run_id}</strong></div>
                    <div class="metric-box"><span>Average Groundedness:</span> <strong style="color:var(--success);">${(m.avg_groundedness * 100).toFixed(1)}%</strong></div>
                    <div class="metric-box"><span>Context Relevance:</span> <strong>${(m.avg_relevance * 100).toFixed(1)}%</strong></div>
                    <div class="metric-box"><span>Answer Faithfulness:</span> <strong>${(m.avg_faithfulness * 100).toFixed(1)}%</strong></div>
                    <div class="metric-box"><span>Overall Pass Rate:</span> <strong style="color:var(--accent);">${(m.pass_rate * 100).toFixed(1)}%</strong></div>
                `;

                // Render judge results
                document.getElementById('judgeResults').innerHTML = data.results.map(r => `
                    <div style="background:#090d16; padding:0.75rem; margin-bottom:0.5rem; border-radius:6px;">
                        <div style="display:flex; justify-content:space-between; font-weight:600;">
                            <span>${r.eval_id} (${r.candidate_model})</span>
                            <span class="badge ${r.overall_pass ? 'badge-APPROVED' : 'badge-REJECTED'}">${r.overall_pass ? 'PASSED' : 'FAILED'}</span>
                        </div>
                        <div style="font-size:0.8rem; color:var(--muted); margin-top:0.25rem;">Groundedness: ${r.groundedness.score} | Relevance: ${r.context_relevance.score}</div>
                        <div style="font-size:0.8rem; color:#a5f3fc; margin-top:0.25rem;">${r.judge_summary}</div>
                    </div>
                `).join('');
            }

            async function testReleaseGate() {
                const res = await fetch('/release-gate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        baseline_run: { prompt_version: "v1.0-legacy", groundedness_scores: [0.65, 0.70, 0.60, 0.75, 0.68] },
                        candidate_run: { prompt_version: "v2.0-candidate", groundedness_scores: [0.95, 0.92, 0.90, 0.94, 0.96] }
                    })
                });

                const decision = await res.json();
                document.getElementById('gateOutput').innerHTML = `
                    <div style="font-weight:600; margin-bottom:0.5rem;">
                        Status: <span class="badge ${decision.release_approved ? 'badge-APPROVED' : 'badge-REJECTED'}">${decision.release_approved ? 'APPROVED' : 'REJECTED'}</span>
                    </div>
                    <div>Baseline Mean: ${decision.baseline_mean} | Candidate Mean: ${decision.candidate_mean}</div>
                    <div>Percentage Lift: <strong style="color:var(--success);">+${decision.percentage_lift}%</strong></div>
                    <div>P-Value (Welch's t-test): <strong>${decision.p_value}</strong></div>
                    <div style="font-size:0.85rem; color:var(--accent); margin-top:0.5rem;">${decision.recommendation}</div>
                `;
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
