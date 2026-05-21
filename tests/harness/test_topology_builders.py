"""
TDD Tests for TopologyBuilder Protocol and Registry.

These tests drive the extraction of the if-elif chain from
TopologyOptimizer.build_topology() into an OCP-compliant registry.

Research basis:
- Meyer (1988): OCP — open for extension, closed for modification
- Fowler (1999): Replace Conditional with Polymorphism
"""

import pytest
from consensus.topology import TopologyType


class TestTopologyBuilderProtocol:
    """Tests for the TopologyBuilder abstraction."""

    def test_topology_builder_protocol_exists(self):
        """A TopologyBuilder protocol must exist."""
        from consensus.topology_builders import TopologyBuilder
        assert TopologyBuilder is not None

    def test_complete_topology_builder_exists(self):
        """A CompleteTopologyBuilder must exist and implement the protocol."""
        from consensus.topology_builders import CompleteTopologyBuilder
        builder = CompleteTopologyBuilder()
        result = builder.build(["a", "b", "c"])
        assert "a" in result
        assert "b" in result["a"]

    def test_star_topology_builder_exists(self):
        """A StarTopologyBuilder must exist."""
        from consensus.topology_builders import StarTopologyBuilder
        builder = StarTopologyBuilder()
        result = builder.build(["a", "b", "c"], hub="a")
        assert result["b"] == ["a"]
        assert "b" in result["a"]

    def test_topology_builders_registry_exists(self):
        """A TOPOLOGY_BUILDERS registry must map TopologyType to builders."""
        from consensus.topology import TOPOLOGY_BUILDERS
        assert TopologyType.COMPLETE in TOPOLOGY_BUILDERS
        assert TopologyType.STAR in TOPOLOGY_BUILDERS
        assert TopologyType.CHAIN in TOPOLOGY_BUILDERS
        assert TopologyType.TREE in TOPOLOGY_BUILDERS
        assert TopologyType.RANDOM in TOPOLOGY_BUILDERS
        assert TopologyType.LAYERED in TOPOLOGY_BUILDERS
        assert TopologyType.ADAPTIVE in TOPOLOGY_BUILDERS

    def test_complete_builder_via_registry(self):
        """The registry's COMPLETE builder must produce correct graph."""
        from consensus.topology import TOPOLOGY_BUILDERS
        builder = TOPOLOGY_BUILDERS[TopologyType.COMPLETE]
        result = builder.build(["a", "b", "c"])
        assert set(result["a"]) == {"b", "c"}


class TestTopologyOptimizerUsesRegistry:
    """Tests that TopologyOptimizer delegates to the registry."""

    def test_optimizer_build_topology_uses_registry(self):
        """TopologyOptimizer.build_topology must delegate to TOPOLOGY_BUILDERS.
        
        This is the OCP test: adding a new builder to the registry should
        be picked up by TopologyOptimizer without editing its source.
        """
        from consensus.topology import TopologyOptimizer, TopologyType
        from consensus.topology import TOPOLOGY_BUILDERS

        optimizer = TopologyOptimizer()
        agents = ["a0", "a1", "a2"]

        # Monkey-patch registry with a spy builder to prove delegation
        spy_called = False

        class SpyBuilder:
            def build(self, agent_ids, **kwargs):
                nonlocal spy_called
                spy_called = True
                return {aid: [] for aid in agent_ids}

        original = TOPOLOGY_BUILDERS.get(TopologyType.COMPLETE)
        TOPOLOGY_BUILDERS[TopologyType.COMPLETE] = SpyBuilder()
        try:
            optimizer.build_topology(agents, TopologyType.COMPLETE)
            assert spy_called, "TopologyOptimizer did NOT delegate to registry"
        finally:
            TOPOLOGY_BUILDERS[TopologyType.COMPLETE] = original
