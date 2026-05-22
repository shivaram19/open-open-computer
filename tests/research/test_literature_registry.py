# tests/research/test_literature_registry.py
"""Tests for the verified academic literature registry."""

import pytest
from research.literature_registry import (
    PAPERS,
    FICTIONAL_CITATIONS,
    COMPONENT_MAP,
    Paper,
    validate_citation,
    get_paper,
    list_fictional_citations,
    suggest_replacement,
    papers_for_component,
)


class TestLiteratureRegistry:
    """Validation tests for the verified paper registry."""

    def test_all_papers_are_verified_real_publications(self):
        """Every entry in PAPERS must have a real title, authors, and year."""
        assert len(PAPERS) >= 16
        for key, paper in PAPERS.items():
            assert isinstance(paper, Paper)
            assert paper.key == key
            assert len(paper.title) > 10
            assert len(paper.authors) > 5
            assert 1980 <= paper.year <= 2026
            assert paper.venue
            assert paper.url.startswith("http")

    def test_critical_papers_present(self):
        """Core architecture-supporting papers must be in the registry."""
        required = {
            "Besta2024",   # Graph of Thoughts
            "Castro1999",  # PBFT
            "Shinn2023",   # Reflexion
            "Yao2023",     # Tree of Thoughts
            "Guo2024",     # Multi-Agent Survey
            "Kulkarni2014", # Hybrid Logical Clocks
        }
        assert required.issubset(set(PAPERS.keys()))

    def test_validate_citation_accepts_real_papers(self):
        """validate_citation returns True for every real paper key."""
        for key in PAPERS:
            assert validate_citation(key) is True

    def test_validate_citation_rejects_fiction(self):
        """validate_citation returns False for all known fictional keys."""
        for key in FICTIONAL_CITATIONS:
            assert validate_citation(key) is False

    def test_validate_citation_rejects_unknown(self):
        """Unknown keys are rejected."""
        assert validate_citation("TotallyFake2027") is False
        assert validate_citation("") is False

    def test_get_paper_returns_record(self):
        """get_paper returns the Paper dataclass for real keys."""
        paper = get_paper("Besta2024")
        assert paper is not None
        assert "Graph of Thoughts" in paper.title
        assert paper.venue == "AAAI"
        assert paper.year == 2024

    def test_get_paper_returns_none_for_fiction(self):
        """get_paper returns None for fictional keys."""
        assert get_paper("CP-WBFT2025") is None
        assert get_paper("Nonsense") is None

    def test_paper_dataclass_is_frozen(self):
        """Paper records are immutable."""
        paper = get_paper("Castro1999")
        with pytest.raises(AttributeError):
            paper.year = 2000

    def test_list_fictional_citations(self):
        """All fictional keys are enumerable."""
        fiction = list_fictional_citations()
        assert isinstance(fiction, list)
        assert len(fiction) >= 10
        assert "CP-WBFT2025" in fiction
        assert "NSED2026" in fiction
        assert "AGoT2025" in fiction

    def test_suggest_replacement_maps_fiction_to_real(self):
        """Fictional keys map to real replacements where known."""
        assert suggest_replacement("CP-WBFT2025") == "Castro1999"
        assert suggest_replacement("GraphMemory2026") == "Besta2024"
        assert suggest_replacement("Strands2026") == "Yao2023"

    def test_suggest_replacement_none_for_unknown(self):
        """Unknown fictional keys return None."""
        assert suggest_replacement("TotallyFake2027") is None
        assert suggest_replacement("Besta2024") is None  # real key

    def test_component_map_has_valid_keys(self):
        """Every citation in COMPONENT_MAP must exist in PAPERS."""
        for component, keys in COMPONENT_MAP.items():
            assert isinstance(keys, list)
            assert len(keys) > 0
            for key in keys:
                assert key in PAPERS, f"Component '{component}' references unknown key '{key}'"

    def test_papers_for_component(self):
        """papers_for_component returns supporting papers."""
        papers = papers_for_component("compute_substrate")
        assert len(papers) > 0
        keys = {p.key for p in papers}
        assert "Besta2024" in keys

    def test_papers_for_unknown_component(self):
        """Unknown components return an empty list."""
        assert papers_for_component("nonexistent") == []

    def test_peer_reviewed_venues_recognized(self):
        """Papers from top venues are present."""
        venues = {p.venue for p in PAPERS.values()}
        assert "NeurIPS" in venues
        assert "OSDI" in venues
        assert "AAAI" in venues
        assert "IJCAI" in venues
