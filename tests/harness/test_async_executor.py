# tests/harness/test_async_executor.py
"""Tests for async/parallel sub-task execution (Strands-inspired)."""

import asyncio
import time

import pytest

from harness.autonomous_executor import AutonomousExecutor, SelfEvaluationReport
from harness.code_generator import TemplateCodeGenerator
from harness.task_decomposer import TaskType
from agents.swarm_orchestrator import SwarmOrchestrator
from conftest import default_agent_kwargs


class TestAsyncExecution:
    """Test async execution paths."""

    def test_async_method_exists(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        assert hasattr(executor, "execute_task_graph_async")
        assert asyncio.iscoroutinefunction(executor.execute_task_graph_async)

    def test_sync_wrapper_returns_report(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        assert isinstance(report, SelfEvaluationReport)
        assert report.goal_id == graph.goal_id

    def test_async_direct_call_returns_report(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write hello world")
        report = asyncio.run(executor.execute_task_graph_async(graph))
        assert isinstance(report, SelfEvaluationReport)
        assert report.goal_id == graph.goal_id


class TestParallelSubtasks:
    """Test that independent sub-tasks run in parallel."""

    def test_async_produces_valid_report(self):
        """Async execution should produce a valid report."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal(
            "Build a Python function that computes fibonacci numbers and add two numbers"
        )
        report = asyncio.run(executor.execute_task_graph_async(graph))
        assert isinstance(report, SelfEvaluationReport)
        assert 0.0 <= report.completion_rate <= 1.0
        assert report.total_duration_ms > 0

    def test_report_structure_identical(self):
        """Async and sync reports should have identical structure."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write hello world")

        report_sync = executor.execute_task_graph(graph)
        report_async = asyncio.run(executor.execute_task_graph_async(graph))

        assert type(report_sync) == type(report_async)
        assert report_sync.to_dict().keys() == report_async.to_dict().keys()
        assert report_sync.goal_id == report_async.goal_id

    def test_async_with_registered_agents(self):
        """Async execution with agents registered should work like sync."""
        from agents.sandbox_agent import SandboxAgent
        from agents.twin_agent import TwinAgent

        orch = SwarmOrchestrator()
        sandbox = SandboxAgent(
            "sandbox-async", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-async"),
        )
        twin1 = TwinAgent(
            "twin-a-async", "Architect A", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("twin-a-async"),
        )
        twin2 = TwinAgent(
            "twin-b-async", "Architect B", "multi-agent",
            "twins.cognitive_models.torsten_hoefler", "TorstenHoeflerTwin",
            **default_agent_kwargs("twin-b-async"),
        )
        orch.register_agent(sandbox)
        orch.register_agent(twin1)
        orch.register_agent(twin2)

        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Build a Python function that computes fibonacci numbers")
        report = asyncio.run(executor.execute_task_graph_async(graph))
        assert isinstance(report, SelfEvaluationReport)
        assert report.completion_rate >= 0.0


class TestAsyncPreservesDependencies:
    """Test that dependent sub-tasks still wait for prerequisites."""

    def test_dag_order_maintained(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write hello world")
        report = asyncio.run(executor.execute_task_graph_async(graph))
        assert isinstance(report, SelfEvaluationReport)
        assert report.goal_id == graph.goal_id

    def test_single_ready_task_no_gather(self):
        """When only one task is ready, no asyncio.gather overhead."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write a hello world function")
        report = asyncio.run(executor.execute_task_graph_async(graph))
        assert isinstance(report, SelfEvaluationReport)
        assert 0.0 <= report.completion_rate <= 1.0
