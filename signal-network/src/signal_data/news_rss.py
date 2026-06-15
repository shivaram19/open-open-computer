"""Stub for regional news RSS aggregation."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NewsItem:
    title: str
    source: str
    summary: str
    language: str


class NewsRssStub:
    """Stub news RSS fetcher.

    In production, point to regional newspaper RSS feeds and summarize with an LLM.
    """

    def fetch(self, topic: str, language: str = "te", max_items: int = 3) -> List[NewsItem]:
        """Return stub news items for a topic/language."""
        items = {
            "te": [
                NewsItem(
                    title="ఉప్పు ధరలు పెరిగాయి",
                    source="eenadu",
                    summary="రాష్ట్రంలో ఉప్పు ధరలు గత నెలతో పోలిస్తే 12% పెరిగాయి.",
                    language="te",
                ),
            ],
            "mr": [
                NewsItem(
                    title="मीठाचे दर वाढले",
                    source="lokmat",
                    summary="राज्यात मीठाचे दर गेल्या महिन्याच्या तुलनेत 10% वाढले.",
                    language="mr",
                ),
            ],
        }
        return items.get(language, [])[:max_items]

    def summarize(self, items: List[NewsItem]) -> str:
        """Stub summarizer."""
        if not items:
            return ""
        return " ".join(item.summary for item in items)
