# tests/memory/test_layered_memory.py
"""Tests for LayeredMemorySystem and layer helpers."""

import pytest
from memory.architecture import MultiModalMemory, MemoryTrace, MemoryType
from memory.layered_memory import (
    ConversationLayer,
    AtomLayer,
    ScenarioLayer,
    PersonaLayer,
    LayeredMemorySystem,
)
from memory.layered_models import MemoryAtom, AtomType, ScenarioPattern, PersonaMemory
from memory.atomizer import MemoryAtomizer


class TestConversationLayer:
    def test_store_and_retrieve(self):
        mem = MultiModalMemory()
        layer = ConversationLayer(mem)
        trace = MemoryTrace(
            trace_id="conv-001",
            memory_type=MemoryType.EPISODIC,
            content="Test reasoning trace",
            source="twin-001",
        )
        layer.store(trace)
        recent = layer.retrieve_recent(limit=5)
        assert len(recent) == 1
        assert recent[0].trace_id == "conv-001"

    def test_retrieve_by_tag(self):
        mem = MultiModalMemory()
        layer = ConversationLayer(mem)
        trace1 = MemoryTrace(
            trace_id="conv-002",
            memory_type=MemoryType.EPISODIC,
            content="Consensus deliberation",
            source="twin-001",
            tags=["consensus", "deliberation"],
        )
        trace2 = MemoryTrace(
            trace_id="conv-003",
            memory_type=MemoryType.EPISODIC,
            content="Code generation",
            source="twin-001",
            tags=["code", "generation"],
        )
        layer.store(trace1)
        layer.store(trace2)
        consensus = layer.retrieve_by_tag("consensus", limit=5)
        assert len(consensus) == 1
        assert consensus[0].trace_id == "conv-002"


class TestAtomLayer:
    def test_store_and_retrieve_atom(self):
        mem = MultiModalMemory()
        layer = AtomLayer(mem)
        atom = MemoryAtom.create(
            atom_type=AtomType.CLAIM,
            content="BFT is optimal",
            source_trace_id="trace-001",
            twin_id="twin-001",
            tags=["consensus"],
        )
        layer.store(atom)
        atoms = layer.retrieve_by_type("claim", limit=5)
        assert len(atoms) == 1
        assert atoms[0].content == "BFT is optimal"

    def test_atomize_and_store(self):
        mem = MultiModalMemory()
        layer = AtomLayer(mem, atomizer=MemoryAtomizer(mode="rule"))
        trace = MemoryTrace(
            trace_id="trace-002",
            memory_type=MemoryType.EPISODIC,
            content="The benchmark result shows 95% accuracy.",
            source="twin-001",
        )
        atoms = layer.atomize_and_store(trace)
        assert len(atoms) >= 1
        # Should be stored in semantic memory
        stored = layer.retrieve_recent(limit=5)
        assert len(stored) >= 1

    def test_retrieve_by_type_filtering(self):
        mem = MultiModalMemory()
        layer = AtomLayer(mem)
        layer.store(MemoryAtom.create(
            atom_type=AtomType.CLAIM, content="Claim A",
            source_trace_id="t1", twin_id="twin-001",
        ))
        layer.store(MemoryAtom.create(
            atom_type=AtomType.INSIGHT, content="Insight B",
            source_trace_id="t1", twin_id="twin-001",
        ))
        claims = layer.retrieve_by_type("claim", limit=5)
        assert len(claims) == 1
        assert claims[0].content == "Claim A"


class TestScenarioLayer:
    def test_store_and_retrieve(self):
        mem = MultiModalMemory()
        layer = ScenarioLayer(mem)
        pattern = ScenarioPattern.create(
            template="When consensus, prefers BFT",
            twin_id="twin-001",
            context_keywords=["consensus", "bft"],
            behavior_summary="Prefers BFT consensus",
            example_atom_ids=["atom-1"],
            confidence=0.8,
        )
        layer.store(pattern)
        patterns = layer.retrieve_for_twin("twin-001", limit=5)
        assert len(patterns) == 1
        assert patterns[0].template == "When consensus, prefers BFT"

    def test_retrieve_by_keyword(self):
        mem = MultiModalMemory()
        layer = ScenarioLayer(mem)
        layer.store(ScenarioPattern.create(
            template="When debugging, uses breakpoints",
            twin_id="twin-001",
            context_keywords=["debug", "breakpoint"],
            behavior_summary="Uses breakpoints",
            example_atom_ids=["atom-1"],
        ))
        layer.store(ScenarioPattern.create(
            template="When testing, uses TDD",
            twin_id="twin-001",
            context_keywords=["test", "tdd"],
            behavior_summary="Uses TDD",
            example_atom_ids=["atom-2"],
        ))
        debug_patterns = layer.retrieve_by_keyword("debug", limit=5)
        assert len(debug_patterns) == 1
        assert "breakpoint" in debug_patterns[0].context_keywords


class TestPersonaLayer:
    def test_store_and_retrieve(self):
        mem = MultiModalMemory()
        layer = PersonaLayer(mem)
        persona = PersonaMemory.create("twin-001")
        persona.confidence_map = {"math": 0.9}
        layer.store(persona)
        retrieved = layer.retrieve_for_twin("twin-001")
        assert retrieved is not None
        assert retrieved.twin_id == "twin-001"
        assert retrieved.confidence_map.get("math") == 0.9

    def test_retrieve_missing_returns_none(self):
        mem = MultiModalMemory()
        layer = PersonaLayer(mem)
        retrieved = layer.retrieve_for_twin("nonexistent-twin")
        assert retrieved is None


class TestLayeredMemorySystem:
    def test_store_trace_creates_atoms(self):
        mem = MultiModalMemory()
        system = LayeredMemorySystem(mem, twin_id="twin-001", atomizer=MemoryAtomizer(mode="rule"))
        trace = MemoryTrace(
            trace_id="trace-sys-001",
            memory_type=MemoryType.EPISODIC,
            content="The benchmark passed with 99% accuracy.",
            source="twin-001",
        )
        result = system.store_trace(trace)
        assert result["trace_id"] == "trace-sys-001"
        assert result["atoms_created"] >= 1
        assert "outcome" in result["atom_types"]

    def test_retrieve_context(self):
        mem = MultiModalMemory()
        system = LayeredMemorySystem(mem, twin_id="twin-001", atomizer=MemoryAtomizer(mode="rule"))
        trace = MemoryTrace(
            trace_id="trace-sys-002",
            memory_type=MemoryType.EPISODIC,
            content="BFT consensus handles Byzantine faults effectively.",
            source="twin-001",
        )
        system.store_trace(trace)
        ctx = system.retrieve_context("consensus", limit_per_layer=3)
        assert ctx.query == "consensus"
        assert len(ctx.l0_traces) >= 1
        assert len(ctx.l1_atoms) >= 1

    def test_get_layer_stats(self):
        mem = MultiModalMemory()
        system = LayeredMemorySystem(mem, twin_id="twin-001", atomizer=MemoryAtomizer(mode="rule"))
        trace = MemoryTrace(
            trace_id="trace-sys-003",
            memory_type=MemoryType.EPISODIC,
            content="The benchmark result shows 95% accuracy on the evaluation dataset.",
            source="twin-001",
        )
        system.store_trace(trace)
        stats = system.get_layer_stats()
        assert stats["twin_id"] == "twin-001"
        assert stats["l0_conversation"] >= 1
        assert stats["l1_atoms"] >= 1

    def test_consolidation_placeholder(self):
        mem = MultiModalMemory()
        system = LayeredMemorySystem(mem, twin_id="twin-001", atomizer=MemoryAtomizer(mode="rule"))
        # Store several traces to have atoms
        for i in range(5):
            trace = MemoryTrace(
                trace_id=f"trace-consol-{i}",
                memory_type=MemoryType.EPISODIC,
                content=f"When debugging code, I use breakpoint strategy {i}.",
                source="twin-001",
            )
            system.store_trace(trace)
        report = system.consolidate()
        assert report.twin_id == "twin-001"
        assert report.atoms_processed >= 5
