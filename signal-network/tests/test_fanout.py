"""Tests for regional fan-out pipeline."""

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
from src.fanout import RegionalFanOut
from src.pipeline import SignalPipeline
from src.translate import IndicTrans2Translator


@pytest.fixture
def fanout(tmp_path):
    def mock_asr(audio_path, language):
        return {
            "text": "ఉప్పు ధర ఎక్కువగా ఉంది Government inflation reason",
            "chunks": [
                {"timestamp": (0.0, 2.0), "text": "ఉప్పు ధర"},
                {"timestamp": (2.0, 7.0), "text": "ఎక్కువగా ఉంది Government inflation reason"},
            ],
        }

    def mock_translate(text, src, tgt):
        return f"[{tgt}] {text}"

    asr = IndicConformerASR(model_pipeline=mock_asr)
    translator = IndicTrans2Translator(model=mock_translate, tokenizer=None)
    spine = SignalPipeline(asr=asr, translator=translator, output_dir=str(tmp_path / "out"))
    clipper = SignalClipper(min_duration=2.0, max_duration=10.0, target_duration=5.0)
    clip_pipeline = ClipPipeline(
        spine_pipeline=spine,
        clipper=clipper,
        output_dir=str(tmp_path / "out"),
        revideo_cmd="npm-not-installed",
    )
    return RegionalFanOut(
        clip_pipeline=clip_pipeline,
        output_dir=str(tmp_path / "out"),
    )


def test_fanout_creates_regional_variants(fanout, sample_video):
    result = fanout.run(
        video_path=str(sample_video),
        source_lang="te",
        topics=["inflation"],
        price_overlay="ఉప్పు ధర: ₹45/kg",
        platforms=["file_manifest"],
    )

    assert result.success
    assert len(result.variants) > 0
    assert "master" in result.manifests
    assert Path(result.manifests["master"]).exists()

    # Verify at least one variant targets Maharashtra (inflation topic).
    region_ids = {v.region_id for v in result.variants}
    assert "maharashtra" in region_ids


def test_fanout_gracefully_skips_azure_without_credentials(fanout, sample_video, monkeypatch):
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("AZURE_STORAGE_CONTAINER", raising=False)

    result = fanout.run(
        video_path=str(sample_video),
        source_lang="te",
        topics=["inflation"],
        price_overlay="ఉప్పు ధర: ₹45/kg",
        platforms=["file_manifest", "azure_blob"],
    )

    assert result.success
    # File manifest still succeeds even though Azure is not configured.
    assert "master" in result.manifests
    assert Path(result.manifests["master"]).exists()
