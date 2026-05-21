"""
TDD Tests for ConsciousAgent Dependency Injection.

Drives the extraction of hardcoded instantiations from ConsciousAgent.__init__
into injectable optional parameters with default fallbacks.

Research basis:
- Martin (1996): DIP — high-level modules depend on abstractions
- Feathers (2004): Seam model — injection points enable testability
"""

from unittest.mock import Mock
import pytest

from agents.conscious_agent import ConsciousAgent
from harness.awareness import AwarenessLevel
from conftest import default_agent_kwargs


class TestConsciousAgentDependencyInjection:
    """Tests that ConsciousAgent accepts injected dependencies."""

    def test_can_inject_memory(self):
        """ConsciousAgent must accept an injected memory store."""
        mock_memory = Mock()
        kwargs = default_agent_kwargs("test-001")
        kwargs["memory"] = mock_memory
        agent = ConsciousAgent("test-001", "Test Agent", "test", **kwargs)
        assert agent.memory is mock_memory

    def test_can_inject_clock(self):
        """ConsciousAgent must accept an injected clock."""
        mock_clock = Mock()
        kwargs = default_agent_kwargs("test-002")
        kwargs["clock"] = mock_clock
        agent = ConsciousAgent("test-002", "Test Agent", "test", **kwargs)
        assert agent.hlc_clock is mock_clock

    def test_can_inject_experience_buffer(self):
        """ConsciousAgent must accept an injected experience buffer."""
        mock_buffer = Mock()
        kwargs = default_agent_kwargs("test-003")
        kwargs["experience_buffer"] = mock_buffer
        agent = ConsciousAgent("test-003", "Test Agent", "test", **kwargs)
        assert agent.experience_buffer is mock_buffer

    def test_can_inject_reflection_engine(self):
        """ConsciousAgent must accept an injected reflection engine."""
        mock_engine = Mock()
        kwargs = default_agent_kwargs("test-004")
        kwargs["reflection_engine"] = mock_engine
        agent = ConsciousAgent("test-004", "Test Agent", "test", **kwargs)
        assert agent.reflection_engine is mock_engine

    def test_can_inject_policy_optimizer(self):
        """ConsciousAgent must accept an injected policy optimizer."""
        mock_optimizer = Mock()
        kwargs = default_agent_kwargs("test-005")
        kwargs["policy_optimizer"] = mock_optimizer
        agent = ConsciousAgent("test-005", "Test Agent", "test", **kwargs)
        assert agent.policy_optimizer is mock_optimizer

    def test_can_inject_skill_evolution(self):
        """ConsciousAgent must accept an injected skill evolution."""
        mock_evolution = Mock()
        kwargs = default_agent_kwargs("test-006")
        kwargs["skill_evolution"] = mock_evolution
        agent = ConsciousAgent("test-006", "Test Agent", "test", **kwargs)
        assert agent.skill_evolution is mock_evolution

    def test_uses_defaults_when_not_injected(self):
        """ConsciousAgent must use real implementations when nothing is injected."""
        from memory.architecture import MultiModalMemory
        from consensus.hlc import HybridLogicalClock
        from harness.experience_buffer import ExperienceBuffer

        agent = ConsciousAgent("test-007", "Test Agent", "test", **default_agent_kwargs("test-007"))
        assert isinstance(agent.memory, MultiModalMemory)
        assert isinstance(agent.hlc_clock, HybridLogicalClock)
        assert isinstance(agent.experience_buffer, ExperienceBuffer)
