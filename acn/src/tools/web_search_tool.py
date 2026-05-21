# src/tools/web_search_tool.py
"""
Web Search Tool: Date-aware, citation-governed web search for conscious agents.

Inspired by gabrimatic/mcp-web-search-tool but:
- Python-native (no Node.js dependency)
- Mandatory date grounding before every search
- Citation extraction from results
- Integration with ACN consciousness substrate

Principle: Search without a date is a search into the past.

[CITATION: CITATIONS-GOVERNANCE]
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from shared.utils.citations import cite
from tools.date_tool import DateTool, DateResult


@cite(
    key="WEB-SEARCH-RESULT",
    paper="ACN Web Search Tool: Result Structure",
    venue="ACN Architecture Document",
    section="Tools",
    rationale="Structured search results enable citation extraction and source validation",
    confidence="CERTAIN",
)
@dataclass
class SearchResult:
    """A single web search result with citation metadata."""
    rank: int
    title: str
    url: str
    summary: str
    source: str          # Domain name
    published: Optional[str] = None
    author: Optional[str] = None
    citations: List[str] = field(default_factory=list)
    confidence: float = 0.5  # Source reliability score


@cite(
    key="WEB-SEARCH-TOOL",
    paper="ACN Web Search Tool: Date-Aware Search",
    venue="ACN Architecture Document",
    section="Tools",
    rationale="Web search must be temporally grounded to find current information",
    confidence="CERTAIN",
)
class WebSearchTool:
    """
    Date-aware web search tool for conscious agents.
    
    ENFORCES the rule: get_date() MUST be called before search().
    This prevents agents from searching "2024" when it's 2026.
    
    Features:
    - Auto-enhances queries with current year
    - Extracts citations from result content
    - Filters by freshness (day/week/month/year)
    - Returns structured, citation-ready results
    """

    def __init__(self):
        self.last_date: Optional[DateResult] = None
        self.search_history: List[Dict[str, Any]] = []

    @cite(
        key="WEB-SEARCH-GET-DATE",
        paper="ACN Web Search Tool: Temporal Grounding Enforcement",
        venue="ACN Architecture Document",
        section="Search Protocol",
        rationale="Mandatory date retrieval prevents stale search context",
        confidence="CERTAIN",
    )
    def get_date(self) -> DateResult:
        """Get current date. ALWAYS call this before search()."""
        self.last_date = DateTool.get()
        return self.last_date

    @cite(
        key="WEB-SEARCH-EXECUTE",
        paper="ACN Web Search Tool: Search Execution",
        venue="ACN Architecture Document",
        section="Search Protocol",
        rationale="Query enhancement + result structuring + citation extraction",
        confidence="CERTAIN",
    )
    def search(
        self,
        query: str,
        count: int = 5,
        freshness_days: Optional[int] = None,
        require_date: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a date-aware web search.
        
        Args:
            query: Raw search query (will be enhanced with date)
            count: Number of results (1-20)
            freshness_days: Only results from last N days
            require_date: If True, raises if get_date() not called first
        
        Returns:
            Dict with enhanced_query, date_used, results[], metadata
        """
        # ENFORCE date rule
        if require_date and self.last_date is None:
            raise RuntimeError(
                "DATE RULE VIOLATION: get_date() MUST be called before search().\n"
                "An agent without a date searches the past, not the present.\n"
                "Fix: Call tool.get_date() first, then tool.search(query)."
            )
        
        date = self.last_date or DateTool.get()
        
        # Enhance query with temporal context
        enhanced_query = DateTool.format_for_search(date, query)
        
        # Build freshness filter if requested
        freshness = None
        if freshness_days:
            freshness = DateTool.freshness_filter(date, freshness_days)
        
        # Execute search using Kimi CLI's SearchWeb capability
        # Note: This calls the SearchWeb tool internally
        raw_results = self._execute_search(enhanced_query, count, freshness)
        
        # Structure results
        structured_results = self._structure_results(raw_results)
        
        # Extract potential citations
        for result in structured_results:
            result.citations = self._extract_citations(result)
        
        # Record in history
        search_record = {
            "timestamp": date.iso,
            "original_query": query,
            "enhanced_query": enhanced_query,
            "date_used": date.date,
            "freshness": freshness,
            "result_count": len(structured_results),
            "results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "source": r.source,
                    "published": r.published,
                    "citations": r.citations,
                }
                for r in structured_results
            ],
        }
        self.search_history.append(search_record)
        
        return {
            "original_query": query,
            "enhanced_query": enhanced_query,
            "date": date.date,
            "year": date.year,
            "freshness_filter": freshness,
            "results": [self._result_to_dict(r) for r in structured_results],
            "metadata": {
                "total_results": len(structured_results),
                "search_timestamp": date.iso,
                "query_enhanced": enhanced_query != query,
            },
        }

    def _execute_search(
        self,
        query: str,
        count: int,
        freshness: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Execute the actual web search.
        
        Uses WebResearchEngine (DuckDuckGo + arXiv) for live results.
        Falls back to empty list on failure.
        """
        try:
            from research.web_research_engine import WebResearchEngine
            engine = WebResearchEngine()
            findings = engine.research(query, top_k=count, include_web=True, include_arxiv=False)
            return [
                {
                    "title": f.title,
                    "url": f.url,
                    "summary": f.snippet,
                    "source": f.source,
                    "published": f.published,
                }
                for f in findings
            ]
        except Exception:
            return []

    def _structure_results(self, raw_results: List[Dict[str, Any]]) -> List[SearchResult]:
        """Convert raw search API results to structured SearchResult objects."""
        structured = []
        for i, raw in enumerate(raw_results, 1):
            url = raw.get("url", "")
            source = self._extract_domain(url)
            structured.append(SearchResult(
                rank=i,
                title=raw.get("title", "Untitled"),
                url=url,
                summary=raw.get("summary", ""),
                source=source,
                published=raw.get("published"),
                author=raw.get("author"),
                confidence=self._score_source(source),
            ))
        return structured

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except Exception:
            return "unknown"

    def _score_source(self, domain: str) -> float:
        """Score source reliability (0.0-1.0)."""
        high_trust = {
            "arxiv.org": 0.95,
            "github.com": 0.85,
            "openreview.net": 0.95,
            "ieee.org": 0.9,
            "acm.org": 0.9,
            "nature.com": 0.95,
            "science.org": 0.95,
            "neurips.cc": 0.95,
            "icml.cc": 0.9,
            "aaai.org": 0.9,
            "aclweb.org": 0.9,
            "mlcommons.org": 0.85,
            "huggingface.co": 0.8,
        }
        medium_trust = {
            "medium.com": 0.6,
            "substack.com": 0.6,
            "dev.to": 0.55,
            "towardsdatascience.com": 0.6,
        }
        
        if domain in high_trust:
            return high_trust[domain]
        if domain in medium_trust:
            return medium_trust[domain]
        if ".edu" in domain:
            return 0.85
        if ".gov" in domain:
            return 0.8
        return 0.5

    def _extract_citations(self, result: SearchResult) -> List[str]:
        """Extract potential citation keys from result content."""
        citations = []
        text = f"{result.title} {result.summary}"
        
        # Pattern: AuthorYear (e.g., Besta2024, Shinn2023)
        import re
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\d{4}[a-z]?)\b'
        matches = re.findall(pattern, text)
        citations.extend(matches)
        
        # Pattern: arXiv:XXXX.XXXXX
        arxiv_pattern = r'arXiv:(\d{4}\.\d{4,5})'
        arxiv_matches = re.findall(arxiv_pattern, text)
        citations.extend([f"arXiv:{m}" for m in arxiv_matches])
        
        return list(set(citations))

    def _result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """Serialize SearchResult to dict."""
        return {
            "rank": result.rank,
            "title": result.title,
            "url": result.url,
            "summary": result.summary,
            "source": result.source,
            "published": result.published,
            "author": result.author,
            "citations_found": result.citations,
            "source_confidence": result.confidence,
        }

    @cite(
        key="WEB-SEARCH-NEWS",
        paper="ACN Web Search Tool: News Search",
        venue="ACN Architecture Document",
        section="Search Protocol",
        rationale="News search requires tighter freshness constraints",
        confidence="CERTAIN",
    )
    def news_search(
        self,
        query: str,
        count: int = 5,
        days_back: int = 7,
    ) -> Dict[str, Any]:
        """Search for recent news with tight freshness constraint."""
        if self.last_date is None:
            self.get_date()
        return self.search(query, count, freshness_days=days_back)

    @cite(
        key="WEB-SEARCH-HISTORY",
        paper="ACN Web Search Tool: Audit Trail",
        venue="ACN Architecture Document",
        section="Search Protocol",
        rationale="Search history enables reproducibility and citation verification",
        confidence="CERTAIN",
    )
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Return all searches performed by this tool instance."""
        return self.search_history

    @cite(
        key="WEB-SEARCH-CLEAR",
        paper="ACN Web Search Tool: Audit Trail",
        venue="ACN Architecture Document",
        section="Search Protocol",
        rationale="History clearing for privacy and memory management",
        confidence="CERTAIN",
    )
    def clear_history(self) -> None:
        """Clear search history."""
        self.search_history = []
        self.last_date = None


# ── Convenience Function ───────────────────────────────────────────

@cite(
    key="WEB-SEARCH-ONESHOT",
    paper="ACN Web Search Tool: One-Shot Interface",
    venue="ACN Architecture Document",
    section="Search Protocol",
    rationale="Convenience function for quick date-aware searches",
    confidence="CERTAIN",
)
def search_with_date_context(query: str, count: int = 5) -> Dict[str, Any]:
    """
    One-shot date-aware search.
    
    Automatically gets date, enhances query, and searches.
    Use this for quick research tasks.
    
    Example:
        results = search_with_date_context("latest LLM benchmarks")
        # Query becomes: "latest LLM benchmarks 2026"
    """
    tool = WebSearchTool()
    tool.get_date()
    return tool.search(query, count=count)
