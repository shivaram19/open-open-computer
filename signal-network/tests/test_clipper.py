"""Tests for signal-aware clip extraction."""

import sys
from pathlib import Path

import pytest

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.asr import ASRSegment
from src.clipper import SignalClipper


def test_clipper_extracts_keyword_rich_segments():
    segments = [
        ASRSegment(start=0.0, end=3.0, text="Hello friends welcome to the kitchen", lang="te"),
        ASRSegment(start=3.0, end=8.0, text="Today salt price is very high", lang="te"),
        ASRSegment(start=8.0, end=15.0, text="Government says inflation is the reason but farmers are worried", lang="te"),
        ASRSegment(start=15.0, end=20.0, text="Let me show you the recipe now", lang="te"),
    ]

    clipper = SignalClipper(min_duration=5.0, max_duration=20.0, target_duration=12.0)
    clips = clipper.extract_clips(segments)

    assert len(clips) > 0
    top = clips[0]
    assert "price" in top.text.lower() or "inflation" in top.text.lower()
    assert top.score > 0
    assert top.hook_sentence


def test_clipper_respects_duration_bounds():
    segments = [
        ASRSegment(start=0.0, end=2.0, text="short", lang="te"),
        ASRSegment(start=2.0, end=25.0, text="a" * 100, lang="te"),
    ]

    clipper = SignalClipper(min_duration=5.0, max_duration=20.0)
    clips = clipper.extract_clips(segments)

    for clip in clips:
        assert clip.end - clip.start >= 5.0
        assert clip.end - clip.start <= 20.0


def test_clipper_empty_segments():
    clipper = SignalClipper()
    assert clipper.extract_clips([]) == []
