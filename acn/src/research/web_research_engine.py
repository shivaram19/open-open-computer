# src/research/web_research_engine.py
"""
Web Research Engine: Unified research interface for ACN twins.

Combines:
- Web search (DuckDuckGo scraping — no API key)
- arXiv paper search (free API)
- Source reliability scoring
- Citation extraction
- Result caching per session

Principle: A twin that cannot research is a twin that cannot learn.

[CITATION: TencentDB2026]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import quote

import requests

from shared.utils.citations import cite
from research.arxiv_client import ArxivClient, ArxivPaper


@dataclass
class ResearchFinding:
    """A single research finding with source and relevance."""
    title: str
    source: str
    url: str
    snippet: str
    source_type: str  # "web" | "arxiv" | "github" | "other"
    confidence: float = 0.5
    published: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)


@cite(
    key="WEB-RESEARCH-ENGINE",
    paper="TencentDB Agent Memory: Research-Augmented Agents",
    venue="ACN Research Architecture",
    section="External Knowledge",
    rationale="Unified research interface combining web search and academic sources",
    confidence="HIGH",
)
class WebResearchEngine:
    """
    Unified research engine for ACN twins.

    Usage:
        engine = WebResearchEngine()
        findings = engine.research("Byzantine fault tolerance multi-agent", top_k=5)
        for f in findings:
            print(f"{f.source}: {f.title}")
    """

    def __init__(
        self,
        arxiv_client: Optional[ArxivClient] = None,
        web_search_backend: Optional[Callable[[str, int], List[Dict[str, Any]]]] = None,
    ):
        self.arxiv = arxiv_client or ArxivClient()
        self.web_search_backend = web_search_backend or self._duckduckgo_search
        self._cache: Dict[str, List[ResearchFinding]] = {}
        self._cache_ttl_seconds = 300  # 5 min cache
        self._cache_timestamp: Dict[str, float] = {}

    def research(
        self,
        query: str,
        top_k: int = 5,
        include_arxiv: bool = True,
        include_web: bool = True,
    ) -> List[ResearchFinding]:
        """
        Research a query across web and arXiv sources.

        Results are cached per query for the session.
        """
        cache_key = f"{query}:{top_k}:{include_arxiv}:{include_web}"
        now = time.time()

        # Check cache
        if cache_key in self._cache:
            cached_at = self._cache_timestamp.get(cache_key, 0)
            if now - cached_at < self._cache_ttl_seconds:
                return self._cache[cache_key]

        findings: List[ResearchFinding] = []

        if include_arxiv:
            findings.extend(self._search_arxiv(query, top_k=top_k // 2 + 1))

        if include_web:
            findings.extend(self._search_web(query, top_k=top_k // 2 + 1))

        # Deduplicate by URL
        seen = set()
        deduped = []
        for f in findings:
            if f.url not in seen:
                seen.add(f.url)
                deduped.append(f)

        # Sort by confidence
        deduped.sort(key=lambda x: x.confidence, reverse=True)
        result = deduped[:top_k]

        # Cache
        self._cache[cache_key] = result
        self._cache_timestamp[cache_key] = now

        return result

    def _search_arxiv(self, query: str, top_k: int) -> List[ResearchFinding]:
        """Search arXiv and convert to ResearchFinding."""
        papers = self.arxiv.search(query, max_results=top_k)
        return [
            ResearchFinding(
                title=p.title,
                source="arxiv.org",
                url=f"https://arxiv.org/abs/{p.arxiv_id}",
                snippet=p.summary[:500] + "..." if len(p.summary) > 500 else p.summary,
                source_type="arxiv",
                confidence=p.confidence,
                published=p.published,
                authors=p.authors,
                citations=[p.arxiv_id],
            )
            for p in papers
        ]

    def _search_web(self, query: str, top_k: int) -> List[ResearchFinding]:
        """Search web via configured backend."""
        raw = self.web_search_backend(query, top_k)
        findings = []
        for item in raw:
            source = item.get("source", "unknown")
            findings.append(ResearchFinding(
                title=item.get("title", "Untitled"),
                source=source,
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                source_type=self._classify_source(source),
                confidence=self._score_source(source),
                published=item.get("published"),
            ))
        return findings

    def _duckduckgo_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo HTML API (no API key required).
        Falls back to empty list on failure.
        """
        try:
            url = "https://html.duckduckgo.com/html/"
            resp = requests.post(
                url,
                data={"q": query, "kl": "us-en"},
                headers={"User-Agent": "ACN-ResearchBot/1.0"},
                timeout=10,
            )
            resp.raise_for_status()
            return self._parse_duckduckgo_html(resp.text, top_k)
        except Exception:
            return []

    def _parse_duckduckgo_html(self, html: str, top_k: int) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results."""
        from html.parser import HTMLParser

        results = []
        class ResultExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_result = False
                self.in_title = False
                self.in_snippet = False
                self.current = {}
                self.results = []
                self.link_href = None
                self.tag_stack = []

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                self.tag_stack.append(tag)

                if tag == "div" and attrs_dict.get("class", "").startswith("result"):
                    self.in_result = True
                    self.current = {}
                elif tag == "a" and self.in_result and "result__a" in attrs_dict.get("class", ""):
                    self.link_href = attrs_dict.get("href", "")
                    self.in_title = True
                elif tag == "a" and self.in_result and self.link_href is None:
                    self.link_href = attrs_dict.get("href", "")

            def handle_endtag(self, tag):
                if self.tag_stack:
                    self.tag_stack.pop()
                if tag == "div" and self.in_result:
                    if self.current.get("title") and self.current.get("url"):
                        self.results.append(self.current)
                    self.in_result = False
                    self.current = {}
                    self.link_href = None
                elif tag == "a" and self.in_title:
                    self.in_title = False

            def handle_data(self, data):
                if self.in_title and self.link_href:
                    self.current["title"] = self.current.get("title", "") + data.strip()
                    self.current["url"] = self.link_href
                elif self.in_result and not self.in_title:
                    # Collect snippet text
                    text = data.strip()
                    if text and len(text) > 20:
                        self.current["snippet"] = self.current.get("snippet", "") + " " + text

        parser = ResultExtractor()
        try:
            parser.feed(html)
        except Exception:
            pass

        for r in parser.results[:top_k]:
            results.append({
                "title": r.get("title", "Untitled"),
                "url": r.get("url", ""),
                "snippet": r.get("snippet", "").strip()[:300],
                "source": self._extract_domain(r.get("url", "")),
            })

        return results

    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "unknown"

    def _classify_source(self, domain: str) -> str:
        if "arxiv" in domain:
            return "arxiv"
        if "github" in domain:
            return "github"
        if any(x in domain for x in ["ieee", "acm", "nature", "science", "neurips", "openreview"]):
            return "academic"
        return "web"

    def _score_source(self, domain: str) -> float:
        high = {
            "arxiv.org": 0.95, "openreview.net": 0.95, "github.com": 0.85,
            "ieee.org": 0.9, "acm.org": 0.9, "nature.com": 0.95,
            "science.org": 0.95, "neurips.cc": 0.95, "icml.cc": 0.9,
        }
        if domain in high:
            return high[domain]
        if ".edu" in domain:
            return 0.85
        if ".gov" in domain:
            return 0.8
        return 0.5

    def clear_cache(self) -> None:
        """Clear research cache."""
        self._cache.clear()
        self._cache_timestamp.clear()
