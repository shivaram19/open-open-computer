"""Stub for Indian Census demographic data integration."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DistrictDemo:
    district: str
    state: str
    population: int
    literacy_rate: float
    urban_percent: float
    primary_language: str


class CensusStub:
    """Stub census data source.

    In production, replace with GeoJSON + censusindia.gov.in parsing.
    """

    DEFAULT_DISTRICTS: Dict[str, DistrictDemo] = {
        "hyderabad": DistrictDemo(
            district="Hyderabad",
            state="Telangana",
            population=6809970,
            literacy_rate=83.25,
            urban_percent=100.0,
            primary_language="te",
        ),
        "mumbai": DistrictDemo(
            district="Mumbai",
            state="Maharashtra",
            population=12478447,
            literacy_rate=89.21,
            urban_percent=100.0,
            primary_language="mr",
        ),
        "kamrup": DistrictDemo(
            district="Kamrup",
            state="Assam",
            population=1517542,
            literacy_rate=82.58,
            urban_percent=45.0,
            primary_language="as",
        ),
    }

    def __init__(self, districts: Optional[Dict[str, DistrictDemo]] = None):
        self.districts = districts or dict(self.DEFAULT_DISTRICTS)

    def get_district(self, district_id: str) -> Optional[DistrictDemo]:
        return self.districts.get(district_id)

    def districts_by_state(self, state: str) -> List[DistrictDemo]:
        return [d for d in self.districts.values() if d.state.lower() == state.lower()]
