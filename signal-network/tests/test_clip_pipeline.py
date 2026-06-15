"""Tests for the clip extraction + rendering pipeline."""

import sys
from pathlib import Path

import pytest

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.asr import IndicConformerASR
from src.clip_pipeline import ClipPipeline
from src.clipper import SignalClipper
from src.pipeline import SignalPipeline
from src.translate import IndicTrans2Translator


@pytest.fixture
def clip_pipeline(tmp_path):
    def mock_asr(audio_path, language):
        return {
            "text": "ఉప్పు ధర ఎక్కువగా ఉంది",
            "chunks": [
                {"timestamp": (0.0, 2.0), "text": "ఉప్పు ధర"},
                {"timestamp": (2.0, 6.0), "text": "ఎక్కువగా ఉంది Government inflation reason"},
            ],
        }

    def mock_translate(text, src, tgt):
        return f"[{tgt}] {text}"

    asr = IndicConformerASR(model_pipeline=mock_asr)
    translator = IndicTrans2Translator(model=mock_translate, tokenizer=None)
    spine = SignalPipeline(asr=asr, translator=translator, output_dir=str(tmp_path / "out"))
    clipper = SignalClipper(min_duration=2.0, max_duration=10.0, target_duration=5.0)
    return ClipPipeline(
        spine_pipeline=spine,
        clipper=clipper,
        output_dir=str(tmp_path / "out"),
        revideo_cmd="npm-not-installed",  # force fallback
    )


def test_clip_pipeline_extracts_clips(clip_pipeline, sample_video):
    result = clip_pipeline.run(
        video_path=str(sample_video),
        source_lang="te",
        target_langs=["hi", "mr"],
        price_overlay="ఉప్పు ధర: ₹45/kg",
        region_tag="తెలంగాణ",
    )

    assert result.success
    assert len(result.clips) > 0
    assert len(result.renders) > 0

    # SRTs should be generated even without Revideo rendering.
    for render in result.renders:
        assert render.srt_path.exists()
        assert render.target_lang in ("hi", "mr")
