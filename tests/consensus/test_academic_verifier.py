# tests/consensus/test_academic_verifier.py
"""Tests for academic consensus verifier."""

import pytest

from consensus.academic_verifier import AcademicVerifier, AcademicVerificationResult
from research.web_research_engine import ResearchFinding


class MockResearchEngine:
    """Mock engine that returns predictable findings."""

    def __init__(self, findings):
        self._findings = findings

    def research(self, query, top_k=5, include_arxiv=True, include_web=True):
        return self._findings[:top_k]


class TestAcademicVerifier:
    """Test academic verification of consensus."""

    def test_no_literature_neutral(self):
        verifier = AcademicVerifier(MockResearchEngine([]))
        result = verifier.verify("Use BFT consensus", consensus_score=0.8)
        assert result.academic_support == 0.0
        assert result.dissent_detected is False
        assert "No relevant academic literature" in result.dissent_reasoning

    def test_strong_support_boosts_confidence(self):
        findings = [
            ResearchFinding("Paper A", "arxiv.org", "http://a", "Supports BFT", "arxiv", confidence=0.95),
            ResearchFinding("Paper B", "arxiv.org", "http://b", "BFT is great", "arxiv", confidence=0.95),
        ]
        verifier = AcademicVerifier(MockResearchEngine(findings))
        result = verifier.verify("Use BFT consensus", consensus_score=0.8)
        assert result.academic_support > 0.8
        assert result.dissent_detected is False
        assert "VERIFIED" in result.recommendation

    def test_dissent_when_high_consensus_low_support(self):
        findings = [
            ResearchFinding("Paper X", "arxiv.org", "http://x", "BFT has issues", "arxiv", confidence=0.3),
        ]
        verifier = AcademicVerifier(MockResearchEngine(findings))
        result = verifier.verify("Use BFT consensus", consensus_score=0.9)
        assert result.dissent_detected is True
        assert "DISSENT FLAG" in result.recommendation

    def test_moderate_support_no_dissent(self):
        findings = [
            ResearchFinding("Paper M", "arxiv.org", "http://m", "Okay approach", "arxiv", confidence=0.7),
        ]
        verifier = AcademicVerifier(MockResearchEngine(findings))
        result = verifier.verify("Use BFT consensus", consensus_score=0.7)
        assert result.dissent_detected is False
        assert "Proceed" in result.recommendation

    def test_top_papers_returned(self):
        findings = [
            ResearchFinding(f"Paper {i}", "arxiv.org", f"http://{i}", "Summary", "arxiv", confidence=0.9)
            for i in range(5)
        ]
        verifier = AcademicVerifier(MockResearchEngine(findings))
        result = verifier.verify("Test", consensus_score=0.8)
        assert result.papers_found == 5
        assert len(result.top_papers) == 3
        assert result.top_papers[0]["title"] == "Paper 0"
