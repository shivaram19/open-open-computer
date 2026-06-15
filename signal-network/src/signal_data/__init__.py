"""Signal data sources for embedded data overlays."""

from src.signal_data.commodity_prices import CommodityPriceFetcher
from src.signal_data.census import CensusStub
from src.signal_data.news_rss import NewsRssStub

__all__ = ["CommodityPriceFetcher", "CensusStub", "NewsRssStub"]
