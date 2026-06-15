"""Demographic intelligence and regional targeting for Signal Network."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegionProfile:
    id: str
    name: str
    languages: List[str]
    topics: List[str]
    age_skew: str
    best_time_ist: str
    format: str
    population_density: Optional[int] = None
    internet_penetration: Optional[float] = None


@dataclass
class ContentPlan:
    region_id: str
    languages: List[str]
    platforms: List[str]
    hashtags: List[str]
    schedule_time: str
    format: str
    topics: List[str]


class DemographicEngine:
    """Maps content topics to regional profiles and generates distribution plans."""

    DEFAULT_PROFILES: Dict[str, RegionProfile] = {
        "telangana": RegionProfile(
            id="telangana",
            name="Telangana",
            languages=["te", "ur"],
            topics=["agriculture", "tech_jobs", "water", "power", "education"],
            age_skew="18-35",
            best_time_ist="19:00-21:00",
            format="reels_9_16",
            population_density=320,
            internet_penetration=0.72,
        ),
        "maharashtra": RegionProfile(
            id="maharashtra",
            name="Maharashtra",
            languages=["mr", "hi"],
            topics=["inflation", "traffic", "health", "drought", "urban_migration"],
            age_skew="22-35",
            best_time_ist="08:00-09:00",
            format="reels_9_16",
            population_density=370,
            internet_penetration=0.78,
        ),
        "assam": RegionProfile(
            id="assam",
            name="Assam",
            languages=["as", "bn"],
            topics=["flooding", "tea_prices", "immigration", "agriculture"],
            age_skew="18-25",
            best_time_ist="19:00-21:00",
            format="whatsapp_status_friendly",
            population_density=400,
            internet_penetration=0.55,
        ),
        "odisha": RegionProfile(
            id="odisha",
            name="Odisha",
            languages=["or", "hi"],
            topics=["cyclone", "farming", "tribal_rights", "education"],
            age_skew="18-30",
            best_time_ist="18:30-20:30",
            format="whatsapp_status_friendly",
            population_density=270,
            internet_penetration=0.51,
        ),
    }

    def __init__(self, profiles: Optional[Dict[str, RegionProfile]] = None):
        self.profiles = profiles or dict(self.DEFAULT_PROFILES)

    def rank_regions(self, topics: List[str]) -> List[RegionProfile]:
        """Rank regions by relevance to the given topics."""
        scored = []
        for profile in self.profiles.values():
            score = sum(1 for t in topics if t.lower() in [pt.lower() for pt in profile.topics])
            if score > 0:
                scored.append((score, profile))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]

    def generate_plan(
        self,
        region_id: str,
        source_lang: str,
        available_languages: List[str],
        platforms: List[str] = None,
    ) -> ContentPlan:
        """Generate a distribution plan for a region."""
        profile = self.profiles.get(region_id)
        if profile is None:
            raise ValueError(f"Unknown region: {region_id}")

        platforms = platforms or ["instagram_reels", "youtube_shorts", "whatsapp_status"]
        target_langs = [lang for lang in profile.languages if lang in available_languages]
        if source_lang in profile.languages and source_lang not in target_langs:
            target_langs.insert(0, source_lang)
        if not target_langs:
            target_langs = [source_lang]

        hashtags = [f"#{region_id}", f"#{source_lang}"] + [f"#{t.replace(' ', '_')}" for t in profile.topics[:3]]

        return ContentPlan(
            region_id=region_id,
            languages=target_langs,
            platforms=platforms,
            hashtags=hashtags,
            schedule_time=profile.best_time_ist,
            format=profile.format,
            topics=profile.topics,
        )
