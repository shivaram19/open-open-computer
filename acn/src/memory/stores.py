# src/memory/stores.py
"""
MemoryStore Protocol and Implementations.

Replaces the monolithic if-elif dispatch in MultiModalMemory with
polymorphic store implementations registered by MemoryType.

These stores operate on storage containers passed from MultiModalMemory,
maintaining backward compatibility with existing tests while enabling
the registry pattern for future memory types.

Research basis:
- Meyer (1988): OCP — open for extension, closed for modification
- Martin (1996): DIP — depend on abstractions
- Fowler (1999): Replace Conditional with Polymorphism

[CITATION: MEMORY-ARCH]
"""

import time
from typing import Protocol, Dict, List, Optional, Any

from shared.utils.citations import cite


class MemoryStore(Protocol):
    """Protocol for a single memory type store."""

    def store(self, trace) -> None: ...
    def retrieve(self, query: Optional[Any], limit: int) -> List: ...
    def clear(self) -> None: ...


@cite(
    key="EPISODIC-STORE",
    paper="Meta-Cognitive Harness: Episodic Memory Store",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Episodic memory stores raw traces with time-decay retention",
    confidence="CERTAIN",
)
class EpisodicStore:
    """Episodic memory: What happened (raw traces)."""

    def __init__(self, buffer: List, capacity: int = 10000):
        self._buffer = buffer
        self.capacity = capacity

    def store(self, trace) -> None:
        self._buffer.append(trace)
        if len(self._buffer) > self.capacity:
            self._prune()

    def retrieve(self, query: Optional[Any], limit: int) -> List:
        return sorted(self._buffer, key=lambda t: t.timestamp, reverse=True)[:limit]

    def _prune(self) -> None:
        """Remove low-importance, low-access traces (old strategy preserved)."""
        self._buffer.sort(
            key=lambda t: (t.importance * (t.access_count + 1)) / (time.time() - t.timestamp + 1),
            reverse=True,
        )
        self._buffer[:] = self._buffer[:self.capacity]

    def __len__(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()


@cite(
    key="SEMANTIC-STORE",
    paper="Meta-Cognitive Harness: Semantic Memory Store",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Semantic memory stores learned patterns keyed by concept with Bayesian merge",
    confidence="CERTAIN",
)
class SemanticStore:
    """Semantic memory: What matters (learned patterns and facts)."""

    def __init__(self, concepts: Dict):
        self._concepts = concepts

    def store(self, trace) -> None:
        concept = trace.tags[0] if trace.tags else trace.trace_id
        if concept in self._concepts:
            existing = self._concepts[concept]
            merged_confidence = 1 - (1 - existing.confidence) * (1 - trace.confidence)
            existing.confidence = merged_confidence
            existing.content = self._merge(existing.content, trace.content)
            existing.timestamp = time.time()
        else:
            self._concepts[concept] = trace

    def retrieve(self, query: Optional[Any], limit: int) -> List:
        if query and isinstance(query, str):
            matching = [
                t for t in self._concepts.values()
                if query in t.tags or query in str(t.content)
            ]
            return sorted(matching, key=lambda t: t.confidence, reverse=True)[:limit]
        return list(self._concepts.values())[:limit]

    @staticmethod
    def _merge(existing: Any, new: Any) -> Any:
        if isinstance(existing, dict) and isinstance(new, dict):
            merged = existing.copy()
            merged.update(new)
            return merged
        return new

    def __len__(self) -> int:
        return len(self._concepts)

    def clear(self) -> None:
        self._concepts.clear()


@cite(
    key="PROCEDURAL-STORE",
    paper="Meta-Cognitive Harness: Procedural Memory Store",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Procedural memory stores skills and workflows keyed by skill name",
    confidence="CERTAIN",
)
class ProceduralStore:
    """Procedural memory: How to do (skills and workflows)."""

    def __init__(self, skills: Dict, capacity: int = 1000):
        self._skills = skills
        self.capacity = capacity

    def store(self, trace) -> None:
        skill_name = trace.tags[0] if trace.tags else trace.trace_id
        if len(self._skills) >= self.capacity:
            self._prune()
        self._skills[skill_name] = trace

    def retrieve(self, query: Optional[Any], limit: int) -> List:
        if query and isinstance(query, str):
            matching = [t for t in self._skills.values() if query in t.tags]
            return sorted(matching, key=lambda t: t.confidence, reverse=True)[:limit]
        return list(self._skills.values())[:limit]

    def _prune(self) -> None:
        """Remove least-used procedures (bottom 10%)."""
        sorted_procs = sorted(
            self._skills.items(),
            key=lambda item: item[1].access_count,
        )
        to_remove = sorted_procs[: len(sorted_procs) // 10]
        for key, _ in to_remove:
            self._skills.pop(key, None)

    def __len__(self) -> int:
        return len(self._skills)

    def clear(self) -> None:
        self._skills.clear()


@cite(
    key="PROSPECTIVE-STORE",
    paper="Meta-Cognitive Harness: Prospective Memory Store",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Prospective memory stores planned future actions",
    confidence="CERTAIN",
)
class ProspectiveStore:
    """Prospective memory: What to do (planned future actions)."""

    def __init__(self, plans: List):
        self._plans = plans

    def store(self, trace) -> None:
        self._plans.append(trace)

    def retrieve(self, query: Optional[Any], limit: int) -> List:
        return self._plans[:limit]

    def __len__(self) -> int:
        return len(self._plans)

    def clear(self) -> None:
        self._plans.clear()


@cite(
    key="WORKING-STORE",
    paper="Meta-Cognitive Harness: Working Memory Store",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Working memory holds active context with Miller-capacity limit",
    confidence="CERTAIN",
)
class WorkingStore:
    """Working memory: What is active now (current context)."""

    def __init__(self, items: List, capacity: int = 7):
        self._items = items
        self.capacity = capacity

    def store(self, trace):
        self._items.append(trace)
        if len(self._items) > self.capacity:
            return self._items.pop(0)
        return None

    def retrieve(self, query: Optional[Any], limit: int) -> List:
        return self._items[-limit:]

    def peek_oldest(self):
        return self._items[0] if self._items else None

    def __len__(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
