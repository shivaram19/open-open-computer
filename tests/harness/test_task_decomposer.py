# tests/harness/test_task_decomposer.py
"""
Unit Tests for Task Decomposer (Harness Layer 1).

Research-backed test patterns:
- AGoT: automatic decomposition without user-defined structures
- KGoT: structured graph representation
- DAG-Plan: dependency-aware scheduling
- TDP: Self-Revision after execution

Citations: Besta2024, AGoT2025, KGoT2025, TDP2026, DAGPlan2025
"""



import pytest

from harness.task_decomposer import (
    TaskDecomposer,
    TaskType,
    SubTask,
    TaskGraph,
)


class TestIntentParsing:
    """P1-6: Intent parser — classify task type from natural language."""

    def test_research_keywords_detected(self):
        """Strict assertion: research keywords → RESEARCH type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("research the latest AI breakthroughs") == TaskType.RESEARCH
        assert decomposer.parse_intent("explore new frameworks") == TaskType.RESEARCH
        assert decomposer.parse_intent("find papers on consensus protocols") == TaskType.RESEARCH

    def test_build_keywords_detected(self):
        """Strict assertion: build keywords → BUILD type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("build a task decomposer") == TaskType.BUILD
        assert decomposer.parse_intent("implement the harness layer") == TaskType.BUILD
        assert decomposer.parse_intent("create a new agent") == TaskType.BUILD

    def test_debug_keywords_detected(self):
        """Strict assertion: debug keywords → DEBUG type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("debug the failing test") == TaskType.DEBUG
        assert decomposer.parse_intent("fix the citation error") == TaskType.DEBUG

    def test_evaluate_keywords_detected(self):
        """Strict assertion: evaluate keywords → EVALUATE type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("benchmark the new model") == TaskType.EVALUATE
        assert decomposer.parse_intent("test the integration") == TaskType.EVALUATE

    def test_analyze_keywords_detected(self):
        """Strict assertion: analyze keywords → ANALYZE type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("analyze the performance data") == TaskType.ANALYZE
        assert decomposer.parse_intent("synthesize the results") == TaskType.ANALYZE

    def test_plan_keywords_detected(self):
        """Strict assertion: plan keywords → PLAN type."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("design the architecture") == TaskType.PLAN
        assert decomposer.parse_intent("plan the next sprint") == TaskType.PLAN

    def test_unknown_when_no_keywords_match(self):
        """Canary prompt: no matching keywords → UNKNOWN."""
        decomposer = TaskDecomposer()
        
        assert decomposer.parse_intent("xyz abc 123") == TaskType.UNKNOWN

    def test_mixed_keywords_picks_best_match(self):
        """Strict assertion: multiple keyword types picks highest score."""
        decomposer = TaskDecomposer()
        
        # "research" and "build" both present — whichever has more matches wins
        result = decomposer.parse_intent("research and build a new system")
        assert result in (TaskType.RESEARCH, TaskType.BUILD)


class TaskDecompositionStructure:
    """P1-6: Sub-task generation — 3-7 tasks with dependencies."""

    def test_research_decomposition_has_5_subtasks(self):
        """Membership testing: research produces 3-7 sub-tasks."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("research latest LLM benchmarks")
        
        assert len(graph.subtasks) == 5
        assert graph.task_type == TaskType.RESEARCH

    def test_build_decomposition_has_4_subtasks(self):
        """Membership testing: build produces 3-7 sub-tasks."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a task decomposer")
        
        assert len(graph.subtasks) == 4
        assert graph.task_type == TaskType.BUILD

    def test_debug_decomposition_has_4_subtasks(self):
        """Membership testing: debug produces 3-7 sub-tasks."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("debug the failing citation check")
        
        assert len(graph.subtasks) == 4
        assert graph.task_type == TaskType.DEBUG

    def test_evaluate_decomposition_has_3_subtasks(self):
        """Membership testing: evaluate produces 3-7 sub-tasks."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("benchmark the new harness")
        
        assert len(graph.subtasks) == 3
        assert graph.task_type == TaskType.EVALUATE

    def test_plan_decomposition_has_4_subtasks(self):
        """Membership testing: plan produces 3-7 sub-tasks."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("design the architecture for the harness")
        
        assert len(graph.subtasks) == 4
        assert graph.task_type == TaskType.PLAN

    def test_generic_fallback_for_unknown(self):
        """Strict assertion: unknown type falls back to generic 3-step."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("xyz abc 123")
        
        assert len(graph.subtasks) == 3
        assert graph.task_type == TaskType.UNKNOWN

    def test_each_subtask_has_success_criteria(self):
        """Strict assertion: every sub-task has at least one success criterion."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        for task in graph.subtasks.values():
            assert len(task.success_criteria) >= 1, f"{task.task_id} missing criteria"

    def test_each_subtask_has_cluster_assignment(self):
        """Strict assertion: every sub-task assigned to a cognitive cluster."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        for task in graph.subtasks.values():
            assert task.cognitive_cluster != "", f"{task.task_id} missing cluster"


class TestDependencyGraph:
    """P1-6: Dependency graph — DAG structure and topological ordering."""

    def test_first_task_has_no_dependencies(self):
        """Strict assertion: root task(s) have empty dependency lists."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        ready = graph.get_ready_tasks()
        assert len(ready) >= 1
        for task in ready:
            assert task.dependencies == []

    def test_later_tasks_depend_on_earlier_tasks(self):
        """Strict assertion: dependencies point to earlier tasks in sequence."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        # Find a task with dependencies
        task_with_deps = next(t for t in graph.subtasks.values() if t.dependencies)
        for dep_id in task_with_deps.dependencies:
            assert dep_id in graph.subtasks

    def test_ready_tasks_after_completion(self):
        """Canary prompt: completing a task unlocks its dependents."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("implement a task decomposer")
        
        # Initially, only design is ready
        ready_initial = graph.get_ready_tasks()
        assert len(ready_initial) == 1
        assert ready_initial[0].task_id.endswith("-design")
        
        # Complete design
        decomposer.update_task_status(graph, ready_initial[0].task_id, "completed")
        
        # Now implement should be ready
        ready_after = graph.get_ready_tasks()
        assert len(ready_after) == 1
        assert ready_after[0].task_id.endswith("-implement")

    def test_no_circular_dependencies(self):
        """Strict assertion: DAG has no cycles."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("research latest AI frameworks")
        
        # DFS to detect cycles
        def has_cycle(task_id: str, visited: set, path: set) -> bool:
            if task_id in path:
                return True
            if task_id in visited:
                return False
            visited.add(task_id)
            path.add(task_id)
            task = graph.subtasks.get(task_id)
            if task:
                for dep in task.dependencies:
                    if has_cycle(dep, visited, path):
                        return True
            path.remove(task_id)
            return False
        
        for task_id in graph.subtasks:
            assert not has_cycle(task_id, set(), set())

    def test_critical_path_computed(self):
        """Strict assertion: critical path returns ordered task list."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        path = graph.get_critical_path()
        
        assert len(path) == len(graph.subtasks)
        # All tasks should be in the path
        assert set(path) == set(graph.subtasks.keys())


class TestTaskGraphSerialization:
    """P1-6: Task graph can be serialized for storage and transmission."""

    def test_to_dict_contains_required_fields(self):
        """Strict assertion: serialization has all expected keys."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        data = graph.to_dict()
        
        required = ["goal_id", "goal_description", "task_type", "subtask_count", "subtasks", "ready_now"]
        for key in required:
            assert key in data

    def test_ready_now_reflects_current_state(self):
        """Strict assertion: ready_now list updates with task completion."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        assert len(graph.to_dict()["ready_now"]) == 1
        
        # Complete the ready task
        ready_id = graph.to_dict()["ready_now"][0]
        decomposer.update_task_status(graph, ready_id, "completed")
        
        assert len(graph.to_dict()["ready_now"]) == 1  # next task ready


class TestDecomposerHistory:
    """P1-6: Decomposition history for learning and audit."""

    def test_decomposition_recorded_in_history(self):
        """Strict assertion: every decomposition stored in history."""
        decomposer = TaskDecomposer()
        
        assert len(decomposer.decomposition_history) == 0
        
        decomposer.decompose("task one")
        assert len(decomposer.decomposition_history) == 1
        
        decomposer.decompose("task two")
        assert len(decomposer.decomposition_history) == 2

    def test_stats_reflect_history(self):
        """Strict assertion: stats summarize decomposition history."""
        decomposer = TaskDecomposer()
        
        decomposer.decompose("build something")
        decomposer.decompose("research something")
        decomposer.decompose("test something")
        
        stats = decomposer.get_decomposition_stats()
        
        assert stats["total_decompositions"] == 3
        assert stats["avg_subtasks_per_goal"] > 0
        assert "build" in stats["type_distribution"]
        assert "research" in stats["type_distribution"]


class TestSelfRevision:
    """P1-6: Self-Revision — update graph after sub-task execution."""

    def test_update_status_changes_task_state(self):
        """Strict assertion: update_task_status modifies task status."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("build a web search tool")
        
        task_id = list(graph.subtasks.keys())[0]
        assert graph.subtasks[task_id].status == "pending"
        
        decomposer.update_task_status(graph, task_id, "completed")
        
        assert graph.subtasks[task_id].status == "completed"

    def test_completing_task_unlocks_dependents(self):
        """Canary prompt: status update propagates to dependency chain."""
        decomposer = TaskDecomposer()
        graph = decomposer.decompose("implement a task decomposer")
        
        # Get initial ready task
        ready = graph.get_ready_tasks()
        design_id = ready[0].task_id
        
        # Complete it
        decomposer.update_task_status(graph, design_id, "completed")
        
        # Implement should now be ready
        new_ready = graph.get_ready_tasks()
        assert any(t.task_id.endswith("-implement") for t in new_ready)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
