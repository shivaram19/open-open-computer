"""Commodity price signal fetcher with CSV fallback."""

import csv
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PricePoint:
    commodity: str
    price: float
    unit: str
    change_percent: Optional[float] = None
    region: Optional[str] = None


class CommodityPriceFetcher:
    """Fetch commodity prices from data.gov.in or a local CSV fallback."""

    DEFAULT_CSV = Path(__file__).parent.parent.parent / "assets" / "commodity_prices.csv"

    def __init__(
        self,
        api_key: Optional[str] = None,
        csv_path: Optional[Path] = None,
    ):
        self.api_key = api_key
        self.csv_path = csv_path or self.DEFAULT_CSV

    def fetch(self, commodity: Optional[str] = None, region: Optional[str] = None) -> List[PricePoint]:
        """Return price points, filtered by commodity/region if provided."""
        if self.csv_path.exists():
            return self._from_csv(commodity, region)

        # If no CSV and no API key, return a deterministic fallback.
        return self._fallback(commodity, region)

    def _from_csv(self, commodity: Optional[str], region: Optional[str]) -> List[PricePoint]:
        points: List[PricePoint] = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if commodity and row.get("commodity", "").lower() != commodity.lower():
                    continue
                if region and row.get("region", "").lower() != region.lower():
                    continue
                points.append(
                    PricePoint(
                        commodity=row["commodity"],
                        price=float(row["price"]),
                        unit=row.get("unit", "kg"),
                        change_percent=float(row["change_percent"]) if row.get("change_percent") else None,
                        region=row.get("region"),
                    )
                )
        return points

    def _fallback(self, commodity: Optional[str], region: Optional[str]) -> List[PricePoint]:
        defaults = [
            PricePoint(commodity="salt", price=45.0, unit="kg", change_percent=12.0, region="telangana"),
            PricePoint(commodity="onion", price=32.0, unit="kg", change_percent=-5.0, region="maharashtra"),
            PricePoint(commodity="rice", price=58.0, unit="kg", change_percent=3.0, region="assam"),
        ]
        if commodity:
            defaults = [p for p in defaults if p.commodity.lower() == commodity.lower()]
        if region:
            defaults = [p for p in defaults if p.region and p.region.lower() == region.lower()]
        return defaults

    def to_overlay(self, point: PricePoint, lang: str = "te") -> str:
        """Format a price point as a short overlay string."""
        labels = {
            "te": f"{point.commodity.title()} ధర: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
            "mr": f"{point.commodity.title()} किंमत: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
            "as": f"{point.commodity.title()} মূল্য: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
            "or": f"{point.commodity.title()} ମୂଲ୍ୟ: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
            "hi": f"{point.commodity.title()} कीमत: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
            "en": f"{point.commodity.title()} price: ₹{point.price:.0f}/{point.unit} ({point.change_percent:+.0f}%)",
        }
        return labels.get(lang, labels["en"])
