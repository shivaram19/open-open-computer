# src/tools/date_tool.py
"""
Date Tool: Grounds every search in real-time.

Without knowing today's date, an agent might search for "AI benchmarks 2024"
when it's 2026. This tool is MANDATORY before any web search.

[CITATION: CITATIONS-GOVERNANCE]
"""

import time
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime, timezone

from shared.utils.citations import cite


@cite(
    key="DATE-TOOL",
    paper="ACN Tool System: Temporal Grounding for Agent Research",
    venue="ACN Architecture Document",
    section="Tools",
    rationale="Agents must know the present date to search for current information",
    confidence="CERTAIN",
)
@dataclass
class DateResult:
    """Structured date result for agent consumption."""
    iso: str           # 2026-05-07T14:24:03+00:00
    date: str          # 2026-05-07
    year: int          # 2026
    month: int         # 5
    day: int           # 7
    weekday: str       # Thursday
    time: str          # 14:24:03
    timezone: str      # UTC
    epoch_ms: int      # 1746627843000


@cite(
    key="DATE-GET",
    paper="ACN Tool System: Temporal Grounding",
    venue="ACN Architecture Document",
    section="Date Tool",
    rationale="System clock provides ground truth for temporal orientation",
    confidence="CERTAIN",
)
class DateTool:
    """
    Mandatory date retrieval for all research operations.
    
    Usage:
        date = DateTool.get()
        search_query = f"latest AI breakthroughs {date.year}"
    """

    @cite(
        key="DATE-GET",
        paper="ACN Tool System: Temporal Grounding",
        venue="ACN Architecture Document",
        section="Date Tool",
        rationale="System clock provides ground truth for temporal orientation",
        confidence="CERTAIN",
    )
    @staticmethod
    def get() -> DateResult:
        """Get current date and time from system clock."""
        now = datetime.now(timezone.utc)
        return DateResult(
            iso=now.isoformat(),
            date=now.strftime("%Y-%m-%d"),
            year=now.year,
            month=now.month,
            day=now.day,
            weekday=now.strftime("%A"),
            time=now.strftime("%H:%M:%S"),
            timezone="UTC",
            epoch_ms=int(now.timestamp() * 1000),
        )

    @cite(
        key="DATE-FORMAT",
        paper="ACN Tool System: Query Enhancement",
        venue="ACN Architecture Document",
        section="Date Tool",
        rationale="Temporal context in queries prevents stale search results",
        confidence="CERTAIN",
    )
    @staticmethod
    def format_for_search(date: DateResult, query: str) -> str:
        """
        Enhance a search query with temporal context.
        
        Transforms:
            "latest LLM benchmarks" → "latest LLM benchmarks 2026"
            "new AI frameworks" → "new AI frameworks 2026 2025"
        """
        # Add current year if not already present
        year_str = str(date.year)
        prev_year = str(date.year - 1)
        
        enhanced = query.strip()
        
        # Don't duplicate year if already in query
        if year_str not in enhanced and prev_year not in enhanced:
            # For "latest", "new", "recent" queries, add current year
            temporal_keywords = ["latest", "new", "recent", "cutting-edge", "state-of-the-art", "sota"]
            if any(kw in enhanced.lower() for kw in temporal_keywords):
                enhanced = f"{enhanced} {year_str}"
            else:
                # For general queries, add year range
                enhanced = f"{enhanced} {prev_year} {year_str}"
        
        return enhanced

    @cite(
        key="DATE-FRESHNESS",
        paper="ACN Tool System: Freshness Filtering",
        venue="ACN Architecture Document",
        section="Date Tool",
        rationale="Date-range filters ensure recent results in search APIs",
        confidence="CERTAIN",
    )
    @staticmethod
    def freshness_filter(date: DateResult, days_back: int = 30) -> str:
        """
        Generate a freshness filter for search APIs.
        
        Brave Search format: YYYY-MM-DDtoYYYY-MM-DD
        """
        from datetime import timedelta
        end = date.date
        start = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
        return f"{start}to{end}"


@cite(
    key="DATE-CONVENIENCE",
    paper="ACN Tool System: Temporal Grounding",
    venue="ACN Architecture Document",
    section="Date Tool",
    rationale="Convenience wrapper for direct date access",
    confidence="CERTAIN",
)
def get_current_date() -> DateResult:
    """Get current date. Always call this before searching."""
    return DateTool.get()
