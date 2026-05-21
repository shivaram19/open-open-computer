# src/tools/__init__.py
"""
ACN Tool Registry: Date-aware, citation-governed tools for conscious agents.

Principle: Every search must know WHEN it is searching.
Without a date, an agent searches the past instead of the present.

[CITATION: CITATIONS-GOVERNANCE]
"""

from tools.date_tool import DateTool, get_current_date
from tools.web_search_tool import WebSearchTool, search_with_date_context

__all__ = [
    "DateTool",
    "get_current_date",
    "WebSearchTool",
    "search_with_date_context",
]
