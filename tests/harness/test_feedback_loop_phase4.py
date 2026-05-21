"""
TDD Tests for Phase 4.5 — SelfImprovementLoop required DI.

Verifies that SelfImprovementLoop requires injected dependencies
and does not silently create default concrete instances.
"""

import pytest

from harness.feedback_loop import SelfImprovementLoop
from harness.experience_buffer import ExperienceBuffer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.policy_optimizer import PolicyOptimizer
from harness.skill_evolution import SkillEvolution


class TestSelfImprovementLoopRequiredDI:
    """SelfImprovementLoop must require DI — no silent defaults."""

    def test_raises_when_no_dependencies_provided(self):
        """Constructing with no args must raise TypeError."""
        with pytest.raises(TypeError):
            SelfImprovementLoop()

    def test_accepts_all_dependencies(self):
        """Constructing with all dependencies must succeed."""
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        assert loop.experience_buffer is not None
        assert loop.reflection_engine is not None
        assert loop.policy_optimizer is not None
        assert loop.skill_evolution is not None
