# src/memory/architecture.py
"""
Multi-Modal Memory Architecture for the Meta-Cognitive Harness.

Memory is not a database. It is a differentiated cognitive substrate:
- Episodic: What happened (raw traces)
- Semantic: What matters (learned patterns)
- Procedural: How to do (skills and workflows)
- Prospective: What to do (planned future actions)
- Working: What is active now (current context)

Each memory type has different retention, retrieval, and forgetting policies.
This is the "different" memory the harness needs to be context-rich.

Principle: In God we trust. All others must bring data.

[CITATION: ViG-RAG2026]
PTKG (Periodic Temporal Knowledge Graph) provides structured temporal memory.

[CITATION: Shinn2023]
Reflexion episodic memory buffer enables self-improvement.

[CITATION: Heins2024]
Active Inference: memory updates minimize expected free energy.
"""

import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from shared.utils.citations import cite
from memory.stores import (
    EpisodicStore,
    SemanticStore,
    ProceduralStore,
    ProspectiveStore,
    WorkingStore,
)


@cite(
    key="MEMORY-TYPE",
    paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
    venue="ACN Architecture Document",
    section="Memory Type Enumeration",
    rationale="Five distinct memory types with different cognitive functions",
    confidence="CERTAIN",
)
class MemoryType(Enum):
    EPISODIC = "episodic"      # Raw event traces
    SEMANTIC = "semantic"      # Learned patterns and facts
    PROCEDURAL = "procedural"  # Skills and workflows
    PROSPECTIVE = "prospective"  # Future intentions and plans
    WORKING = "working"        # Active context (limited capacity)


@cite(
    key="MEMORY-RETRIEVAL",
    paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
    venue="ACN Architecture Document",
    section="Retrieval Strategy Enumeration",
    rationale="Different retrieval strategies match different cognitive needs",
    confidence="CERTAIN",
)
class RetrievalStrategy(Enum):
    RECENCY = "recency"        # Most recent first
    RELEVANCE = "relevance"    # Semantic similarity
    CAUSAL = "causal"          # Causal chain following
    SURPRISE = "surprise"      # High free energy (unexpected events)


@cite(
    key="MEMORY-TRACE",
    paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
    venue="ACN Architecture Document",
    section="Memory Trace Dataclass",
    rationale="Immutable trace with metadata enables differentiated storage and retrieval",
    confidence="CERTAIN",
)
@dataclass
class MemoryTrace:
    """A single memory entry with metadata for differentiated storage."""
    trace_id: str
    memory_type: MemoryType
    content: Any
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None  # Which twin/system created this
    confidence: float = 1.0
    importance: float = 0.5  # 0.0-1.0, determines retention priority
    tags: List[str] = field(default_factory=list)
    causal_links: List[str] = field(default_factory=list)  # trace_ids that caused/followed this
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)


@cite(
    key="MEMORY-ARCH",
    paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
    venue="ACN Architecture Document",
    section="Memory Subsystem",
    rationale="Different memory types with different policies enable context-rich operation",
    confidence="CERTAIN",
)
class MultiModalMemory:
    """
    The harness memory system.
    
    Not a uniform database. Each memory type is optimized for its cognitive function:
    
    **Episodic Memory:**
    - Stores: Raw execution traces, twin reasoning outputs, search results
    - Retention: Time-decay (older traces less relevant)
    - Retrieval: Recency + causal chaining
    - Forgetting: Traces with low access_count and old timestamp are pruned
    - Capacity: Large but not infinite (auto-pruning)
    
    **Semantic Memory:**
    - Stores: Learned patterns, cross-task generalizations, verified facts
    - Retention: Permanent (unless contradicted)
    - Retrieval: Relevance (semantic similarity to query)
    - Forgetting: Only on explicit contradiction (Bayesian update)
    - Capacity: Unbounded (graph-structured)
    
    **Procedural Memory:**
    - Stores: Skills, workflows, API usage patterns, debugging strategies
    - Retention: Reinforcement-based (successful procedures strengthened)
    - Retrieval: Task matching ("what skill fits this task?")
    - Forgetting: Unused procedures decay
    - Capacity: Moderate (skill registry)
    
    **Prospective Memory:**
    - Stores: Planned actions, scheduled tasks, intentions
    - Retention: Until executed or cancelled
    - Retrieval: Time-based ("what should I do next?")
    - Forgetting: Executed plans archived to episodic
    - Capacity: Small (only active plans)
    
    **Working Memory:**
    - Stores: Current task context, active twin outputs, pending decisions
    - Retention: Task-bound (cleared on task completion)
    - Retrieval: Direct access (always available)
    - Forgetting: Immediate on context switch
    - Capacity: Very limited (7±2 items, Miller's law)
    """

    def __init__(
        self,
        working_capacity: int = 7,
        episodic_capacity: int = 10000,
        procedural_capacity: int = 1000,
        backend: Optional[Any] = None,
    ):
        self.working_capacity = working_capacity
        self.episodic_capacity = episodic_capacity
        self.procedural_capacity = procedural_capacity
        self.backend = backend

        # Storage containers — shared between MultiModalMemory (coordinator)
        # and the polymorphic stores (SRP/OCP compliant)
        self._episodic: List[MemoryTrace] = []
        self._semantic: Dict[str, MemoryTrace] = {}
        self._procedural: Dict[str, MemoryTrace] = {}
        self._prospective: List[MemoryTrace] = []
        self._working: List[MemoryTrace] = []

        # Polymorphic store registry — delegates to shared containers
        self._stores = {
            MemoryType.EPISODIC: EpisodicStore(self._episodic, capacity=episodic_capacity),
            MemoryType.SEMANTIC: SemanticStore(self._semantic),
            MemoryType.PROCEDURAL: ProceduralStore(self._procedural, capacity=procedural_capacity),
            MemoryType.PROSPECTIVE: ProspectiveStore(self._prospective),
            MemoryType.WORKING: WorkingStore(self._working, capacity=working_capacity),
        }

        # Index for fast retrieval (cross-cutting, stays in coordinator)
        self._tag_index: Dict[str, List[str]] = {}  # tag -> trace_ids
        self._causal_index: Dict[str, List[str]] = {}  # trace_id -> caused trace_ids

        # Load from persistent backend if provided
        if self.backend is not None:
            self._load_from_backend()

    @cite(
        key="MEMORY-STORE",
        paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
        venue="ACN Architecture Document",
        section="Storage Policies",
        rationale="Different storage policies match cognitive function",
        confidence="CERTAIN",
    )
    def store(self, trace: MemoryTrace) -> None:
        """Store a memory trace in the appropriate memory type."""
        store = self._stores.get(trace.memory_type)
        if store is None:
            raise ValueError(f"Unknown memory type: {trace.memory_type}")

        evicted = store.store(trace)
        if evicted is not None and trace.memory_type == MemoryType.WORKING:
            # Promote evicted working memory item to episodic
            evicted.memory_type = MemoryType.EPISODIC
            self._stores[MemoryType.EPISODIC].store(evicted)

        # Update indices
        for tag in trace.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(trace.trace_id)

        for link in trace.causal_links:
            if link not in self._causal_index:
                self._causal_index[link] = []
            self._causal_index[link].append(trace.trace_id)

    @cite(
        key="MEMORY-RETRIEVE",
        paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
        venue="ACN Architecture Document",
        section="Retrieval Policies",
        rationale="Different retrieval strategies match different cognitive needs",
        confidence="CERTAIN",
    )
    def retrieve(
        self,
        memory_type: MemoryType,
        strategy: RetrievalStrategy,
        query: Optional[Any] = None,
        limit: int = 5,
    ) -> List[MemoryTrace]:
        """Retrieve memories using the appropriate strategy."""
        store = self._stores.get(memory_type)
        if store is None:
            return []

        # Episodic has special strategies not in the generic store interface
        if memory_type == MemoryType.EPISODIC:
            return self._retrieve_episodic(strategy, query, limit)

        # Working memory returns a copy to prevent external mutation
        if memory_type == MemoryType.WORKING:
            return store.retrieve(query, limit)

        return store.retrieve(query, limit)

    def _retrieve_episodic(
        self, strategy: RetrievalStrategy, query: Any, limit: int
    ) -> List[MemoryTrace]:
        """Episodic retrieval with specialized strategies."""
        episodic_store = self._stores[MemoryType.EPISODIC]
        all_traces = episodic_store.retrieve(None, episodic_store.capacity)

        if strategy == RetrievalStrategy.RECENCY:
            sorted_traces = sorted(all_traces, key=lambda t: t.timestamp, reverse=True)
        elif strategy == RetrievalStrategy.SURPRISE:
            sorted_traces = sorted(
                all_traces,
                key=lambda t: t.importance * (1 - t.confidence),
                reverse=True,
            )
        elif strategy == RetrievalStrategy.CAUSAL and isinstance(query, str):
            chain = []
            current = query
            visited = set()
            while current and current not in visited:
                visited.add(current)
                trace = next((t for t in all_traces if t.trace_id == current), None)
                if trace:
                    chain.append(trace)
                current = self._causal_index.get(current, [None])[0]
            return chain[:limit]
        else:
            sorted_traces = all_traces

        return sorted_traces[:limit]

    @cite(
        key="MEMORY-STATS",
        paper="Meta-Cognitive Harness: Multi-Modal Memory Architecture",
        venue="ACN Architecture Document",
        section="Memory Statistics",
        rationale="Operational metrics for memory subsystem monitoring",
        confidence="CERTAIN",
    )
    def get_memory_stats(self) -> Dict[str, Any]:
        """Report on memory usage across all types."""
        return {
            "episodic_count": len(self._stores[MemoryType.EPISODIC]),
            "semantic_count": len(self._stores[MemoryType.SEMANTIC]),
            "procedural_count": len(self._stores[MemoryType.PROCEDURAL]),
            "prospective_count": len(self._stores[MemoryType.PROSPECTIVE]),
            "working_count": len(self._stores[MemoryType.WORKING]),
            "working_capacity": self.working_capacity,
            "tag_index_size": len(self._tag_index),
            "causal_index_size": len(self._causal_index),
        }
