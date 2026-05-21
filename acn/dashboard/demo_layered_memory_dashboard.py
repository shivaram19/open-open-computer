#!/usr/bin/env python3
"""
Demo script: Create twins with layered memory, run deliberation, export dashboard state.

Usage:
    python acn/dashboard/demo_layered_memory_dashboard.py
    streamlit run acn/dashboard/consensus_dashboard.py
"""

import sys
sys.path.insert(0, "acn/src")

from agents.twin_agent import TwinAgent
from agents.conscious_agent import AgentGoal
from memory.twin_memory_profile import TwinMemoryProfile
from dashboard.data_collector import DashboardDataCollector


def main():
    print("Creating twins with layered memory profiles...")

    # Twin 1: Noah Shinn (streaming-reflection)
    profile1 = TwinMemoryProfile(
        twin_id="noah-shinn-001",
        base_signature={
            "name": "Noah Shinn",
            "cluster": "streaming-reflection",
            "heuristics": {"composition": "Verbal feedback loop"},
            "biases": {"verbal_bias": "Overemphasizes linguistic reasoning"},
        },
    )
    twin1 = TwinAgent(
        agent_id="agent-001",
        name="Noah",
        cluster="streaming-reflection",
        twin_module_path="twins.cognitive_models.noah_shinn",
        twin_class_name="NoahShinnTwin",
        layered_memory_profile=profile1,
    )

    # Twin 2: Conor Heins (consensus-safety)
    profile2 = TwinMemoryProfile(
        twin_id="conor-heins-001",
        base_signature={
            "name": "Conor Heins",
            "cluster": "consensus-safety",
            "heuristics": {"verification": "Trust = proof + test"},
            "biases": {"pessimism_bias": "Over-engineers safety"},
        },
    )
    twin2 = TwinAgent(
        agent_id="agent-002",
        name="Conor",
        cluster="consensus-safety",
        twin_module_path="twins.cognitive_models.conor_heins",
        twin_class_name="ConorHeinsTwin",
        layered_memory_profile=profile2,
    )

    # Simulate several thinking rounds
    tasks = [
        "Should we use BFT or PoS for consensus?",
        "How to handle Byzantine faults in a 5-node network?",
        "What is the optimal consensus for safety-critical systems?",
        "Can we combine BFT with self-correcting feedback loops?",
        "What are the tradeoffs between liveness and safety?",
    ]

    print("Simulating thinking rounds...")
    for i, task in enumerate(tasks):
        goal1 = AgentGoal(goal_id=f"g1-{i}", description=task, success_criteria=["decided"])
        twin1.activate(goal1)
        twin1.think()

        goal2 = AgentGoal(goal_id=f"g2-{i}", description=task, success_criteria=["decided"])
        twin2.activate(goal2)
        twin2.think()

        # Simulate some peer critiques
        if i % 2 == 0:
            twin1.receive("agent-002", {"confidence": 0.9, "reasoning": {"approach": "BFT is safer"}})
            twin2.receive("agent-001", {"confidence": 0.85, "reasoning": {"approach": "Add verbal feedback"}})

    print("Running consolidation...")
    report1 = profile1.consolidate()
    report2 = profile2.consolidate()
    print(f"  Noah: {report1.atoms_processed} atoms → {report1.scenarios_mined} scenarios → persona v{report1.persona_version}")
    print(f"  Conor: {report2.atoms_processed} atoms → {report2.scenarios_mined} scenarios → persona v{report2.persona_version}")

    # Create a mock orchestrator and collect data
    class MockOrchestrator:
        def __init__(self, agents):
            self.agents = agents

    orchestrator = MockOrchestrator({"agent-001": twin1, "agent-002": twin2})

    print("Exporting dashboard state...")
    collector = DashboardDataCollector()
    collector.collect_from_swarm(orchestrator)
    collector.record_consensus(score=0.82, round_num=3, academic_support=0.75, dissent=False)
    collector.save()

    print(f"Dashboard state saved to: {collector.state_path}")
    print("\nRun the dashboard with:")
    print("  streamlit run acn/dashboard/consensus_dashboard.py")


if __name__ == "__main__":
    main()
