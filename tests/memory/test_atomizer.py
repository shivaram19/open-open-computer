# tests/memory/test_atomizer.py
"""Tests for MemoryAtomizer."""

import pytest
from unittest.mock import MagicMock, patch

from memory.architecture import MemoryTrace, MemoryType
from memory.atomizer import MemoryAtomizer
from memory.layered_models import AtomType, MemoryAtom


class TestMemoryAtomizerRuleMode:
    def test_atomize_string_content(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-001",
            memory_type=MemoryType.EPISODIC,
            content="I realized that BFT consensus is optimal for small networks. "
                    "My initial assumption was wrong — PoS has liveness issues. "
                    "The benchmark result shows 95% accuracy.",
            source="twin-001",
            confidence=0.8,
        )
        atoms = atomizer.atomize(trace)
        assert len(atoms) >= 2
        types = {a.atom_type for a in atoms}
        # Should get some meaningful atom types
        assert len(types) >= 1
        assert any(t in types for t in [
            AtomType.INSIGHT, AtomType.CLAIM, AtomType.OUTCOME,
            AtomType.CORRECTION, AtomType.META_COGNITIVE,
        ])

    def test_atomize_dict_content(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-002",
            memory_type=MemoryType.EPISODIC,
            content={
                "phase_1": "I discovered a new pattern in the data.",
                "phase_2": "The correction was necessary because the model overfit.",
                "confidence": 0.9,
                "recommendation": "Use cross-validation for robust evaluation.",
            },
            source="twin-002",
        )
        atoms = atomizer.atomize(trace)
        assert len(atoms) >= 2
        types = {a.atom_type for a in atoms}
        # Should catch insight, correction, and/or recommendation
        assert len(types) >= 1

    def test_atomize_empty_content(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-003",
            memory_type=MemoryType.EPISODIC,
            content="",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert atoms == []

    def test_atomize_short_content(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-004",
            memory_type=MemoryType.EPISODIC,
            content="OK.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert atoms == []

    def test_meta_cognitive_detection(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-005",
            memory_type=MemoryType.EPISODIC,
            content="I noticed my confidence was too high because I ignored peer critiques.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert any(a.atom_type == AtomType.META_COGNITIVE for a in atoms)

    def test_recommendation_detection(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-006",
            memory_type=MemoryType.EPISODIC,
            content="My recommendation is to start with verbal feedback before fine-tuning.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert any(a.atom_type == AtomType.RECOMMENDATION for a in atoms)

    def test_outcome_detection(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-007",
            memory_type=MemoryType.EPISODIC,
            content="The benchmark passed with 91% accuracy on HumanEval.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert any(a.atom_type == AtomType.OUTCOME for a in atoms)

    def test_correction_detection(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-008",
            memory_type=MemoryType.EPISODIC,
            content="I was wrong about the liveness guarantee. The proof had an edge case.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert any(a.atom_type == AtomType.CORRECTION for a in atoms)

    def test_hypothesis_detection(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-009",
            memory_type=MemoryType.EPISODIC,
            content="It might be that the issue is related to message delays rather than faults.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert any(a.atom_type == AtomType.HYPOTHESIS for a in atoms)

    def test_atoms_have_provenance(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-provenance",
            memory_type=MemoryType.EPISODIC,
            content="BFT handles Byzantine faults effectively.",
            source="conor-heins-001",
        )
        atoms = atomizer.atomize(trace)
        assert len(atoms) >= 1
        for atom in atoms:
            assert atom.source_trace_id == "trace-provenance"
            assert atom.twin_id == "conor-heins-001"
            assert atom.atom_id.startswith("atom-")

    def test_extract_text_from_dict(self):
        atomizer = MemoryAtomizer(mode="rule")
        trace = MemoryTrace(
            trace_id="trace-dict",
            memory_type=MemoryType.EPISODIC,
            content={
                "phase_1": "Initial analysis complete.",
                "self_critique": "The approach has a flaw in edge cases.",
                "proposed_approach": "Use formal verification.",
            },
            source="twin-001",
        )
        text = MemoryAtomizer._extract_text(trace)
        assert "Initial analysis" in text
        assert "flaw" in text
        assert "formal verification" in text


class TestMemoryAtomizerLLMMode:
    def test_llm_mode_with_mock(self):
        atomizer = MemoryAtomizer(mode="llm", api_key="fake-key")
        trace = MemoryTrace(
            trace_id="trace-llm",
            memory_type=MemoryType.EPISODIC,
            content="This is a reasoning trace about consensus mechanisms.",
            source="twin-001",
        )

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "atoms": [
                {
                    "atom_type": "claim",
                    "content": "BFT is better for small networks",
                    "confidence": 0.9,
                    "tags": ["consensus", "bft"],
                },
                {
                    "atom_type": "insight",
                    "content": "PoS has liveness tradeoffs",
                    "confidence": 0.8,
                    "tags": ["pos", "liveness"],
                },
            ]
        })

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        atomizer._client = mock_client

        atoms = atomizer.atomize(trace)
        assert len(atoms) == 2
        assert atoms[0].atom_type == AtomType.CLAIM
        assert atoms[1].atom_type == AtomType.INSIGHT
        assert atoms[0].source_trace_id == "trace-llm"

    def test_llm_mode_fallback_on_error(self):
        atomizer = MemoryAtomizer(mode="auto", api_key="fake-key")
        trace = MemoryTrace(
            trace_id="trace-fallback",
            memory_type=MemoryType.EPISODIC,
            content="The result was a 95% pass rate on the benchmark.",
            source="twin-001",
        )

        # Force LLM to fail, should fall back to rule mode
        atomizer._client = None
        with patch.object(atomizer, '_atomize_llm', side_effect=Exception("API down")):
            atoms = atomizer.atomize(trace)

        # Should still get atoms from rule-based fallback
        assert len(atoms) >= 1
        assert any(a.atom_type == AtomType.OUTCOME for a in atoms)

    def test_auto_mode_uses_rule_when_no_api_key(self):
        atomizer = MemoryAtomizer(mode="auto", api_key=None)
        # Force no API key regardless of environment
        atomizer._api_key = None
        trace = MemoryTrace(
            trace_id="trace-auto",
            memory_type=MemoryType.EPISODIC,
            content="I discovered that caching improves performance by 40%.",
            source="twin-001",
        )
        atoms = atomizer.atomize(trace)
        assert len(atoms) >= 1
        # "discovered" triggers insight, but "performance" triggers outcome first
        assert any(a.atom_type in (AtomType.INSIGHT, AtomType.OUTCOME) for a in atoms)


import os
import json
