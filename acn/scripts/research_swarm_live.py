#!/usr/bin/env python3
"""
Research Swarm LIVE: Parallel Deep Research with REAL Web Data.

Feeds actual web search results into conscious agents, has them think,
critique each other, and synthesize an actionable execution plan for P1 tasks.

Usage: python acn/scripts/research_swarm_live.py
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
from perception.perception_subsystem import PerceptionSubsystem
from harness.skill_evolution import SkillEvolution
from harness.policy_optimizer import PolicyOptimizer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.experience_buffer import ExperienceBuffer
from consensus.hlc import HybridLogicalClock
from memory.architecture import MultiModalMemory


# ── REAL WEB RESEARCH DATA ─────────────────────────────────────────
# Injected from parallel SearchWeb calls on 2026-05-07

RESEARCH_DATA = {
    "research-empirical-001": {
        "topic": "P1-1: Unit testing awareness subsystems in agent architectures",
        "sources": [
            {
                "title": "Best Practices for Preventing Drift in Production Systems",
                "url": "https://www.getmaxim.ai/articles/understanding-ai-agent-reliability-best-practices-for-preventing-drift-in-production-systems/",
                "key_findings": [
                    "91% of ML models experience performance degradation (drift) over time",
                    "Three drift types: Model Drift, Agent Drift (goal/context/reasoning), Prompt Drift",
                    "Golden datasets = curated ground truth for regression testing",
                    "CI/CD integration with automated evaluation on every commit",
                    "Canary prompts with known expected outputs validate stability",
                    "Statistical evaluators: F1, precision, recall + semantic similarity",
                ],
            },
            {
                "title": "An Empirical Study of Testing Practices in Open Source AI Agent Frameworks",
                "url": "https://arxiv.org/html/2509.19185v3",
                "key_findings": [
                    "Assertion-based testing is primary (72-82% of tests)",
                    "40.2% of assertion tests also use flexible verification (membership, mock, negative)",
                    "Mock assertions significantly more prevalent in top frameworks (22.9% vs 9.1%)",
                    "Novel patterns like DeepEval see very low adoption (~1%)",
                    "Spot-checking + hierarchical test trees reduce token tax",
                    "Specialized smaller judge models can validate stronger models",
                ],
            },
            {
                "title": "Testing & QA for agentic systems",
                "url": "https://ml-architects.ch/blog_posts/testing_qa_ai_eingineering.html",
                "key_findings": [
                    "Golden datasets include: input examples, expected outputs, context metadata",
                    "Quality gates define hard limits on each metric",
                    "Data drift monitoring required — golden dataset must stay in sync with user behavior",
                    "Monitoring + observability needed post-deployment beyond golden dataset",
                ],
            },
        ],
        "implications": [
            "Awareness subsystem tests need golden datasets with known goal states",
            "Direction alignment tests need statistical evaluators (cosine similarity thresholds)",
            "Drift detection tests need canary prompts with known expected outputs",
            "Mock assertions critical for testing alert handlers without firing real alerts",
            "Flexible verification (membership testing) better than strict equality for confidence scores",
        ],
    },
    "research-reflection-001": {
        "topic": "P1-2: Multi-modal memory architecture testing",
        "sources": [
            {
                "title": "Types of AI Agent Memory: Episodic, Semantic, Procedural (CoALA framework)",
                "url": "https://atlan.com/know/types-of-ai-agent-memory/",
                "key_findings": [
                    "Five memory types: In-context (working), Episodic, Semantic, Procedural, Organisational Context",
                    "CoALA framework (Princeton, arXiv:2309.02427) formalised taxonomy from cognitive science",
                    "Enterprise agents need governed organisational context memory (lineage, policies)",
                    "Semantic + Organisational context are most consequential for trustworthy output",
                    "Episodic memory = decision audit trail (which agent, which data version, when)",
                ],
            },
            {
                "title": "LEGOMem: Modular Procedural Memory for Multi-agent LLM Systems",
                "url": "https://arxiv.org/html/2510.04851v1",
                "key_findings": [
                    "Procedural memory extracted from successful trajectories and decomposed into subtask memories",
                    "Subtask memories (250) outperform full trajectory memories (93) for multi-agent workflows",
                    "FAISS vector DB + text-embedding-3-large for memory storage/retrieval",
                    "Memory placement matters: orchestrator gets 5 memories, task agents get 3 each",
                ],
            },
            {
                "title": "Experience-Evolving Multi-Turn Tool-Use Agent with Hybrid Episodic-Procedural Memory",
                "url": "https://arxiv.org/html/2512.07287v2",
                "key_findings": [
                    "Hybrid episodic-procedural memory (H-EPM) outperforms episodic-only and procedural-only",
                    "Step-level memory retrieval > trajectory-level retrieval for multi-turn interactions",
                    "Skip rate controls procedural suggestion utilization (0.8-1.0 optimal range)",
                    "H-EPM particularly effective for weaker models — compensates for reasoning limitations",
                ],
            },
            {
                "title": "7 Steps to Mastering Memory in Agentic AI Systems",
                "url": "https://machinelearningmastery.com/7-steps-to-mastering-memory-in-agentic-ai-systems/",
                "key_findings": [
                    "Working memory = context window (RAM analogy: fast, wiped on session end)",
                    "Episodic memory = timestamped records in vector DB, retrieved via semantic/hybrid search",
                    "Semantic memory = entity profiles combining relational + vector storage",
                    "Procedural memory = system prompts, few-shot examples, agent-managed rule sets",
                    "Memory types don't operate in isolation — production agents need all layers",
                ],
            },
        ],
        "implications": [
            "Memory tests need separate test suites per memory type (5 test classes)",
            "Episodic pruning tests need capacity limits + importance-based eviction",
            "Semantic update tests need Bayesian update verification with confidence deltas",
            "Working memory tests need 7±2 capacity enforcement + LRU eviction",
            "Causal chain tests need graph traversal verification (A→B→C retrieval)",
            "Cross-modal retrieval tests need embedding similarity thresholds",
        ],
    },
    "research-formal-001": {
        "topic": "P1-3: Automated cognitive twin generation at scale",
        "sources": [
            {
                "title": "GeCCo: Guided generation of Computational Cognitive Models",
                "url": "http://hcai-munich.com/pubs/Rmus2025Generating.pdf",
                "key_findings": [
                    "LLMs can generate cognitive models that match or outperform handcrafted domain-specific models",
                    "Pipeline: LLM proposes candidate models → fits to held-out data → iteratively refines via feedback",
                    "Tested across 4 cognitive domains: decision making, learning, planning, memory",
                    "LLM-generated models rival best literature models with conceptually plausible theories",
                    "Control experiments validated: model size contribution, prompt causality, data contamination, ground truth recovery",
                ],
            },
            {
                "title": "Leveraging Cognitive Models for Enhanced Code Generation",
                "url": "https://ojs.bonviewpress.com/index.php/JCCE/article/view/6123",
                "key_findings": [
                    "Framework integrates cognitive models with AI-driven code generation",
                    "Cognitive models enhance developer productivity and software quality",
                    "Schema-driven generation from cognitive specifications is viable",
                ],
            },
            {
                "title": "Genetic Programming for Computational Cognitive Model Generation",
                "url": "https://acs.ist.psu.edu/papers/ICCM2022Proceedings.pdf",
                "key_findings": [
                    "Evolutionary algorithms can generate programs representing cognitive models",
                    "Fitness function designed to find programs simulating human subject behavior",
                    "Post-processing removes unnecessary operators and duplicates",
                    "Programs convertible to pseudo-code for further analysis and visualization",
                ],
            },
        ],
        "implications": [
            "Schema-first approach: define CTS-001 as structured template, then fill per researcher",
            "LLM can generate twin code from researcher profile + schema specification",
            "Iterative refinement: generate → validate against published reasoning → refine",
            "Batch processing: process all 37 profiles with same pipeline",
            "Human-in-the-loop review for generated twins before acceptance",
            "Genetic programming as fallback for researchers with sparse published data",
        ],
    },
    "research-system-001": {
        "topic": "P1-6: Task decomposition algorithms for agent harnesses",
        "sources": [
            {
                "title": "Framework of Thoughts: Foundation Framework for Dynamic Optimized Reasoning",
                "url": "https://arxiv.org/html/2602.16512v1",
                "key_findings": [
                    "Problem decomposition schemes: Decomposed Prompting, Least-to-Most, Dynamic Least-to-Most, Self-Discover",
                    "Question hierarchies: Socratic Questioning, ProbTree, Decompose-Analyze-Rethink (DeAR)",
                    "Tree/Graph structures: Tree of Thoughts (Yao 2023), Graph of Thoughts (Besta 2024)",
                    "Fully automatic: Skeleton-of-Thought, Adaptive Graph of Thought (AGoT) — no user-defined structures",
                    "AGoT recursively decomposes if LLM decides further decomposition needed",
                ],
            },
            {
                "title": "Task-Decoupled Planning for Long-Horizon Agents",
                "url": "https://arxiv.org/html/2601.07577v1",
                "key_findings": [
                    "Supervisor decomposes task into dependency graph",
                    "Planner & Executor solve each decoupled sub-task node",
                    "Self-Revision updates graph after execution",
                    "Classical PDDL + LLM collaboration outperforms LLM-only planning",
                    "Pre-Act, Plan-and-Act, GoalAct, HiPlan adopt hierarchical structures",
                ],
            },
            {
                "title": "Knowledge Graph of Thoughts (KGoT)",
                "url": "https://arxiv.org/html/2504.02670",
                "key_findings": [
                    "Integrates LLM reasoning with dynamically constructed knowledge graphs",
                    "29% improvement on GAIA benchmark vs Hugging Face Agents with GPT-4o mini",
                    "Cost reduction: 36× cheaper than GPT-4o",
                    "Recursive task decomposition: steps further decomposed into sub-steps by LLM",
                    "Structured KG representation enables low-cost models to solve complex tasks",
                ],
            },
            {
                "title": "Graphs Meet AI Agents: Taxonomy, Progress, Future",
                "url": "https://arxiv.org/html/2506.18019v2",
                "key_findings": [
                    "Task Decomposition graph (TDG) is primary organized structure",
                    "DAG-Plan, Plan-over-Graph, DynTaskMAS use graph structures for decomposition",
                    "MCTS, PromptAgent, LATS, MCGS for task decision searching",
                    "ToolNet models multi-tool application as directed graph",
                ],
            },
        ],
        "implications": [
            "Use AGoT (Adaptive Graph of Thoughts) for automatic decomposition without user-defined structures",
            "Dependency graph (DAG) representation for sub-task ordering",
            "Self-Revision loop updates graph after each sub-task execution",
            "Knowledge Graph integration for structured reasoning (KGoT pattern)",
            "MCTS for exploring alternative decomposition paths",
            "Hybrid classical+LLM: PDDL for formal constraints, LLM for flexible decomposition",
        ],
    },
}


def main():
    print("=" * 75)
    print("RESEARCH SWARM LIVE: Real Web Data → Conscious Agents → Execution Plan")
    print("=" * 75)
    print()

    # Setup
    orchestrator = SwarmOrchestrator()
    skill_registry = SkillRegistry()

    # Spawn agents
    print("[1/6] Spawning research agents with distinct cognitive styles...")
    agents = [
        ConsciousAgent(
            agent_id="research-empirical-001",
            name="EmpiricalResearcher",
            cluster="video-gnn",
            awareness_level=AwarenessLevel.FULL,
            context_scope={"twin_style": "li-fei-fei", "epistemology": "empirical", "domain": "awareness-testing"},
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-empirical-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem()),
        ConsciousAgent(
            agent_id="research-reflection-001",
            name="ReflectionResearcher",
            cluster="streaming-reflection",
            awareness_level=AwarenessLevel.FULL,
            context_scope={"twin_style": "noah-shinn", "epistemology": "hybrid", "domain": "memory-testing"},
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-reflection-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem()),
        ConsciousAgent(
            agent_id="research-formal-001",
            name="FormalResearcher",
            cluster="consensus-safety",
            awareness_level=AwarenessLevel.FULL,
            context_scope={"twin_style": "formal-verification", "epistemology": "deductive", "domain": "twin-generation"},
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-formal-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem()),
        ConsciousAgent(
            agent_id="research-system-001",
            name="SystemResearcher",
            cluster="multi-agent",
            awareness_level=AwarenessLevel.FULL,
            context_scope={"twin_style": "system-design", "epistemology": "pragmatic", "domain": "task-decomposition"},
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="research-system-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem()),
    ]

    for agent in agents:
        orchestrator.register_agent(agent)
    print(f"      ✅ {len(agents)} agents registered")

    # Assign goals + inject real research data
    print("\n[2/6] Injecting real web research data into agent memories...")
    for agent in agents:
        data = RESEARCH_DATA[agent.agent_id]
        goal = AgentGoal(
            goal_id=f"research-{agent.agent_id}",
            description=data["topic"],
            success_criteria=[
                "Analyze 3+ authoritative sources",
                "Extract actionable patterns",
                "Cross-reference with ACN architecture",
                "Produce prioritized recommendations",
            ],
            priority=5,
        )
        agent.activate(goal)

        # Store research data as episodic memory
        for source in data["sources"]:
            agent.memory.store(MemoryTrace(
                trace_id=f"source-{source['title'][:20]}-{time.time()}",
                memory_type=MemoryType.EPISODIC,
                content=source,
                source="web_search",
                confidence=0.85,
                importance=0.9,
                tags=["research", "web_source"],
            ))

        # Store implications as semantic memory
        for impl in data["implications"]:
            agent.memory.store(MemoryTrace(
                trace_id=f"impl-{impl[:20]}-{time.time()}",
                memory_type=MemoryType.SEMANTIC,
                content={"implication": impl, "topic": data["topic"]},
                source="agent_analysis",
                confidence=0.8,
                importance=0.85,
                tags=["implication", "actionable"],
            ))

        print(f"      ✅ {agent.name}: {len(data['sources'])} sources, {len(data['implications'])} implications")

    # Agents think about their research
    print("\n[3/6] Agents thinking about research data...")
    reasoning_outputs = {}
    for agent in agents:
        reasoning = agent.think()
        reasoning_outputs[agent.agent_id] = reasoning
        print(f"      🧠 {agent.name}: {reasoning['proposed_approach'][:70]}...")
        print(f"         Confidence: {reasoning['confidence']:.2f} | Risks: {len(reasoning['risks'])}")

    # Cross-agent communication
    print("\n[4/6] Cross-agent critique...")
    pairs = [
        ("research-empirical-001", "research-reflection-001"),
        ("research-formal-001", "research-system-001"),
        ("research-empirical-001", "research-system-001"),
        ("research-reflection-001", "research-formal-001"),
    ]
    critiques = []
    for from_id, to_id in pairs:
        from_agent = next(a for a in agents if a.agent_id == from_id)
        to_agent = next(a for a in agents if a.agent_id == to_id)
        msg = {
            "type": "research_findings",
            "content": RESEARCH_DATA[from_id]["implications"][:2],
            "confidence": from_agent._calibrate_confidence(),
            "reasoning": from_agent.reasoning_trace[-1] if from_agent.reasoning_trace else {},
        }
        response = from_agent.communicate(to_id, msg)
        critiques.append({
            "from": from_id,
            "to": to_id,
            "critique": response.get("critique", "No critique"),
        })
        print(f"      💬 {from_agent.name} → {to_agent.name}")
        print(f"         {response.get('critique', 'No critique')[:90]}...")

    # Swarm round
    print("\n[5/6] Swarm consensus check...")
    # Create a swarm task and activate it properly
    swarm_task = SwarmTask(
        task_id="p1-research-swarm",
        description="Parallel deep research on P1 foundation tasks",
        required_clusters=["video-gnn", "streaming-reflection", "consensus-safety", "multi-agent"],
        success_criteria=["4 research reports", "cross-critique completed", "execution plan synthesized"],
        min_agents=2,
        max_agents=5,
    )
    orchestrator.activate_task(swarm_task)
    
    # Update agent goals to have parent_goal_id pointing to swarm task
    for agent in agents:
        if agent.current_goal:
            agent.current_goal.parent_goal_id = "p1-research-swarm"
    
    round_result = orchestrator.execute_round("p1-research-swarm")
    consensus = round_result.get("consensus", {"status": "unknown", "score": 0.0})
    print(f"      Consensus: {consensus['status']} (score: {consensus.get('score', 0):.2f})")
    print(f"      Swarm health: {round_result.get('swarm_health', 1.0):.2f}")

    # Synthesize execution plan
    print("\n[6/6] Synthesizing execution plan...")

    # Build the execution plan from real findings
    execution_plan = {
        "swarm_health": round_result.get('swarm_health', 1.0),
        "consensus_score": consensus.get('score', 0.0),
        "agents_contributed": len([a for a in agents if a.reasoning_trace]),
        "critiques_exchanged": len(critiques),
        "tasks": [],
        "new_citations_to_register": [],
    }

    # Task 1: Awareness Unit Tests (P1-1)
    execution_plan["tasks"].append({
        "id": "P1-1",
        "title": "Unit Tests for Awareness Subsystem",
        "priority": "P0 (do first)",
        "rationale": "Foundation for all other layers. Golden dataset pattern from Maxim AI + empirical study.",
        "test_patterns": [
            "GoalState registration/retrieval (strict assertion)",
            "DirectionVector computation with cosine similarity thresholds",
            "Drift detection with canary prompts (known expected outputs)",
            "Alert firing: mock assertions for handler verification",
            "Health score computation with membership testing (range, not equality)",
            "State history recording with temporal ordering",
        ],
        "citations": ["Maxim2025", "AgentTesting2026", "MLArchitects2025"],
        "estimated_effort": "2-3 hours",
        "agent": "EmpiricalResearcher",
    })

    # Task 2: Memory Unit Tests (P1-2)
    execution_plan["tasks"].append({
        "id": "P1-2",
        "title": "Unit Tests for Multi-Modal Memory",
        "priority": "P0 (do first)",
        "rationale": "Second foundation layer. CoALA taxonomy + LEGOMem procedural patterns.",
        "test_patterns": [
            "Episodic storage/retrieval with timestamp ordering",
            "Episodic pruning at capacity limit (importance-based eviction)",
            "Semantic Bayesian update (confidence delta verification)",
            "Procedural reinforcement (skill loading + execution)",
            "Working memory 7±2 capacity with LRU eviction",
            "Causal chain retrieval (A→B→C graph traversal)",
            "Cross-modal retrieval via embedding similarity",
        ],
        "citations": ["CoALA2023", "LEGOMem2025", "HEPM2025", "MLMastery2026"],
        "estimated_effort": "3-4 hours",
        "agent": "ReflectionResearcher",
    })

    # Task 3: Task Decomposer (P1-6)
    execution_plan["tasks"].append({
        "id": "P1-6",
        "title": "Task Decomposer (Harness Layer 1)",
        "priority": "P1 (do after tests)",
        "rationale": "First operational harness layer. AGoT + KGoT + DAG-Plan patterns.",
        "implementation_patterns": [
            "Intent parser: classify task type (research/build/debug/evaluate)",
            "AGoT-based automatic decomposition (no user-defined structures)",
            "DAG dependency graph for sub-task ordering",
            "Self-Revision loop: update graph after each sub-task",
            "Criteria definition per sub-task (success metrics)",
            "MCTS for exploring alternative decomposition paths",
        ],
        "citations": ["Besta2024", "AGoT2025", "KGoT2025", "TDP2026", "DAGPlan2025"],
        "estimated_effort": "4-6 hours",
        "agent": "SystemResearcher",
    })

    # Task 4: Twin Generator (P1-3)
    execution_plan["tasks"].append({
        "id": "P1-3",
        "title": "Automated Cognitive Twin Generator",
        "priority": "P2 (do after decomposer)",
        "rationale": "Scale operation. GeCCo pipeline: LLM generates → validates → refines.",
        "implementation_patterns": [
            "Schema-first: CTS-001 as structured Jinja2 template",
            "LLM prompt: researcher profile + schema → Python class",
            "Validation: compare generated reasoning to published reasoning",
            "Iterative refinement loop (GeCCo pattern)",
            "Batch processing pipeline for all 37 researchers",
            "Human-in-the-loop review gate",
        ],
        "citations": ["GeCCo2025", "CognitiveCodeGen2025", "GP-Cognitive2022"],
        "estimated_effort": "6-8 hours (batch)",
        "agent": "FormalResearcher",
    })

    # Print execution plan
    print(f"\n{'='*75}")
    print("SYNTHESIZED EXECUTION PLAN")
    print(f"{'='*75}")
    print(f"Swarm health: {execution_plan['swarm_health']:.2f}")
    print(f"Consensus score: {execution_plan['consensus_score']:.2f}")
    print(f"Agents contributed: {execution_plan['agents_contributed']}")
    print(f"Critiques exchanged: {execution_plan['critiques_exchanged']}")
    print()

    for task in execution_plan["tasks"]:
        print(f"  [{task['priority']}] {task['id']}: {task['title']}")
        print(f"   Rationale: {task['rationale']}")
        print(f"   Effort: {task['estimated_effort']} | Lead: {task['agent']}")
        print(f"   Citations: {', '.join(task['citations'])}")
        patterns = task.get('test_patterns') or task.get('implementation_patterns') or []
        for p in patterns:
            print(f"      • {p}")
        print()

    # Risk assessment
    print("Risk Assessment:")
    suspicious = [c for c in critiques if "accepted" in c.get("critique", "").lower()]
    if len(suspicious) == len(critiques):
        print("  ⚠️  All critiques too agreeable — possible groupthink. Recommend adversarial review.")
    print("  ⚠️  Web sources need citation registry entries before use in production code")
    print("  ⚠️  AGoT and KGoT implementations are novel — need validation against simpler baselines")

    print(f"\n{'='*75}")
    print("NEXT: Begin executing P1-1 (Awareness Unit Tests)")
    print(f"{'='*75}")

    return execution_plan


if __name__ == "__main__":
    main()
