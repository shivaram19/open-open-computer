# tests/memory/test_layered_models.py
"""Tests for layered memory data models."""

import pytest
from memory.layered_models import (
    AtomType,
    MemoryAtom,
    ScenarioPattern,
    PersonaMemory,
    LayeredContext,
    ConsolidationReport,
)


class TestMemoryAtom:
    def test_create_basic(self):
        atom = MemoryAtom.create(
            atom_type=AtomType.CLAIM,
            content="BFT consensus handles Byzantine faults",
            source_trace_id="trace-001",
            twin_id="noah-shinn-001",
            confidence=0.9,
            tags=["consensus", "bft"],
        )
        assert atom.atom_type == AtomType.CLAIM
        assert atom.content == "BFT consensus handles Byzantine faults"
        assert atom.twin_id == "noah-shinn-001"
        assert atom.confidence == 0.9
        assert "consensus" in atom.tags
        assert atom.atom_id.startswith("atom-")

    def test_create_all_types(self):
        for atype in AtomType:
            atom = MemoryAtom.create(
                atom_type=atype,
                content=f"Test {atype.value}",
                source_trace_id="trace-001",
                twin_id="twin-001",
            )
            assert atom.atom_type == atype

    def test_serialization_roundtrip(self):
        atom = MemoryAtom.create(
            atom_type=AtomType.INSIGHT,
            content="Verbal RL works best for discrete tasks",
            source_trace_id="trace-002",
            twin_id="noah-shinn-001",
            confidence=0.85,
            tags=["reflexion", "verbal_rl"],
            metadata={"source_paper": "Shinn2023"},
        )
        data = atom.to_dict()
        restored = MemoryAtom.from_dict(data)
        assert restored.atom_id == atom.atom_id
        assert restored.atom_type == atom.atom_type
        assert restored.content == atom.content
        assert restored.confidence == atom.confidence
        assert restored.metadata == atom.metadata


class TestScenarioPattern:
    def test_create_basic(self):
        pattern = ScenarioPattern.create(
            template="When consensus task, twin emphasizes formal verification",
            twin_id="conor-heins-001",
            context_keywords=["consensus", "safety"],
            behavior_summary="Emphasizes formal verification",
            example_atom_ids=["atom-1", "atom-2"],
            confidence=0.8,
        )
        assert pattern.support_count == 2
        assert pattern.confidence == 0.8
        assert "consensus" in pattern.context_keywords
        assert pattern.pattern_id.startswith("scen-")

    def test_add_support(self):
        pattern = ScenarioPattern.create(
            template="Test pattern",
            twin_id="twin-001",
            context_keywords=["test"],
            behavior_summary="Tests things",
            example_atom_ids=["atom-1"],
        )
        original_count = pattern.support_count
        pattern.add_support("atom-2")
        assert pattern.support_count == original_count + 1
        assert "atom-2" in pattern.example_atom_ids
        # Duplicate add is idempotent
        pattern.add_support("atom-2")
        assert pattern.support_count == original_count + 1

    def test_serialization_roundtrip(self):
        pattern = ScenarioPattern.create(
            template="When debugging, twin uses breakpoint strategy",
            twin_id="noah-shinn-001",
            context_keywords=["debug", "code"],
            behavior_summary="Uses breakpoints and step-through",
            example_atom_ids=["atom-a", "atom-b"],
            confidence=0.75,
        )
        data = pattern.to_dict()
        restored = ScenarioPattern.from_dict(data)
        assert restored.pattern_id == pattern.pattern_id
        assert restored.template == pattern.template
        assert restored.support_count == pattern.support_count


class TestPersonaMemory:
    def test_create_empty(self):
        persona = PersonaMemory.create(twin_id="twin-001")
        assert persona.twin_id == "twin-001"
        assert persona.version == 1
        assert persona.persona_id.startswith("persona-twin-001-")

    def test_create_from_signature(self):
        signature = {
            "heuristics": {"verification": "Trust = proof + test", "abstraction": "Model first"},
            "biases": {"pessimism": "Over-engineers safety"},
        }
        persona = PersonaMemory.create(twin_id="twin-001", base_signature=signature)
        assert "verification" in persona.heuristic_evidence
        assert "abstraction" in persona.heuristic_evidence
        assert "pessimism" in persona.bias_manifestations

    def test_update_from_scenarios(self):
        persona = PersonaMemory.create(twin_id="twin-001")
        scenarios = [
            ScenarioPattern.create(
                template="When code task, high confidence",
                twin_id="twin-001",
                context_keywords=["code", "programming"],
                behavior_summary="Confident in code tasks",
                example_atom_ids=["atom-1"],
                confidence=0.9,
            ),
            ScenarioPattern.create(
                template="When visual task, lower confidence",
                twin_id="twin-001",
                context_keywords=["visual", "image"],
                behavior_summary="Less confident in visual tasks",
                example_atom_ids=["atom-2"],
                confidence=0.5,
            ),
        ]
        persona.update_from_scenarios(scenarios)
        assert persona.version == 2
        assert len(persona.source_scenario_ids) == 2
        assert persona.confidence_map.get("code") > 0.5
        assert persona.confidence_map.get("visual") == 0.5

    def test_serialization_roundtrip(self):
        persona = PersonaMemory.create(twin_id="twin-001")
        persona.confidence_map = {"math": 0.9, "art": 0.3}
        data = persona.to_dict()
        restored = PersonaMemory.from_dict(data)
        assert restored.persona_id == persona.persona_id
        assert restored.confidence_map == {"math": 0.9, "art": 0.3}
        assert restored.version == persona.version


class TestLayeredContext:
    def test_empty_context(self):
        ctx = LayeredContext(query="test query")
        prompt = ctx.to_prompt_string()
        assert "LAYERED MEMORY CONTEXT" in prompt
        assert "test query" in prompt

    def test_with_all_layers(self):
        ctx = LayeredContext(
            query="consensus algorithm",
            l3_persona={
                "twin_id": "conor-heins-001",
                "confidence_map": {"consensus": 0.92, "safety": 0.88},
            },
            l2_scenarios=[
                {"template": "When consensus, prefers BFT", "support_count": 5},
            ],
            l1_atoms=[
                {"atom_type": "insight", "content": "BFT is optimal for small networks"},
                {"atom_type": "claim", "content": "PoS has liveness issues"},
            ],
        )
        prompt = ctx.to_prompt_string()
        assert "conor-heins-001" in prompt
        assert "BFT" in prompt
        assert "BFT is optimal" in prompt

    def test_token_truncation(self):
        # Create many large atoms to exceed token budget
        ctx = LayeredContext(
            query="x",
            l1_atoms=[
                {"atom_type": "claim", "content": "A" * 500}
                for _ in range(20)
            ],
        )
        prompt = ctx.to_prompt_string(max_tokens=50)
        assert len(prompt) < 300  # Should be truncated well before 50 tokens * 4 chars
        assert "[truncated]" in prompt


class TestConsolidationReport:
    def test_basic_report(self):
        report = ConsolidationReport(
            twin_id="twin-001",
            atoms_processed=42,
            scenarios_mined=3,
            persona_updated=True,
            persona_version=5,
        )
        assert report.twin_id == "twin-001"
        assert report.atoms_processed == 42
        assert report.persona_updated is True
