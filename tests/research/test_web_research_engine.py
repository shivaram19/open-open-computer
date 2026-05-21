# tests/research/test_web_research_engine.py
"""Tests for WebResearchEngine."""

import pytest

from research.web_research_engine import WebResearchEngine, ResearchFinding
from research.arxiv_client import ArxivClient


class TestWebResearchEngine:
    """Test unified research engine."""

    def test_research_returns_findings(self):
        engine = WebResearchEngine()
        findings = engine.research("multi-agent systems", top_k=3)
        assert isinstance(findings, list)
        assert len(findings) <= 3

    def test_research_caches_results(self):
        engine = WebResearchEngine()
        f1 = engine.research("cache test query", top_k=2)
        f2 = engine.research("cache test query", top_k=2)
        assert f1 == f2  # Same object from cache

    def test_clear_cache(self):
        engine = WebResearchEngine()
        engine.research("test", top_k=1)
        assert len(engine._cache) > 0
        engine.clear_cache()
        assert len(engine._cache) == 0

    def test_mock_backend(self):
        """Test with mock backend for determinism."""
        def mock_backend(query, count):
            return [
                {"title": f"Result {i}", "url": f"http://example.com/{i}",
                 "snippet": f"Snippet {i}", "source": "example.com"}
                for i in range(count)
            ]

        engine = WebResearchEngine(web_search_backend=mock_backend)
        findings = engine.research("test", top_k=4, include_arxiv=False, include_web=True)
        assert len(findings) == 3  # mock returns count=3 (top_k//2+1=3)
        assert findings[0].title == "Result 0"
        assert findings[0].source_type == "web"

    def test_source_scoring(self):
        engine = WebResearchEngine()
        assert engine._score_source("arxiv.org") > 0.9
        assert engine._score_source("unknown.blog") == 0.5
        assert engine._score_source("mit.edu") > 0.8

    def test_classify_source(self):
        engine = WebResearchEngine()
        assert engine._classify_source("arxiv.org") == "arxiv"
        assert engine._classify_source("github.com") == "github"
        assert engine._classify_source("ieee.org") == "academic"
        assert engine._classify_source("example.com") == "web"
