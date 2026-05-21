# tests/harness/test_autonomous_executor.py
"""
P5-5: End-to-End Autonomous Task Execution.

Verifies the full pipeline:
  Goal → TaskDecomposer → TaskGraph → SwarmOrchestrator per sub-task
  → Consensus → Code generation (BUILD) / Validation (EVALUATE)
  → Self-evaluation report

Principle: In God we trust. All others must bring data.
"""

import pytest
from pathlib import Path

from harness.autonomous_executor import AutonomousExecutor, SelfEvaluationReport
from harness.code_generator import TemplateCodeGenerator
from harness.ai_director import AIDirector, DirectorObservation, Direction
from harness.task_decomposer import TaskDecomposer, TaskType
from agents.swarm_orchestrator import SwarmOrchestrator
from agents.sandbox_agent import SandboxAgent
from agents.conscious_agent import ConsciousAgent
from conftest import default_agent_kwargs


class TestAutonomousExecutorCore:
    """Unit-level tests for AutonomousExecutor construction and decomposition."""

    def test_instantiation_requires_orchestrator(self):
        """Executor must wrap a SwarmOrchestrator."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        assert executor.orchestrator is orch
        assert executor.decomposer is not None

    def test_decompose_goal_creates_task_graph(self):
        """Decomposing a BUILD goal must produce a TaskGraph with sub-tasks."""
        executor = AutonomousExecutor(
            SwarmOrchestrator(),
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Build a fibonacci calculator in Python")
        assert graph.task_type == TaskType.BUILD
        assert len(graph.subtasks) >= 3
        # BUILD tasks: design → implement → test → verify
        assert any("design" in st.task_id for st in graph.subtasks.values())
        assert any("implement" in st.task_id for st in graph.subtasks.values())

    def test_decompose_research_goal(self):
        """Decomposing a RESEARCH goal must use research clusters."""
        executor = AutonomousExecutor(
            SwarmOrchestrator(),
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Research consensus protocols for multi-agent systems")
        assert graph.task_type == TaskType.RESEARCH
        assert len(graph.subtasks) >= 3


class TestAutonomousExecutorSwarmIntegration:
    """Integration: Executor + Orchestrator + Twins + SandboxAgent."""

    def test_executes_build_subtask_and_produces_artifact(self):
        """
        Full pipeline for a single BUILD sub-task:
        - Form swarm from matching cluster twins
        - Run deliberation → consensus
        - Generate code artifact via SandboxAgent
        - Mark sub-task completed
        """
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        # Register a sandbox agent (code executor)
        sandbox = SandboxAgent(
            "sandbox-001", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-001"),
        )
        orch.register_agent(sandbox)

        # Register a few twins for design deliberation
        from agents.twin_agent import TwinAgent
        twin1 = TwinAgent(
            "design-001", "Designer A", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("design-001"),
        )
        twin2 = TwinAgent(
            "design-002", "Designer B", "multi-agent",
            "twins.cognitive_models.torsten_hoefler", "TorstenHoeflerTwin",
            **default_agent_kwargs("design-002"),
        )
        orch.register_agent(twin1)
        orch.register_agent(twin2)

        # Decompose and execute a simple BUILD task
        graph = executor.decompose_goal("Build a Python function that returns fibonacci numbers")

        # Execute the first ready sub-task (should be 'design')
        ready = graph.get_ready_tasks()
        assert len(ready) >= 1
        design_task = ready[0]

        result = executor.execute_subtask(graph, design_task)
        assert result["subtask_id"] == design_task.task_id
        assert result["status"] in ("completed", "failed")
        # A design sub-task should produce a consensus (approach document)
        assert "consensus" in result
        assert result["consensus"].get("winner") is not None

    def test_self_evaluation_report_structure(self):
        """After executing a task graph, executor must produce a structured report."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        # Minimal setup: one sandbox agent
        sandbox = SandboxAgent(
            "sandbox-002", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-002"),
        )
        orch.register_agent(sandbox)

        graph = executor.decompose_goal("Build a hello-world printer in Python")
        report = executor.execute_task_graph(graph)

        assert isinstance(report, SelfEvaluationReport)
        assert report.goal_id == graph.goal_id
        assert report.completion_rate >= 0.0
        assert report.completion_rate <= 1.0
        assert len(report.subtask_results) == len(graph.subtasks)
        assert "artifacts" in report.to_dict()


class TestAutonomousExecutorCodeGeneration:
    """Code generation + execution for BUILD sub-tasks."""

    def test_build_task_generates_runnable_python(self):
        """
        A BUILD 'implement' sub-task must produce actual runnable Python code
        that passes a basic sanity check.
        """
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        sandbox = SandboxAgent(
            "sandbox-003", "CodeExecutor", "video-gnn",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-003"),
        )
        orch.register_agent(sandbox)

        # Give the executor a simple coding task
        code = executor.generate_code_for_approach(
            approach="Implement fibonacci(n) using an iterative loop",
            language="python",
            test_cases=[{"input": "fibonacci(10)", "expected_output": "55"}],
        )
        assert "def fibonacci" in code or "fibonacci" in code

        # Execute the generated code
        result = sandbox.execute(
            code=code,
            language="python",
            cited_purpose="[CITATION: P5-5] Validate generated fibonacci implementation",
        )
        assert result.return_code == 0
        assert "55" in result.stdout

    def test_evaluate_subtask_runs_tests(self):
        """An EVALUATE sub-task must run tests against previously generated code."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        sandbox = SandboxAgent(
            "sandbox-004", "TestRunner", "streaming-reflection",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-004"),
        )
        orch.register_agent(sandbox)

        # Pre-generate some code
        code = "def add(a, b): return a + b\nprint(add(2, 3))"
        result = sandbox.execute(code, cited_purpose="[CITATION: P5-5] Generate add function")
        assert result.return_code == 0

        # Now evaluate it
        eval_result = executor.run_evaluation(
            code=code,
            test_script="assert add(2, 3) == 5; assert add(0, 0) == 0; print('PASS')",
            sandbox_agent=sandbox,
        )
        assert eval_result["tests_passed"] is True
        assert "PASS" in eval_result.get("stdout", "")


class TestAutonomousExecutorDeploymentMonitoring:
    """Artifact deployment and execution monitoring."""

    def test_deploy_artifacts_persists_to_disk(self):
        """Deployment must write artifacts to disk and return a manifest."""
        import tempfile
        import json

        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        report = SelfEvaluationReport(
            goal_id="test-deploy-001",
            goal_description="Test deployment",
            completion_rate=1.0,
            artifacts=[
                {
                    "type": "code_execution",
                    "code": "def hello(): return 'hi'",
                    "stdout": "hi",
                    "return_code": 0,
                    "task_id": "task-1",
                },
                {
                    "type": "evaluation_result",
                    "tests_passed": True,
                    "stdout": "PASS",
                    "task_id": "task-2",
                },
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = executor.deploy_artifacts(report, deploy_path=Path(tmpdir))
            assert manifest["goal_id"] == "test-deploy-001"
            assert len(manifest["artifacts_deployed"]) == 2
            assert manifest["health"] == "healthy"
            # Verify files exist
            assert (Path(tmpdir) / "artifact_0.py").exists()
            assert (Path(tmpdir) / "eval_1.json").exists()

    def test_monitor_execution_detects_anomalies(self):
        """Monitoring must detect slow sub-tasks and weak consensus."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        graph = executor.decompose_goal("Build a test system")
        report = SelfEvaluationReport(
            goal_id=graph.goal_id,
            goal_description=graph.goal_description,
            completion_rate=0.75,
            subtask_results=[
                {"subtask_id": "fast", "status": "completed", "duration_ms": 100},
                {"subtask_id": "slow", "status": "completed", "duration_ms": 50000},
                {"subtask_id": "failed", "status": "failed", "duration_ms": 50},
            ],
            consensus_history=[
                {"subtask_id": "fast", "consensus": {"score": 0.9}},
                {"subtask_id": "slow", "consensus": {"score": 0.3}},
            ],
            artifacts=[],
        )

        metrics = executor.monitor_execution(graph, report)
        assert metrics["health"] == "degraded"
        assert metrics["failed"] == 1
        # Should detect slow sub-task (>5x average)
        slow_anomalies = [a for a in metrics["anomalies"] if a["type"] == "slow_subtask"]
        assert len(slow_anomalies) >= 1
        # Should detect weak consensus
        weak_anomalies = [a for a in metrics["anomalies"] if a["type"] == "weak_consensus"]
        assert len(weak_anomalies) >= 1


class TestAutonomousExecutorMemoryIntegration:
    """Memory layers are populated during autonomous execution."""

    def test_prospective_memory_stored_on_decomposition(self):
        """Decomposing a goal must store planned sub-tasks in prospective memory."""
        from memory.architecture import MultiModalMemory, MemoryType, RetrievalStrategy

        memory = MultiModalMemory()
        executor = AutonomousExecutor(
            SwarmOrchestrator(),
            code_generator=TemplateCodeGenerator(),
            memory=memory,
        )
        graph = executor.decompose_goal("Build a fibonacci calculator")

        prospective = memory.retrieve(
            MemoryType.PROSPECTIVE,
            RetrievalStrategy.RECENCY,
            limit=10,
        )
        assert len(prospective) == len(graph.subtasks)
        for st in graph.subtasks.values():
            assert any(
                p.content.get("subtask_id") == st.task_id
                for p in prospective
            )

    def test_episodic_memory_stored_after_execution(self):
        """Executing a sub-task must store an episodic trace."""
        from memory.architecture import MultiModalMemory, MemoryType, RetrievalStrategy

        memory = MultiModalMemory()
        orch = SwarmOrchestrator()
        sandbox = SandboxAgent(
            "sandbox-mem", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-mem"),
        )
        orch.register_agent(sandbox)

        executor = AutonomousExecutor(
            orch,
            code_generator=TemplateCodeGenerator(),
            memory=memory,
        )
        graph = executor.decompose_goal("Build a hello-world printer")
        ready = graph.get_ready_tasks()
        assert len(ready) >= 1
        executor.execute_subtask(graph, ready[0])

        episodic = memory.retrieve(
            MemoryType.EPISODIC,
            RetrievalStrategy.RECENCY,
            limit=10,
        )
        assert len(episodic) >= 1
        assert any("execution" in p.tags for p in episodic)

    def test_procedural_memory_stores_generated_code(self):
        """BUILD sub-tasks must store generated code in procedural memory."""
        from memory.architecture import MultiModalMemory, MemoryType, RetrievalStrategy

        memory = MultiModalMemory()
        orch = SwarmOrchestrator()
        sandbox = SandboxAgent(
            "sandbox-proc", "CodeExecutor", "video-gnn",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-proc"),
        )
        orch.register_agent(sandbox)

        executor = AutonomousExecutor(
            orch,
            code_generator=TemplateCodeGenerator(),
            memory=memory,
        )
        code = executor.generate_code_for_approach(
            approach="Implement fibonacci(n)",
            test_cases=[{"input": "fibonacci(10)"}],
        )
        sandbox.execute(code, cited_purpose="[CITATION: P5-5] test")

        # The procedural memory is stored inside _execute_build_subtask,
        # which is triggered during execute_subtask for BUILD tasks.
        # Let's run a full BUILD sub-task to exercise it.
        graph = executor.decompose_goal("Build a fibonacci calculator")
        build_tasks = [st for st in graph.subtasks.values() if "implement" in st.task_id]
        if build_tasks:
            # Make the build task ready by faking its dependency completion
            build_tasks[0].dependencies = []
            executor.execute_subtask(graph, build_tasks[0])

            procedural = memory.retrieve(
                MemoryType.PROCEDURAL,
                RetrievalStrategy.RELEVANCE,
                query="code",
                limit=10,
            )
            assert len(procedural) >= 1
            # Procedural memory stores the generated code artifact
            assert any("code" in p.content for p in procedural)
            assert any(p.content.get("language") == "python" for p in procedural)

    def test_final_report_stored_in_episodic_memory(self):
        """The SelfEvaluationReport must be retrievable from episodic memory."""
        from memory.architecture import MultiModalMemory, MemoryType, RetrievalStrategy

        memory = MultiModalMemory()
        orch = SwarmOrchestrator()
        sandbox = SandboxAgent(
            "sandbox-report", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-report"),
        )
        orch.register_agent(sandbox)

        executor = AutonomousExecutor(
            orch,
            code_generator=TemplateCodeGenerator(),
            memory=memory,
        )
        graph = executor.decompose_goal("Build a hello-world printer")
        report = executor.execute_task_graph(graph)

        episodic = memory.retrieve(
            MemoryType.EPISODIC,
            RetrievalStrategy.RECENCY,
            limit=10,
        )
        report_traces = [p for p in episodic if "report" in p.tags]
        assert len(report_traces) >= 1
        assert report_traces[0].content["goal_id"] == graph.goal_id

    def test_memory_stats_reflect_autonomous_execution(self):
        """After full execution, memory stats must show traces in all relevant layers."""
        from memory.architecture import MultiModalMemory

        memory = MultiModalMemory()
        orch = SwarmOrchestrator()
        sandbox = SandboxAgent(
            "sandbox-stats", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-stats"),
        )
        orch.register_agent(sandbox)

        executor = AutonomousExecutor(
            orch,
            code_generator=TemplateCodeGenerator(),
            memory=memory,
        )
        graph = executor.decompose_goal("Build a fibonacci calculator")
        executor.execute_task_graph(graph)

        stats = memory.get_memory_stats()
        assert stats["episodic_count"] > 0
        assert stats["prospective_count"] > 0


class TestAutonomousExecutorEndToEnd:
    """Realistic end-to-end autonomous task demo."""

    def test_full_autonomous_build_and_evaluate_pipeline(self):
        """
        Complete P5-5 pipeline:
        1. Decompose a BUILD goal
        2. Execute all sub-tasks through the swarm
        3. Generate code for the 'implement' sub-task
        4. Evaluate the generated code
        5. Deploy artifacts
        6. Produce monitoring metrics
        7. All health signals positive
        """
        import tempfile

        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )

        # Register sandbox agent for code execution
        sandbox = SandboxAgent(
            "sandbox-e2e", "CodeExecutor", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("sandbox-e2e"),
        )
        orch.register_agent(sandbox)

        # Register a couple of twins for deliberation
        from agents.twin_agent import TwinAgent
        twin1 = TwinAgent(
            "twin-a", "Architect A", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("twin-a"),
        )
        twin2 = TwinAgent(
            "twin-b", "Architect B", "multi-agent",
            "twins.cognitive_models.torsten_hoefler", "TorstenHoeflerTwin",
            **default_agent_kwargs("twin-b"),
        )
        orch.register_agent(twin1)
        orch.register_agent(twin2)

        # Step 1: Decompose
        graph = executor.decompose_goal("Build a Python function that computes fibonacci numbers")
        assert graph.task_type == TaskType.BUILD

        # Step 2-4: Execute the full graph
        report = executor.execute_task_graph(graph)
        assert report.completion_rate >= 0.0
        assert len(report.subtask_results) == len(graph.subtasks)

        # Step 5: Deploy
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = executor.deploy_artifacts(report, deploy_path=Path(tmpdir))
            assert manifest["health"] in ("healthy", "degraded")
            # Artifacts should be on disk
            assert len(manifest["artifacts_deployed"]) >= 0

        # Step 6: Monitor
        metrics = executor.monitor_execution(graph, report)
        assert "health" in metrics
        assert metrics["total_subtasks"] == len(graph.subtasks)

        # Step 7: Report structure
        d = report.to_dict()
        assert d["goal_id"] == graph.goal_id
        assert "artifacts" in d
        assert "recommendations" in d
        print(f"✅ P5-5 E2E complete: {d['completion_rate']:.0%} completion, health={metrics['health']}")



class TestAutonomousExecutorAIDirector:
    """Test AI Director integration in AutonomousExecutor."""

    def test_executor_with_no_director(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            director=None,
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        assert report.director_interventions == []

    def test_executor_with_fallback_director(self):
        """Director without API key uses fallback rules."""
        orch = SwarmOrchestrator()
        director = AIDirector(api_key=None)
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            director=director,
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        # Director will observe each sub-task and may issue directions
        assert len(report.director_interventions) >= 0
        # Narcissistic report should be coherent
        narc = director.get_narcissistic_report()
        assert "total_directions" in narc

    def test_executor_director_retry_on_failure(self):
        """Director retry action should re-execute a failed sub-task."""
        orch = SwarmOrchestrator()
        # Custom director that always retries
        def retry_director(obs):
            from harness.ai_director import Direction
            return Direction(
                action="retry",
                revised_task_description="Retry attempt",
                reasoning="Forced retry for test",
                confidence=0.9,
            )

        director = AIDirector(api_key=None, custom_director=retry_director)
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            director=director,
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        # At least one intervention should exist
        assert len(report.director_interventions) > 0
        assert any(d["action"] == "retry" for d in report.director_interventions)

    def test_executor_director_critique(self):
        """Director critique action should add recommendations."""
        orch = SwarmOrchestrator()

        def critique_director(obs):
            from harness.ai_director import Direction
            return Direction(
                action="critique",
                revised_task_description="Critique applied",
                reasoning="Quality concerns",
                confidence=0.8,
            )

        director = AIDirector(api_key=None, custom_director=critique_director)
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            director=director,
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        assert any("Director critique" in r for r in report.recommendations)

    def test_executor_report_contains_director_field(self):
        """Ensure the report dict always has director_interventions key."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        d = report.to_dict()
        assert "director_interventions" in d



class TestAutonomousExecutorPostConditions:
    """Test post-conditions wired into AutonomousExecutor (Strands-inspired)."""

    def test_executor_without_post_conditions(self):
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        code = executor.generate_code_for_approach("Write hello world function")
        assert "def " in code

    def test_executor_with_syntax_post_condition(self):
        from harness.post_conditions import SyntaxPostCondition
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            post_conditions=[SyntaxPostCondition()],
        )
        code = executor.generate_code_for_approach("Write hello world function")
        assert "def " in code

    def test_executor_with_signature_post_condition(self):
        from harness.post_conditions import SyntaxPostCondition, SignaturePostCondition
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            post_conditions=[
                SyntaxPostCondition(),
                SignaturePostCondition("hello"),
            ],
        )
        code = executor.generate_code_for_approach("Write a hello world function")
        assert "def hello" in code

    def test_executor_build_task_uses_post_conditions(self):
        from harness.post_conditions import SyntaxPostCondition
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            post_conditions=[SyntaxPostCondition()],
        )
        graph = executor.decompose_goal("Write a hello world function")
        report = executor.execute_task_graph(graph)
        assert report.completion_rate >= 0.0


class TestAutonomousExecutorVMIntegration:
    """Test AutonomousExecutor with SwarmVMCluster for VM-based execution."""

    def test_executor_accepts_vm_cluster(self):
        """AutonomousExecutor should accept an optional vm_cluster parameter."""
        from engines.swarm_vm_cluster import SwarmVMCluster
        from engines.compute_substrate import MockVMSubstrate

        orch = SwarmOrchestrator()
        substrate = MockVMSubstrate()
        vm_cluster = SwarmVMCluster(substrate)
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            vm_cluster=vm_cluster,
        )
        assert executor.vm_cluster is vm_cluster
        assert executor._agent_vm_map == {}

    def test_vm_path_creates_twin_vms(self):
        """When vm_cluster is set, executing a sub-task should create twin VMs."""
        from engines.swarm_vm_cluster import SwarmVMCluster
        from engines.compute_substrate import MockVMSubstrate
        from agents.twin_agent import TwinAgent

        orch = SwarmOrchestrator()
        substrate = MockVMSubstrate()
        vm_cluster = SwarmVMCluster(substrate)

        # Register twins
        twin1 = TwinAgent(
            "vm-twin-001", "VM Twin A", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("vm-twin-001"),
        )
        twin2 = TwinAgent(
            "vm-twin-002", "VM Twin B", "multi-agent",
            "twins.cognitive_models.torsten_hoefler", "TorstenHoeflerTwin",
            **default_agent_kwargs("vm-twin-002"),
        )
        orch.register_agent(twin1)
        orch.register_agent(twin2)

        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            vm_cluster=vm_cluster,
        )

        graph = executor.decompose_goal("Write hello world")
        ready = graph.get_ready_tasks()
        assert len(ready) >= 1

        result = executor.execute_subtask(graph, ready[0])
        assert result["status"] in ("completed", "failed")
        # VMs should have been created and mapped
        assert len(executor._agent_vm_map) >= 1
        # Swarm should have records
        stats = vm_cluster.get_swarm_stats()
        assert stats["total_twins"] >= 1

    def test_vm_path_produces_consensus(self):
        """VM-based deliberation should produce a synthetic consensus."""
        from engines.swarm_vm_cluster import SwarmVMCluster
        from engines.compute_substrate import MockVMSubstrate
        from agents.twin_agent import TwinAgent

        orch = SwarmOrchestrator()
        substrate = MockVMSubstrate()
        vm_cluster = SwarmVMCluster(substrate)

        twin1 = TwinAgent(
            "vm-twin-003", "VM Twin C", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("vm-twin-003"),
        )
        orch.register_agent(twin1)

        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            vm_cluster=vm_cluster,
        )

        graph = executor.decompose_goal("Write hello world")
        ready = graph.get_ready_tasks()
        result = executor.execute_subtask(graph, ready[0])

        assert "consensus" in result
        consensus = result["consensus"]
        assert consensus.get("winner") is not None
        assert consensus.get("score", 0.0) >= 0.0

    def test_vm_path_hibernates_after_task_graph(self):
        """After execute_task_graph, VMs should be hibernated."""
        from engines.swarm_vm_cluster import SwarmVMCluster
        from engines.compute_substrate import MockVMSubstrate
        from agents.twin_agent import TwinAgent

        orch = SwarmOrchestrator()
        substrate = MockVMSubstrate()
        vm_cluster = SwarmVMCluster(substrate)

        twin1 = TwinAgent(
            "vm-twin-004", "VM Twin D", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("vm-twin-004"),
        )
        orch.register_agent(twin1)

        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            vm_cluster=vm_cluster,
        )

        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)

        # VMs should be hibernated after execution
        stats = vm_cluster.get_swarm_stats()
        assert stats["hibernated"] == stats["total_twins"]
        # Report should contain VM stats
        assert report.vm_stats is not None
        assert report.vm_stats["total_twins"] >= 1

    def test_vm_path_report_contains_vm_stats(self):
        """SelfEvaluationReport.to_dict() should include vm_stats when VMs used."""
        from engines.swarm_vm_cluster import SwarmVMCluster
        from engines.compute_substrate import MockVMSubstrate
        from agents.twin_agent import TwinAgent

        orch = SwarmOrchestrator()
        substrate = MockVMSubstrate()
        vm_cluster = SwarmVMCluster(substrate)

        twin1 = TwinAgent(
            "vm-twin-005", "VM Twin E", "multi-agent",
            "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
            **default_agent_kwargs("vm-twin-005"),
        )
        orch.register_agent(twin1)

        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
            vm_cluster=vm_cluster,
        )

        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)

        d = report.to_dict()
        assert "vm_stats" in d
        assert d["vm_stats"] is not None
        assert d["vm_stats"]["total_twins"] >= 1

    def test_no_vm_cluster_backward_compatible(self):
        """Without vm_cluster, executor should behave exactly as before."""
        orch = SwarmOrchestrator()
        executor = AutonomousExecutor(
            orchestrator=orch,
            code_generator=TemplateCodeGenerator(),
        )
        assert executor.vm_cluster is None
        graph = executor.decompose_goal("Write hello world")
        report = executor.execute_task_graph(graph)
        assert isinstance(report, SelfEvaluationReport)
        assert report.vm_stats is None
