# src/memory/layered_memory.py
"""
Layered Memory System: L0→L3 hierarchical abstraction for digital twins.

Maps to existing MultiModalMemory stores:
- L0 (Conversation): EpisodicStore — raw traces
- L1 (Atom): SemanticStore — structured facts (tagged "l1_atom")
- L2 (Scenario): SemanticStore — pattern templates (tagged "l2_scenario")
- L3 (Persona): SemanticStore — cognitive profile (tagged "l3_persona")

[CITATION: LAYERED-MEMORY]
[CITATION: TencentDB2026]
"""

import time
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from memory.architecture import MultiModalMemory, MemoryType, MemoryTrace, RetrievalStrategy
from memory.layered_models import (
    MemoryAtom,
    ScenarioPattern,
    PersonaMemory,
    LayeredContext,
    ConsolidationReport,
)
from memory.atomizer import MemoryAtomizer


# ── Layer helpers ──────────────────────────────────────────────────────────

class ConversationLayer:
    """L0: Raw conversation/reasoning traces. Delegates to EpisodicStore."""

    def __init__(self, memory: MultiModalMemory):
        self.memory = memory

    def store(self, trace: MemoryTrace) -> None:
        self.memory.store(trace)

    def retrieve_recent(self, limit: int = 5) -> List[MemoryTrace]:
        return self.memory.retrieve(
            MemoryType.EPISODIC, RetrievalStrategy.RECENCY, limit=limit
        )

    def retrieve_by_tag(self, tag: str, limit: int = 10) -> List[MemoryTrace]:
        all_traces = self.memory.retrieve(
            MemoryType.EPISODIC, RetrievalStrategy.RECENCY,
            limit=self.memory.episodic_capacity,
        )
        return [t for t in all_traces if tag in getattr(t, "tags", [])][:limit]


class AtomLayer:
    """L1: Structured atomic facts. Delegates to SemanticStore."""

    def __init__(self, memory: MultiModalMemory, atomizer: Optional[MemoryAtomizer] = None):
        self.memory = memory
        self.atomizer = atomizer or MemoryAtomizer(mode="rule")

    def store(self, atom: MemoryAtom) -> None:
        trace = MemoryTrace(
            trace_id=atom.atom_id,
            memory_type=MemoryType.SEMANTIC,
            content=atom.to_dict(),
            source=atom.twin_id,
            confidence=atom.confidence,
            importance=0.6,
            # First tag must be unique to prevent SemanticStore merging
            tags=[atom.atom_id, "l1_atom", atom.atom_type.value, atom.twin_id] + atom.tags,
        )
        self.memory.store(trace)

    def atomize_and_store(self, trace: MemoryTrace, twin_signature: Optional[Dict] = None) -> List[MemoryAtom]:
        atoms = self.atomizer.atomize(trace, twin_signature)
        for atom in atoms:
            self.store(atom)
        return atoms

    def retrieve_by_type(self, atom_type: str, limit: int = 10) -> List[MemoryAtom]:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query=atom_type, limit=limit * 3)
        atoms = []
        for t in traces:
            if "l1_atom" in getattr(t, "tags", []):
                try:
                    data = t.content if isinstance(t.content, dict) else {}
                    if data and "atom_id" in data:
                        atoms.append(MemoryAtom.from_dict(data))
                except Exception:
                    continue
        return atoms[:limit]

    def retrieve_recent(self, limit: int = 10) -> List[MemoryAtom]:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RECENCY, limit=limit * 3)
        atoms = []
        for t in traces:
            if "l1_atom" in getattr(t, "tags", []):
                try:
                    data = t.content if isinstance(t.content, dict) else {}
                    if data and "atom_id" in data:
                        atoms.append(MemoryAtom.from_dict(data))
                except Exception:
                    continue
        return atoms[:limit]

    def count(self) -> int:
        # Approximate: count semantic traces with l1_atom tag
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query="l1_atom", limit=10000)
        return sum(1 for t in traces if "l1_atom" in getattr(t, "tags", []))


class ScenarioLayer:
    """L2: Recurrent scenario patterns. Delegates to SemanticStore."""

    def __init__(self, memory: MultiModalMemory):
        self.memory = memory

    def store(self, pattern: ScenarioPattern) -> None:
        trace = MemoryTrace(
            trace_id=pattern.pattern_id,
            memory_type=MemoryType.SEMANTIC,
            content=pattern.to_dict(),
            source=pattern.twin_id,
            confidence=pattern.confidence,
            importance=0.7,
            tags=[pattern.pattern_id, "l2_scenario", pattern.twin_id] + pattern.context_keywords,
        )
        self.memory.store(trace)

    def retrieve_for_twin(self, twin_id: str, limit: int = 10) -> List[ScenarioPattern]:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query=twin_id, limit=limit * 3)
        patterns = []
        for t in traces:
            if "l2_scenario" in getattr(t, "tags", []):
                try:
                    data = t.content if isinstance(t.content, dict) else {}
                    if data and "pattern_id" in data:
                        patterns.append(ScenarioPattern.from_dict(data))
                except Exception:
                    continue
        return patterns[:limit]

    def retrieve_by_keyword(self, keyword: str, limit: int = 5) -> List[ScenarioPattern]:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query=keyword, limit=limit * 3)
        patterns = []
        for t in traces:
            if "l2_scenario" in getattr(t, "tags", []):
                try:
                    data = t.content if isinstance(t.content, dict) else {}
                    if data and "pattern_id" in data:
                        patterns.append(ScenarioPattern.from_dict(data))
                except Exception:
                    continue
        return patterns[:limit]

    def count(self) -> int:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query="l2_scenario", limit=10000)
        return sum(1 for t in traces if "l2_scenario" in getattr(t, "tags", []))


class PersonaLayer:
    """L3: Evolved cognitive profile. Delegates to SemanticStore."""

    def __init__(self, memory: MultiModalMemory):
        self.memory = memory

    def store(self, persona: PersonaMemory) -> None:
        trace = MemoryTrace(
            trace_id=persona.persona_id,
            memory_type=MemoryType.SEMANTIC,
            content=persona.to_dict(),
            source=persona.twin_id,
            confidence=0.9,
            importance=0.95,
            tags=[persona.persona_id, "l3_persona", persona.twin_id],
        )
        self.memory.store(trace)

    def retrieve_for_twin(self, twin_id: str) -> Optional[PersonaMemory]:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query=twin_id, limit=50)
        for t in traces:
            tags = getattr(t, "tags", [])
            if "l3_persona" in tags and getattr(t, "source", None) == twin_id:
                try:
                    data = t.content if isinstance(t.content, dict) else {}
                    if data and "persona_id" in data:
                        return PersonaMemory.from_dict(data)
                except Exception:
                    continue
        return None

    def count(self) -> int:
        traces = self.memory.retrieve(MemoryType.SEMANTIC, RetrievalStrategy.RELEVANCE, query="l3_persona", limit=10000)
        return sum(1 for t in traces if "l3_persona" in getattr(t, "tags", []))


# ── Main coordinator ───────────────────────────────────────────────────────

@cite(
    key="LAYERED-MEMORY-SYSTEM",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="System Coordinator",
    rationale="Unified coordinator manages hierarchical memory abstraction while preserving existing store semantics",
    confidence="HIGH",
)
class LayeredMemorySystem:
    """
    Central coordinator for L0-L3 memory layers.

    Wraps MultiModalMemory and adds hierarchical abstraction without
    modifying the underlying stores. Each layer uses tag-based
    discrimination within the existing SemanticStore.
    """

    def __init__(
        self,
        base_memory: MultiModalMemory,
        twin_id: str,
        atomizer: Optional[MemoryAtomizer] = None,
    ):
        self.base = base_memory
        self.twin_id = twin_id
        self.l0 = ConversationLayer(base_memory)
        self.l1 = AtomLayer(base_memory, atomizer)
        self.l2 = ScenarioLayer(base_memory)
        self.l3 = PersonaLayer(base_memory)

    def store_trace(self, trace: MemoryTrace, twin_signature: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Store an L0 trace and trigger L1 atomization.

        Returns a dict with trace_id and atom count.
        """
        self.l0.store(trace)
        atoms = self.l1.atomize_and_store(trace, twin_signature)
        return {
            "trace_id": trace.trace_id,
            "atoms_created": len(atoms),
            "atom_types": [a.atom_type.value for a in atoms],
        }

    def retrieve_context(self, query: str, limit_per_layer: int = 3) -> LayeredContext:
        """Retrieve ranked context from all layers."""
        l0_traces = self.l0.retrieve_recent(limit_per_layer)
        l1_atoms = self.l1.retrieve_recent(limit_per_layer)
        l2_scenarios = self.l2.retrieve_by_keyword(query, limit_per_layer)
        l3_persona = self.l3.retrieve_for_twin(self.twin_id)

        ctx = LayeredContext(
            query=query,
            l0_traces=[t.to_dict() if hasattr(t, "to_dict") else {"trace_id": getattr(t, "trace_id", "")} for t in l0_traces],
            l1_atoms=[a.to_dict() for a in l1_atoms],
            l2_scenarios=[s.to_dict() for s in l2_scenarios],
            l3_persona=l3_persona.to_dict() if l3_persona else None,
        )
        return ctx

    def get_layer_stats(self) -> Dict[str, int]:
        """Return counts for each layer."""
        return {
            "l0_conversation": len(self.l0.retrieve_recent(limit=10000)),
            "l1_atoms": self.l1.count(),
            "l2_scenarios": self.l2.count(),
            "l3_personas": self.l3.count(),
            "twin_id": self.twin_id,
        }

    def consolidate(self, scenario_miner=None, persona_distiller=None, base_signature=None) -> ConsolidationReport:
        """
        Run L1→L2 scenario mining and L2→L3 persona distillation.

        This is a placeholder for the full consolidation pipeline.
        Steps 4-6 will provide the real implementations.
        """
        all_atoms = self.l1.retrieve_recent(limit=1000)
        report = ConsolidationReport(twin_id=self.twin_id, atoms_processed=len(all_atoms))

        if scenario_miner and len(all_atoms) >= 3:
            scenarios = scenario_miner.mine_scenarios(all_atoms)
            for scenario in scenarios:
                self.l2.store(scenario)
            report.scenarios_mined = len(scenarios)

            if persona_distiller and scenarios:
                existing = self.l3.retrieve_for_twin(self.twin_id)
                if existing:
                    persona = existing
                else:
                    persona = PersonaMemory.create(self.twin_id, base_signature)
                persona.update_from_scenarios(scenarios)
                self.l3.store(persona)
                report.persona_updated = True
                report.persona_version = persona.version

        return report
