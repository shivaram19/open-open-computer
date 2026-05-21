# tests/memory/test_twin_agent_layered_memory.py
"""Tests for TwinAgent + LayeredMemory integration."""

import pytest
from agents.twin_agent import TwinAgent
from memory.twin_memory_profile import TwinMemoryProfile
from memory.layered_models import AtomType


class TestTwinAgentLayeredMemory:
    def test_twin_agent_without_layered_memory(self):
        """TwinAgent works normally without layered memory (backward compat)."""
        agent = TwinAgent(
            agent_id="test-001",
            name="Test Twin",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
        )
        assert agent.layered_memory is None
        from agents.conscious_agent import AgentGoal
        goal = AgentGoal(
            goal_id="g1",
            description="Test consensus",
            success_criteria=["done"],
        )
        agent.activate(goal)
        result = agent.think()
        assert "error" not in result
        assert result["agent_id"] == "test-001"

    def test_twin_agent_with_layered_memory(self):
        profile = TwinMemoryProfile(
            twin_id="conor-heins-001",
            base_signature={"name": "Conor Heins", "cluster": "consensus-safety"},
        )
        agent = TwinAgent(
            agent_id="test-002",
            name="Conor Twin",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
            layered_memory_profile=profile,
        )
        from agents.conscious_agent import AgentGoal
        goal = AgentGoal(
            goal_id="g2",
            description="Should we use BFT or PoS?",
            success_criteria=["decision made"],
        )
        agent.activate(goal)
        result = agent.think()
        assert result["agent_id"] == "test-002"
        # Memory should have been recorded
        stats = profile.get_stats()
        assert stats["l0_conversation"] >= 1
        assert stats["l1_atoms"] >= 1

    def test_twin_agent_layered_memory_context_injection(self):
        profile = TwinMemoryProfile(
            twin_id="noah-shinn-001",
            base_signature={"name": "Noah Shinn", "cluster": "streaming-reflection"},
        )
        # Pre-seed memory with a prior thought
        profile.record_think({
            "task": "debugging strategy",
            "confidence": 0.9,
            "phase_1_initial_attempt": "Use breakpoints and step through code.",
            "timestamp": 1234567890,
        })

        agent = TwinAgent(
            agent_id="test-003",
            name="Noah Twin",
            cluster="streaming-reflection",
            twin_module_path="twins.cognitive_models.noah_shinn",
            twin_class_name="NoahShinnTwin",
            layered_memory_profile=profile,
        )
        from agents.conscious_agent import AgentGoal
        goal = AgentGoal(
            goal_id="g3",
            description="How to debug this failure?",
            success_criteria=["strategy found"],
        )
        agent.activate(goal)
        result = agent.think()
        # The twin_reasoning should have received layered memory context
        assert "twin_reasoning" in result

    def test_twin_agent_receive_with_layered_memory(self):
        profile = TwinMemoryProfile(
            twin_id="conor-heins-001",
            base_signature={"name": "Conor Heins", "cluster": "consensus-safety"},
        )
        agent = TwinAgent(
            agent_id="test-004",
            name="Conor Twin",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
            layered_memory_profile=profile,
        )
        response = agent.receive(
            from_agent_id="peer-001",
            message={
                "confidence": 0.95,
                "reasoning": {"approach": "PoS is better"},
            },
        )
        assert response["status"] == "received"
        assert "critique" in response
        # Critique should be recorded in layered memory
        stats = profile.get_stats()
        assert stats["l0_conversation"] >= 1

    def test_twin_agent_backward_compat_receive_without_layered_memory(self):
        agent = TwinAgent(
            agent_id="test-005",
            name="Test Twin",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
        )
        response = agent.receive(
            from_agent_id="peer-001",
            message={"confidence": 0.8, "reasoning": {}},
        )
        assert response["status"] == "received"
        # Should not crash without layered memory
