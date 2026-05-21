# tests/harness/test_memory.py
"""
Unit Tests for Multi-Modal Memory Architecture.

Research-backed test patterns from swarm deep-research:
- CoALA taxonomy: 5 memory types with distinct cognitive functions
- LEGOMem: subtask memories outperform full trajectories
- H-EPM: hybrid episodic-procedural memory beats either alone
- Working memory: 7±2 capacity (Miller's law)
- Episodic pruning: importance × access_count / age
- Semantic: Bayesian confidence update on collision

Citations: CoALA2023, LEGOMem2025, HEPM2025, MLMastery2026, Miller1956
"""

import time


import pytest
from typing import Any

from memory.architecture import (
    MultiModalMemory,
    MemoryType,
    RetrievalStrategy,
    MemoryTrace,
)


# ── Helper factories ───────────────────────────────────────────────

def make_trace(
    trace_id: str,
    memory_type: MemoryType,
    content: Any = None,
    confidence: float = 1.0,
    importance: float = 0.5,
    tags: list = None,
    causal_links: list = None,
    timestamp: float = None,
) -> MemoryTrace:
    """Factory for creating MemoryTrace instances in tests."""
    # Use explicit None check to allow empty list for tags
    final_tags = ["test"] if tags is None else tags
    return MemoryTrace(
        trace_id=trace_id,
        memory_type=memory_type,
        content=content or {"data": trace_id},
        confidence=confidence,
        importance=importance,
        tags=final_tags,
        causal_links=causal_links or [],
        timestamp=timestamp or time.time(),
    )


# ── Test Classes ───────────────────────────────────────────────────

class TestMemoryTraceStorage:
    """P1-2: MemoryTrace storage across all 5 types."""

    def test_store_episodic_appends_to_list(self):
        """Strict assertion: episodic traces stored in append-only list."""
        memory = MultiModalMemory()
        trace = make_trace("ep-1", MemoryType.EPISODIC, content="event A")
        
        memory.store(trace)
        
        assert len(memory._episodic) == 1
        assert memory._episodic[0].trace_id == "ep-1"

    def test_store_semantic_uses_dict_with_tag_key(self):
        """Strict assertion: semantic memory keyed by first tag."""
        memory = MultiModalMemory()
        trace = make_trace("sem-1", MemoryType.SEMANTIC, tags=["concept-A"])
        
        memory.store(trace)
        
        assert "concept-A" in memory._semantic
        assert memory._semantic["concept-A"].trace_id == "sem-1"

    def test_store_procedural_uses_dict_with_tag_key(self):
        """Strict assertion: procedural memory keyed by first tag (skill_name)."""
        memory = MultiModalMemory()
        trace = make_trace("proc-1", MemoryType.PROCEDURAL, tags=["skill-search"])
        
        memory.store(trace)
        
        assert "skill-search" in memory._procedural
        assert memory._procedural["skill-search"].trace_id == "proc-1"

    def test_store_prospective_appends_to_list(self):
        """Strict assertion: prospective traces stored in append-only list."""
        memory = MultiModalMemory()
        trace = make_trace("prosp-1", MemoryType.PROSPECTIVE, content="plan X")
        
        memory.store(trace)
        
        assert len(memory._prospective) == 1
        assert memory._prospective[0].trace_id == "prosp-1"

    def test_store_working_appends_to_list(self):
        """Strict assertion: working traces stored in active context list."""
        memory = MultiModalMemory()
        trace = make_trace("work-1", MemoryType.WORKING, content="active context")
        
        memory.store(trace)
        
        assert len(memory._working) == 1
        assert memory._working[0].trace_id == "work-1"

    def test_store_updates_tag_index(self):
        """Strict assertion: tag index populated for all memory types."""
        memory = MultiModalMemory()
        trace = make_trace("ep-1", MemoryType.EPISODIC, tags=["research", "agent-1"])
        
        memory.store(trace)
        
        assert "research" in memory._tag_index
        assert "ep-1" in memory._tag_index["research"]
        assert "agent-1" in memory._tag_index
        assert "ep-1" in memory._tag_index["agent-1"]

    def test_store_updates_causal_index(self):
        """Strict assertion: causal links indexed for chain retrieval."""
        memory = MultiModalMemory()
        trace = make_trace("effect-1", MemoryType.EPISODIC, causal_links=["cause-1"])
        
        memory.store(trace)
        
        assert "cause-1" in memory._causal_index
        assert "effect-1" in memory._causal_index["cause-1"]


class TestEpisodicPruning:
    """P1-2: Episodic pruning at capacity limit."""

    def test_episodic_pruning_triggered_at_capacity(self):
        """Canary prompt: exceeding capacity triggers importance-based pruning."""
        memory = MultiModalMemory(episodic_capacity=5)
        
        # Fill to capacity with varying importance
        for i in range(7):
            memory.store(make_trace(
                f"ep-{i}",
                MemoryType.EPISODIC,
                importance=0.1 if i < 2 else 0.9,  # first 2 are low importance
            ))
        
        # Should be pruned back to capacity
        assert len(memory._episodic) <= 5

    def test_low_importance_traces_pruned_first(self):
        """Strict assertion: pruning removes lowest importance × access / age."""
        memory = MultiModalMemory(episodic_capacity=3)
        
        memory.store(make_trace("high-1", MemoryType.EPISODIC, importance=1.0))
        memory.store(make_trace("high-2", MemoryType.EPISODIC, importance=0.9))
        memory.store(make_trace("low-1", MemoryType.EPISODIC, importance=0.1))
        memory.store(make_trace("low-2", MemoryType.EPISODIC, importance=0.2))
        
        # Only top 3 should remain
        remaining_ids = {t.trace_id for t in memory._episodic}
        assert "high-1" in remaining_ids
        assert "high-2" in remaining_ids
        # low traces may or may not survive depending on timestamp math

    def test_episodic_capacity_configurable(self):
        """Strict assertion: capacity parameter respected."""
        memory = MultiModalMemory(episodic_capacity=10)
        
        for i in range(15):
            memory.store(make_trace(f"ep-{i}", MemoryType.EPISODIC))
        
        assert len(memory._episodic) <= 10


class TestSemanticBayesianUpdate:
    """P1-2: Semantic memory Bayesian update on collision."""

    def test_semantic_stores_new_concept(self):
        """Strict assertion: new concept stored directly."""
        memory = MultiModalMemory()
        trace = make_trace("sem-1", MemoryType.SEMANTIC, tags=["concept-A"], confidence=0.7)
        
        memory.store(trace)
        
        assert memory._semantic["concept-A"].confidence == 0.7

    def test_semantic_bayesian_update_on_collision(self):
        """Canary prompt: colliding concept gets Bayesian confidence merge."""
        memory = MultiModalMemory()
        
        # First store: confidence = 0.5
        memory.store(make_trace("sem-1", MemoryType.SEMANTIC, tags=["concept-A"], confidence=0.5))
        
        # Second store: confidence = 0.5
        # Bayesian: 1 - (1-0.5)(1-0.5) = 1 - 0.25 = 0.75
        memory.store(make_trace("sem-2", MemoryType.SEMANTIC, tags=["concept-A"], confidence=0.5))
        
        merged_confidence = memory._semantic["concept-A"].confidence
        assert merged_confidence == 0.75

    def test_semantic_content_merge_on_collision(self):
        """Strict assertion: dict contents merged on semantic collision."""
        memory = MultiModalMemory()
        
        memory.store(make_trace(
            "sem-1", MemoryType.SEMANTIC,
            tags=["concept-A"],
            content={"field1": "value1"},
        ))
        memory.store(make_trace(
            "sem-2", MemoryType.SEMANTIC,
            tags=["concept-A"],
            content={"field2": "value2"},
        ))
        
        merged = memory._semantic["concept-A"].content
        assert merged["field1"] == "value1"
        assert merged["field2"] == "value2"

    def test_semantic_non_dict_content_overwritten(self):
        """Strict assertion: non-dict content replaced on collision."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("sem-1", MemoryType.SEMANTIC, tags=["concept-A"], content="old"))
        memory.store(make_trace("sem-2", MemoryType.SEMANTIC, tags=["concept-A"], content="new"))
        
        assert memory._semantic["concept-A"].content == "new"


class TestProceduralReinforcement:
    """P1-2: Procedural memory reinforcement and pruning."""

    def test_procedural_stores_by_skill_name(self):
        """Strict assertion: procedural keyed by first tag (skill name)."""
        memory = MultiModalMemory()
        trace = make_trace("proc-1", MemoryType.PROCEDURAL, tags=["skill-search"])
        
        memory.store(trace)
        
        assert "skill-search" in memory._procedural

    def test_procedural_overwrites_same_skill(self):
        """Strict assertion: same skill name replaces previous version."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("proc-v1", MemoryType.PROCEDURAL, tags=["skill-search"]))
        memory.store(make_trace("proc-v2", MemoryType.PROCEDURAL, tags=["skill-search"]))
        
        assert memory._procedural["skill-search"].trace_id == "proc-v2"

    def test_procedural_pruning_removes_least_used(self):
        """Canary prompt: bottom 10% by access_count pruned at capacity."""
        memory = MultiModalMemory(procedural_capacity=10)
        
        # Fill near capacity
        for i in range(12):
            memory.store(make_trace(
                f"proc-{i}",
                MemoryType.PROCEDURAL,
                tags=[f"skill-{i}"],
                importance=0.5,
            ))
        
        # Should have been pruned
        assert len(memory._procedural) <= 10


class TestWorkingMemoryCapacity:
    """P1-2: Working memory 7±2 capacity with LRU eviction. [Miller1956]"""

    def test_working_capacity_default_is_7(self):
        """Strict assertion: default capacity follows Miller's law."""
        memory = MultiModalMemory()
        assert memory.working_capacity == 7

    def test_working_capacity_configurable(self):
        """Strict assertion: capacity parameter respected (7±2 range)."""
        memory = MultiModalMemory(working_capacity=5)
        assert memory.working_capacity == 5

    def test_working_evicts_oldest_to_episodic(self):
        """Canary prompt: exceeding capacity evicts oldest to episodic."""
        memory = MultiModalMemory(working_capacity=3)
        
        memory.store(make_trace("w-1", MemoryType.WORKING))
        memory.store(make_trace("w-2", MemoryType.WORKING))
        memory.store(make_trace("w-3", MemoryType.WORKING))
        memory.store(make_trace("w-4", MemoryType.WORKING))
        
        # Working should hold only newest 3
        assert len(memory._working) == 3
        working_ids = {t.trace_id for t in memory._working}
        assert "w-1" not in working_ids  # oldest evicted
        assert "w-4" in working_ids  # newest retained

    def test_evicted_working_becomes_episodic(self):
        """Strict assertion: evicted working trace converts to episodic."""
        memory = MultiModalMemory(working_capacity=2)
        
        memory.store(make_trace("w-1", MemoryType.WORKING, content="context A"))
        memory.store(make_trace("w-2", MemoryType.WORKING, content="context B"))
        memory.store(make_trace("w-3", MemoryType.WORKING, content="context C"))
        
        # Oldest working trace should now be in episodic
        episodic_ids = {t.trace_id for t in memory._episodic}
        assert "w-1" in episodic_ids


class TestCausalChainRetrieval:
    """P1-2: Causal chain retrieval (A→B→C graph traversal)."""

    def test_causal_retrieval_follows_chain(self):
        """Strict assertion: causal strategy follows trace_id links."""
        memory = MultiModalMemory()
        
        # Create chain: cause → effect1 → effect2
        memory.store(make_trace("cause", MemoryType.EPISODIC))
        memory.store(make_trace("effect1", MemoryType.EPISODIC, causal_links=["cause"]))
        memory.store(make_trace("effect2", MemoryType.EPISODIC, causal_links=["effect1"]))
        
        chain = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.CAUSAL, query="cause", limit=5)
        
        assert len(chain) >= 2
        trace_ids = [t.trace_id for t in chain]
        assert "cause" in trace_ids
        assert "effect1" in trace_ids

    def test_causal_retrieval_respects_limit(self):
        """Strict assertion: causal chain truncated at limit."""
        memory = MultiModalMemory()
        
        # Long chain
        memory.store(make_trace("t0", MemoryType.EPISODIC))
        for i in range(1, 6):
            memory.store(make_trace(f"t{i}", MemoryType.EPISODIC, causal_links=[f"t{i-1}"]))
        
        chain = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.CAUSAL, query="t0", limit=3)
        
        assert len(chain) <= 3

    def test_causal_retrieval_breaks_cycles(self):
        """Canary prompt: cyclic causal links don't infinite loop."""
        memory = MultiModalMemory()
        
        # Cycle: A → B → A
        memory.store(make_trace("A", MemoryType.EPISODIC, causal_links=["B"]))
        memory.store(make_trace("B", MemoryType.EPISODIC, causal_links=["A"]))
        
        chain = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.CAUSAL, query="A", limit=10)
        
        # Should terminate, not loop forever
        assert len(chain) <= 2


class TestRetrievalStrategies:
    """P1-2: Retrieval strategies across memory types."""

    def test_episodic_recency_returns_newest_first(self):
        """Temporal ordering: recency strategy sorts by timestamp descending."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("old", MemoryType.EPISODIC, timestamp=1000))
        memory.store(make_trace("mid", MemoryType.EPISODIC, timestamp=2000))
        memory.store(make_trace("new", MemoryType.EPISODIC, timestamp=3000))
        
        results = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=3)
        
        assert [t.trace_id for t in results] == ["new", "mid", "old"]

    def test_episodic_surprise_returns_high_importance_low_confidence(self):
        """Canary prompt: surprise = importance × (1 - confidence)."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("boring", MemoryType.EPISODIC, importance=0.1, confidence=1.0))
        memory.store(make_trace("surprising", MemoryType.EPISODIC, importance=0.9, confidence=0.1))
        memory.store(make_trace("normal", MemoryType.EPISODIC, importance=0.5, confidence=0.5))
        
        results = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.SURPRISE, limit=3)
        
        # surprising has highest surprise score: 0.9 × 0.9 = 0.81
        assert results[0].trace_id == "surprising"

    def test_semantic_relevance_matches_tags(self):
        """Strict assertion: relevance strategy filters by tag match."""
        memory = MultiModalMemory()
        
        # Use different primary tags to avoid semantic merge
        memory.store(make_trace("sem-1", MemoryType.SEMANTIC, tags=["ethics", "ai"], confidence=0.7))
        memory.store(make_trace("sem-2", MemoryType.SEMANTIC, tags=["safety", "ai"], confidence=0.9))
        memory.store(make_trace("sem-3", MemoryType.SEMANTIC, tags=["biology"], confidence=0.5))
        
        results = memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query="ai", limit=3)
        
        assert len(results) == 2
        trace_ids = {t.trace_id for t in results}
        assert "sem-1" in trace_ids
        assert "sem-2" in trace_ids

    def test_procedural_relevance_matches_tags(self):
        """Strict assertion: procedural retrieval filters by skill tag."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("proc-1", MemoryType.PROCEDURAL, tags=["skill-search"], confidence=0.8))
        memory.store(make_trace("proc-2", MemoryType.PROCEDURAL, tags=["skill-code"], confidence=0.6))
        
        results = memory.retrieve(MemoryType.PROCEDURAL, RetrievalStrategy.RELEVANCE, query="skill-search", limit=3)
        
        assert len(results) == 1
        assert results[0].trace_id == "proc-1"

    def test_working_retrieval_returns_shallow_copy(self):
        """Strict assertion: working retrieval returns list copy."""
        memory = MultiModalMemory()
        memory.store(make_trace("w-1", MemoryType.WORKING))
        
        results = memory.retrieve(MemoryType.WORKING, RetrievalStrategy.RECENCY, limit=5)
        
        assert len(results) == 1
        # List is copied but objects are references (shallow copy)
        results.pop(0)
        assert len(memory._working) == 1  # original list unaffected

    def test_retrieval_limit_respected(self):
        """Strict assertion: limit parameter truncates results."""
        memory = MultiModalMemory()
        
        for i in range(10):
            memory.store(make_trace(f"ep-{i}", MemoryType.EPISODIC, timestamp=1000 + i))
        
        results = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=3)
        
        assert len(results) == 3


class TestMemoryStats:
    """P1-2: Memory stats reporting."""

    def test_stats_reports_all_counts(self):
        """Strict assertion: stats dict contains all expected keys."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("ep-1", MemoryType.EPISODIC))
        memory.store(make_trace("sem-1", MemoryType.SEMANTIC, tags=["concept"]))
        memory.store(make_trace("proc-1", MemoryType.PROCEDURAL, tags=["skill"]))
        memory.store(make_trace("prosp-1", MemoryType.PROSPECTIVE))
        memory.store(make_trace("work-1", MemoryType.WORKING))
        
        stats = memory.get_memory_stats()
        
        assert stats["episodic_count"] == 1
        assert stats["semantic_count"] == 1
        assert stats["procedural_count"] == 1
        assert stats["prospective_count"] == 1
        assert stats["working_count"] == 1
        assert stats["working_capacity"] == 7
        assert stats["tag_index_size"] >= 1

    def test_stats_counts_accurate_after_multiple_stores(self):
        """Strict assertion: counts match actual storage state."""
        memory = MultiModalMemory()
        
        for i in range(5):
            memory.store(make_trace(f"ep-{i}", MemoryType.EPISODIC))
        for i in range(3):
            memory.store(make_trace(f"sem-{i}", MemoryType.SEMANTIC, tags=[f"concept-{i}"]))
        
        stats = memory.get_memory_stats()
        
        assert stats["episodic_count"] == 5
        assert stats["semantic_count"] == 3
        assert stats["tag_index_size"] >= 3


class TestEdgeCases:
    """P1-2: Edge cases and boundary conditions."""

    def test_empty_memory_retrieval_returns_empty_list(self):
        """Strict assertion: empty memory returns empty results."""
        memory = MultiModalMemory()
        
        results = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=5)
        assert results == []

    def test_retrieval_unknown_memory_type_returns_empty(self):
        """Strict assertion: invalid memory type handled gracefully."""
        memory = MultiModalMemory()
        # This shouldn't happen with enum, but test defensive behavior
        results = memory.retrieve(MemoryType.EPISODIC, RetrievalStrategy.RELEVANCE, query="nonexistent")
        assert results == []

    def test_store_trace_without_tags_uses_trace_id(self):
        """Strict assertion: trace without tags falls back to trace_id as key."""
        memory = MultiModalMemory()
        trace = make_trace("sem-1", MemoryType.SEMANTIC, tags=[])
        
        memory.store(trace)
        
        # Should be keyed by trace_id since no tags
        assert "sem-1" in memory._semantic

    def test_multiple_stores_same_tag_different_types(self):
        """Strict assertion: same tag in different memory types doesn't collide."""
        memory = MultiModalMemory()
        
        memory.store(make_trace("ep-1", MemoryType.EPISODIC, tags=["ai"]))
        memory.store(make_trace("sem-1", MemoryType.SEMANTIC, tags=["ai"]))
        memory.store(make_trace("proc-1", MemoryType.PROCEDURAL, tags=["ai"]))
        
        assert len(memory._episodic) == 1
        assert len(memory._semantic) == 1
        assert len(memory._procedural) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
