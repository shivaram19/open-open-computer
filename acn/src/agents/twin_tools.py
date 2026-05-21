# src/agents/twin_tools.py
"""
Agent-as-Tool Pattern: Twins expose capabilities as callable tools.

Inspired by Strands AI Functions (strands-labs/ai-functions, 2026):
- Agents register capabilities as named, typed tools
- Other agents invoke them via a registry
- Enables composable agent workflows beyond deliberation

Principle: A twin that cannot be called is a twin that cannot collaborate.

[CITATION: Strands2026]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type

from pydantic import BaseModel, ValidationError

from shared.utils.citations import cite


@dataclass
class TwinTool:
    """A capability exposed by a twin as a callable tool."""
    name: str
    description: str
    twin_id: str
    handler: Callable[..., Any]
    input_schema: Optional[Type[BaseModel]] = None
    output_schema: Optional[Type[BaseModel]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ToolInvocationResult:
    """Outcome of invoking a twin tool."""
    success: bool
    output: Any = None
    latency_ms: float = 0.0
    error: Optional[str] = None
    tool_name: str = ""
    twin_id: str = ""


@cite(
    key="TWIN-TOOL-REGISTRY",
    paper="Strands AI Functions: Agent-as-Tool Composition",
    venue="ACN Agents Architecture",
    section="P5-5 Agent-as-Tool",
    rationale="Registry pattern for composable agent capabilities",
    confidence="HIGH",
)
class TwinToolRegistry:
    """
    Registry of tools exposed by twins.

    Usage:
        registry = TwinToolRegistry()
        registry.register(TwinTool(name="summarize", ...))
        result = registry.invoke("summarize", {"text": "..."})
    """

    def __init__(self):
        self._tools: Dict[str, TwinTool] = {}
        self._twin_tools: Dict[str, List[str]] = {}  # twin_id -> tool_names

    def register(self, tool: TwinTool) -> None:
        """Register a tool. Raises ValueError on name collision."""
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool
        self._twin_tools.setdefault(tool.twin_id, []).append(tool.name)

    def invoke(self, tool_name: str, inputs: Dict[str, Any]) -> ToolInvocationResult:
        """
        Invoke a tool by name with validated inputs.

        Returns ToolInvocationResult with success flag and output or error.
        """
        start = time.time()
        tool = self._tools.get(tool_name)
        if tool is None:
            return ToolInvocationResult(
                success=False,
                error=f"Tool '{tool_name}' not found",
                tool_name=tool_name,
                latency_ms=(time.time() - start) * 1000,
            )

        # Validate inputs if schema provided
        if tool.input_schema is not None:
            try:
                validated = tool.input_schema(**inputs)
                inputs = validated.model_dump()
            except ValidationError as exc:
                return ToolInvocationResult(
                    success=False,
                    error=f"Input validation failed: {exc}",
                    tool_name=tool_name,
                    twin_id=tool.twin_id,
                    latency_ms=(time.time() - start) * 1000,
                )

        # Invoke handler with timeout protection
        try:
            output = tool.handler(**inputs)
        except Exception as exc:
            return ToolInvocationResult(
                success=False,
                error=f"Handler raised exception: {exc}",
                tool_name=tool_name,
                twin_id=tool.twin_id,
                latency_ms=(time.time() - start) * 1000,
            )

        # Validate output if schema provided
        if tool.output_schema is not None:
            try:
                tool.output_schema(**(output if isinstance(output, dict) else {"result": output}))
            except ValidationError as exc:
                return ToolInvocationResult(
                    success=True,
                    output=output,
                    error=f"Output validation warning: {exc}",
                    tool_name=tool_name,
                    twin_id=tool.twin_id,
                    latency_ms=(time.time() - start) * 1000,
                )

        return ToolInvocationResult(
            success=True,
            output=output,
            tool_name=tool_name,
            twin_id=tool.twin_id,
            latency_ms=(time.time() - start) * 1000,
        )

    def list_tools(self) -> List[TwinTool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def get_tools_for_twin(self, twin_id: str) -> List[TwinTool]:
        """Return all tools registered by a specific twin."""
        names = self._twin_tools.get(twin_id, [])
        return [self._tools[n] for n in names if n in self._tools]

    def search_tools(self, query: str) -> List[TwinTool]:
        """Search tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for tool in self._tools.values():
            if query_lower in tool.name.lower():
                results.append(tool)
            elif query_lower in tool.description.lower():
                results.append(tool)
            elif any(query_lower in t.lower() for t in tool.tags):
                results.append(tool)
        return results

    def unregister(self, tool_name: str) -> bool:
        """Remove a tool from the registry. Returns True if found."""
        tool = self._tools.pop(tool_name, None)
        if tool is None:
            return False
        twin_tools = self._twin_tools.get(tool.twin_id, [])
        if tool_name in twin_tools:
            twin_tools.remove(tool_name)
        return True

    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def __len__(self) -> int:
        return len(self._tools)



@cite(
    key="TOOL-CALLING-TWIN",
    paper="Strands AI Functions: Tool-Calling Agent",
    venue="ACN Agents Architecture",
    section="P5-5 Agent-as-Tool",
    rationale="Twin that can invoke capabilities of other twins via registry",
    confidence="HIGH",
)
class ToolCallingTwin:
    """
    Mixin-like capability for twins to call tools from a registry.

    Must be combined with TwinAgent via multiple inheritance:

        class MyTwin(ToolCallingTwin, TwinAgent):
            pass

    Usage:
        twin = MyTwin(agent_id="t1", ..., tool_registry=registry)
        result = twin.call_tool("summarize", text="...")
    """

    _tool_registry: Optional[TwinToolRegistry] = None

    def __init__(self, *args, tool_registry: Optional[TwinToolRegistry] = None, **kwargs):
        self._tool_registry = tool_registry
        # Call next class in MRO (should be TwinAgent)
        super().__init__(*args, **kwargs)

    def call_tool(self, tool_name: str, **inputs) -> ToolInvocationResult:
        """Invoke a tool from the registry."""
        if self._tool_registry is None:
            return ToolInvocationResult(
                success=False,
                error="No tool registry configured",
                tool_name=tool_name,
            )
        return self._tool_registry.invoke(tool_name, inputs)

    def get_available_tools(self) -> List[TwinTool]:
        """List all tools available in the registry."""
        if self._tool_registry is None:
            return []
        return self._tool_registry.list_tools()

    def propose_tool_call(self, tool_name: str, reasoning: str) -> Dict[str, Any]:
        """Propose a tool call during deliberation. Returns proposal dict."""
        return {
            "type": "tool_call_proposal",
            "twin_id": getattr(self, "agent_id", "unknown"),
            "tool_name": tool_name,
            "reasoning": reasoning,
        }
