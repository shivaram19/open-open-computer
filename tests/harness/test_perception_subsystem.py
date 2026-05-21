"""
TDD Tests for PerceptionSubsystem extraction.

Drives the extraction of P6 perception code from ConsciousAgent into
a separate, injectable PerceptionSubsystem.

Research basis:
- Martin (2002): SRP — ConsciousAgent should not know about scene graphs
- Martin (1996): ISP — agents that don't process video shouldn't carry video infra
"""

from unittest.mock import Mock
import pytest

from agents.conscious_agent import ConsciousAgent
from conftest import default_agent_kwargs


class TestPerceptionSubsystem:
    """Tests for the PerceptionSubsystem abstraction."""

    def test_perception_subsystem_exists(self):
        """A PerceptionSubsystem class must exist."""
        from perception.perception_subsystem import PerceptionSubsystem
        ps = PerceptionSubsystem()
        assert ps is not None

    def test_perception_subsystem_has_scene_graph(self):
        """PerceptionSubsystem must expose scene graph capabilities."""
        from perception.perception_subsystem import PerceptionSubsystem
        ps = PerceptionSubsystem()
        ps.initialize(video_id="test-video")
        assert ps.scene_graph is not None

    def test_perception_subsystem_perceives_frame(self):
        """PerceptionSubsystem must process video frames."""
        from perception.perception_subsystem import PerceptionSubsystem
        ps = PerceptionSubsystem()
        ps.initialize(video_id="test-video")
        result = ps.perceive_frame(
            frame_id=0,
            detections=[{"class_name": "person", "bbox": [10, 10, 50, 50], "confidence": 0.9}],
        )
        assert "objects_detected" in result


class TestConsciousAgentAcceptsPerception:
    """Tests that ConsciousAgent accepts injected PerceptionSubsystem."""

    def test_can_inject_perception_subsystem(self):
        """ConsciousAgent must accept an injected PerceptionSubsystem."""
        from perception.perception_subsystem import PerceptionSubsystem
        ps = PerceptionSubsystem()
        kwargs = default_agent_kwargs("test-008")
        kwargs["perception"] = ps
        agent = ConsciousAgent("test-008", "Test Agent", "test", **kwargs)
        assert agent.perception is ps

    def test_has_default_perception_by_default(self):
        """ConsciousAgent must have a default PerceptionSubsystem when not injected."""
        from perception.perception_subsystem import PerceptionSubsystem
        agent = ConsciousAgent("test-009", "Test Agent", "test", **default_agent_kwargs("test-009"))
        assert isinstance(agent.perception, PerceptionSubsystem)
