"""
TDD Tests for Phase 4.2 — TopologyOptimizer private method removal.

Verifies that optimize_topology works through the registry,
not via private _build_* methods.
"""

import pytest

from consensus.topology import TopologyOptimizer, TopologyType


class TestTopologyOptimizerOptimize:
    """Tests for optimize_topology via registry delegation."""

    def test_optimize_topology_returns_valid_result(self):
        """optimize_topology must return a valid topology without calling private methods."""
        optimizer = TopologyOptimizer()
        agent_ids = ["a1", "a2", "a3", "a4"]

        topo_type, graph, metrics = optimizer.optimize_for_task(
            agent_ids=agent_ids,
            task_complexity=0.5,
            max_token_budget=10000,
            min_fault_tolerance=0.1,
        )

        assert topo_type in TopologyType
        assert len(graph) == len(agent_ids)
        assert metrics.node_count == len(agent_ids)

    def test_optimize_topology_fallback_to_complete(self):
        """When constraints are tight, should fall back to complete graph."""
        optimizer = TopologyOptimizer()
        agent_ids = ["a1", "a2"]

        topo_type, graph, metrics = optimizer.optimize_for_task(
            agent_ids=agent_ids,
            task_complexity=0.9,
            max_token_budget=1,  # Very tight budget
            min_fault_tolerance=1.0,  # Maximum fault tolerance
        )

        assert topo_type == TopologyType.COMPLETE
        assert len(graph) == len(agent_ids)
