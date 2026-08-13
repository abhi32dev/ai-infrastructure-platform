"""
FastAPI REST Application & Web UI for Event Ingestion & PySpark ETL Platform.
Provides endpoints for MIB OID packet decoding, TTL deduplication, 3-Pass storage reconciliation,
and PySpark feature transformation.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import Any, Dict, List, Optional
import uvicorn

from src.mib_decoder import SNMPVersion
from src.streaming_ingestion import StreamingIngestionOrchestrator

app = FastAPI(
    title="High-Throughput Event Streaming, PySpark ETL & 3-Pass Reconciliation Engine",
    version="1.0.0",
    description="Real-time MIB OID packet decoding, TTL deduplication, 3-pass reconciliation, and PySpark feature ETL."
)

orchestrator = StreamingIngestionOrchestrator()


@app.post("/ingest/packet")
async def ingest_packet(payload: Dict[str, Any] = Body(...)):
    node_id = payload.get("node_id", "edge-node-108")
    raw_oid = payload.get("raw_oid", "1.3.6.1.4.1.9.9.43.1.1.1")
    snmp_ver_str = payload.get("snmp_version", "SNMPv3_SHA_AES")

    is_processed, result = orchestrator.process_incoming_packet(
        node_id=node_id,
        raw_oid=raw_oid,
        snmp_version=SNMPVersion(snmp_ver_str)
    )
    return {"processed": is_processed, "result": result}


@app.post("/reconcile")
async def run_reconciliation(payload: Dict[str, Any] = Body(...)):
    expected = payload.get("expected_files", ["file_01.xml", "file_02.xml", "file_03.xml"])
    storage = payload.get("storage_listing", ["file_01.xml", "file_02.xml", "file_03.xml"])
    simulate_fail = payload.get("simulate_failure", False)

    res = orchestrator.run_reconciliation_pass(expected, storage, simulate_failure=simulate_fail)
    return res


@app.post("/etl/process")
async def run_etl(payload: Dict[str, Any] = Body(...)):
    raw_events = payload.get("events", [
        {"alarm_id": "a1", "node_id": "edge-node-108", "severity": "CRITICAL", "payload_size_bytes": 1024},
        {"alarm_id": "a2", "node_id": "edge-node-108", "severity": "MAJOR", "payload_size_bytes": 512},
        {"alarm_id": "a3", "node_id": "edge-node-204", "severity": "CRITICAL", "payload_size_bytes": 2048}
    ])

    features = orchestrator.run_batch_feature_etl(raw_events)
    return {"feature_records": features}


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Embedded Single-Page Visualizer for Event Ingestion & 3-Pass Reconciliation.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Event Ingestion & 3-Pass Reconciliation Dashboard</title>
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
                --danger: #ef4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
            .header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
            h1 { color: var(--accent); font-size: 1.5rem; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
            .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; }
            input, select, button { width: 100%; padding: 0.75rem; background: #090d16; border: 1px solid var(--border); color: #fff; border-radius: 6px; margin-bottom: 1rem; font-family: inherit; }
            .btn { background: var(--accent); color: #000; font-weight: 600; border: none; cursor: pointer; }
            .btn:hover { opacity: 0.9; }
            .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
            .badge-SUCCESS { background: rgba(34, 197, 94, 0.2); color: var(--success); }
            .badge-DROPPED { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
            pre { background: #070a10; padding: 1rem; border-radius: 6px; font-size: 0.85rem; color: #a5f3fc; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>📡 Event Streaming, TTL Dedup & 3-Pass Reconciliation Engine</h1>
                <div style="color:var(--muted); font-size:0.9rem;">MIB OID Packet Decoder • DynamoDB TTL Deduplication • 3-Pass Reconciliation • PySpark Feature ETL</div>
            </div>
        </div>

        <div class="grid">
            <div>
                <div class="card">
                    <div class="card-title">📥 Ingest Packet & Test TTL Deduplication</div>
                    <label>Node ID:</label>
                    <input type="text" id="nodeId" value="edge-node-108">
                    
                    <label>Raw MIB OID:</label>
                    <select id="oidInput">
                        <option value="1.3.6.1.4.1.9.9.43.1.1.1">1.3.6.1.4.1.9.9.43.1.1.1 (High CPU Temp - CRITICAL)</option>
                        <option value="1.3.6.1.4.1.9.9.48.1.1.1">1.3.6.1.4.1.9.9.48.1.1.1 (Memory Pressure - MAJOR)</option>
                    </select>

                    <button class="btn" onclick="sendPacket()">Send UDP Trap Packet</button>
                    <div id="packetOutput" style="font-size:0.9rem; color:var(--muted);">Send packet to view MIB decoding and TTL dedup status...</div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div class="card-title">🔄 3-Pass Reconciliation Simulator</div>
                    <button class="btn" style="background:var(--warning); color:#000;" onclick="testReconciliation(true)">Simulate Storage Partial Failure & Run 3-Pass Recovery</button>
                    <div id="reconOutput" style="margin-top:1rem; font-size:0.9rem; color:var(--muted);">Click above to run 3-pass reconciliation...</div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title">⚡ PySpark Batch Feature ETL Output</div>
                    <button class="btn" onclick="runETL()">Run PySpark Aggregation ETL</button>
                    <pre id="etlOutput">Run PySpark ETL to see node feature metrics...</pre>
                </div>
            </div>
        </div>

        <script>
            async function sendPacket() {
                const node = document.getElementById('nodeId').value;
                const oid = document.getElementById('oidInput').value;

                const res = await fetch('/ingest/packet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ node_id: node, raw_oid: oid })
                });

                const data = await res.json();
                document.getElementById('packetOutput').innerHTML = `
                    <div style="margin-bottom:0.5rem;">
                        Status: <span class="badge ${data.processed ? 'badge-SUCCESS' : 'badge-DROPPED'}">${data.processed ? 'PROCESSED' : 'TTL_DUPLICATE_DROPPED'}</span>
                    </div>
                    <pre>${JSON.stringify(data.result, null, 2)}</pre>
                `;
            }

            async function testReconciliation(fail) {
                const res = await fetch('/reconcile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        expected_files: ["file_01.xml", "file_02.xml", "file_03.xml", "file_04.xml"],
                        storage_listing: ["file_01.xml", "file_02.xml", "file_03.xml", "file_04.xml"],
                        simulate_failure: fail
                    })
                });

                const data = await res.json();
                document.getElementById('reconOutput').innerHTML = `
                    <div><strong>Status:</strong> <span class="badge badge-SUCCESS">${data.status}</span></div>
                    <div><strong>Passes Executed:</strong> ${data.reconciliation_passes_run}</div>
                    <div><strong>Recovered Files:</strong> ${data.recovered_files.join(', ')}</div>
                    <div><strong>Silent Data Gaps:</strong> ${data.silent_gaps}</div>
                `;
            }

            async function runETL() {
                const res = await fetch('/etl/process', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({}) });
                const data = await res.json();
                document.getElementById('etlOutput').innerText = JSON.stringify(data.feature_records, null, 2);
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8004)
