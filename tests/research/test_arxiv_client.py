# tests/research/test_arxiv_client.py
"""Tests for arXiv client."""

import pytest

from research.arxiv_client import ArxivClient, ArxivPaper


class TestArxivClient:
    """Test arXiv API client."""

    def test_search_returns_papers(self):
        client = ArxivClient()
        papers = client.search("multi-agent consensus", max_results=3)
        assert isinstance(papers, list)
        assert len(papers) <= 3
        if papers:
            assert all(isinstance(p, ArxivPaper) for p in papers)
            assert papers[0].arxiv_id
            assert papers[0].title

    def test_paper_structure(self):
        client = ArxivClient()
        papers = client.search("Byzantine fault tolerance", max_results=1)
        if papers:
            p = papers[0]
            assert p.arxiv_id
            assert p.title
            assert p.summary
            assert isinstance(p.authors, list)
            assert p.confidence == 0.95
            assert "arxiv.org/pdf/" in p.pdf_url

    def test_empty_results_for_nonsense(self):
        client = ArxivClient()
        papers = client.search("xyzqwerty12345nonsense", max_results=5)
        assert papers == []

    def test_parse_feed_with_valid_xml(self):
        client = ArxivClient()
        xml = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom"
              xmlns:arxiv="http://arxiv.org/schemas/atom">
            <entry>
                <id>http://arxiv.org/abs/2401.00001</id>
                <title>Test Paper</title>
                <summary>This is a test abstract.</summary>
                <published>2024-01-01T00:00:00Z</published>
                <updated>2024-01-02T00:00:00Z</updated>
                <author><name>John Doe</name></author>
                <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
            </entry>
        </feed>"""
        papers = client._parse_feed(xml)
        assert len(papers) == 1
        assert papers[0].arxiv_id == "2401.00001"
        assert papers[0].title == "Test Paper"
        assert papers[0].authors == ["John Doe"]

    def test_parse_feed_with_bad_xml(self):
        client = ArxivClient()
        papers = client._parse_feed("not xml")
        assert papers == []
