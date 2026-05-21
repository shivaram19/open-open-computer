# tests/conftest.py
"""
Shared pytest fixtures and configuration for ACN test suite.

Eliminates the need for sys.path.insert in every test file.
All test modules automatically have acn/src in their Python path.

Research basis: Fowler (1999) — shared test infrastructure reduces
duplication and makes tests easier to write and maintain.
"""

import pytest


@pytest.fixture
def mock_agent_id():
    """Return a standard mock agent ID for tests."""
    return "test-agent-001"


@pytest.fixture
def mock_task():
    """Return a standard mock task description for tests."""
    return "Design a fault-tolerant consensus protocol for multi-agent systems"


def default_agent_kwargs(agent_id: str):
    """Return default DI kwargs for ConsciousAgent construction in tests."""
    from memory.architecture import MultiModalMemory
    from consensus.hlc import HybridLogicalClock
    from harness.experience_buffer import ExperienceBuffer
    from harness.meta_cognitive_reflection import ReflectionEngine
    from harness.policy_optimizer import PolicyOptimizer
    from harness.skill_evolution import SkillEvolution
    from perception.perception_subsystem import PerceptionSubsystem

    return {
        "memory": MultiModalMemory(),
        "clock": HybridLogicalClock(node_id=agent_id),
        "experience_buffer": ExperienceBuffer(),
        "reflection_engine": ReflectionEngine(),
        "policy_optimizer": PolicyOptimizer(),
        "skill_evolution": SkillEvolution(),
        "perception": PerceptionSubsystem(),
    }
