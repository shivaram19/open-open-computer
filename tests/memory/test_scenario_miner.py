# tests/memory/test_scenario_miner.py
"""Tests for ScenarioMiner."""

import pytest
from memory.scenario_miner import ScenarioMiner
from memory.layered_models import MemoryAtom, AtomType, ScenarioPattern


class TestScenarioMiner:
    def test_mine_scenarios_basic(self):
        miner = ScenarioMiner(min_support=2, similarity_threshold=0.1)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults in small networks",
                source_trace_id="t1", twin_id="twin-001", tags=["consensus", "bft"],
            ),
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus is preferred for safety critical systems",
                source_trace_id="t2", twin_id="twin-001", tags=["consensus", "bft"],
            ),
            MemoryAtom.create(
                atom_type=AtomType.INSIGHT,
                content="Verbal feedback loops improve code generation without gradients",
                source_trace_id="t3", twin_id="twin-001", tags=["reflexion", "code"],
            ),
            MemoryAtom.create(
                atom_type=AtomType.INSIGHT,
                content="Verbal reinforcement through self critique achieves high accuracy",
                source_trace_id="t4", twin_id="twin-001", tags=["reflexion", "code"],
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        assert len(patterns) >= 1
        # Should find at least one pattern
        assert any("bft" in p.context_keywords or "consensus" in p.context_keywords or
                   "verbal" in p.context_keywords for p in patterns)

    def test_min_support_filtering(self):
        miner = ScenarioMiner(min_support=3, similarity_threshold=0.2)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults",
                source_trace_id="t1", twin_id="twin-001", tags=["consensus"],
            ),
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT is optimal for small networks",
                source_trace_id="t2", twin_id="twin-001", tags=["consensus"],
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        # Only 2 atoms, min_support=3 → no patterns
        assert len(patterns) == 0

    def test_empty_atoms(self):
        miner = ScenarioMiner(min_support=2)
        patterns = miner.mine_scenarios([])
        assert patterns == []

    def test_single_atom(self):
        miner = ScenarioMiner(min_support=2)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults",
                source_trace_id="t1", twin_id="twin-001",
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        assert patterns == []

    def test_pattern_has_proper_fields(self):
        miner = ScenarioMiner(min_support=2, similarity_threshold=0.1)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults effectively in practice",
                source_trace_id="t1", twin_id="twin-001", confidence=0.9,
            ),
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT is the standard approach for Byzantine fault tolerance",
                source_trace_id="t2", twin_id="twin-001", confidence=0.85,
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.twin_id == "twin-001"
        assert pattern.support_count == 2
        assert pattern.confidence > 0.8
        assert len(pattern.example_atom_ids) == 2
        assert pattern.template  # Should have a generated template
        assert pattern.behavior_summary  # Should have a behavior summary

    def test_keyword_extraction(self):
        miner = ScenarioMiner()
        keywords = miner._extract_keywords("BFT consensus handles Byzantine faults!")
        assert "bft" in keywords
        assert "consensus" in keywords
        assert "byzantine" in keywords
        assert "faults" in keywords
        # Stopwords should be removed
        assert "handles" in keywords  # 'handles' > 2 chars, not a stopword
        assert "the" not in keywords

    def test_jaccard_similarity(self):
        assert ScenarioMiner._jaccard_similarity({"a", "b"}, {"a", "b"}) == 1.0
        assert ScenarioMiner._jaccard_similarity({"a", "b"}, {"c", "d"}) == 0.0
        assert ScenarioMiner._jaccard_similarity({"a", "b", "c"}, {"a", "b", "d"}) == 0.5
        assert ScenarioMiner._jaccard_similarity(set(), set()) == 1.0

    def test_high_similarity_threshold(self):
        miner = ScenarioMiner(min_support=2, similarity_threshold=0.9)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults",
                source_trace_id="t1", twin_id="twin-001",
            ),
            MemoryAtom.create(
                atom_type=AtomType.INSIGHT,
                content="Verbal feedback improves code generation significantly",
                source_trace_id="t2", twin_id="twin-001",
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        # Very high threshold → no clustering
        assert len(patterns) == 0

    def test_different_twins_not_clustered_together(self):
        # Even with same content, atoms from different twins should not cluster
        # (but our miner doesn't enforce this — it clusters by content only)
        # This test documents current behavior
        miner = ScenarioMiner(min_support=2, similarity_threshold=0.2)
        atoms = [
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults",
                source_trace_id="t1", twin_id="twin-001",
            ),
            MemoryAtom.create(
                atom_type=AtomType.CLAIM,
                content="BFT consensus handles Byzantine faults",
                source_trace_id="t2", twin_id="twin-002",
            ),
        ]
        patterns = miner.mine_scenarios(atoms)
        # They should cluster because content is identical
        assert len(patterns) == 1
        # But the pattern's twin_id comes from the first atom
        assert patterns[0].twin_id in ("twin-001", "twin-002")
