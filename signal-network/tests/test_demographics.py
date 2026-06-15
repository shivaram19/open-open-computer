"""Tests for demographic targeting engine."""

import sys
from pathlib import Path

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.demographics import DemographicEngine


def test_rank_regions_by_topics():
    engine = DemographicEngine()
    ranked = engine.rank_regions(["inflation", "traffic"])
    assert ranked[0].id == "maharashtra"


def test_generate_plan():
    engine = DemographicEngine()
    plan = engine.generate_plan(
        region_id="assam",
        source_lang="as",
        available_languages=["as", "bn"],
        platforms=["whatsapp_status"],
    )
    assert plan.region_id == "assam"
    assert "as" in plan.languages
    assert "whatsapp_status" in plan.platforms
    assert len(plan.hashtags) > 0


def test_unknown_region_raises():
    engine = DemographicEngine()
    try:
        engine.generate_plan("mars", "te", ["te"])
        assert False, "expected ValueError"
    except ValueError:
        pass
