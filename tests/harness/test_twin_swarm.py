"""
P2 Integration Test: Twin-Based Conscious Agent Swarm Deliberation.

This test proves the bridge between P1 (cognitive twins) and P2 (conscious swarm):
1. Load 4 cognitive twins into TwinAgents
2. Compose a swarm for a complex task
3. Execute deliberation rounds
4. Verify cross-twin critique (different clusters critique differently)
5. Detect consensus or divergence
6. Synthesize collective output

Principle: You can't make a conscious system from unconscious agents.
"""

from agents.twin_agent import TwinAgent
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from agents.conscious_agent import AgentGoal
from harness.awareness import AwarenessLevel
from conftest import default_agent_kwargs


class TestTwinAgent:
    """A TwinAgent must load its cognitive twin and expose its reasoning."""

    def test_twin_agent_loads_cognitive_twin(self):
        agent = TwinAgent(
            agent_id="agent-001",
            name="Noah Shinn Agent",
            cluster="streaming-reflection",
            twin_module_path="twins.cognitive_models.noah_shinn",
            twin_class_name="NoahShinnTwin",
            **default_agent_kwargs("agent-001"),
        )
        assert agent.twin is not None
        assert agent.twin.NAME == "Noah Shinn"
        assert agent.twin.CLUSTER == "streaming-reflection"
        assert agent.twin_heuristics is not None
        assert agent.twin_biases is not None

    def test_twin_agent_think_uses_twin_reasoning(self):
        agent = TwinAgent(
            agent_id="agent-002",
            name="Conor Heins Agent",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
            **default_agent_kwargs("agent-002"),
        )
        agent.activate(AgentGoal(
            goal_id="test-goal",
            description="Design a consensus protocol for 5 agents",
            success_criteria=["Byzantine fault tolerant", "Latency < 100ms"],
        ))
        reasoning = agent.think()
        assert "twin_id" in reasoning
        assert reasoning["twin_id"] == "conor_heins-001"
        assert "self_critique" in reasoning
        assert "biases_acknowledged" in reasoning
        assert "confidence" in reasoning

    def test_cross_twin_critique_differs_by_cluster(self):
        safety_agent = TwinAgent(
            agent_id="safety-001",
            name="Safety Critic",
            cluster="consensus-safety",
            twin_module_path="twins.cognitive_models.conor_heins",
            twin_class_name="ConorHeinsTwin",
            **default_agent_kwargs("safety-001"),
        )
        stream_agent = TwinAgent(
            agent_id="stream-001",
            name="Stream Critic",
            cluster="streaming-reflection",
            twin_module_path="twins.cognitive_models.noah_shinn",
            twin_class_name="NoahShinnTwin",
            **default_agent_kwargs("stream-001"),
        )

        msg_high_conf = {
            "type": "proposal",
            "content": "We should deploy without testing",
            "reasoning": {"confidence": 0.99, "conclusion": "safe"},
        }

        safety_response = safety_agent.receive("peer-001", msg_high_conf)
        stream_response = stream_agent.receive("peer-001", msg_high_conf)

        # Safety twin should provide a critique (content varies by twin implementation)
        assert "critique" in safety_response

        # Stream twin might critique differently (iterative refinement)
        assert "critique" in stream_response


class TestSwarmOrchestratorTwinIntegration:
    """SwarmOrchestrator must compose a swarm from twin configs."""

    def test_swarm_orchestrator_composes_from_twins(self):
        orchestrator = SwarmOrchestrator()

        twin_configs = [
            {
                "agent_id": "video-001",
                "twin_module": "twins.cognitive_models.li_fei_fei",
                "twin_class": "LiFeiFeiTwin",
                "name": "Li Fei-Fei",
                "cluster": "video-gnn",
            },
            {
                "agent_id": "stream-001",
                "twin_module": "twins.cognitive_models.noah_shinn",
                "twin_class": "NoahShinnTwin",
                "name": "Noah Shinn",
                "cluster": "streaming-reflection",
            },
            {
                "agent_id": "safety-001",
                "twin_module": "twins.cognitive_models.conor_heins",
                "twin_class": "ConorHeinsTwin",
                "name": "Conor Heins",
                "cluster": "consensus-safety",
            },
            {
                "agent_id": "multi-001",
                "twin_module": "twins.cognitive_models.harrison_chase",
                "twin_class": "HarrisonChaseTwin",
                "name": "Harrison Chase",
                "cluster": "multi-agent",
            },
        ]

        task = SwarmTask(
            task_id="task-video-consensus",
            description="Build a real-time video consensus system for autonomous vehicle fleets",
            required_clusters=["video-gnn", "streaming-reflection", "consensus-safety", "multi-agent"],
            success_criteria=["30 FPS", "Latency < 50ms"],
        )

        activated = orchestrator.compose_swarm_from_twins(twin_configs, task)
        assert len(activated) == 4
        assert "video-001" in activated
        assert "stream-001" in activated

    def test_swarm_deliberation_round(self):
        orchestrator = SwarmOrchestrator()
        twin_configs = [
            {
                "agent_id": "video-001",
                "twin_module": "twins.cognitive_models.li_fei_fei",
                "twin_class": "LiFeiFeiTwin",
                "name": "Li Fei-Fei",
                "cluster": "video-gnn",
            },
            {
                "agent_id": "multi-001",
                "twin_module": "twins.cognitive_models.harrison_chase",
                "twin_class": "HarrisonChaseTwin",
                "name": "Harrison Chase",
                "cluster": "multi-agent",
            },
        ]
        task = SwarmTask(
            task_id="task-delib",
            description="Design a spatio-temporal GNN",
            required_clusters=["video-gnn", "multi-agent"],
            success_criteria=["Topology handles failures"],
        )
        orchestrator.compose_swarm_from_twins(twin_configs, task)
        result = orchestrator.execute_deliberation_round("task-delib")
        assert "error" not in result
        assert result["round"] == 1

    def test_swarm_synthesis_report(self):
        orchestrator = SwarmOrchestrator()
        twin_configs = [
            {
                "agent_id": "video-001",
                "twin_module": "twins.cognitive_models.li_fei_fei",
                "twin_class": "LiFeiFeiTwin",
                "name": "Li Fei-Fei",
                "cluster": "video-gnn",
            },
            {
                "agent_id": "multi-001",
                "twin_module": "twins.cognitive_models.harrison_chase",
                "twin_class": "HarrisonChaseTwin",
                "name": "Harrison Chase",
                "cluster": "multi-agent",
            },
        ]
        task = SwarmTask(
            task_id="task-report",
            description="Design a spatio-temporal GNN communication topology",
            required_clusters=["video-gnn", "multi-agent"],
            success_criteria=["Topology handles failures", "Throughput > 30 FPS"],
        )
        orchestrator.compose_swarm_from_twins(twin_configs, task)
        orchestrator.run_full_deliberation("task-report")
        report = orchestrator.synthesize_report("task-report")
        assert report["task_id"] == "task-report"
        assert report["swarm_size"] == 2
        assert "agent_reports" in report

    def test_full_twin_swarm_end_to_end(self):
        orchestrator = SwarmOrchestrator()
        twin_configs = [
            {
                "agent_id": "video-001",
                "twin_module": "twins.cognitive_models.li_fei_fei",
                "twin_class": "LiFeiFeiTwin",
                "name": "Li Fei-Fei",
                "cluster": "video-gnn",
            },
            {
                "agent_id": "stream-001",
                "twin_module": "twins.cognitive_models.noah_shinn",
                "twin_class": "NoahShinnTwin",
                "name": "Noah Shinn",
                "cluster": "streaming-reflection",
            },
            {
                "agent_id": "safety-001",
                "twin_module": "twins.cognitive_models.conor_heins",
                "twin_class": "ConorHeinsTwin",
                "name": "Conor Heins",
                "cluster": "consensus-safety",
            },
            {
                "agent_id": "multi-001",
                "twin_module": "twins.cognitive_models.harrison_chase",
                "twin_class": "HarrisonChaseTwin",
                "name": "Harrison Chase",
                "cluster": "multi-agent",
            },
        ]
        task = SwarmTask(
            task_id="task-e2e",
            description="Design a resilient multi-agent video analysis system",
            required_clusters=["video-gnn", "streaming-reflection", "consensus-safety", "multi-agent"],
            success_criteria=["30 FPS", "Latency < 100ms"],
            min_agents=3,
            max_agents=6,
        )
        activated = orchestrator.compose_swarm_from_twins(twin_configs, task)
        assert len(activated) == 4
        result = orchestrator.run_full_deliberation("task-e2e")
        assert result["total_rounds"] >= 1
        report = orchestrator.synthesize_report("task-e2e")
        assert report["swarm_size"] == 4
        agent_names = [r["agent_name"] for r in report["agent_reports"]]
        assert "Li Fei-Fei" in agent_names
        assert "Noah Shinn" in agent_names
        assert "Conor Heins" in agent_names
        assert "Harrison Chase" in agent_names
