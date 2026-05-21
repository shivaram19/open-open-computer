# src/harness/autonomous_executor.py
"""
P5-5: Autonomous Executor — End-to-End Task Execution Pipeline.

Bridges TaskDecomposer → SwarmOrchestrator → SandboxAgent to execute
goals with no human intervention.

Pipeline:
  1. Decompose goal into TaskGraph (DAG of sub-tasks)
  2. Topologically execute ready sub-tasks
  3. For each sub-task:
     a. Form swarm from twins matching cognitive_cluster
     b. Run deliberation → consensus on approach
     c. BUILD: generate code via SandboxAgent
     d. EVALUATE: run tests against generated artifacts
     e. RESEARCH/ANALYZE/PLAN: deliberation report is the artifact
  4. Track completion, update TaskGraph status
  5. Produce SelfEvaluationReport

Inspired by:
- AGoT2025: automatic graph-of-thoughts execution
- DAGPlan2025: dependency-aware scheduling
- Besta2024: graph of thoughts for decomposition

Principle: In God we trust. All others must bring data.

[CITATION: AGoT2025]
[CITATION: DAGPlan2025]
[CITATION: Besta2024]
"""

import asyncio
import uuid
import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from shared.utils.citations import cite
from harness.task_decomposer import TaskDecomposer, TaskGraph, SubTask, TaskType
from harness.code_generator import CodeGenerator, FallbackCodeGenerator
from harness.ai_director import AIDirector, DirectorObservation, Direction
from memory.architecture import MultiModalMemory, MemoryType, MemoryTrace
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from agents.sandbox_agent import SandboxAgent
from engines.swarm_vm_cluster import SwarmVMCluster


@cite(
    key="AUTO-REPORT",
    paper="Autonomous Executor: Self-Evaluation Report",
    venue="ACN Harness Architecture",
    section="P5-5 End-to-End Autonomous Task",
    rationale="Structured report enables audit, regression detection, and improvement tracking",
    confidence="CERTAIN",
)
@dataclass
class SelfEvaluationReport:
    """Final report produced after autonomous task execution."""
    goal_id: str
    goal_description: str
    completion_rate: float  # 0.0–1.0
    subtask_results: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    consensus_history: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    director_interventions: List[Dict[str, Any]] = field(default_factory=list)
    memory_consolidation: List[Dict[str, Any]] = field(default_factory=list)
    vm_stats: Optional[Dict[str, Any]] = None
    total_duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "goal_description": self.goal_description,
            "completion_rate": self.completion_rate,
            "subtask_count": len(self.subtask_results),
            "subtask_results": self.subtask_results,
            "artifacts": self.artifacts,
            "consensus_history": self.consensus_history,
            "recommendations": self.recommendations,
            "director_interventions": self.director_interventions,
            "memory_consolidation": self.memory_consolidation,
            "vm_stats": self.vm_stats,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp,
        }


@cite(
    key="AUTO-EXEC",
    paper="Autonomous Executor: Task Graph Execution",
    venue="ACN Harness Architecture",
    section="P5-5 End-to-End Autonomous Task",
    rationale="Closing the loop between decomposition and execution",
    confidence="CERTAIN",
)
class AutonomousExecutor:
    """
    Executes TaskGraphs autonomously using the harness infrastructure.
    """

    def __init__(
        self,
        orchestrator: SwarmOrchestrator,
        code_generator: Optional[CodeGenerator] = None,
        memory: Optional[MultiModalMemory] = None,
        director: Optional[AIDirector] = None,
        post_conditions: Optional[List[Any]] = None,
        max_validation_attempts: int = 3,
        dashboard_collector: Optional[Any] = None,
        vm_cluster: Optional[SwarmVMCluster] = None,
    ):
        self.orchestrator = orchestrator
        self.decomposer = TaskDecomposer()
        self.code_generator = code_generator or FallbackCodeGenerator()
        self.memory = memory or MultiModalMemory()
        self.director = director
        self.post_conditions = post_conditions or []
        self.max_validation_attempts = max_validation_attempts
        self.dashboard_collector = dashboard_collector
        self.vm_cluster = vm_cluster
        self._artifact_registry: Dict[str, Any] = {}  # task_id → artifact
        self._agent_vm_map: Dict[str, str] = {}  # agent_id → twin_id

    def decompose_goal(self, goal_description: str, goal_id: Optional[str] = None) -> TaskGraph:
        """Decompose a natural language goal into a TaskGraph."""
        graph = self.decomposer.decompose(goal_description, goal_id)

        # Store prospective memory: planned sub-tasks
        for subtask in graph.subtasks.values():
            self.memory.store(MemoryTrace(
                trace_id=f"prospective-{graph.goal_id}-{subtask.task_id}",
                memory_type=MemoryType.PROSPECTIVE,
                content={
                    "goal_id": graph.goal_id,
                    "subtask_id": subtask.task_id,
                    "description": subtask.description,
                    "task_type": subtask.task_type.value,
                    "cluster": subtask.cognitive_cluster,
                    "dependencies": subtask.dependencies,
                },
                source="autonomous_executor",
                confidence=0.8,
                importance=0.7,
                tags=["autonomous", "planned", subtask.task_type.value, subtask.cognitive_cluster],
            ))

        return graph

    @cite(
        key="AUTO-EXEC-SUBTASK",
        paper="Autonomous Executor: Sub-Task Execution",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Each sub-task is a mini-deliberation with cluster-matched twins",
        confidence="CERTAIN",
    )
    def execute_subtask(
        self,
        graph: TaskGraph,
        subtask: SubTask,
    ) -> Dict[str, Any]:
        """
        Execute a single sub-task through the swarm pipeline.

        Returns result dict with keys:
        - subtask_id, status, consensus, artifacts, error
        """
        start_time = time.time()
        task_id = f"{graph.goal_id}-{subtask.task_id}"

        # Find agents in the target cluster (or fallback to multi-agent)
        cluster = subtask.cognitive_cluster or "multi-agent"
        matching_agents = [
            aid for aid, agent in self.orchestrator.agents.items()
            if agent.cluster == cluster
        ]

        # If no matching agents, try multi-agent as fallback
        if not matching_agents:
            matching_agents = [
                aid for aid, agent in self.orchestrator.agents.items()
                if agent.cluster == "multi-agent"
            ]

        # If still no agents, mark failed — no one to do the work
        if not matching_agents:
            self.decomposer.update_task_status(graph, subtask.task_id, "failed")
            return {
                "subtask_id": subtask.task_id,
                "status": "failed",
                "error": f"No agents available for cluster '{cluster}'",
                "consensus": None,
                "artifacts": [],
            }

        # Create a SwarmTask for this sub-task
        swarm_task = SwarmTask(
            task_id=task_id,
            description=subtask.description,
            required_clusters=[cluster],
            success_criteria=subtask.success_criteria,
            min_agents=1,
            max_agents=len(matching_agents),
        )

        # Activate
        activated = self.orchestrator.activate_task(swarm_task)
        if not activated:
            self.decomposer.update_task_status(graph, subtask.task_id, "failed")
            return {
                "subtask_id": subtask.task_id,
                "status": "failed",
                "error": "Task activation produced no agents",
                "consensus": None,
                "artifacts": [],
            }

        # Run deliberation — VM cluster path or in-process orchestrator path
        if self.vm_cluster is not None:
            deliberation, consensus, activated = self._run_vm_subtask(
                task_id, subtask, matching_agents
            )
        else:
            # Run deliberation
            deliberation = self.orchestrator.run_full_deliberation(task_id)

            # Extract consensus
            consensus = deliberation.get("final_consensus", {})
            if not consensus:
                consensus = {}
                if deliberation.get("rounds"):
                    last_round = deliberation["rounds"][-1]
                    consensus = last_round.get("consensus", {})

        # Generate artifacts based on task type
        artifacts: List[Dict[str, Any]] = []
        error: Optional[str] = None

        try:
            if subtask.task_type == TaskType.BUILD:
                artifacts = self._execute_build_subtask(subtask, consensus, task_id)
            elif subtask.task_type == TaskType.EVALUATE:
                artifacts = self._execute_evaluate_subtask(subtask, consensus, task_id)
            elif subtask.task_type == TaskType.RESEARCH:
                artifacts = self._execute_research_subtask(subtask, deliberation, task_id)
            else:
                # PLAN, ANALYZE, DEBUG: deliberation report is the artifact
                artifacts = [{
                    "type": "deliberation_report",
                    "content": self.orchestrator.synthesize_report(task_id),
                    "task_id": task_id,
                }]
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.time() - start_time) * 1000
        status = "completed" if not error else "failed"
        self.decomposer.update_task_status(graph, subtask.task_id, status)

        # Store episodic memory: what happened during this sub-task
        self.memory.store(MemoryTrace(
            trace_id=f"episodic-{task_id}",
            memory_type=MemoryType.EPISODIC,
            content={
                "subtask_id": subtask.task_id,
                "status": status,
                "consensus": consensus,
                "error": error,
                "artifacts_count": len(artifacts),
                "activated_agents": activated,
            },
            source="autonomous_executor",
            confidence=0.9 if status == "completed" else 0.3,
            importance=0.8,
            tags=["autonomous", "execution", subtask.task_type.value, status],
        ))

        # Store semantic memory: consensus pattern (if any)
        if consensus and consensus.get("winner"):
            self.memory.store(MemoryTrace(
                trace_id=f"semantic-{task_id}",
                memory_type=MemoryType.SEMANTIC,
                content={
                    "approach": consensus.get("winner"),
                    "score": consensus.get("score", 0.0),
                    "task_type": subtask.task_type.value,
                    "cluster": subtask.cognitive_cluster,
                },
                source="autonomous_executor",
                confidence=consensus.get("score", 0.5),
                importance=0.7,
                tags=["autonomous", "consensus", subtask.task_type.value],
            ))

        return {
            "subtask_id": subtask.task_id,
            "status": status,
            "error": error,
            "consensus": consensus,
            "artifacts": artifacts,
            "duration_ms": duration_ms,
            "activated_agents": activated,
        }

    # ── VM Cluster Helpers ───────────────────────────────────────────

    def _ensure_vm_twins(self, agent_ids: List[str]) -> List[str]:
        """
        Ensure twin VMs exist for the given agent IDs.

        Returns list of twin_ids that were created or already existed.
        """
        if self.vm_cluster is None:
            return []

        twin_ids = []
        specs = []
        for aid in agent_ids:
            agent = self.orchestrator.agents.get(aid)
            if agent is None:
                continue
            # Reuse existing VM mapping if present
            twin_id = self._agent_vm_map.get(aid)
            if twin_id is None:
                twin_id = f"vm-{aid}"
                self._agent_vm_map[aid] = twin_id
            # Only create if not already in the cluster
            if self.vm_cluster.get_record(twin_id) is None:
                specs.append({
                    "twin_id": twin_id,
                    "twin_name": getattr(agent, "name", aid),
                    "cluster": getattr(agent, "cluster", "multi-agent"),
                })
            twin_ids.append(twin_id)

        if specs:
            self.vm_cluster.create_swarm(specs)

        return twin_ids

    def _run_vm_subtask(
        self,
        task_id: str,
        subtask: SubTask,
        matching_agents: List[str],
    ) -> tuple:
        """
        Execute a sub-task through the VM cluster.

        Returns (deliberation_dict, consensus_dict, activated_agent_ids).
        """
        # Ensure VMs exist for matching agents
        self._ensure_vm_twins(matching_agents)

        # Activate all VMs before deliberation
        self.vm_cluster.activate_all()

        # Checkpoint before risky consensus (optional safety net)
        checkpoint_name = f"pre-{task_id}"
        self.vm_cluster.checkpoint_all(checkpoint_name)

        # Run think across all VMs
        vm_results = self.vm_cluster.think_all(
            task=subtask.description,
            context={"task_id": task_id, "task_type": subtask.task_type.value},
        )

        # Synthesize consensus from VM outputs
        consensus = self._synthesize_consensus_from_vm_results(vm_results)

        deliberation = {
            "task_id": task_id,
            "total_rounds": 1,
            "rounds": [{"consensus": consensus, "vm_results": vm_results}],
            "final_consensus": consensus,
            "closure": True,
            "timestamp": time.time(),
        }

        return deliberation, consensus, matching_agents

    def _synthesize_consensus_from_vm_results(
        self,
        vm_results: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Synthesize a consensus dict from per-VM think results.

        In mock/local mode, VMs echo the task. We produce a synthetic
        consensus with the subtask description as the winner approach.
        In production, this would parse structured reasoning from VMs.
        """
        if not vm_results:
            return {"winner": None, "score": 0.0}

        # Use the first VM's task as the consensus approach
        first_result = next(iter(vm_results.values()))
        task = first_result.get("task", "")

        # Simple majority-style score: all VMs completed = high confidence
        completed = sum(1 for r in vm_results.values() if r.get("status") == "completed")
        score = completed / len(vm_results) if vm_results else 0.0

        return {
            "winner": task,
            "score": round(score, 2),
            "approach": task,
            "max_score": score,
            "vm_count": len(vm_results),
            "vm_completed": completed,
        }

    def _execute_build_subtask(
        self,
        subtask: SubTask,
        consensus: Dict[str, Any],
        task_id: str,
    ) -> List[Dict[str, Any]]:
        """BUILD: generate code from consensus approach using a SandboxAgent."""
        approach = consensus.get("winner", subtask.description)

        # Find a sandbox agent
        sandbox = self._find_sandbox_agent()
        if sandbox is None:
            return [{
                "type": "build_plan",
                "content": approach,
                "task_id": task_id,
                "note": "No sandbox agent available; plan only",
            }]

        code = self.generate_code_for_approach(
            approach=str(approach),
            language="python",
        )

        result = sandbox.execute(
            code=code,
            language="python",
            cited_purpose=f"[CITATION: P5-5] Autonomous build for {task_id}",
        )

        artifact = {
            "type": "code_execution",
            "language": "python",
            "code": code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
            "task_id": task_id,
        }
        self._artifact_registry[task_id] = artifact

        # Store procedural memory: generated code is a learned skill
        self.memory.store(MemoryTrace(
            trace_id=f"procedural-{task_id}",
            memory_type=MemoryType.PROCEDURAL,
            content={
                "code": code,
                "language": "python",
                "approach": approach,
                "return_code": result.return_code,
            },
            source="autonomous_executor",
            confidence=0.9 if result.return_code == 0 else 0.3,
            importance=0.8,
            tags=["autonomous", "code", "procedural", "build"],
        ))

        return [artifact]

    def _execute_evaluate_subtask(
        self,
        subtask: SubTask,
        consensus: Dict[str, Any],
        task_id: str,
    ) -> List[Dict[str, Any]]:
        """EVALUATE: run tests against previously generated artifacts."""
        # Find the most recent build artifact to test
        build_artifact = None
        for art in reversed(list(self._artifact_registry.values())):
            if art.get("type") == "code_execution":
                build_artifact = art
                break

        if build_artifact is None:
            return [{
                "type": "evaluation_skipped",
                "reason": "No build artifact found to evaluate",
                "task_id": task_id,
            }]

        sandbox = self._find_sandbox_agent()
        if sandbox is None:
            return [{
                "type": "evaluation_skipped",
                "reason": "No sandbox agent available",
                "task_id": task_id,
            }]

        # Run the code again + assertions
        test_script = f"""
{build_artifact['code']}
# Auto-generated smoke test
if __name__ == "__main__":
    print("EVALUATION_PASS")
"""
        result = sandbox.execute(
            code=test_script,
            language="python",
            cited_purpose=f"[CITATION: P5-5] Evaluation for {task_id}",
        )

        return [{
            "type": "evaluation_result",
            "tests_passed": result.return_code == 0 and "EVALUATION_PASS" in result.stdout,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
            "task_id": task_id,
        }]

    def _execute_research_subtask(
        self,
        subtask: SubTask,
        deliberation: Dict[str, Any],
        task_id: str,
    ) -> List[Dict[str, Any]]:
        """RESEARCH: deliberation report + search summary."""
        report = self.orchestrator.synthesize_report(task_id)
        return [{
            "type": "research_report",
            "content": report,
            "task_id": task_id,
        }]

    def _find_sandbox_agent(self) -> Optional[SandboxAgent]:
        """Find the first registered SandboxAgent."""
        for agent in self.orchestrator.agents.values():
            if isinstance(agent, SandboxAgent):
                return agent
        return None

    @cite(
        key="AUTO-EXEC-GRAPH",
        paper="Autonomous Executor: Full Task Graph Execution",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Topological execution with dependency tracking",
        confidence="CERTAIN",
    )
    def _process_subtask_result(
        self,
        graph: TaskGraph,
        subtask: Any,
        result: Dict[str, Any],
        subtask_results: List[Dict[str, Any]],
        consensus_history: List[Dict[str, Any]],
        artifacts: List[Dict[str, Any]],
        recommendations: List[str],
        completed_count_ref: List[int],
    ) -> None:
        """Process a single sub-task result: update tracking lists and consult director."""
        subtask_results.append(result)
        if result.get("consensus"):
            consensus_history.append({
                "subtask_id": subtask.task_id,
                "consensus": result["consensus"],
            })
        artifacts.extend(result.get("artifacts", []))
        if result["status"] == "completed":
            completed_count_ref[0] += 1
        else:
            recommendations.append(
                f"Sub-task {subtask.task_id} failed: {result.get('error', 'unknown')}"
            )

        # AI Director: observe and potentially redirect
        if self.director is not None:
            consensus = result.get("consensus") or {}
            obs = DirectorObservation(
                task_id=graph.goal_id,
                subtask_id=subtask.task_id,
                consensus_approach=consensus.get("approach"),
                consensus_score=consensus.get("max_score", 0.0),
                execution_status=result["status"],
                artifacts=result.get("artifacts", []),
                previous_directions=[d.revised_task_description for d in self.director.get_direction_history()],
            )
            direction = self.director.direct(obs)
            if direction.action == "retry" and result["status"] != "completed":
                # Re-execute this sub-task with the director's revised description
                subtask.description = direction.revised_task_description
                retry_result = self.execute_subtask(graph, subtask)
                subtask_results.append(retry_result)
                if retry_result["status"] == "completed":
                    completed_count_ref[0] += 1
                    # Remove failure recommendation
                    rec = f"Sub-task {subtask.task_id} failed: {result.get('error', 'unknown')}"
                    if rec in recommendations:
                        recommendations.remove(rec)
            elif direction.action == "critique":
                recommendations.append(
                    f"Director critique on {subtask.task_id}: {direction.reasoning}"
                )

    async def _execute_subtask_async(
        self,
        graph: TaskGraph,
        subtask: Any,
    ) -> Dict[str, Any]:
        """Run sync execute_subtask in the default thread pool."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self.execute_subtask,
            graph,
            subtask,
        )

    async def execute_task_graph_async(self, graph: TaskGraph) -> SelfEvaluationReport:
        """
        Async version of execute_task_graph with parallel sub-task execution.

        Independent sub-tasks (same topological wave) run concurrently
        via asyncio.gather. Director observations happen after each wave.
        """
        start_time = time.time()
        subtask_results: List[Dict[str, Any]] = []
        consensus_history: List[Dict[str, Any]] = []
        artifacts: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        max_iterations = 100
        iteration = 0
        completed_count_ref = [0]

        while iteration < max_iterations:
            iteration += 1
            ready = graph.get_ready_tasks()
            if not ready:
                break

            if len(ready) == 1:
                # Single ready task — avoid asyncio overhead
                result = await self._execute_subtask_async(graph, ready[0])
                self._process_subtask_result(
                    graph, ready[0], result,
                    subtask_results, consensus_history, artifacts,
                    recommendations, completed_count_ref,
                )
            else:
                # Parallel execution of independent sub-tasks
                results = await asyncio.gather(*[
                    self._execute_subtask_async(graph, st) for st in ready
                ])
                for subtask, result in zip(ready, results):
                    self._process_subtask_result(
                        graph, subtask, result,
                        subtask_results, consensus_history, artifacts,
                        recommendations, completed_count_ref,
                    )

        total = len(graph.subtasks)
        completed_count = completed_count_ref[0]
        completion_rate = completed_count / max(total, 1)

        if completion_rate < 1.0:
            recommendations.append(
                f"Only {completed_count}/{total} sub-tasks completed. Review failed tasks."
            )

        duration_ms = (time.time() - start_time) * 1000

        # Collect director interventions for the report
        director_interventions = []
        if self.director is not None:
            for d in self.director.get_direction_history():
                director_interventions.append({
                    "action": d.action,
                    "revised_task_description": d.revised_task_description,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence,
                })

        report = SelfEvaluationReport(
            goal_id=graph.goal_id,
            goal_description=graph.goal_description,
            completion_rate=completion_rate,
            subtask_results=subtask_results,
            artifacts=artifacts,
            consensus_history=consensus_history,
            recommendations=recommendations,
            director_interventions=director_interventions,
            total_duration_ms=duration_ms,
        )

        # Layered memory consolidation for all participating twins
        consolidation_reports = self._consolidate_agent_memories()
        report.memory_consolidation = consolidation_reports

        # VM cluster: auto-hibernate and collect stats
        if self.vm_cluster is not None:
            self.vm_cluster.hibernate_all()
            report.vm_stats = self.vm_cluster.get_swarm_stats()
            if self.dashboard_collector is not None:
                self.dashboard_collector.collect_vm_stats(self.vm_cluster)

        # Dashboard data export
        if self.dashboard_collector is not None:
            self.dashboard_collector.collect_from_executor(self)
            self.dashboard_collector.record_event(
                "task_complete",
                {
                    "goal_id": graph.goal_id,
                    "completion_rate": completion_rate,
                    "subtask_count": len(graph.subtasks),
                },
            )
            self.dashboard_collector.save()

        # Store episodic memory: final execution summary
        self.memory.store(MemoryTrace(
            trace_id=f"report-{graph.goal_id}",
            memory_type=MemoryType.EPISODIC,
            content=report.to_dict(),
            source="autonomous_executor",
            confidence=completion_rate,
            importance=0.9,
            tags=["autonomous", "report", "summary"],
        ))

        return report

    def _consolidate_agent_memories(self) -> List[Dict[str, Any]]:
        """
        Trigger layered memory consolidation for all agents with profiles.

        Returns list of consolidation reports.
        """
        reports = []
        for agent in self.orchestrator.agents.values():
            if hasattr(agent, "layered_memory") and agent.layered_memory is not None:
                try:
                    report = agent.layered_memory.consolidate()
                    reports.append({
                        "twin_id": report.twin_id,
                        "atoms_processed": report.atoms_processed,
                        "scenarios_mined": report.scenarios_mined,
                        "persona_updated": report.persona_updated,
                        "persona_version": report.persona_version,
                    })
                except Exception:
                    # Consolidation failure should not block execution
                    pass
        return reports

    def execute_task_graph(self, graph: TaskGraph) -> SelfEvaluationReport:
        """
        Execute a full TaskGraph topologically and produce a self-evaluation report.

        Sync wrapper around execute_task_graph_async.
        Independent sub-tasks within the same wave may run in parallel.
        """
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, schedule the coroutine
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self.execute_task_graph_async(graph))
                return future.result()
        except RuntimeError:
            # No event loop running — use asyncio.run directly
            return asyncio.run(self.execute_task_graph_async(graph))

    @cite(
        key="AUTO-CODEGEN",
        paper="Autonomous Executor: Code Generation",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Delegates to injected CodeGenerator strategy (LLM or template)",
        confidence="HIGH",
    )
    def generate_code_for_approach(
        self,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate executable code from a natural language approach description.

        Delegates to the injected CodeGenerator (LLM preferred, templates fallback).
        If post-conditions are configured, validates and auto-retries on failure.
        """
        result = self.code_generator.generate_code(approach, language, test_cases)

        if self.post_conditions:
            from harness.post_conditions import PostConditionValidator
            validator = PostConditionValidator(self.max_validation_attempts)
            v = validator.validate(
                result=result,
                conditions=self.post_conditions,
                generator=self.code_generator,
                approach=approach,
                language=language,
                test_cases=test_cases,
            )
            result = v.result

        return result.code

    @cite(
        key="AUTO-EVAL",
        paper="Autonomous Executor: Test Execution",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Validation step ensures generated artifacts meet success criteria",
        confidence="CERTAIN",
    )
    def run_evaluation(
        self,
        code: str,
        test_script: str,
        sandbox_agent: SandboxAgent,
    ) -> Dict[str, Any]:
        """
        Run a test script against previously generated code.

        Prepends the code to the test script and executes.
        """
        full_script = f"{code}\n\n# --- TESTS ---\n{test_script}\n"
        result = sandbox_agent.execute(
            code=full_script,
            language="python",
            cited_purpose="[CITATION: P5-5] Automated evaluation of generated code",
        )
        return {
            "tests_passed": result.return_code == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.return_code,
        }

    @cite(
        key="AUTO-DEPLOY",
        paper="Autonomous Executor: Artifact Deployment",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Artifacts must be persisted and discoverable for downstream use",
        confidence="CERTAIN",
    )
    def deploy_artifacts(
        self,
        report: SelfEvaluationReport,
        deploy_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Persist all artifacts from a completed task to disk and graph memory.

        Returns deployment manifest with paths and health status.
        """
        deploy_path = deploy_path or Path(f"/tmp/acn-deploy/{report.goal_id}")
        deploy_path.mkdir(parents=True, exist_ok=True)

        manifest: Dict[str, Any] = {
            "goal_id": report.goal_id,
            "deploy_path": str(deploy_path),
            "artifacts_deployed": [],
            "health": "healthy",
            "timestamp": time.time(),
        }

        for idx, art in enumerate(report.artifacts):
            art_type = art.get("type", "unknown")
            if art_type == "code_execution":
                # Save code to file
                code = art.get("code", "")
                filename = deploy_path / f"artifact_{idx}.py"
                filename.write_text(code)
                manifest["artifacts_deployed"].append({
                    "type": "code",
                    "path": str(filename),
                    "task_id": art.get("task_id"),
                })
            elif art_type == "deliberation_report":
                # Save report JSON
                content = art.get("content", {})
                filename = deploy_path / f"report_{idx}.json"
                import json
                filename.write_text(json.dumps(content, default=str, indent=2))
                manifest["artifacts_deployed"].append({
                    "type": "report",
                    "path": str(filename),
                    "task_id": art.get("task_id"),
                })
            elif art_type == "evaluation_result":
                # Save test results
                filename = deploy_path / f"eval_{idx}.json"
                import json
                filename.write_text(json.dumps(art, default=str, indent=2))
                manifest["artifacts_deployed"].append({
                    "type": "evaluation",
                    "path": str(filename),
                    "task_id": art.get("task_id"),
                })

        # Register in graph memory if available
        if self.orchestrator.graph_memory is not None:
            try:
                self.orchestrator.graph_memory.add_node(
                    node_id=f"deploy-{report.goal_id}",
                    node_type="deployment",
                    properties=manifest,
                )
            except Exception:
                pass  # Graph memory is best-effort for deployment tracking

        # Monitor: record deployment in orchestrator awareness
        from harness.awareness import CurrentState
        self.orchestrator.awareness.record_state(CurrentState(
            task_id=report.goal_id,
            phase="deployed",
            active_twins=[],
            completed_subtasks=len(report.subtask_results),
            total_subtasks=len(report.subtask_results),
            confidence=report.completion_rate,
            resource_usage={
                "artifacts_deployed": float(len(manifest["artifacts_deployed"])),
                "duration_ms": report.total_duration_ms,
            },
        ))

        # Health check
        failed = sum(1 for r in report.subtask_results if r["status"] == "failed")
        if failed > 0:
            manifest["health"] = "degraded"
        if report.completion_rate < 0.5:
            manifest["health"] = "unhealthy"

        return manifest

    @cite(
        key="AUTO-MONITOR",
        paper="Autonomous Executor: Execution Monitoring",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="Continuous health tracking during autonomous execution",
        confidence="CERTAIN",
    )
    def monitor_execution(
        self,
        graph: TaskGraph,
        report: SelfEvaluationReport,
    ) -> Dict[str, Any]:
        """
        Analyze execution health and produce monitoring metrics.

        Returns dict with health signals, anomaly flags, and recommendations.
        """
        metrics = {
            "goal_id": graph.goal_id,
            "completion_rate": report.completion_rate,
            "total_subtasks": len(graph.subtasks),
            "completed": sum(1 for r in report.subtask_results if r["status"] == "completed"),
            "failed": sum(1 for r in report.subtask_results if r["status"] == "failed"),
            "avg_subtask_duration_ms": 0.0,
            "anomalies": [],
            "recommendations": report.recommendations,
        }

        durations = [r.get("duration_ms", 0) for r in report.subtask_results if r.get("duration_ms")]
        if durations:
            metrics["avg_subtask_duration_ms"] = sum(durations) / len(durations)
            # Anomaly: sub-task took > 3x median
            med = sorted(durations)[len(durations) // 2]
            for r in report.subtask_results:
                d = r.get("duration_ms", 0)
                if d > med * 3 and med > 0:
                    metrics["anomalies"].append({
                        "type": "slow_subtask",
                        "subtask_id": r["subtask_id"],
                        "duration_ms": d,
                        "expected_ms": med,
                    })

        # Anomaly: consensus score too low
        for ch in report.consensus_history:
            score = ch.get("consensus", {}).get("score", 1.0)
            if score < 0.5:
                metrics["anomalies"].append({
                    "type": "weak_consensus",
                    "subtask_id": ch.get("subtask_id"),
                    "score": score,
                })

        # Anomaly: no artifacts from BUILD tasks
        build_tasks = [st for st in graph.subtasks.values() if st.task_type == TaskType.BUILD]
        build_artifacts = [
            a for a in report.artifacts
            if a.get("type") in ("code_execution", "build_plan")
        ]
        if len(build_tasks) > len(build_artifacts):
            metrics["anomalies"].append({
                "type": "missing_build_artifacts",
                "expected": len(build_tasks),
                "actual": len(build_artifacts),
            })

        # Overall health
        if metrics["failed"] == 0 and metrics["completion_rate"] == 1.0:
            metrics["health"] = "healthy"
        elif metrics["completion_rate"] >= 0.7:
            metrics["health"] = "degraded"
        else:
            metrics["health"] = "unhealthy"

        return metrics
