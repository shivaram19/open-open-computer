"""
TDD Tests for Phase 4.4 — WorkingStore eviction transparency.

Verifies that WorkingStore.store() returns the evicted item when overflow
occurs, enabling MultiModalMemory to promote it to episodic without
accessing private containers.
"""

import pytest

from memory.stores import WorkingStore, EpisodicStore
from memory.architecture import MemoryTrace, MemoryType


class TestWorkingStoreEviction:
    """WorkingStore must return evicted item on overflow."""

    def test_store_returns_none_when_no_overflow(self):
        store = WorkingStore(items=[], capacity=3)
        trace = MemoryTrace(
            trace_id="t1",
            content="hello",
            memory_type=MemoryType.WORKING,
            timestamp=1.0,
        )
        evicted = store.store(trace)
        assert evicted is None
        assert len(store) == 1

    def test_store_returns_evicted_on_overflow(self):
        store = WorkingStore(items=[], capacity=2)
        t1 = MemoryTrace(trace_id="t1", content="a", memory_type=MemoryType.WORKING, timestamp=1.0)
        t2 = MemoryTrace(trace_id="t2", content="b", memory_type=MemoryType.WORKING, timestamp=2.0)
        t3 = MemoryTrace(trace_id="t3", content="c", memory_type=MemoryType.WORKING, timestamp=3.0)

        assert store.store(t1) is None
        assert store.store(t2) is None
        evicted = store.store(t3)

        assert evicted is t1  # FIFO eviction
        assert len(store) == 2
        assert store.retrieve(None, 10) == [t2, t3]
