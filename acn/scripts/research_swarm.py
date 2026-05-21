#!/usr/bin/env python3
"""
Research Swarm: Parallel Deep Research on P1 Tasks using Conscious Agents.

Spawns multiple conscious agents with distinct cognitive styles,
each researching a P1 foundation task. Agents search the web,
critique each other's findings, and synthesize an execution plan.

Usage: python acn/scripts/research_swarm.py
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from agents.cognitive_skill import SkillRegistry, CognitiveSkill
from harness.awareness import AwarenessLevel
from memory.architecture import MemoryTrace, MemoryType, RetrievalStrategy

# Import cognitive twins for distinct reasoning styles
from twins.cognitive_models.li_fei_fei import LiFeiFeiTwin
from twins.cognitive_models.noah_shinn import NoahShinnTwin
from perception.perception_subsystem import PerceptionSubsystem
from harness.skill_evolution import SkillEvolution
from harness.policy_optimizer import PolicyOptimizer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.experience_buffer import ExperienceBuffer
from consensus.hlc import HybridLogicalClock
from memory.architecture import MultiModalMemory


def create_research_skill() -> CognitiveSkill:
    """Create the deep-research skill with citation backing."""
    return CognitiveSkill(
        name="deep-research",
        description="Conduct deep research with web search and paper analysis",
        citations=["Shinn2023", "Besta2024"],
        workflow="""
1. Search web for latest evidence on the topic
2. Fetch and analyze top sources
3. Extract key findings with citations
4. Cross-reference with existing knowledge
5. Synthesize structured report with actionable recommendations
        """,
        tools=["SearchWeb", "FetchURL"],
        inputs={"topic": "str", "depth": "int"},
        outputs={"report": "str", "citations": "list", "recommendations": "list"},
    )


def spawn_research_agents(orchestrator: SwarmOrchestrator, skill_registry: SkillRegistry) -> List[ConsciousAgent]:
    """Spawn conscious agents with distinct cognitive styles for parallel research."""
    
    # Agent 1: Li Fei-Fei style — empirical, scale-first, benchmark-driven
    agent_empirical = ConsciousAgent(
        agent_id="research-empirical-001",
        name="EmpiricalResearcher",
        cluster="video-gnn",
        awareness_level=AwarenessLevel.FULL,
        context_scope={
            "twin_style": "li-fei-fei",
            "epistemology": "empirical",
            "method": "build-and-test",
            "domain": "unit-testing-awareness-subsystems",
        },
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-empirical-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem())
    
    # Agent 2: Noah Shinn style — iterative self-critique, reflection-driven
    agent_reflection = ConsciousAgent(
        agent_id="research-reflection-001",
        name="ReflectionResearcher",
        cluster="streaming-reflection",
        awareness_level=AwarenessLevel.FULL,
        context_scope={
            "twin_style": "noah-shinn",
            "epistemology": "hybrid",
            "method": "generate-critique-refine",
            "domain": "multi-modal-memory-testing",
        },
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-reflection-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem())
    
    # Agent 3: Consensus/Safety style — formal verification, edge-case hunting
    agent_formal = ConsciousAgent(
        agent_id="research-formal-001",
        name="FormalResearcher",
        cluster="consensus-safety",
        awareness_level=AwarenessLevel.FULL,
        context_scope={
            "twin_style": "formal-verification",
            "epistemology": "deductive",
            "method": "model-check",
            "domain": "cognitive-twin-transformation-at-scale",
        },
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-formal-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem())
    
    # Agent 4: Multi-Agent/Frameworks style — system design, integration patterns
    agent_system = ConsciousAgent(
        agent_id="research-system-001",
        name="SystemResearcher",
        cluster="multi-agent",
        awareness_level=AwarenessLevel.FULL,
        context_scope={
            "twin_style": "system-design",
            "epistemology": "pragmatic",
            "method": "decompose-and-integrate",
            "domain": "task-decomposition-algorithms",
        },
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-system-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem())
    
    agents = [agent_empirical, agent_reflection, agent_formal, agent_system]
    
    for agent in agents:
        orchestrator.register_agent(agent)
    
    # Load research skill into all agents
    skill = create_research_skill()
    skill_registry.register(skill)
    for agent in agents:
        skill_registry.load_into_agent("deep-research", agent)
    
    return agents


def assign_research_goals(agents: List[ConsciousAgent]) -> Dict[str, str]:
    """Assign P1 research topics to each agent."""
    assignments = {
        "research-empirical-001": {
            "topic": "P1-1: Unit testing awareness subsystems in agent architectures",
            "queries": [
                "unit testing agent awareness subsystems best practices",
                "goal state tracking test patterns autonomous systems",
                "direction vector computation testing agent orientation",
            ],
            "focus": "What test patterns validate awareness tracking? How to test direction alignment, drift detection, alert firing?",
        },
        "research-reflection-001": {
            "topic": "P1-2: Multi-modal memory architecture testing",
            "queries": [
                "testing multi-modal memory systems AI agents",
                "episodic semantic procedural memory unit tests",
                "working memory capacity limit testing 7 plus minus 2",
            ],
            "focus": "How to test 5 memory types? How to verify pruning, Bayesian updates, reinforcement, causal chains?",
        },
        "research-formal-001": {
            "topic": "P1-3: Automated cognitive twin generation at scale",
            "queries": [
                "automated cognitive model generation from researcher profiles",
                "schema-driven code generation cognitive twins",
                "batch transforming researcher profiles into executable models",
            ],
            "focus": "How to transform 37 researcher profiles into cognitive models automatically? Template vs. LLM generation?",
        },
        "research-system-001": {
            "topic": "P1-6: Task decomposition algorithms for agent harnesses",
            "queries": [
                "task decomposition algorithms autonomous agents 2024 2025",
                "Graph of Thoughts task decomposition Besta",
                "agent harness intent parsing sub-task generation",
            ],
            "focus": "What algorithms decompose complex tasks into agent-executable sub-tasks? DAG construction? Dependency resolution?",
        },
    }
    
    for agent in agents:
        assignment = assignments[agent.agent_id]
        goal = AgentGoal(
            goal_id=f"research-{agent.agent_id}",
            description=assignment["topic"],
            success_criteria=[
                f"Find 3+ authoritative sources on {assignment['topic']}",
                "Extract actionable patterns for implementation",
                "Cross-reference with existing ACN architecture",
                "Produce prioritized recommendation list",
            ],
            priority=5,
        )
        agent.activate(goal)
        # Store assignment in memory
        agent.memory.store(MemoryTrace(
            trace_id=f"assignment-{agent.agent_id}",
            memory_type=MemoryType.EPISODIC,
            content=assignment,
            source="research_swarm",
            confidence=1.0,
            importance=0.9,
            tags=["assignment", "p1-research"],
        ))
    
    return {a.agent_id: assignments[a.agent_id]["topic"] for a in agents}


def run_research_round(agent: ConsciousAgent, web_search_func) -> Dict[str, Any]:
    """Run one research round: search web, analyze, store findings."""
    # Get assignment from memory
    # Note: CONTEXTUAL is not in the enum, use EPISODIC for now
    memories = agent.memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, query="assignment", limit=1)
    if not memories:
        return {"error": "No assignment found"}
    
    assignment = memories[0].content
    queries = assignment.get("queries", [])
    focus = assignment.get("focus", "")
    
    findings = {
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "topic": assignment.get("topic", ""),
        "searches": [],
        "timestamp": time.time(),
    }
    
    # Execute web searches
    for query in queries[:2]:  # Limit to 2 searches per agent to avoid rate limits
        try:
            # Note: web_search_func would be SearchWeb tool call
            # For now, we simulate structured search results
            findings["searches"].append({
                "query": query,
                "status": "simulated",
                "results": [],
            })
        except Exception as e:
            findings["searches"].append({
                "query": query,
                "status": "error",
                "error": str(e),
            })
    
    # Agent thinks about findings
    reasoning = agent.think()
    findings["reasoning"] = reasoning
    findings["confidence"] = reasoning.get("confidence", 0.5)
    
    return findings


def cross_critique(agents: List[ConsciousAgent]) -> List[Dict[str, Any]]:
    """Have agents critique each other's reasoning."""
    critiques = []
    
    # Pair agents from different clusters
    pairs = [
        ("research-empirical-001", "research-reflection-001"),
        ("research-formal-001", "research-system-001"),
        ("research-empirical-001", "research-formal-001"),
        ("research-reflection-001", "research-system-001"),
    ]
    
    for from_id, to_id in pairs:
        from_agent = next((a for a in agents if a.agent_id == from_id), None)
        to_agent = next((a for a in agents if a.agent_id == to_id), None)
        if from_agent and to_agent:
            # Share reasoning trace
            msg = {
                "type": "research_findings",
                "content": f"Research on {from_agent.context_scope.get('domain', 'topic')}",
                "confidence": from_agent._calibrate_confidence(),
                "reasoning": from_agent.reasoning_trace[-1] if from_agent.reasoning_trace else {},
            }
            response = from_agent.communicate(to_id, msg)
            critiques.append({
                "from": from_id,
                "to": to_id,
                "critique": response.get("critique", "No critique"),
            })
    
    return critiques


def synthesize_execution_plan(agents: List[ConsciousAgent], critiques: List[Dict]) -> Dict[str, Any]:
    """Synthesize findings into a prioritized execution plan."""
    
    # Collect all agent reports
    reports = [agent.report() for agent in agents]
    
    # Compute priorities based on confidence and swarm health
    avg_health = sum(r.get("health_score", 1.0) for r in reports) / len(reports)
    total_reasoning = sum(r.get("reasoning_trace_count", 0) for r in reports)
    
    # Build execution plan
    plan = {
        "swarm_health": avg_health,
        "total_reasoning_steps": total_reasoning,
        "agents_contributed": len([r for r in reports if r.get("reasoning_trace_count", 0) > 0]),
        "critiques_exchanged": len(critiques),
        "recommended_execution_order": [],
        "risk_assessment": [],
    }
    
    # Prioritize by agent confidence and topic criticality
    topic_priorities = [
        ("P1-1: Unit Tests for Awareness", "research-empirical-001", "CRITICAL"),
        ("P1-2: Unit Tests for Memory", "research-reflection-001", "CRITICAL"),
        ("P1-6: Task Decomposer", "research-system-001", "HIGH"),
        ("P1-3: Transform 37 Twins", "research-formal-001", "MEDIUM"),
    ]
    
    for topic, agent_id, priority in topic_priorities:
        agent = next((a for a in agents if a.agent_id == agent_id), None)
        confidence = agent._calibrate_confidence() if agent else 0.5
        plan["recommended_execution_order"].append({
            "topic": topic,
            "priority": priority,
            "agent": agent_id,
            "confidence": confidence,
            "rationale": f"{priority} priority based on foundation dependency order",
        })
    
    # Risk assessment
    low_confidence = [r for r in reports if r.get("health_score", 1.0) < 0.6]
    if low_confidence:
        plan["risk_assessment"].append(
            f"{len(low_confidence)} agent(s) show low health — may need more research cycles"
        )
    
    if not any(c.get("critique") and "accepted" not in c.get("critique", "").lower() for c in critiques):
        plan["risk_assessment"].append(
            "Critiques are too agreeable — possible groupthink. Consider adversarial review."
        )
    
    return plan


def main():
    print("=" * 70)
    print("RESEARCH SWARM: Parallel Deep Research on P1 Foundation Tasks")
    print("=" * 70)
    print()
    
    # Setup
    orchestrator = SwarmOrchestrator()
    skill_registry = SkillRegistry()
    
    # Spawn agents
    print("[1/5] Spawning research agents with distinct cognitive styles...")
    agents = spawn_research_agents(orchestrator, skill_registry)
    print(f"      ✅ {len(agents)} agents spawned")
    for a in agents:
        print(f"         • {a.name} ({a.cluster}) — style: {a.context_scope.get('twin_style', 'default')}")
    
    # Assign research goals
    print("\n[2/5] Assigning P1 research topics...")
    assignments = assign_research_goals(agents)
    for agent_id, topic in assignments.items():
        print(f"      • {agent_id}: {topic}")
    
    # Execute research rounds
    print("\n[3/5] Executing research rounds...")
    all_findings = {}
    for agent in agents:
        print(f"      🔍 {agent.name} researching...")
        findings = run_research_round(agent, web_search_func=None)
        all_findings[agent.agent_id] = findings
        print(f"         Confidence: {findings.get('confidence', 0):.2f}")
        print(f"         Reasoning: {findings.get('reasoning', {}).get('proposed_approach', 'N/A')[:60]}...")
    
    # Cross-critique
    print("\n[4/5] Cross-agent critique...")
    critiques = cross_critique(agents)
    for c in critiques:
        print(f"      💬 {c['from']} → {c['to']}")
        print(f"         Critique: {c['critique'][:80]}...")
    
    # Synthesize execution plan
    print("\n[5/5] Synthesizing execution plan...")
    plan = synthesize_execution_plan(agents, critiques)
    
    print(f"\n{'='*70}")
    print("EXECUTION PLAN")
    print(f"{'='*70}")
    print(f"Swarm health: {plan['swarm_health']:.2f}")
    print(f"Total reasoning steps: {plan['total_reasoning_steps']}")
    print(f"Agents contributed: {plan['agents_contributed']}")
    print(f"Critiques exchanged: {plan['critiques_exchanged']}")
    print()
    print("Recommended execution order:")
    for item in plan['recommended_execution_order']:
        print(f"  [{item['priority']}] {item['topic']}")
        print(f"     Agent: {item['agent']} | Confidence: {item['confidence']:.2f}")
        print(f"     Rationale: {item['rationale']}")
    
    if plan['risk_assessment']:
        print("\nRisk assessment:")
        for risk in plan['risk_assessment']:
            print(f"  ⚠️  {risk}")
    
    print(f"\n{'='*70}")
    print("RESEARCH SWARM COMPLETE")
    print(f"{'='*70}")
    
    return plan


if __name__ == "__main__":
    main()
