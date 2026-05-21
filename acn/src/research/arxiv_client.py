# src/research/arxiv_client.py
"""
arXiv Client: Fetch academic papers for research-grounded deliberation.

Uses arXiv API (export.arxiv.org/api/query) — no API key required.
Returns structured paper metadata with abstracts, authors, and arXiv IDs.

Principle: Ground consensus in peer-reviewed literature, not just agent opinion.

[CITATION: arXivAPI]
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from urllib.parse import quote

import requests

from shared.utils.citations import cite


@dataclass
class ArxivPaper:
    """A paper from arXiv with metadata."""
    arxiv_id: str
    title: str
    summary: str
    authors: List[str] = field(default_factory=list)
    published: str = ""
    updated: str = ""
    primary_category: str = ""
    categories: List[str] = field(default_factory=list)
    pdf_url: str = ""
    confidence: float = 0.95  # arXiv is high-trust


@cite(
    key="ARXIV-CLIENT",
    paper="arXiv API Client for ACN Research",
    venue="ACN Research Architecture",
    section="External Knowledge",
    rationale="Free, open access to 2M+ CS papers for agent deliberation",
    confidence="HIGH",
)
class ArxivClient:
    """
    Client for arXiv API — no API key required.

    Usage:
        client = ArxivClient()
        papers = client.search("multi-agent consensus", max_results=5)
        for p in papers:
            print(f"{p.arxiv_id}: {p.title}")
    """

    API_URL = "http://export.arxiv.org/api/query"
    NS = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(
        self,
        query: str,
        max_results: int = 5,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> List[ArxivPaper]:
        """
        Search arXiv for papers matching query.

        Args:
            query: Search terms (e.g., "Byzantine fault tolerance multi-agent")
            max_results: Number of results (1-50)
            sort_by: "relevance" | "lastUpdatedDate" | "submittedDate"
            sort_order: "ascending" | "descending"

        Returns:
            List of ArxivPaper objects
        """
        params = {
            "search_query": f"all:{quote(query)}",
            "start": 0,
            "max_results": min(max_results, 50),
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        try:
            resp = requests.get(self.API_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            return []

        return self._parse_feed(resp.text)

    def _parse_feed(self, xml_text: str) -> List[ArxivPaper]:
        """Parse arXiv Atom feed XML into ArxivPaper objects."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        papers = []
        for entry in root.findall("atom:entry", self.NS):
            paper = self._parse_entry(entry)
            if paper:
                papers.append(paper)
        return papers

    def _parse_entry(self, entry: ET.Element) -> Optional[ArxivPaper]:
        """Parse a single Atom entry."""
        id_elem = entry.find("atom:id", self.NS)
        if id_elem is None or id_elem.text is None:
            return None

        arxiv_id = id_elem.text.split("/")[-1]
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.split("v")[0]

        title = self._get_text(entry, "atom:title") or "Untitled"
        summary = self._get_text(entry, "atom:summary") or ""
        published = self._get_text(entry, "atom:published") or ""
        updated = self._get_text(entry, "atom:updated") or ""

        authors = []
        for author in entry.findall("atom:author", self.NS):
            name = author.find("atom:name", self.NS)
            if name is not None and name.text:
                authors.append(name.text)

        categories = []
        primary = ""
        for cat in entry.findall("atom:category", self.NS):
            term = cat.get("term", "")
            if term:
                categories.append(term)
            if cat.get("scheme") == "http://arxiv.org/schemas/atom":
                primary = term

        # PDF link
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        return ArxivPaper(
            arxiv_id=arxiv_id,
            title=title.strip(),
            summary=summary.strip(),
            authors=authors,
            published=published,
            updated=updated,
            primary_category=primary or (categories[0] if categories else ""),
            categories=categories,
            pdf_url=pdf_url,
        )

    def _get_text(self, elem: ET.Element, path: str) -> Optional[str]:
        child = elem.find(path, self.NS)
        return child.text if child is not None else None
