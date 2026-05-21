# src/memory/layered_models.py
"""
Data models for the Layered Memory Architecture.

L0: ConversationMemory — raw traces (MemoryTrace, already exists)
L1: AtomMemory — structured facts extracted from traces
L2: ScenarioMemory — recurrent pattern templates from atom clusters
L3: PersonaMemory — evolved cognitive profile from scenarios

[CITATION: TencentDB2026]
[CITATION: LAYERED-MEMORY]
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="ATOM-TYPE",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="L1 Atom Memory",
    rationale="Typed atoms enable structured reasoning trace decomposition",
    confidence="CERTAIN",
)
class AtomType(Enum):
    """Types of atomic facts extracted from reasoning traces."""
    CLAIM = "claim"              # Factual assertion
    INSIGHT = "insight"          # Novel realization or connection
    CORRECTION = "correction"    # Self-critique or peer-induced fix
    OUTCOME = "outcome"          # Execution result (success/failure)
    META_COGNITIVE = "meta_cognitive"  # Confidence shift, bias detection
    HYPOTHESIS = "hypothesis"    # Tentative assumption to validate
    RECOMMENDATION = "recommendation"  # Proposed action or approach


@cite(
    key="MEMORY-ATOM",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="L1 Atom Memory",
    rationale="Immutable atom with provenance enables traceable knowledge extraction",
    confidence="CERTAIN",
)
@dataclass
class MemoryAtom:
    """
    A single atomic fact extracted from a reasoning trace (L1).

    Atoms are the building blocks of higher-level memory.
    They carry full provenance so their origin is always traceable.
    """
    atom_id: str
    atom_type: AtomType
    content: str
    source_trace_id: str           # Which L0 trace this came from
    twin_id: str                   # Which twin generated this
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.7
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        atom_type: AtomType,
        content: str,
        source_trace_id: str,
        twin_id: str,
        confidence: float = 0.7,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "MemoryAtom":
        return cls(
            atom_id=f"atom-{uuid.uuid4().hex[:12]}",
            atom_type=atom_type,
            content=content,
            source_trace_id=source_trace_id,
            twin_id=twin_id,
            confidence=confidence,
            tags=tags or [],
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_id": self.atom_id,
            "atom_type": self.atom_type.value,
            "content": self.content,
            "source_trace_id": self.source_trace_id,
            "twin_id": self.twin_id,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryAtom":
        return cls(
            atom_id=data["atom_id"],
            atom_type=AtomType(data["atom_type"]),
            content=data["content"],
            source_trace_id=data["source_trace_id"],
            twin_id=data["twin_id"],
            timestamp=data.get("timestamp", time.time()),
            confidence=data.get("confidence", 0.7),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@cite(
    key="SCENARIO-PATTERN",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="L2 Scenario Memory",
    rationale="Pattern templates capture recurrent twin behavior for prediction and retrieval",
    confidence="CERTAIN",
)
@dataclass
class ScenarioPattern:
    """
    A recurrent pattern mined from L1 atoms (L2).

    Represents: "When [context], twin [twin_id] typically [behavior]"
    """
    pattern_id: str
    template: str                    # Human-readable pattern description
    twin_id: str
    context_keywords: List[str]      # What triggers this pattern
    behavior_summary: str            # What the twin does
    support_count: int = 0           # How many atoms support this
    confidence: float = 0.5
    example_atom_ids: List[str] = field(default_factory=list)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        template: str,
        twin_id: str,
        context_keywords: List[str],
        behavior_summary: str,
        example_atom_ids: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> "ScenarioPattern":
        now = time.time()
        return cls(
            pattern_id=f"scen-{uuid.uuid4().hex[:12]}",
            template=template,
            twin_id=twin_id,
            context_keywords=context_keywords,
            behavior_summary=behavior_summary,
            support_count=len(example_atom_ids) if example_atom_ids else 0,
            confidence=confidence,
            example_atom_ids=example_atom_ids or [],
            first_seen=now,
            last_seen=now,
        )

    def add_support(self, atom_id: str) -> None:
        """Add another atom as supporting evidence."""
        if atom_id not in self.example_atom_ids:
            self.example_atom_ids.append(atom_id)
            self.support_count = len(self.example_atom_ids)
            self.last_seen = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "template": self.template,
            "twin_id": self.twin_id,
            "context_keywords": self.context_keywords,
            "behavior_summary": self.behavior_summary,
            "support_count": self.support_count,
            "confidence": self.confidence,
            "example_atom_ids": self.example_atom_ids,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScenarioPattern":
        return cls(
            pattern_id=data["pattern_id"],
            template=data["template"],
            twin_id=data["twin_id"],
            context_keywords=data.get("context_keywords", []),
            behavior_summary=data.get("behavior_summary", ""),
            support_count=data.get("support_count", 0),
            confidence=data.get("confidence", 0.5),
            example_atom_ids=data.get("example_atom_ids", []),
            first_seen=data.get("first_seen", time.time()),
            last_seen=data.get("last_seen", time.time()),
            metadata=data.get("metadata", {}),
        )


@cite(
    key="PERSONA-MEMORY",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="L3 Persona Memory",
    rationale="Evolved cognitive profile captures learned behavior beyond base twin signature",
    confidence="CERTAIN",
)
@dataclass
class PersonaMemory:
    """
    An evolved cognitive profile distilled from L2 scenarios (L3).

    This is NOT a replacement for the twin's base signature — it's
    an empirical overlay: "Base says X, but experience shows Y."
    """
    persona_id: str
    twin_id: str
    version: int = 1

    # Evolved heuristics: base heuristic → empirical validation
    heuristic_evidence: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # e.g., {"verification": {"success_rate": 0.85, "contexts": ["consensus", "safety"]}}

    # Calibrated biases: bias name → when it actually manifests
    bias_manifestations: Dict[str, List[str]] = field(default_factory=dict)
    # e.g., {"verbal_bias": ["visual tasks", "spatial reasoning"]}

    # Confidence map: task keyword → empirical confidence
    confidence_map: Dict[str, float] = field(default_factory=dict)
    # e.g., {"code": 0.92, "math": 0.88, "creative": 0.45}

    # Expertise boundaries: what the twin should/shouldn't handle
    expertise_boundaries: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"strong_in": ["debugging", "benchmarking"], "weak_in": ["ui_design"]}

    # Scenarios that contributed to this persona
    source_scenario_ids: List[str] = field(default_factory=list)

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        twin_id: str,
        base_signature: Optional[Dict[str, Any]] = None,
    ) -> "PersonaMemory":
        now = time.time()
        persona = cls(
            persona_id=f"persona-{twin_id}-{uuid.uuid4().hex[:8]}",
            twin_id=twin_id,
            version=1,
            created_at=now,
            updated_at=now,
        )
        if base_signature:
            # Seed from base signature
            heuristics = base_signature.get("heuristics", {})
            for key in heuristics:
                persona.heuristic_evidence[key] = {
                    "success_rate": 0.5,
                    "support_count": 0,
                    "contexts": [],
                }
            biases = base_signature.get("biases", {})
            for key in biases:
                persona.bias_manifestations[key] = []
        return persona

    def update_from_scenarios(self, scenarios: List[ScenarioPattern]) -> None:
        """Incorporate new scenarios into the persona."""
        for scen in scenarios:
            if scen.pattern_id not in self.source_scenario_ids:
                self.source_scenario_ids.append(scen.pattern_id)
            # Update confidence map from behavior summaries
            for kw in scen.context_keywords:
                current = self.confidence_map.get(kw, 0.5)
                self.confidence_map[kw] = (current + scen.confidence) / 2
        self.version += 1
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "twin_id": self.twin_id,
            "version": self.version,
            "heuristic_evidence": self.heuristic_evidence,
            "bias_manifestations": self.bias_manifestations,
            "confidence_map": self.confidence_map,
            "expertise_boundaries": self.expertise_boundaries,
            "source_scenario_ids": self.source_scenario_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonaMemory":
        return cls(
            persona_id=data["persona_id"],
            twin_id=data["twin_id"],
            version=data.get("version", 1),
            heuristic_evidence=data.get("heuristic_evidence", {}),
            bias_manifestations=data.get("bias_manifestations", {}),
            confidence_map=data.get("confidence_map", {}),
            expertise_boundaries=data.get("expertise_boundaries", {}),
            source_scenario_ids=data.get("source_scenario_ids", []),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            metadata=data.get("metadata", {}),
        )


@cite(
    key="LAYERED-CONTEXT",
    paper="Layered Memory Architecture for Digital Twins",
    venue="ACN Architecture Document",
    section="Cross-Layer Retrieval",
    rationale="Unified context object enables ranked retrieval from all memory layers",
    confidence="CERTAIN",
)
@dataclass
class LayeredContext:
    """Retrieved context from all memory layers, ranked for prompt injection."""
    query: str
    l0_traces: List[Dict[str, Any]] = field(default_factory=list)
    l1_atoms: List[Dict[str, Any]] = field(default_factory=list)
    l2_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    l3_persona: Optional[Dict[str, Any]] = None
    total_tokens_estimate: int = 0

    def to_prompt_string(self, max_tokens: int = 2000) -> str:
        """Build a prompt-ready context string, respecting token budget."""
        parts = [f"=== LAYERED MEMORY CONTEXT for: {self.query} ==="]
        if self.l3_persona:
            parts.append(f"\n[Persona Profile] {self.l3_persona.get('twin_id', '')}")
            confidence_map = self.l3_persona.get("confidence_map", {})
            if confidence_map:
                top = sorted(confidence_map.items(), key=lambda x: x[1], reverse=True)[:3]
                parts.append("Top confidence areas: " + ", ".join(f"{k}({v:.2f})" for k, v in top))
        if self.l2_scenarios:
            parts.append(f"\n[Scenarios] {len(self.l2_scenarios)} patterns:")
            for s in self.l2_scenarios[:3]:
                parts.append(f"  - {s.get('template', '')} (support: {s.get('support_count', 0)})")
        if self.l1_atoms:
            parts.append(f"\n[Recent Insights] {len(self.l1_atoms)} atoms:")
            for a in self.l1_atoms[:5]:
                parts.append(f"  [{a.get('atom_type', '')}] {a.get('content', '')[:100]}...")
        parts.append("\n=== END LAYERED CONTEXT ===")
        result = "\n".join(parts)
        # Rough token estimate: ~4 chars per token
        if len(result) > max_tokens * 4:
            result = result[:max_tokens * 4] + "\n...[truncated]"
        return result


@dataclass
class ConsolidationReport:
    """Report from a consolidation pass (L1→L2→L3)."""
    twin_id: str
    atoms_processed: int = 0
    scenarios_mined: int = 0
    persona_updated: bool = False
    persona_version: int = 0
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
