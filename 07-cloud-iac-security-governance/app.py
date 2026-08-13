"""
FastAPI REST Application & Web UI for Cloud IaC & Security Governance Platform.
Provides REST endpoints for CDK multi-account synthesis, IAM policy auditing,
and EC2 security agent compliance tracking.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict, List
import uvicorn

from src.cloud_security_governance import CloudSecurityGovernanceOrchestrator

app = FastAPI(
    title="Multi-Account Cloud IaC & Security Governance Engine",
    version="1.0.0",
    description="AWS CDK golden path synthesis, least-privilege IAM auditing, and EC2 endpoint security monitoring."
)

orchestrator = CloudSecurityGovernanceOrchestrator()


@app.post("/cdk/synthesize")
async def synthesize_stack(payload: Dict[str, Any] = Body(...)):
    env = payload.get("environment", "Prod")
    stack = orchestrator.synthesize_cdk_stack(env)
    return stack.dict()


@app.post("/iam/audit")
async def audit_iam(payload: Dict[str, Any] = Body(...)):
    policy_name = payload.get("policy_name", "CONDOR-ServiceRole-Policy")
    is_prod = payload.get("is_production", True)
    doc = payload.get("policy_doc", {
        "Statement": [
            {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"], "Resource": "arn:aws:s3:::condor-data-bucket/*"},
            {"Effect": "Allow", "Action": "*", "Resource": "*"}  # Over-permissioned statement
        ]
    })

    violations = orchestrator.audit_iam_policy(policy_name, doc, is_prod=is_prod)
    return {"policy_name": policy_name, "violations_count": len(violations), "violations": [v.dict() for v in violations]}


@app.post("/security/audit-host")
async def audit_host(payload: Dict[str, Any] = Body(...)):
    instance_id = payload.get("instance_id", "i-0a1b2c3d4e5f")
    os_ver = payload.get("os_version", "Amazon Linux 2023")
    agents = payload.get("installed_agents", {
        "crowdstrike": "7.10.0",
        "qualys": "3.1.5",
        "opens": "2.4.1"
    })

    status = orchestrator.audit_ec2_host_security(instance_id, os_ver, agents)
    return status.dict()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Cloud IaC & Security Governance Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
            h1 { color: #38bdf8; font-size: 1.5rem; margin-bottom: 1rem; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
            .btn { background: #38bdf8; color: #000; font-weight: 600; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; }
            pre { background: #090d16; padding: 1rem; border-radius: 6px; color: #a5f3fc; }
        </style>
    </head>
    <body>
        <h1>🛡️ Multi-Account Cloud IaC & Security Governance Center</h1>
        <div class="card">
            <h3>⚡ Synthesize AWS CDK Stack Definition</h3>
            <button class="btn" onclick="synthCDK()">Synthesize Prod Stack</button>
            <pre id="cdkOutput">Click button to synthesize stack...</pre>
        </div>
        <script>
            async function synthCDK() {
                const res = await fetch('/cdk/synthesize', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ environment: 'Prod' }) });
                const data = await res.json();
                document.getElementById('cdkOutput').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
