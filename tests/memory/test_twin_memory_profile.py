# tests/memory/test_twin_memory_profile.py
"""Tests for TwinMemoryProfile."""

import pytest
from memory.twin_memory_profile import TwinMemoryProfile
from memory.layered_models import AtomType


class TestTwinMemoryProfile:
    def test_record_think(self):
        profile = TwinMemoryProfile(
            twin_id="noah-shinn-001",
            base_signature={"name": "Noah Shinn", "cluster": "streaming-reflection"},
        )
        reasoning = {
            "twin_id": "noah-shinn-001",
            "task": "Should we use BFT?",
            "confidence": 0.85,
            "phase_1_initial_attempt": "Try BFT first.",
            "phase_2_self_critique": "Consider edge cases.",
            "timestamp": 1234567890,
        }
        result = profile.record_think(reasoning)
        assert result["atoms_created"] >= 1
        assert "trace_id" in result

    def test_record_critique(self):
        profile = TwinMemoryProfile(
            twin_id="conor-heins-001",
            base_signature={"name": "Conor Heins", "cluster": "consensus-safety"},
        )
        result = profile.record_critique(
            critique="Your confidence is too high without formal proof.",
            source_peer="noah-shinn-001",
        )
        assert result["atoms_created"] >= 1

    def test_get_reasoning_context(self):
        profile = TwinMemoryProfile(twin_id="twin-001")
        reasoning = {
            "task": "consensus algorithm selection",
            "confidence": 0.8,
            "phase_1": "BFT is optimal for small networks",
            "timestamp": 1234567890,
        }
        profile.record_think(reasoning)
        context = profile.get_reasoning_context("consensus")
        assert "LAYERED MEMORY CONTEXT" in context
        assert "consensus" in context

    def test_get_layered_context(self):
        profile = TwinMemoryProfile(twin_id="twin-001")
        reasoning = {
            "task": "debugging strategy",
            "confidence": 0.9,
            "phase_1": "Use breakpoints for debugging.",
            "timestamp": 1234567890,
        }
        profile.record_think(reasoning)
        ctx = profile.get_layered_context("debugging")
        assert ctx.query == "debugging"
        assert len(ctx.l0_traces) >= 1
        assert len(ctx.l1_atoms) >= 1

    def test_consolidation(self):
        profile = TwinMemoryProfile(twin_id="twin-001")
        # Record several similar traces to form a cluster
        for i in range(5):
            profile.record_think({
                "task": f"consensus task {i}",
                "confidence": 0.8,
                "phase_1": "BFT consensus handles Byzantine faults effectively in practice.",
                "timestamp": 1234567890 + i,
            })
        report = profile.consolidate()
        assert report.twin_id == "twin-001"
        assert report.atoms_processed >= 5
        # With 5 similar atoms, should mine at least 1 scenario
        assert report.scenarios_mined >= 1
        assert report.persona_updated is True
        assert report.persona_version >= 2

    def test_get_stats(self):
        profile = TwinMemoryProfile(
            twin_id="twin-001",
            base_signature={"name": "Test Twin", "cluster": "test"},
        )
        profile.record_think({
            "task": "test",
            "confidence": 0.7,
            "phase_1": "The benchmark passed with 95 percent accuracy.",
            "timestamp": 1234567890,
        })
        stats = profile.get_stats()
        assert stats["twin_id"] == "twin-001"
        assert stats["twin_name"] == "Test Twin"
        assert stats["cluster"] == "test"
        assert stats["l0_conversation"] >= 1
        assert stats["l1_atoms"] >= 1
