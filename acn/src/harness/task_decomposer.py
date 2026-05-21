# src/harness/task_decomposer.py
"""
Task Decomposer: Harness Layer 1 — The First Operational Layer.

Transforms natural language goals into structured, executable sub-task graphs.
Inspired by:
- AGoT (Adaptive Graph of Thoughts): automatic recursive decomposition [Pandey2025]
- KGoT (Knowledge Graph of Thoughts): structured KG representation [KGoT2025]
- DAG-Plan: dependency-aware task scheduling [DAGPlan2025]
- Besta2024: Graph of Thoughts for decomposition

Principle: Every complex task is a DAG of simpler tasks.

[CITATION: Besta2024]
[CITATION: AGoT2025]
[CITATION: KGoT2025]
"""

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="TASK-TYPE",
    paper="Task Decomposer: Intent Classification",
    venue="ACN Architecture Document",
    section="Task Types",
    rationale="Classifying task type enables appropriate decomposition strategy",
    confidence="CERTAIN",
)
class TaskType(Enum):
    """Types of tasks the harness can decompose and execute."""
    RESEARCH = "research"      # Gather evidence, analyze sources
    BUILD = "build"            # Create code, configs, documents
    DEBUG = "debug"            # Find and fix errors
    EVALUATE = "evaluate"      # Test, benchmark, validate
    ANALYZE = "analyze"        # Synthesize findings, detect patterns
    PLAN = "plan"              # Create roadmap, define strategy
    UNKNOWN = "unknown"        # Needs clarification


@cite(
    key="SUBTASK-DEF",
    paper="Task Decomposer: Sub-Task Representation",
    venue="ACN Architecture Document",
    section="Sub-Task Model",
    rationale="Structured sub-tasks enable dependency tracking and parallel execution",
    confidence="CERTAIN",
)
@dataclass
class SubTask:
    """A single sub-task within a decomposed goal."""
    task_id: str
    description: str
    task_type: TaskType
    dependencies: List[str] = field(default_factory=list)  # task_ids that must complete first
    success_criteria: List[str] = field(default_factory=list)
    estimated_effort_minutes: int = 30
    cognitive_cluster: str = ""  # Which twin cluster should handle this
    citations_required: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, active, completed, failed
    parent_task_id: Optional[str] = None


@cite(
    key="TASK-GRAPH",
    paper="Task Decomposer: Dependency Graph",
    venue="ACN Architecture Document",
    section="DAG Representation",
    rationale="DAG enables topological ordering and parallel execution of independent sub-tasks",
    confidence="CERTAIN",
)
@dataclass
class TaskGraph:
    """A directed acyclic graph of sub-tasks."""
    goal_id: str
    goal_description: str
    task_type: TaskType
    subtasks: Dict[str, SubTask] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    @cite(
        key="TASK-READY",
        paper="Task Decomposer: Ready Task Detection",
        venue="ACN Architecture Document",
        section="DAG Operations",
        rationale="Topological ordering enables parallel execution of independent tasks",
        confidence="CERTAIN",
    )
    def get_ready_tasks(self) -> List[SubTask]:
        """Return sub-tasks whose dependencies are all completed."""
        ready = []
        for task in self.subtasks.values():
            if task.status != "pending":
                continue
            deps_complete = all(
                self.subtasks.get(d, SubTask("", "", TaskType.UNKNOWN)).status == "completed"
                for d in task.dependencies
            )
            if deps_complete:
                ready.append(task)
        return ready
    
    @cite(
        key="TASK-CRITICAL",
        paper="Task Decomposer: Critical Path Analysis",
        venue="ACN Architecture Document",
        section="DAG Operations",
        rationale="Critical path identifies bottleneck tasks for schedule optimization",
        confidence="CERTAIN",
    )
    def get_critical_path(self) -> List[str]:
        """Estimate critical path: longest dependency chain."""
        # Simple DFS for longest path
        def longest_from(task_id: str, memo: Dict[str, int]) -> int:
            if task_id in memo:
                return memo[task_id]
            task = self.subtasks.get(task_id)
            if not task or not task.dependencies:
                memo[task_id] = task.estimated_effort_minutes if task else 0
                return memo[task_id]
            max_dep = max(longest_from(d, memo) for d in task.dependencies)
            memo[task_id] = max_dep + task.estimated_effort_minutes
            return memo[task_id]
        
        memo: Dict[str, int] = {}
        for task_id in self.subtasks:
            longest_from(task_id, memo)
        
        # Return path in descending order of length
        return sorted(memo.keys(), key=lambda k: memo[k], reverse=True)
    
    @cite(
        key="TASK-SERIALIZE",
        paper="Task Decomposer: Graph Serialization",
        venue="ACN Architecture Document",
        section="DAG Operations",
        rationale="Serializable graphs enable storage, transmission, and audit",
        confidence="CERTAIN",
    )
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "goal_description": self.goal_description,
            "task_type": self.task_type.value,
            "subtask_count": len(self.subtasks),
            "subtasks": [
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "type": t.task_type.value,
                    "dependencies": t.dependencies,
                    "status": t.status,
                    "cluster": t.cognitive_cluster,
                }
                for t in self.subtasks.values()
            ],
            "ready_now": [t.task_id for t in self.get_ready_tasks()],
        }


@cite(
    key="TASK-DECOMPOSER",
    paper="Task Decomposer: Harness Layer 1",
    venue="ACN Architecture Document",
    section="Decomposition Engine",
    rationale="Automatic task decomposition with dependency graph generation",
    confidence="CERTAIN",
)
class TaskDecomposer:
    """
    Layer 1 of the harness: transforms goals into executable sub-task DAGs.
    
    Inspired by AGoT (Adaptive Graph of Thoughts):
    - Recursively decomposes if further breakdown is needed
    - No user-defined structures required
    - Automatically detects task type and applies appropriate strategy
    
    Decomposition strategies by task type:
    - RESEARCH: BFS → search → fetch → analyze → synthesize
    - BUILD: design → implement → test → deploy
    - DEBUG: reproduce → isolate → fix → verify
    - EVALUATE: setup → run → measure → compare
    - ANALYZE: gather → pattern-detect → hypothesis → validate
    - PLAN: scope → decompose → sequence → resource
    """

    def __init__(self):
        self.decomposition_history: List[TaskGraph] = []
        self._type_keywords = {
            TaskType.RESEARCH: ["research", "investigate", "study", "find", "search", "explore", "analyze literature"],
            TaskType.BUILD: ["build", "create", "implement", "develop", "write", "code", "make", "construct"],
            TaskType.DEBUG: ["debug", "fix", "repair", "resolve", "investigate bug", "error", "crash", "broken"],
            TaskType.EVALUATE: ["test", "evaluate", "benchmark", "measure", "validate", "verify", "assess"],
            TaskType.ANALYZE: ["analyze", "synthesize", "compare", "review", "summarize", "extract patterns"],
            TaskType.PLAN: ["plan", "design", "roadmap", "strategy", "architecture", "organize"],
        }

    @cite(
        key="TASK-INTENT",
        paper="Task Decomposer: Intent Parser",
        venue="ACN Architecture Document",
        section="Intent Classification",
        rationale="Task type determines decomposition strategy and twin cluster assignment",
        confidence="CERTAIN",
    )
    def parse_intent(self, goal_description: str) -> TaskType:
        """
        Classify the goal into a task type.
        
        Uses keyword matching (AGoT-inspired simple classification).
        Future: LLM-based intent classification.
        """
        desc_lower = goal_description.lower()
        scores: Dict[TaskType, int] = {task_type: 0 for task_type in TaskType}
        
        for task_type, keywords in self._type_keywords.items():
            for kw in keywords:
                if kw in desc_lower:
                    scores[task_type] += 1
        
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else TaskType.UNKNOWN

    @cite(
        key="TASK-DECOMPOSE",
        paper="Task Decomposer: Sub-Task Generation",
        venue="ACN Architecture Document",
        section="Decomposition Engine",
        rationale="Breaking complex goals into 3-7 researchable sub-tasks with dependencies",
        confidence="CERTAIN",
    )
    def decompose(self, goal_description: str, goal_id: Optional[str] = None) -> TaskGraph:
        """
        Decompose a goal into a DAG of sub-tasks.
        
        Args:
            goal_description: Natural language description of the goal
            goal_id: Optional explicit goal ID
        
        Returns:
            TaskGraph with sub-tasks and dependencies
        """
        goal_id = goal_id or f"goal-{uuid.uuid4().hex[:8]}"
        task_type = self.parse_intent(goal_description)
        
        # Generate sub-tasks based on task type
        subtasks = self._generate_subtasks(goal_description, task_type, goal_id)
        
        # Build dependency graph
        graph = TaskGraph(
            goal_id=goal_id,
            goal_description=goal_description,
            task_type=task_type,
            subtasks={st.task_id: st for st in subtasks},
        )
        
        self.decomposition_history.append(graph)
        return graph

    def _generate_subtasks(
        self,
        goal: str,
        task_type: TaskType,
        parent_id: str,
    ) -> List[SubTask]:
        """Generate sub-tasks appropriate for the task type."""
        generators = {
            TaskType.RESEARCH: self._decompose_research,
            TaskType.BUILD: self._decompose_build,
            TaskType.DEBUG: self._decompose_debug,
            TaskType.EVALUATE: self._decompose_evaluate,
            TaskType.ANALYZE: self._decompose_analyze,
            TaskType.PLAN: self._decompose_plan,
            TaskType.UNKNOWN: self._decompose_generic,
        }
        generator = generators.get(task_type, self._decompose_generic)
        return generator(goal, parent_id)

    def _decompose_research(self, goal: str, parent_id: str) -> List[SubTask]:
        """Research tasks: BFS → search → fetch → analyze → synthesize."""
        return [
            SubTask(
                task_id=f"{parent_id}-scope",
                description=f"Scope the research question: {goal}",
                task_type=TaskType.RESEARCH,
                dependencies=[],
                success_criteria=["Research question defined", "Key terms identified"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-search",
                description="Search for authoritative sources",
                task_type=TaskType.RESEARCH,
                dependencies=[f"{parent_id}-scope"],
                success_criteria=["3+ peer-reviewed sources found", "Sources cited"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-fetch",
                description="Fetch and read top sources",
                task_type=TaskType.RESEARCH,
                dependencies=[f"{parent_id}-search"],
                success_criteria=["Key findings extracted", "Citations verified"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-analyze",
                description="Analyze and cross-reference findings",
                task_type=TaskType.ANALYZE,
                dependencies=[f"{parent_id}-fetch"],
                success_criteria=["Patterns identified", "Contradictions flagged"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-synthesize",
                description="Synthesize structured report",
                task_type=TaskType.ANALYZE,
                dependencies=[f"{parent_id}-analyze"],
                success_criteria=["Report with citations", "Actionable recommendations"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_build(self, goal: str, parent_id: str) -> List[SubTask]:
        """Build tasks: design → implement → test → deploy."""
        return [
            SubTask(
                task_id=f"{parent_id}-design",
                description=f"Design architecture for: {goal}",
                task_type=TaskType.PLAN,
                dependencies=[],
                success_criteria=["Architecture documented", "Interfaces defined"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-implement",
                description="Implement the solution",
                task_type=TaskType.BUILD,
                dependencies=[f"{parent_id}-design"],
                success_criteria=["Code written", "All functions have citations"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-test",
                description="Write and run tests",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-implement"],
                success_criteria=["Tests pass", "Coverage >70%"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-verify",
                description="Verify citations and integration",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-test"],
                success_criteria=["verify_citations.py passes", "Integration test passes"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_debug(self, goal: str, parent_id: str) -> List[SubTask]:
        """Debug tasks: reproduce → isolate → fix → verify."""
        return [
            SubTask(
                task_id=f"{parent_id}-reproduce",
                description=f"Reproduce the issue: {goal}",
                task_type=TaskType.DEBUG,
                dependencies=[],
                success_criteria=["Issue reproduced consistently", "Error logs captured"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-isolate",
                description="Isolate root cause",
                task_type=TaskType.DEBUG,
                dependencies=[f"{parent_id}-reproduce"],
                success_criteria=["Minimal reproduction case", "Root cause identified"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-fix",
                description="Implement fix",
                task_type=TaskType.BUILD,
                dependencies=[f"{parent_id}-isolate"],
                success_criteria=["Fix implemented", "No regressions introduced"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-verify",
                description="Verify fix resolves issue",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-fix"],
                success_criteria=["Issue no longer reproduces", "Tests pass"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_evaluate(self, goal: str, parent_id: str) -> List[SubTask]:
        """Evaluate tasks: setup → run → measure → compare."""
        return [
            SubTask(
                task_id=f"{parent_id}-setup",
                description=f"Setup evaluation environment for: {goal}",
                task_type=TaskType.EVALUATE,
                dependencies=[],
                success_criteria=["Environment ready", "Baseline recorded"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-run",
                description="Run evaluation",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-setup"],
                success_criteria=["Evaluation complete", "Metrics captured"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-measure",
                description="Measure and analyze results",
                task_type=TaskType.ANALYZE,
                dependencies=[f"{parent_id}-run"],
                success_criteria=["Results analyzed", "Statistical significance checked"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_analyze(self, goal: str, parent_id: str) -> List[SubTask]:
        """Analyze tasks: gather → pattern-detect → hypothesis → validate."""
        return [
            SubTask(
                task_id=f"{parent_id}-gather",
                description=f"Gather data for analysis: {goal}",
                task_type=TaskType.ANALYZE,
                dependencies=[],
                success_criteria=["Data collected", "Quality verified"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-patterns",
                description="Detect patterns and anomalies",
                task_type=TaskType.ANALYZE,
                dependencies=[f"{parent_id}-gather"],
                success_criteria=["Patterns identified", "Anomalies flagged"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-hypothesis",
                description="Formulate hypotheses",
                task_type=TaskType.ANALYZE,
                dependencies=[f"{parent_id}-patterns"],
                success_criteria=["Hypotheses stated", "Testability verified"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-validate",
                description="Validate hypotheses against data",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-hypothesis"],
                success_criteria=["Hypotheses tested", "Conclusions drawn"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_plan(self, goal: str, parent_id: str) -> List[SubTask]:
        """Plan tasks: scope → decompose → sequence → resource."""
        return [
            SubTask(
                task_id=f"{parent_id}-scope",
                description=f"Define scope and constraints: {goal}",
                task_type=TaskType.PLAN,
                dependencies=[],
                success_criteria=["Scope defined", "Constraints listed"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-decompose",
                description="Break into major components",
                task_type=TaskType.PLAN,
                dependencies=[f"{parent_id}-scope"],
                success_criteria=["Components identified", "Interfaces defined"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-sequence",
                description="Sequence components with dependencies",
                task_type=TaskType.PLAN,
                dependencies=[f"{parent_id}-decompose"],
                success_criteria=["Dependency graph created", "Critical path identified"],
                cognitive_cluster="multi-agent",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-resource",
                description="Estimate resources and assign owners",
                task_type=TaskType.PLAN,
                dependencies=[f"{parent_id}-sequence"],
                success_criteria=["Resource estimates", "Owner assignments"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
        ]

    def _decompose_generic(self, goal: str, parent_id: str) -> List[SubTask]:
        """Generic fallback: understand → execute → verify."""
        return [
            SubTask(
                task_id=f"{parent_id}-understand",
                description=f"Understand the goal: {goal}",
                task_type=TaskType.RESEARCH,
                dependencies=[],
                success_criteria=["Goal clarified", "Success criteria defined"],
                cognitive_cluster="consensus-safety",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-execute",
                description="Execute the task",
                task_type=TaskType.BUILD,
                dependencies=[f"{parent_id}-understand"],
                success_criteria=["Task completed", "Output produced"],
                cognitive_cluster="video-gnn",
                parent_task_id=parent_id,
            ),
            SubTask(
                task_id=f"{parent_id}-verify",
                description="Verify the outcome",
                task_type=TaskType.EVALUATE,
                dependencies=[f"{parent_id}-execute"],
                success_criteria=["Outcome verified", "Success criteria met"],
                cognitive_cluster="streaming-reflection",
                parent_task_id=parent_id,
            ),
        ]

    @cite(
        key="TASK-REVISION",
        paper="Task Decomposer: Self-Revision Loop",
        venue="ACN Architecture Document",
        section="Dynamic Replanning",
        rationale="Update dependency graph after each sub-task execution (TDP pattern)",
        confidence="CERTAIN",
    )
    def update_task_status(self, graph: TaskGraph, task_id: str, status: str) -> None:
        """
        Update a sub-task's status and trigger replanning if needed.
        
        Inspired by TDP (Task-Decoupled Planning): Self-Revision updates
        the graph after execution.
        """
        if task_id in graph.subtasks:
            graph.subtasks[task_id].status = status
            
            # If task failed, its dependent tasks may need reassignment
            if status == "failed":
                for task in graph.subtasks.values():
                    if task_id in task.dependencies:
                        # Mark dependent tasks as blocked
                        # In full implementation, trigger replanning
                        pass

    @cite(
        key="TASK-HISTORY",
        paper="Task Decomposer: Decomposition History",
        venue="ACN Architecture Document",
        section="Learning from Decomposition",
        rationale="Historical decomposition patterns improve future decomposition quality",
        confidence="CERTAIN",
    )
    def get_decomposition_stats(self) -> Dict[str, Any]:
        """Report on decomposition history."""
        if not self.decomposition_history:
            return {"total_decompositions": 0}
        
        type_counts: Dict[str, int] = {}
        avg_subtasks = 0
        
        for graph in self.decomposition_history:
            type_counts[graph.task_type.value] = type_counts.get(graph.task_type.value, 0) + 1
            avg_subtasks += len(graph.subtasks)
        
        return {
            "total_decompositions": len(self.decomposition_history),
            "avg_subtasks_per_goal": avg_subtasks / len(self.decomposition_history),
            "type_distribution": type_counts,
        }
