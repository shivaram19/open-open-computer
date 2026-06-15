# src/generation/mcp_server.py
"""
Model Context Protocol (MCP) bridge for ACN media generation tools.

Exposes every tool registered in a TwinToolRegistry as an MCP tool, with
SecurityManager authorization and audit logging inherited from the underlying
media tools.

[CITATION: GopherMCP]
Reference MCP implementation: GopherSecurity/gopher-mcp — C++ SDK with
multi-language bindings and transport support.

[CITATION: ADR-011]
Enterprise Security Baseline — all media generation calls route through
SecurityManager for authentication, authorization, and audit logging.
"""

import json
from typing import Any, Dict, List, Optional

from mcp import types
from mcp.server.lowlevel.server import Server

from agents.twin_tools import TwinToolRegistry
from security import SecurityManager
from shared.utils.citations import cite


@cite(
    key="MCP-MEDIA-BRIDGE",
    paper="ACN Media Generation Subsystem",
    venue="ACN Architecture Document",
    section="MCP Bridge",
    rationale="MCP bridge lets any MCP-compatible client invoke ACN media tools without knowing ACN internals",
    confidence="CERTAIN",
)
class MediaMcpServer:
    """Bridge between TwinToolRegistry and the Model Context Protocol."""

    def __init__(
        self,
        tool_registry: TwinToolRegistry,
        security: SecurityManager,
        default_tenant_id: str = "public",
        default_agent_id: str = "mcp_client",
        default_roles: Optional[List[str]] = None,
        server_name: str = "acn-media-server",
        version: str = "0.1.0",
    ):
        self.registry = tool_registry
        self.security = security
        self.default_tenant_id = default_tenant_id
        self.default_agent_id = default_agent_id
        self.default_roles = default_roles or ["service"]
        self.server = Server(
            name=server_name,
            version=version,
            instructions=(
                "ACN media generation bridge. Tools can generate images and videos "
                "via ComfyUI, HyperFrames, and Bernini. Every call requires "
                "tenant_id and agent_id and is authorized by SecurityManager."
            ),
        )
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Wire MCP request handlers."""
        self.server.list_tools()(self._list_tools_handler)
        self.server.call_tool()(self._call_tool_handler)

    def _twin_tool_to_mcp_tool(self, tool) -> types.Tool:
        """Convert a TwinTool definition to an MCP Tool."""
        if tool.input_schema is not None:
            schema = tool.input_schema.model_json_schema()
        else:
            schema = {"type": "object", "properties": {}}

        # Ensure required security fields are present in the schema.
        properties = schema.setdefault("properties", {})
        for field, field_schema in {
            "tenant_id": {"type": "string", "description": "Tenant that owns the request"},
            "agent_id": {"type": "string", "description": "Agent or service invoking the tool"},
            "roles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "RBAC roles assigned to the caller",
            },
        }.items():
            if field not in properties:
                properties[field] = field_schema

        # Security context fields are injected by the bridge if missing, so
        # they are advertised but not strictly required at the MCP boundary.
        required = set(schema.get("required", []))
        required.discard("tenant_id")
        required.discard("agent_id")
        required.discard("roles")
        if required:
            schema["required"] = sorted(required)
        elif "required" in schema:
            del schema["required"]

        return types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=schema,
        )

    async def _list_tools_handler(
        self,
        request: types.ListToolsRequest,
    ) -> types.ListToolsResult:
        """Return all registered media tools as MCP tool definitions."""
        tools = [self._twin_tool_to_mcp_tool(tool) for tool in self.registry.list_tools()]
        return types.ListToolsResult(tools=tools)

    async def _call_tool_handler(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> types.CallToolResult:
        """Invoke a TwinTool by name and return the result as MCP content."""
        if tool_name not in self.registry:
            return self._error_result(f"Tool '{tool_name}' not found")

        # Ensure security context is present.
        arguments.setdefault("tenant_id", self.default_tenant_id)
        arguments.setdefault("agent_id", self.default_agent_id)
        arguments.setdefault("roles", self.default_roles)

        try:
            invocation = self.registry.invoke(tool_name, arguments)
        except Exception as exc:
            return self._error_result(f"Tool invocation failed: {exc}")

        payload = {
            "success": invocation.success,
            "output": invocation.output,
            "latency_ms": invocation.latency_ms,
            "error": invocation.error,
            "tool_name": invocation.tool_name,
            "twin_id": invocation.twin_id,
        }
        content = [types.TextContent(type="text", text=json.dumps(payload, default=str))]
        return types.CallToolResult(content=content)

    @staticmethod
    def _error_result(message: str) -> types.CallToolResult:
        payload = json.dumps({"success": False, "error": message})
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=payload)],
            isError=True,
        )

    def get_server(self) -> Server:
        """Return the configured low-level MCP server."""
        return self.server

    async def run_stdio(self) -> None:
        """Run the server over stdio transport."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
