"""
FastAPI REST Application & Web UI for Agent Runtime Engine.
Provides endpoints for task submission, step inspection, Human-in-the-Loop approvals,
deterministic replay triggers, and an embedded HTML/JS state visualizer.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict, Optional
import uvicorn

from src.agent_orchestrator import AgentOrchestrator
from src.state_models import TaskStatus

app = FastAPI(
    title="Enterprise AI Agent Runtime & Durable Execution Platform",
    version="1.0.0",
    description="Durable execution engine with state checkpoints, deterministic replay, MCP tools, and HITL controls."
)

orchestrator = AgentOrchestrator(db_path="agent_state.db")

from src.mcp_agent_protocol import MCPAgentProtocolEngine, MCPJSONRPCMessage
mcp_engine = MCPAgentProtocolEngine("agent-orchestrator-01", "OrchestratorAgent")


@app.post("/mcp")
async def handle_mcp_socket_call(message: Dict[str, Any] = Body(...)):
    """Real REST / JSON-RPC 2.0 MCP Socket Server for inter-agent container communication."""
    rpc_msg = MCPJSONRPCMessage(**message)
    resp = mcp_engine.handle_mcp_message(rpc_msg)
    return resp.dict()



@app.post("/tasks/submit")
async def submit_task(payload: Dict[str, Any] = Body(...)):
    goal = payload.get("goal", "Remediate high memory pressure on edge-node-108")
    metadata = payload.get("metadata", {})
    state = orchestrator.submit_task(goal=goal, metadata=metadata)
    return state.dict()


@app.post("/tasks/{task_id}/run")
async def run_task(task_id: str, simulate_failure_at_step: Optional[int] = None):
    try:
        state = await orchestrator.run_task(task_id, simulate_failure_at_step=simulate_failure_at_step)
        return state.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    state = orchestrator.store.load_task_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    return state.dict()


@app.post("/tasks/{task_id}/approve")
async def approve_step(task_id: str, payload: Dict[str, Any] = Body(...)):
    step_index = payload.get("step_index", 3)
    try:
        state = orchestrator.approve_step(task_id, step_index=step_index)
        # Resume task after approval
        resumed_state = await orchestrator.run_task(task_id)
        return resumed_state.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/tasks/{task_id}/replay")
async def replay_task(task_id: str):
    try:
        state = await orchestrator.replay_task_from_last_checkpoint(task_id)
        return state.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/tools")
async def list_tools():
    tools = orchestrator.tool_registry.list_tools()
    return [t.dict() for t in tools]


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Embedded HTML/JS Visualizer Dashboard for Agent Task Execution, Checkpoints, & Replay.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agent Runtime & Durable Execution Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0f172a;
                --card-bg: #1e293b;
                --accent: #38bdf8;
                --accent-hover: #0284c7;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --success: #22c55e;
                --warning: #f59e0b;
                --danger: #ef4444;
                --border: #334155;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; line-height: 1.5; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
            h1 { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
            .subtitle { color: var(--text-muted); font-size: 0.9rem; }
            .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; }
            .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
            .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text); display: flex; align-items: center; gap: 0.5rem; }
            .btn { background: var(--accent); color: #000; border: none; padding: 0.6rem 1.2rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
            .btn:hover { background: var(--accent-hover); color: #fff; }
            .btn-warning { background: var(--warning); color: #000; }
            .btn-danger { background: var(--danger); color: #fff; }
            .btn-group { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; }
            input, select { width: 100%; padding: 0.75rem; background: #0f172a; border: 1px solid var(--border); color: #fff; border-radius: 6px; margin-bottom: 1rem; }
            .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
            .badge-COMPLETED { background: rgba(34, 197, 94, 0.2); color: var(--success); }
            .badge-FAILED { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
            .badge-HUMAN_APPROVAL_REQUIRED { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
            .badge-CHECKPOINTED, .badge-RUNNING { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
            .timeline { margin-top: 1.5rem; position: relative; padding-left: 1.5rem; border-left: 2px solid var(--border); }
            .timeline-item { position: relative; margin-bottom: 1.5rem; }
            .timeline-dot { position: absolute; left: -2.05rem; top: 0.2rem; width: 1rem; height: 1rem; border-radius: 50%; background: var(--border); border: 2px solid var(--card-bg); }
            .timeline-dot.active { background: var(--accent); }
            .timeline-dot.success { background: var(--success); }
            .timeline-dot.failed { background: var(--danger); }
            .timeline-dot.warning { background: var(--warning); }
            .step-title { font-weight: 600; font-size: 0.95rem; }
            .step-meta { font-size: 0.8rem; color: var(--text-muted); }
            pre { background: #090d16; padding: 1rem; border-radius: 6px; font-size: 0.85rem; color: #a5f3fc; overflow-x: auto; margin-top: 0.5rem; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>⚡ Enterprise AI Agent Runtime & Durable Execution</h1>
                <div class="subtitle">State Machine Checkpointing • Deterministic Replay • MCP Tools • HITL Approval Gate</div>
            </div>
            <button class="btn" onclick="submitNewTask()">+ Submit Agent Task</button>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <div class="card-title">🎮 Task Control Center</div>
                    <label>Active Task ID:</label>
                    <input type="text" id="taskIdInput" placeholder="Submit a task or enter ID...">
                    
                    <div class="btn-group">
                        <button class="btn" onclick="runTask(null)">Run Normal Workflow</button>
                        <button class="btn btn-warning" onclick="runTask(2)">Simulate Failure @ Step 2</button>
                        <button class="btn btn-danger" onclick="replayTask()">Deterministic Replay</button>
                        <button class="btn" onclick="approveStep()" style="background:#a855f7; color:#fff;">Approve HITL Gate</button>
                    </div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">🛡️ Registered MCP Tools</div>
                    <div id="toolsList" style="font-size: 0.85rem; color: var(--text-muted);">Loading tool registry...</div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title">
                        <span>📌 Task Execution Timeline & Checkpoint History</span>
                        <span id="statusBadge" class="badge badge-CHECKPOINTED">IDLE</span>
                    </div>

                    <div id="taskGoal" style="font-size: 0.95rem; color: var(--text-muted); margin-bottom: 1rem;">
                        No active task loaded. Click "+ Submit Agent Task" to begin.
                    </div>

                    <div class="timeline" id="timeline"></div>
                </div>
            </div>
        </div>

        <script>
            let currentTaskId = "";

            async function fetchTools() {
                const res = await fetch('/tools');
                const tools = await res.json();
                const container = document.getElementById('toolsList');
                container.innerHTML = tools.map(t => `
                    <div style="margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
                        <strong style="color:var(--text);">${t.name}</strong> 
                        <span class="badge ${t.permission_level === 'SENSITIVE_REQUIRES_APPROVAL' ? 'badge-HUMAN_APPROVAL_REQUIRED' : 'badge-COMPLETED'}">${t.permission_level}</span>
                        <div style="font-size: 0.8rem; margin-top:0.25rem;">${t.description}</div>
                    </div>
                `).join('');
            }

            async function submitNewTask() {
                const res = await fetch('/tasks/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ goal: "Detect and remediate memory pressure on edge-node-108" })
                });
                const data = await res.json();
                currentTaskId = data.task_id;
                document.getElementById('taskIdInput').value = currentTaskId;
                renderTaskState(data);
            }

            async function runTask(failAtStep = null) {
                if (!currentTaskId) currentTaskId = document.getElementById('taskIdInput').value;
                if (!currentTaskId) return alert("Please submit a task first!");

                let url = `/tasks/${currentTaskId}/run`;
                if (failAtStep !== null) url += `?simulate_failure_at_step=${failAtStep}`;

                const res = await fetch(url, { method: 'POST' });
                const data = await res.json();
                renderTaskState(data);
            }

            async function replayTask() {
                if (!currentTaskId) currentTaskId = document.getElementById('taskIdInput').value;
                if (!currentTaskId) return alert("Enter task ID!");

                const res = await fetch(`/tasks/${currentTaskId}/replay`, { method: 'POST' });
                const data = await res.json();
                renderTaskState(data);
            }

            async function approveStep() {
                if (!currentTaskId) currentTaskId = document.getElementById('taskIdInput').value;
                if (!currentTaskId) return alert("Enter task ID!");

                const res = await fetch(`/tasks/${currentTaskId}/approve`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ step_index: 3 })
                });
                const data = await res.json();
                renderTaskState(data);
            }

            function renderTaskState(task) {
                document.getElementById('taskGoal').innerText = `Goal: ${task.goal} | Task ID: ${task.task_id}`;
                const badge = document.getElementById('statusBadge');
                badge.className = `badge badge-${task.status}`;
                badge.innerText = task.status;

                const timeline = document.getElementById('timeline');
                if (!task.checkpoints || task.checkpoints.length === 0) {
                    timeline.innerHTML = '<div style="color:var(--text-muted);">No step checkpoints recorded yet. Click "Run Normal Workflow".</div>';
                    return;
                }

                timeline.innerHTML = task.checkpoints.map(cp => {
                    let dotClass = 'active';
                    if (cp.status === 'COMPLETED') dotClass = 'success';
                    if (cp.status === 'FAILED') dotClass = 'failed';
                    if (cp.status === 'HUMAN_APPROVAL_REQUIRED') dotClass = 'warning';

                    return `
                        <div class="timeline-item">
                            <div class="timeline-dot ${dotClass}"></div>
                            <div class="step-title">Step ${cp.step_index}: ${cp.step_name}</div>
                            <div class="step-meta">Status: <span class="badge badge-${cp.status}">${cp.status}</span> | Timestamp: ${new Date(cp.timestamp * 1000).toLocaleTimeString()}</div>
                            ${cp.error_message ? `<div style="color:var(--danger); font-size:0.85rem; margin-top:0.25rem;">⚠️ ${cp.error_message}</div>` : ''}
                            ${cp.output_data ? `<pre>${JSON.stringify(cp.output_data, null, 2)}</pre>` : ''}
                        </div>
                    `;
                }).join('');
            }

            fetchTools();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
