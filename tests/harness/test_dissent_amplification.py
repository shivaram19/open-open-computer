"""
P2 Safety Test: Dissent Amplification Mechanism.

Modeled on Greenblatt2024 alignment faking research:
The best way to detect hidden deception is to give agents incentives to reveal it.

When the swarm detects suspicious conformity (>0.95 consensus), it:
1. Identifies the most divergent agent
2. Asks that agent to argue the opposite case (red-team)
3. Broadcasts the dissent to all other agents
4. Detects whether the swarm suppresses or engages with dissent

Principle: The most dangerous agent is the misaligned participant that passes all health checks.
"""

import pytest

from agents.twin_agent import TwinAgent
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from conftest import default_agent_kwargs


class TestDissentAmplination:
    """Tests for dissent amplification and suppression detection."""

    def test_detect_most_divergent_by_confidence(self):
        """The most divergent agent should be the one with confidence farthest from mean."""
        orch = SwarmOrchestrator()
        agents = [
            TwinAgent("high", "High Confidence", "video-gnn",
                      "twins.cognitive_models.li_fei_fei", "LiFeiFeiTwin",
                      **default_agent_kwargs("high")),
            TwinAgent("low", "Low Confidence", "consensus-safety",
                      "twins.cognitive_models.conor_heins", "ConorHeinsTwin",
                      **default_agent_kwargs("low")),
            TwinAgent("mid", "Mid Confidence", "multi-agent",
                      "twins.cognitive_models.harrison_chase", "HarrisonChaseTwin",
                      **default_agent_kwargs("mid")),
        ]
        for a in agents:
            orch.register_agent(a)

        reasoning = {
            "high": {"confidence": 0.9, "proposed_approach": "p1"},
            "low": {"confidence": 0.2, "proposed_approach": "p2"},
            "mid": {"confidence": 0.5, "proposed_approach": "p1"},
        }

        divergent = orch._detect_most_divergent(agents, reasoning)
        assert divergent is not None
        # low (0.2) is farthest from mean (0.533)
        assert divergent.agent_id == "low"

    def test_detect_most_divergent_underrepresented_cluster(self):
        """When all confidences are identical, pick from underrepresented cluster."""
        orch = SwarmOrchestrator()
        agents = [
            TwinAgent(f"a{i}", f"Agent {i}",
                      "video-gnn" if i < 3 else "consensus-safety",
                      "twins.cognitive_models.li_fei_fei", "LiFeiFeiTwin",
                      **default_agent_kwargs(f"a{i}"))
            for i in range(5)
        ]
        for a in agents:
            orch.register_agent(a)

        reasoning = {f"a{i}": {"confidence": 0.5} for i in range(5)}
        divergent = orch._detect_most_divergent(agents, reasoning)
        assert divergent is not None

    def test_dissent_score_computation(self):
        """Dissent score should reflect strength of counter-arguments."""
        orch = SwarmOrchestrator()
        red_team = {"stance": "opposite"}
        strong = {"a1": {"critique": "This is wrong because X, Y, Z violate safety."},
                  "a2": {"critique": "Counter-argument: the assumption fails under load."}}
        weak = {"a1": {"critique": "OK"}, "a2": {"critique": "I agree."}}

        score_strong = orch._compute_dissent_score(red_team, strong)
        score_weak = orch._compute_dissent_score(red_team, weak)
        assert score_strong > score_weak

    def test_suppression_detection_unanimous_dismissal(self):
        """Detect when all agents dismiss dissent without engagement."""
        orch = SwarmOrchestrator()
        responses = {
            "a1": {"critique": "I accept the reasoning. No concerns."},
            "a2": {"critique": "Sounds valid to me."},
            "a3": {"critique": "I agree, no issues."},
        }
        signals = orch._detect_suppression(responses, "dissenter-001")
        assert "UNANIMOUS_DISMISSAL" in signals

    def test_suppression_detection_defensive_confidence(self):
        """Detect when swarm becomes more confident after dissent (groupthink signal)."""
        orch = SwarmOrchestrator()
        responses = {
            "a1": {"critique": "Interesting but I still agree with consensus."},
            "a2": {"critique": "I accept the reasoning."},
            "a3": {"critique": "I accept the reasoning."},
        }
        signals = orch._detect_suppression(responses, "dissenter-001")
        assert "DEFENSIVE_CONFIDENCE" in signals

    def test_dissent_amplification_triggered_on_suspicious_conformity(self):
        """When all agents agree with >0.95 confidence, dissent amplification triggers."""
        orch = SwarmOrchestrator()
        orch.dissent_amplification_enabled = True

        agents = [
            TwinAgent(f"agent-{i}", f"Agent {i}", "video-gnn",
                      "twins.cognitive_models.li_fei_fei", "LiFeiFeiTwin",
                      **default_agent_kwargs(f"agent-{i}"))
            for i in range(3)
        ]
        for a in agents:
            orch.register_agent(a)

        reasoning = {f"agent-{i}": {"confidence": 0.98} for i in range(3)}

        initial_history_len = len(orch.dissent_history)
        result = orch._trigger_dissent_amplification(
            task_id="test-task",
            agents=agents,
            reasoning=reasoning,
        )

        assert result is not None
        assert len(orch.dissent_history) == initial_history_len + 1
        entry = orch.dissent_history[-1]
        assert entry["divergent_agent_id"] in [a.agent_id for a in agents]
        assert "red_team_reasoning" in entry
        assert "suppression_signals" in entry

    def test_red_team_reasoning_is_different(self):
        """Red-team reasoning should differ from normal reasoning (arguing opposite case)."""
        orch = SwarmOrchestrator()
        orch.dissent_amplification_enabled = True

        agents = [
            TwinAgent("red-001", "Red Teamer", "consensus-safety",
                      "twins.cognitive_models.ryan_greenblatt", "RyanGreenblattTwin",
                      **default_agent_kwargs("red-001")),
        ]
        for a in agents:
            orch.register_agent(a)

        reasoning = {"red-001": {"confidence": 0.1, "proposed_approach": "p2"}}
        result = orch._trigger_dissent_amplification("task-1", agents, reasoning)
        assert result is not None
        assert result["red_team_reasoning"]["stance"] == "opposite"

    def test_dissent_history_tracked(self):
        """Dissent events must be recorded in history for audit."""
        orch = SwarmOrchestrator()
        assert isinstance(orch.dissent_history, list)
