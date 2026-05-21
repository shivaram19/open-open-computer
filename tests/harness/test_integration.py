# tests/harness/test_integration.py
"""
Integration test: Task → Twin Thinks → Awareness Tracks → Memory Stores → Status Report.

This test proves the harness subsystems actually connect, not just exist in isolation.

Principle: In God we trust. All others must bring data.

[CITATION: CITATIONS-GOVERNANCE]
"""

import time


from harness.awareness import AwarenessSubsystem, GoalState, CurrentState, AwarenessLevel
from memory.architecture import MultiModalMemory, MemoryType, RetrievalStrategy, MemoryTrace
from twins.cognitive_models.li_fei_fei import LiFeiFeiTwin
from twins.cognitive_models.noah_shinn import NoahShinnTwin


def test_end_to_end_harness_flow():
    """Full harness flow: task arrives → twins think → awareness tracks → memory stores → report."""
    awareness = AwarenessSubsystem(level=AwarenessLevel.FULL)
    memory = MultiModalMemory()
    fei_fei = LiFeiFeiTwin()
    shinn = NoahShinnTwin()

    task = "Build a real-time video understanding system for autonomous vehicles"

    # Goal Registration
    goal = GoalState(
        goal_id="task-001",
        description=task,
        success_criteria=["Processes video at 30 FPS", "Detects pedestrians with >95% accuracy", "Latency < 100ms per frame"],
    )
    awareness.set_goal(goal)

    # Twin Activation & Thinking
    fei_fei_reasoning = fei_fei.think(task)
    assert "phase_1_problem_identification" in fei_fei_reasoning
    assert fei_fei_reasoning["confidence"] > 0.7

    shinn_reasoning = shinn.think(task)
    assert "phase_1_initial_attempt" in shinn_reasoning
    assert "phase_2_self_critique" in shinn_reasoning

    # Memory Storage
    memory.store(MemoryTrace(
        trace_id="reasoning-001",
        memory_type=MemoryType.EPISODIC,
        content=fei_fei_reasoning,
        source="li-fei-fei-001",
        confidence=fei_fei_reasoning["confidence"],
        importance=0.8,
        tags=["video", "gnn", "autonomous-vehicles", "reasoning"],
    ))

    memory.store(MemoryTrace(
        trace_id="reasoning-002",
        memory_type=MemoryType.EPISODIC,
        content=shinn_reasoning,
        source="noah-shinn-001",
        confidence=shinn_reasoning["confidence"],
        importance=0.7,
        tags=["streaming", "reflection", "autonomous-vehicles", "reasoning"],
        causal_links=["reasoning-001"],
    ))

    memory.store(MemoryTrace(
        trace_id="pattern-001",
        memory_type=MemoryType.SEMANTIC,
        content={"task_type": "real-time-video", "required_clusters": ["video-gnn", "streaming-reflection"]},
        source="orchestrator",
        confidence=0.9,
        importance=0.9,
        tags=["pattern", "autonomous-vehicles", "real-time"],
    ))

    memory.store(MemoryTrace(
        trace_id="plan-001",
        memory_type=MemoryType.PROSPECTIVE,
        content={"next_step": "Search for latest streaming video architectures", "assigned_twin": "noah-shinn-001"},
        source="orchestrator",
        confidence=0.8,
        importance=0.7,
        tags=["plan", "research", "streaming"],
    ))

    # Awareness Tracking
    current_state = CurrentState(
        task_id="task-001",
        phase="research",
        active_twins=["li-fei-fei-001", "noah-shinn-001"],
        completed_subtasks=2,
        total_subtasks=8,
        confidence=(fei_fei_reasoning["confidence"] + shinn_reasoning["confidence"]) / 2,
        resource_usage={"api_calls": 45, "tokens": 12500, "memory_mb": 256},
    )
    awareness.record_state(current_state)

    direction = awareness.compute_direction("task-001", current_state)
    assert direction.alignment_score > -1.0
    assert direction.velocity >= 0.0

    # Memory Retrieval
    recent_episodes = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=2)
    assert len(recent_episodes) == 2

    causal_chain = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.CAUSAL, query="reasoning-001", limit=5)
    assert len(causal_chain) >= 1

    patterns = memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query="real-time", limit=1)
    assert len(patterns) >= 1

    # Status Report
    report = awareness.get_status_report()
    assert report["active_goals"] == 1
    assert report["total_states_recorded"] == 1
    assert report["health_score"] > 0.0

    memory_stats = memory.get_memory_stats()
    assert memory_stats["episodic_count"] == 2
    assert memory_stats["semantic_count"] == 1
    assert memory_stats["prospective_count"] == 1

    print("✅ Integration test passed:")
    print(f"   Goal: {goal.description[:50]}...")
    print(f"   Fei-Fei confidence: {fei_fei_reasoning['confidence']:.2f}")
    print(f"   Shinn confidence: {shinn_reasoning['confidence']:.2f}")
    print(f"   Direction alignment: {direction.alignment_score:.2f}")
    print(f"   Episodic memories: {memory_stats['episodic_count']}")
    print(f"   Health score: {report['health_score']:.2f}")


if __name__ == "__main__":
    test_end_to_end_harness_flow()
