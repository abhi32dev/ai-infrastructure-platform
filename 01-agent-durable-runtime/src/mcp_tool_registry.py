"""
MCP Tool Registry & Execution Controller.
Implements Model Context Protocol concepts: tool discovery, JSON Schema validation, permission scoping,
and least-privilege tool execution with Human-in-the-Loop escalation patterns.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from src.state_models import ToolDefinition, ToolPermissionLevel


class MCPToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()

    def register_tool(
        self,
        name: str,
        description: str,
        permission_level: ToolPermissionLevel,
        parameters_schema: Dict[str, Any],
        handler: Callable
    ):
        tool_def = ToolDefinition(
            name=name,
            description=description,
            permission_level=permission_level,
            parameters_schema=parameters_schema
        )
        self._tools[name] = tool_def
        self._handlers[name] = handler

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], is_human_approved: bool = False) -> Tuple[bool, Any]:
        """
        Executes a registered tool.
        Returns: (success: bool, result_or_error: Any)
        """
        tool_def = self.get_tool(tool_name)
        if not tool_def:
            return False, f"Tool '{tool_name}' not found in registry."

        # Enforcement of Least-Privilege & Human-in-the-Loop (HITL) gate
        if tool_def.permission_level == ToolPermissionLevel.SENSITIVE_REQUIRES_APPROVAL and not is_human_approved:
            return False, {
                "error": "REQUIRES_HUMAN_APPROVAL",
                "message": f"Action '{tool_name}' involves sensitive operations and requires explicit human approval.",
                "tool_name": tool_name,
                "parameters": parameters
            }

        handler = self._handlers.get(tool_name)
        try:
            result = handler(**parameters)
            return True, result
        except Exception as e:
            return False, f"Error executing tool '{tool_name}': {str(e)}"

    def _register_default_tools(self):
        # Tool 1: READ_ONLY Knowledge Base Search
        self.register_tool(
            name="search_knowledge_base",
            description="Search internal documentation and runbooks for standard operating procedures.",
            permission_level=ToolPermissionLevel.READ_ONLY,
            parameters_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query terms"}
                },
                "required": ["query"]
            },
            handler=self._mock_kb_search
        )

        # Tool 2: READ_ONLY Telemetry Query
        self.register_tool(
            name="query_telemetry",
            description="Fetch health metrics and node status for distributed infrastructure.",
            permission_level=ToolPermissionLevel.READ_ONLY,
            parameters_schema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Target edge or node ID"}
                },
                "required": ["node_id"]
            },
            handler=self._mock_query_telemetry
        )

        # Tool 3: SENSITIVE System Remediation (Triggers HITL!)
        self.register_tool(
            name="execute_system_remediation",
            description="Restart a service daemon or isolate a degraded node in production.",
            permission_level=ToolPermissionLevel.SENSITIVE_REQUIRES_APPROVAL,
            parameters_schema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Target node ID"},
                    "remediation_action": {"type": "string", "description": "RESTART, ISOLATE, or FAILOVER"}
                },
                "required": ["node_id", "remediation_action"]
            },
            handler=self._mock_execute_remediation
        )

    @staticmethod
    def _mock_kb_search(query: str) -> Dict[str, Any]:
        return {
            "query": query,
            "matched_runbook": "SOP-104: Node Memory Pressure Resolution",
            "recommended_steps": ["Query telemetry for node", "Trigger graceful worker failover if CPU > 90%"]
        }

    @staticmethod
    def _mock_query_telemetry(node_id: str) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "status": "DEGRADED",
            "cpu_utilization": 94.2,
            "memory_usage_mb": 7890,
            "active_connections": 1240,
            "error_rate_pct": 4.8
        }

    @staticmethod
    def _mock_execute_remediation(node_id: str, remediation_action: str) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "remediation_action": remediation_action,
            "status": "SUCCESSFULLY_EXECUTED",
            "message": f"Action {remediation_action} completed on node {node_id}. Health restored."
        }
