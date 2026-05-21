# tests/agents/test_twin_tools.py
"""Tests for agent-as-tool pattern (Strands-inspired)."""

import pytest
from pydantic import BaseModel

from agents.twin_tools import (
    TwinTool,
    TwinToolRegistry,
    ToolInvocationResult,
    ToolCallingTwin,
)


class SumInput(BaseModel):
    a: int
    b: int


class SumOutput(BaseModel):
    result: int


class TestTwinToolRegistry:
    """Test tool registration and invocation."""

    def test_register_and_invoke(self):
        registry = TwinToolRegistry()
        tool = TwinTool(
            name="add",
            description="Add two numbers",
            twin_id="t1",
            handler=lambda a, b: a + b,
        )
        registry.register(tool)
        result = registry.invoke("add", {"a": 2, "b": 3})
        assert result.success is True
        assert result.output == 5
        assert result.tool_name == "add"
        assert result.twin_id == "t1"

    def test_invoke_tool_not_found(self):
        registry = TwinToolRegistry()
        result = registry.invoke("missing", {})
        assert result.success is False
        assert "not found" in result.error

    def test_register_duplicate_raises(self):
        registry = TwinToolRegistry()
        tool = TwinTool(name="add", description="", twin_id="t1", handler=lambda: None)
        registry.register(tool)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(tool)

    def test_list_tools(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(name="a", description="", twin_id="t1", handler=lambda: 1))
        registry.register(TwinTool(name="b", description="", twin_id="t2", handler=lambda: 2))
        tools = registry.list_tools()
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"a", "b"}

    def test_get_tools_for_twin(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(name="a", description="", twin_id="t1", handler=lambda: 1))
        registry.register(TwinTool(name="b", description="", twin_id="t1", handler=lambda: 2))
        registry.register(TwinTool(name="c", description="", twin_id="t2", handler=lambda: 3))
        t1_tools = registry.get_tools_for_twin("t1")
        assert len(t1_tools) == 2
        assert {t.name for t in t1_tools} == {"a", "b"}

    def test_search_tools(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(
            name="summarize", description="Summarize text", twin_id="t1",
            handler=lambda: None, tags=["nlp"],
        ))
        registry.register(TwinTool(
            name="add", description="Add numbers", twin_id="t2",
            handler=lambda: None, tags=["math"],
        ))
        assert len(registry.search_tools("summarize")) == 1
        assert len(registry.search_tools("text")) == 1
        assert len(registry.search_tools("nlp")) == 1
        assert len(registry.search_tools("math")) == 1
        assert len(registry.search_tools("missing")) == 0

    def test_unregister(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(name="x", description="", twin_id="t1", handler=lambda: 1))
        assert "x" in registry
        assert registry.unregister("x") is True
        assert "x" not in registry
        assert registry.unregister("x") is False

    def test_len(self):
        registry = TwinToolRegistry()
        assert len(registry) == 0
        registry.register(TwinTool(name="x", description="", twin_id="t1", handler=lambda: 1))
        assert len(registry) == 1


class TestTwinToolRegistryValidation:
    """Test Pydantic input/output validation."""

    def test_input_validation_passes(self):
        registry = TwinToolRegistry()
        tool = TwinTool(
            name="add",
            description="Add two numbers",
            twin_id="t1",
            handler=lambda a, b: {"result": a + b},
            input_schema=SumInput,
            output_schema=SumOutput,
        )
        registry.register(tool)
        result = registry.invoke("add", {"a": 2, "b": 3})
        assert result.success is True
        assert result.output == {"result": 5}

    def test_input_validation_fails(self):
        registry = TwinToolRegistry()
        tool = TwinTool(
            name="add",
            description="Add two numbers",
            twin_id="t1",
            handler=lambda a, b: a + b,
            input_schema=SumInput,
        )
        registry.register(tool)
        result = registry.invoke("add", {"a": "not_int", "b": 3})
        assert result.success is False
        assert "validation failed" in result.error.lower()

    def test_handler_exception(self):
        registry = TwinToolRegistry()
        def bad_handler():
            raise RuntimeError("oops")
        tool = TwinTool(name="bad", description="", twin_id="t1", handler=bad_handler)
        registry.register(tool)
        result = registry.invoke("bad", {})
        assert result.success is False
        assert "oops" in result.error


class TestToolCallingTwin:
    """Test ToolCallingTwin mixin."""

    def test_call_tool_success(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(
            name="greet", description="", twin_id="t1",
            handler=lambda name: f"Hello {name}",
        ))

        from agents.twin_agent import TwinAgent
        class TestTwin(ToolCallingTwin, TwinAgent):
            pass

        twin = TestTwin(
            "tt1", "Test", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            tool_registry=registry,
        )
        result = twin.call_tool("greet", name="World")
        assert result.success is True
        assert result.output == "Hello World"

    def test_call_tool_not_found(self):
        from agents.twin_agent import TwinAgent
        class TestTwin(ToolCallingTwin, TwinAgent):
            pass

        twin = TestTwin(
            "tt1", "Test", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            tool_registry=TwinToolRegistry(),
        )
        result = twin.call_tool("missing")
        assert result.success is False
        assert "not found" in result.error

    def test_call_tool_no_registry(self):
        from agents.twin_agent import TwinAgent
        class TestTwin(ToolCallingTwin, TwinAgent):
            pass

        twin = TestTwin(
            "tt1", "Test", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            tool_registry=None,
        )
        result = twin.call_tool("anything")
        assert result.success is False
        assert "No tool registry" in result.error

    def test_get_available_tools(self):
        registry = TwinToolRegistry()
        registry.register(TwinTool(
            name="t1", description="", twin_id="x", handler=lambda: 1,
        ))
        from agents.twin_agent import TwinAgent
        class TestTwin(ToolCallingTwin, TwinAgent):
            pass

        twin = TestTwin(
            "tt1", "Test", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            tool_registry=registry,
        )
        tools = twin.get_available_tools()
        assert len(tools) == 1
        assert tools[0].name == "t1"

    def test_propose_tool_call(self):
        from agents.twin_agent import TwinAgent
        class TestTwin(ToolCallingTwin, TwinAgent):
            pass

        twin = TestTwin(
            "tt1", "Test", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            tool_registry=None,
        )
        proposal = twin.propose_tool_call("search", "Need to find papers")
        assert proposal["type"] == "tool_call_proposal"
        assert proposal["tool_name"] == "search"
        assert "Need to find papers" in proposal["reasoning"]



class TestSwarmOrchestratorToolIntegration:
    """Test tool registry wired into SwarmOrchestrator."""

    def test_orchestrator_with_tool_registry(self):
        from agents.swarm_orchestrator import SwarmOrchestrator
        registry = TwinToolRegistry()
        registry.register(TwinTool(
            name="multiply", description="", twin_id="t1",
            handler=lambda a, b: a * b,
        ))
        orch = SwarmOrchestrator(tool_registry=registry)
        result = orch.execute_tool_call("multiply", {"a": 3, "b": 4})
        assert result["success"] is True
        assert result["output"] == 12

    def test_orchestrator_without_tool_registry(self):
        from agents.swarm_orchestrator import SwarmOrchestrator
        orch = SwarmOrchestrator()
        result = orch.execute_tool_call("anything", {})
        assert result["success"] is False
        assert "No tool_registry" in result["error"]

    def test_orchestrator_list_tools(self):
        from agents.swarm_orchestrator import SwarmOrchestrator
        registry = TwinToolRegistry()
        registry.register(TwinTool(
            name="search", description="Search papers", twin_id="t1",
            handler=lambda q: [], tags=["research"],
        ))
        orch = SwarmOrchestrator(tool_registry=registry)
        tools = orch.list_available_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "search"
        assert tools[0]["description"] == "Search papers"

    def test_orchestrator_list_tools_empty(self):
        from agents.swarm_orchestrator import SwarmOrchestrator
        orch = SwarmOrchestrator()
        assert orch.list_available_tools() == []
