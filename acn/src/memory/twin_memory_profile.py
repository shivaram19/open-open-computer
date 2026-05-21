# src/memory/twin_memory_profile.py
"""
TwinMemoryProfile: Per-twin layered memory binding.

Provides a clean interface for twins to store reasoning traces,
retrieve layered context, and run consolidation.

[CITATION: TWIN-MEMORY-PROFILE]
[CITATION: LAYERED-MEMORY]
"""

from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from memory.architecture import MultiModalMemory, MemoryTrace, MemoryType
from memory.layered_memory import LayeredMemorySystem
from memory.layered_models import LayeredContext, ConsolidationReport
from memory.atomizer import MemoryAtomizer
from memory.scenario_miner import ScenarioMiner
from memory.persona_distiller import PersonaDistiller


@cite(
    key="TWIN-MEMORY-PROFILE",
    paper="Layered Memory Architecture: Twin Binding",
    venue="ACN Architecture Document",
    section="Per-Twin Memory Profile",
    rationale="Clean interface binds twins to layered memory without exposing layer internals",
    confidence="HIGH",
)
class TwinMemoryProfile:
    """
    A twin's personal layered memory profile.

    Usage:
        profile = TwinMemoryProfile(twin_id="noah-shinn-001", base_signature=...)
        profile.record_think(reasoning)
        context = profile.get_reasoning_context("Should we use BFT?")
        report = profile.consolidate()
    """

    def __init__(
        self,
        twin_id: str,
        base_memory: Optional[MultiModalMemory] = None,
        base_signature: Optional[Dict[str, Any]] = None,
        atomizer: Optional[MemoryAtomizer] = None,
    ):
        self.twin_id = twin_id
        self.base_signature = base_signature or {}
        self.layered = LayeredMemorySystem(
            base_memory=base_memory or MultiModalMemory(),
            twin_id=twin_id,
            atomizer=atomizer,
        )
        self._scenario_miner = ScenarioMiner(min_support=2, similarity_threshold=0.15)
        self._persona_distiller = PersonaDistiller()

    def record_think(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a reasoning trace from think() and atomize it.

        Returns dict with trace_id and atoms_created.
        """
        trace = MemoryTrace(
            trace_id=f"think-{self.twin_id}-{reasoning.get('timestamp', 0)}",
            memory_type=MemoryType.EPISODIC,
            content=reasoning,
            source=self.twin_id,
            confidence=reasoning.get("confidence", 0.7),
            importance=0.8,
            tags=["twin_reasoning", self.twin_id],
        )
        return self.layered.store_trace(trace, self.base_signature)

    def record_critique(self, critique: str, source_peer: str) -> Dict[str, Any]:
        """Record a peer critique received by this twin."""
        trace = MemoryTrace(
            trace_id=f"critique-{self.twin_id}-{source_peer}-{hash(critique) & 0xFFFFFFFF}",
            memory_type=MemoryType.EPISODIC,
            content={
                "critique": critique,
                "from_peer": source_peer,
                "twin_id": self.twin_id,
            },
            source=source_peer,
            confidence=0.6,
            importance=0.7,
            tags=["peer_critique", source_peer, self.twin_id],
        )
        return self.layered.store_trace(trace, self.base_signature)

    def get_reasoning_context(self, task: str, max_tokens: int = 1500) -> str:
        """Build a prompt-ready context string from all memory layers."""
        ctx = self.layered.retrieve_context(task, limit_per_layer=3)
        return ctx.to_prompt_string(max_tokens=max_tokens)

    def get_layered_context(self, task: str) -> LayeredContext:
        """Get structured context from all layers."""
        return self.layered.retrieve_context(task, limit_per_layer=3)

    def consolidate(self) -> ConsolidationReport:
        """Run full consolidation: L1→L2 scenario mining, L2→L3 persona distillation."""
        return self.layered.consolidate(
            scenario_miner=self._scenario_miner,
            persona_distiller=self._persona_distiller,
            base_signature=self.base_signature,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get memory layer statistics."""
        stats = self.layered.get_layer_stats()
        stats["twin_name"] = self.base_signature.get("name", self.twin_id)
        stats["cluster"] = self.base_signature.get("cluster", "unknown")
        return stats
