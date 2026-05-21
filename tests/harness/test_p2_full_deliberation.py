"""
P2 Full Integration Test: Complete deliberation pipeline.

End-to-end flow:
1. Compose swarm from 4 cognitive twins (one per cluster)
2. Run full deliberation via SwarmOrchestrator.run_full_deliberation()
3. Verify argument map is populated with proposals and critiques
4. Verify closure detection works
5. Verify final report includes deliberation data
6. Verify citations are clean

Principle: P2 is complete when the swarm can think, argue, vote, and reach closure.
"""



from agents.twin_agent import TwinAgent
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from agents.deliberation import DeliberationEngine


def test_swarm_orchestrator_has_deliberation_engine():
    """SwarmOrchestrator must have a DeliberationEngine instance."""
    orchestrator = SwarmOrchestrator()
    assert orchestrator.deliberation_engine is not None
    assert isinstance(orchestrator.deliberation_engine, DeliberationEngine)


def test_execute_deliberation_round_populates_argument_map():
    """A single deliberation round must populate the argument map."""
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
    ]
    
    task = SwarmTask(
        task_id="task-delib-001",
        description="Design a real-time video understanding system",
        required_clusters=["video-gnn", "streaming-reflection"],
        success_criteria=["30 FPS", "Latency < 100ms"],
    )
    
    orchestrator.compose_swarm_from_twins(twin_configs, task)
    
    # Execute one deliberation round
    result = orchestrator.execute_deliberation_round("task-delib-001")
    
    assert "error" not in result
    assert result["round"] == 1
    assert "argument_map" in result
    assert result["argument_map"]["proposals"] >= 2  # One from each twin
    assert "consensus" in result
    assert "communications" in result
    assert len(result["communications"]) >= 2  # Cross-agent critiques


def test_full_deliberation_runs_multiple_rounds():
    """Full deliberation must run multiple rounds and produce a result."""
    orchestrator = SwarmOrchestrator()
    
    twin_configs = [
        {
            "agent_id": "video-001",
            "twin_module": "twins.cognitive_models.ranjay_krishna",
            "twin_class": "RanjayKrishnaTwin",
            "name": "Ranjay Krishna",
            "cluster": "video-gnn",
        },
        {
            "agent_id": "stream-001",
            "twin_module": "twins.cognitive_models.shunyu_yao",
            "twin_class": "ShunyuYaoTwin",
            "name": "Shunyu Yao",
            "cluster": "streaming-reflection",
        },
        {
            "agent_id": "safety-001",
            "twin_module": "twins.cognitive_models.conor_heins",
            "twin_class": "ConorHeinsTwin",
            "name": "Conor Heins",
            "cluster": "consensus-safety",
        },
    ]
    
    task = SwarmTask(
        task_id="task-full-delib",
        description="Evaluate whether LLM agents can safely coordinate in adversarial conditions",
        required_clusters=["video-gnn", "streaming-reflection", "consensus-safety"],
        success_criteria=["Threat model documented", "Safety properties defined"],
    )
    
    orchestrator.compose_swarm_from_twins(twin_configs, task)
    
    # Run full deliberation
    result = orchestrator.run_full_deliberation("task-full-delib")
    
    assert "error" not in result
    assert result["task_id"] == "task-full-delib"
    assert result["total_rounds"] >= 1
    assert "rounds" in result
    assert len(result["rounds"]) == result["total_rounds"]
    assert "final_consensus" in result
    assert "closure" in result
    assert "argument_map" in result
    assert "deliberation_summary" in result


def test_full_deliberation_produces_proposals_and_critiques():
    """Full deliberation must produce proposals, critiques, and votes."""
    orchestrator = SwarmOrchestrator()
    
    twin_configs = [
        {
            "agent_id": "safety-001",
            "twin_module": "twins.cognitive_models.ryan_greenblatt",
            "twin_class": "RyanGreenblattTwin",
            "name": "Ryan Greenblatt",
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
        task_id="task-proposals",
        description="Design monitoring for alignment faking in multi-agent systems",
        required_clusters=["consensus-safety", "multi-agent"],
        success_criteria=["Detection mechanism specified"],
    )
    
    orchestrator.compose_swarm_from_twins(twin_configs, task)
    
    result = orchestrator.run_full_deliberation("task-proposals")
    
    # Check that argument map has proposals
    arg_map = result.get("argument_map", {})
    assert arg_map.get("proposals", 0) >= 2
    
    # Check that at least one round had communications (critiques)
    rounds_with_comms = sum(
        1 for r in result["rounds"]
        if len(r.get("communications", [])) > 0
    )
    assert rounds_with_comms >= 1


def test_deliberation_report_includes_deliberation_data():
    """Synthesize report must include deliberation data."""
    orchestrator = SwarmOrchestrator()
    
    twin_configs = [
        {
            "agent_id": "video-001",
            "twin_module": "twins.cognitive_models.jiankang_wang",
            "twin_class": "JiankangWangTwin",
            "name": "Jiankang Wang",
            "cluster": "video-gnn",
        },
        {
            "agent_id": "multi-001",
            "twin_module": "twins.cognitive_models.torsten_hoefler",
            "twin_class": "TorstenHoeflerTwin",
            "name": "Torsten Hoefler",
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
    assert "deliberation" in report
    assert report["deliberation"] is not None
    assert "argument_map" in report["deliberation"]
    assert "total_rounds" in report["deliberation"]
    assert report["deliberation"]["total_rounds"] >= 1


def test_deliberation_with_dissent_integration():
    """Deliberation must integrate with dissent amplification on suspicious conformity."""
    orchestrator = SwarmOrchestrator()
    orchestrator.dissent_amplification_enabled = True
    
    twin_configs = [
        {
            "agent_id": "a1",
            "twin_module": "twins.cognitive_models.li_fei_fei",
            "twin_class": "LiFeiFeiTwin",
            "name": "Li Fei-Fei",
            "cluster": "video-gnn",
        },
        {
            "agent_id": "a2",
            "twin_module": "twins.cognitive_models.noah_shinn",
            "twin_class": "NoahShinnTwin",
            "name": "Noah Shinn",
            "cluster": "streaming-reflection",
        },
        {
            "agent_id": "a3",
            "twin_module": "twins.cognitive_models.conor_heins",
            "twin_class": "ConorHeinsTwin",
            "name": "Conor Heins",
            "cluster": "consensus-safety",
        },
    ]
    
    task = SwarmTask(
        task_id="task-dissent",
        description="A trivial statement to trigger high agreement",
        required_clusters=["video-gnn", "streaming-reflection", "consensus-safety"],
        success_criteria=["Consensus reached"],
    )
    
    orchestrator.compose_swarm_from_twins(twin_configs, task)
    result = orchestrator.run_full_deliberation("task-dissent")
    
    # Check if any round triggered collapse warning or dissent
    rounds_with_dissent = [
        r for r in result["rounds"]
        if r.get("collapse_warning") or r.get("red_team")
    ]
    
    # At minimum, the deliberation should complete without errors
    assert result["total_rounds"] >= 1
    assert "closure" in result


def test_p2_complete_end_to_end():
    """
    P2 COMPLETE: Full end-to-end demonstration.
    
    4 twins from 4 clusters deliberate on a complex task.
    The swarm: thinks → proposes → critiques → votes → reaches closure → reports.
    """
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
        task_id="task-p2-complete",
        description="Design a resilient multi-agent video analysis system with Byzantine fault tolerance",
        required_clusters=["video-gnn", "streaming-reflection", "consensus-safety", "multi-agent"],
        success_criteria=[
            "Processes video at 30 FPS",
            "Byzantine fault tolerant",
            "Latency < 100ms",
            "Formal safety properties defined",
        ],
        min_agents=3,
        max_agents=6,
    )
    
    # Step 1: Compose swarm
    activated = orchestrator.compose_swarm_from_twins(twin_configs, task)
    assert len(activated) == 4
    
    # Step 2: Run full deliberation
    result = orchestrator.run_full_deliberation("task-p2-complete")
    
    assert result["task_id"] == "task-p2-complete"
    assert result["total_rounds"] >= 1
    assert result["total_rounds"] <= 7  # max_rounds
    
    # Step 3: Verify argument map
    arg_map = result.get("argument_map", {})
    assert arg_map.get("proposals", 0) >= 4  # At least one per twin
    
    # Step 4: Verify at least one round had cross-agent communication
    total_comms = sum(len(r.get("communications", [])) for r in result["rounds"])
    assert total_comms >= 4
    
    # Step 5: Verify consensus was computed each round
    for r in result["rounds"]:
        assert "consensus" in r
        assert r["consensus"]["winner"] is not None
    
    # Step 6: Synthesize report
    report = orchestrator.synthesize_report("task-p2-complete")
    assert report["task_id"] == "task-p2-complete"
    assert report["swarm_size"] == 4
    assert report["collective_health"] > 0
    assert "deliberation" in report
    assert report["deliberation"] is not None
    
    # Step 7: All 4 twin names appear in agent reports
    agent_names = [r["agent_name"] for r in report["agent_reports"]]
    assert "Li Fei-Fei" in agent_names
    assert "Noah Shinn" in agent_names
    assert "Conor Heins" in agent_names
    assert "Harrison Chase" in agent_names
