"""Tests for signal data modules."""

import sys
from pathlib import Path

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.signal_data import CensusStub, CommodityPriceFetcher, NewsRssStub
from src.signal_injector import SignalInjector


def test_fetcher_reads_csv():
    fetcher = CommodityPriceFetcher()
    points = fetcher.fetch(commodity="salt", region="telangana")
    assert len(points) == 1
    assert points[0].price == 45.0
    assert points[0].change_percent == 12.0


def test_fetcher_fallback_when_no_csv(tmp_path):
    fetcher = CommodityPriceFetcher(csv_path=tmp_path / "missing.csv")
    points = fetcher.fetch(commodity="salt")
    assert len(points) >= 1


def test_overlay_formatting():
    fetcher = CommodityPriceFetcher()
    points = fetcher.fetch(commodity="salt", region="telangana")
    overlay = fetcher.to_overlay(points[0], "te")
    assert "ధర" in overlay
    assert "₹45" in overlay


def test_census_stub():
    census = CensusStub()
    district = census.get_district("hyderabad")
    assert district is not None
    assert district.primary_language == "te"


def test_news_rss_stub():
    news = NewsRssStub()
    items = news.fetch(topic="inflation", language="te")
    assert len(items) > 0
    assert items[0].language == "te"


def test_signal_injector_detects_topics():
    injector = SignalInjector()
    topics = injector.detect_topics("salt price is very high today")
    assert "salt" in topics
    assert "price" in topics


def test_signal_injector_generates_overlay():
    injector = SignalInjector()
    overlay = injector.generate_overlay("salt price inflation", "te", region="telangana")
    assert overlay is not None
    assert "ధర" in overlay.overlay_text
    assert overlay.source == "commodity_prices"
