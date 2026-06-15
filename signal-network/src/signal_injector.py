"""Map transcript topics to live signal data and generate overlays."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.signal_data import CensusStub, CommodityPriceFetcher, NewsRssStub


@dataclass
class SignalOverlay:
    topic: str
    overlay_text: str
    source: str
    region: Optional[str] = None


class SignalInjector:
    """Inject live signal data into the pipeline based on detected topics."""

    TOPIC_TO_COMMODITY = {
        "inflation": "salt",
        "salt": "salt",
        "price": "salt",
        "cooking": "salt",
        "food": "onion",
        "agriculture": "rice",
        "farming": "rice",
    }

    def __init__(
        self,
        price_fetcher: Optional[CommodityPriceFetcher] = None,
        census: Optional[CensusStub] = None,
        news: Optional[NewsRssStub] = None,
    ):
        self.price_fetcher = price_fetcher or CommodityPriceFetcher()
        self.census = census or CensusStub()
        self.news = news or NewsRssStub()

    def detect_topics(self, text: str) -> List[str]:
        """Detect signal topics in transcript text."""
        text_lower = text.lower()
        detected = []
        for topic in self.TOPIC_TO_COMMODITY:
            if topic in text_lower:
                detected.append(topic)
        return detected

    def generate_overlay(
        self,
        text: str,
        lang: str,
        region: Optional[str] = None,
    ) -> Optional[SignalOverlay]:
        """Generate a price overlay for the first detected topic."""
        topics = self.detect_topics(text)
        if not topics:
            return None

        topic = topics[0]
        commodity = self.TOPIC_TO_COMMODITY[topic]
        points = self.price_fetcher.fetch(commodity=commodity, region=region)
        if not points:
            points = self.price_fetcher.fetch(commodity=commodity)

        if not points:
            return None

        point = points[0]
        overlay_text = self.price_fetcher.to_overlay(point, lang)
        return SignalOverlay(
            topic=topic,
            overlay_text=overlay_text,
            source="commodity_prices",
            region=region,
        )
