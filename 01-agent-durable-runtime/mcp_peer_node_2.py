"""
Real Containerized MCP Subagent Peer Node (Node 2).
Boots up as an independent microservice container (port 8010), performs live MCP JSON-RPC 2.0
handshakes with Orchestrator Agent (port 8000), discovers remote tools, and executes A2A calls over HTTP sockets.
"""

import asyncio
import httpx
from typing import Any, Dict


async def run_mcp_peer_client(target_orchestrator_url: str = "http://127.0.0.1:8000/mcp"):
    print(f"[MCP PEER SUBAGENT] Booting Subagent Node 2... Target Orchestrator: {target_orchestrator_url}")

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Step 1: Handshake
        init_payload = {
            "jsonrpc": "2.0",
            "id": "req-001",
            "method": "initialize",
            "params": {"agent_id": "subagent-worker-02", "agent_name": "WorkerSubagent"}
        }
        res_init = await client.post(target_orchestrator_url, json=init_payload)
        print(f"[MCP PEER SUBAGENT] Handshake Response: {res_init.json()}")

        # Step 2: Tool Discovery
        tools_payload = {
            "jsonrpc": "2.0",
            "id": "req-002",
            "method": "tools/list",
            "params": {}
        }
        res_tools = await client.post(target_orchestrator_url, json=tools_payload)
        print(f"[MCP PEER SUBAGENT] Remote Tool Discovery: {res_tools.json()}")

        # Step 3: Remote Tool Call
        call_payload = {
            "jsonrpc": "2.0",
            "id": "req-003",
            "method": "tools/call",
            "params": {
                "name": "sql_query_executor",
                "arguments": {"query": "SELECT * FROM task_checkpoints WHERE status='COMPLETED'"}
            }
        }
        res_call = await client.post(target_orchestrator_url, json=call_payload)
        print(f"[MCP PEER SUBAGENT] Remote Tool Call Result: {res_call.json()}")


if __name__ == "__main__":
    asyncio.run(run_mcp_peer_client())
