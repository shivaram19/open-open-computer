#!/usr/bin/env python3
"""
MVP Web Search Tool Demo: Date-first search with real-time awareness.

Demonstrates:
1. DateTool — mandatory date retrieval
2. WebSearchTool — date-aware query enhancement
3. ConsciousAgent.research() — integrated date + search
4. DATE RULE enforcement — search without date raises error

Usage: python acn/scripts/mvp_web_search_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.date_tool import DateTool, get_current_date
from tools.web_search_tool import WebSearchTool, search_with_date_context
from agents.conscious_agent import ConsciousAgent
from harness.awareness import AwarenessLevel
from memory.architecture import MemoryType, RetrievalStrategy
from perception.perception_subsystem import PerceptionSubsystem
from harness.skill_evolution import SkillEvolution
from harness.policy_optimizer import PolicyOptimizer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.experience_buffer import ExperienceBuffer
from consensus.hlc import HybridLogicalClock
from memory.architecture import MultiModalMemory


def demo_date_tool():
    """Demonstrate the DateTool."""
    print("=" * 60)
    print("DEMO 1: DateTool — Temporal Grounding")
    print("=" * 60)
    
    date = get_current_date()
    print(f"\n📅 Current Date:")
    print(f"   ISO:     {date.iso}")
    print(f"   Date:    {date.date}")
    print(f"   Year:    {date.year}")
    print(f"   Weekday: {date.weekday}")
    print(f"   Time:    {date.time} {date.timezone}")
    
    # Show query enhancement
    queries = [
        "latest LLM benchmarks",
        "new AI frameworks",
        "Graph of Thoughts paper",
        "autonomous agent testing 2024",
    ]
    print(f"\n🔍 Query Enhancement (Date-Aware):")
    for q in queries:
        enhanced = DateTool.format_for_search(date, q)
        print(f"   '{q}'")
        print(f"   → '{enhanced}'")
    
    # Show freshness filter
    print(f"\n📊 Freshness Filter:")
    print(f"   Last 7 days:  {DateTool.freshness_filter(date, 7)}")
    print(f"   Last 30 days: {DateTool.freshness_filter(date, 30)}")
    print(f"   Last year:    {DateTool.freshness_filter(date, 365)}")


def demo_web_search_tool():
    """Demonstrate the WebSearchTool with date enforcement."""
    print("\n" + "=" * 60)
    print("DEMO 2: WebSearchTool — Date-First Enforcement")
    print("=" * 60)
    
    tool = WebSearchTool()
    
    # Show date rule enforcement
    print("\n🛡️  DATE RULE ENFORCEMENT:")
    print("   Attempting search WITHOUT calling get_date() first...")
    try:
        tool.search("latest AI breakthroughs")
    except RuntimeError as e:
        print(f"   ✅ Caught violation: {str(e).split(chr(10))[0]}")
    
    # Correct usage
    print("\n✅ CORRECT USAGE: get_date() → search()")
    tool.get_date()
    result = tool.search("latest AI breakthroughs", count=3)
    
    print(f"\n   Original query:  '{result['original_query']}'")
    print(f"   Enhanced query:  '{result['enhanced_query']}'")
    print(f"   Date used:       {result['date']} (year: {result['year']})")
    print(f"   Query enhanced:  {result['metadata']['query_enhanced']}")
    print(f"   Status:          {result['results'] and 'results ready' or 'pending external execution'}")
    
    # Show search history
    history = tool.get_search_history()
    print(f"\n📜 Search History ({len(history)} entries):")
    for h in history:
        print(f"   [{h['timestamp']}] '{h['original_query']}' → '{h['enhanced_query']}'")


def demo_conscious_agent_research():
    """Demonstrate ConsciousAgent with integrated date-aware research."""
    print("\n" + "=" * 60)
    print("DEMO 3: ConsciousAgent — Integrated Date + Search")
    print("=" * 60)
    
    agent = ConsciousAgent(
        agent_id="demo-researcher-001",
        name="DemoResearcher",
        cluster="streaming-reflection",
        awareness_level=AwarenessLevel.FULL,
        memory=MultiModalMemory(), clock=HybridLogicalClock(node_id="demo-researcher-001"), experience_buffer=ExperienceBuffer(), reflection_engine=ReflectionEngine(), policy_optimizer=PolicyOptimizer(), skill_evolution=SkillEvolution(), perception=PerceptionSubsystem())
    
    from agents.conscious_agent import AgentGoal
    goal = AgentGoal(
        goal_id="demo-goal-001",
        description="Research latest agent testing practices",
        success_criteria=["Find 3+ sources", "Extract patterns", "Cite sources"],
    )
    agent.activate(goal)
    
    print(f"\n🤖 Agent: {agent.name} ({agent.cluster})")
    print(f"   Goal: {agent.current_goal.description}")
    
    # Execute research (automatically gets date)
    print(f"\n🔬 Executing research() — date is auto-fetched...")
    findings = agent.research("latest agent testing practices", count=3)
    
    print(f"   Query:          '{findings['query']}'")
    print(f"   Enhanced:       '{findings['enhanced_query']}'")
    print(f"   Date:           {findings['date']} (year: {findings['year']})")
    print(f"   Status:         {findings['status']}")
    print(f"   Confidence:     {findings['confidence']:.2f}")
    print(f"   Sources found:  {findings['source_count']}")
    print(f"   Citations made: {agent.citations_made}")
    
    # Verify memory storage
    memories = agent.memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=2)
    print(f"\n🧠 Memory Check:")
    print(f"   Episodic memories stored: {len(memories)}")
    for m in memories:
        tags = getattr(m, 'tags', [])
        trace_id = getattr(m, 'trace_id', '?')
        print(f"   • {trace_id} — tags: {tags}")


def demo_one_shot_search():
    """Demonstrate the convenience one-shot function."""
    print("\n" + "=" * 60)
    print("DEMO 4: One-Shot Convenience Function")
    print("=" * 60)
    
    print("\n⚡ search_with_date_context() — auto date + search:")
    result = search_with_date_context("cutting-edge video generation models", count=3)
    
    print(f"   Original:  '{result['original_query']}'")
    print(f"   Enhanced:  '{result['enhanced_query']}'")
    print(f"   Date:      {result['date']}")
    print(f"   Enhanced?: {result['metadata']['query_enhanced']}")


def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + " MVP WEB SEARCH TOOL — Date-First Research ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("Principle: An agent without a date searches the past, not the present.")
    print("Every search MUST call get_date() first. This is enforced, not optional.")
    
    demo_date_tool()
    demo_web_search_tool()
    demo_conscious_agent_research()
    demo_one_shot_search()
    
    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. DateTool.get() is MANDATORY before any search")
    print("  2. Queries auto-enhanced with current year (2026)")
    print("  3. RuntimeError if search without date — enforced, not suggested")
    print("  4. ConsciousAgent.research() handles date automatically")
    print("  5. Search history enables audit and reproducibility")


if __name__ == "__main__":
    main()
