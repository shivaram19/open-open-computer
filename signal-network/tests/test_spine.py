"""Tests for the Signal Network spine pipeline."""

import sys
from pathlib import Path

import pytest

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.ingest import extract_audio
from src.asr import IndicConformerASR, ASRSegment
from src.translate import IndicTrans2Translator, TranslationResult
from src.captions import CaptionSegment, generate_srt, seconds_to_srt_time
from src.pipeline import SignalPipeline


def test_extract_audio_from_sample_video(sample_video, tmp_path):
    output = tmp_path / "audio.wav"
    result = extract_audio(sample_video, output)
    assert result.success
    assert output.exists()
    assert result.sample_rate == 16000
    assert result.channels == 1


def test_asr_with_mock_pipeline(tmp_path):
    def mock_pipeline(audio_path, language):
        return {
            "text": "ఉప్పు ధర ఎక్కువగా ఉంది",
            "chunks": [
                {"timestamp": (0.0, 2.5), "text": "ఉప్పు ధర"},
                {"timestamp": (2.5, 4.0), "text": "ఎక్కువగా ఉంది"},
            ],
        }

    dummy_audio = tmp_path / "dummy.wav"
    dummy_audio.write_bytes(b"RIFF" + b"\x00" * 100)  # enough to pass exists() check

    asr = IndicConformerASR(model_pipeline=mock_pipeline)
    result = asr.transcribe(dummy_audio, language="te")
    assert result.success
    assert result.language == "te"
    assert len(result.segments) == 2
    assert result.segments[0].text == "ఉప్పు ధర"


def test_translate_with_mock_model():
    def mock_model(text, src, tgt):
        return f"{tgt}: {text}"

    translator = IndicTrans2Translator(model=mock_model, tokenizer=None)
    result = translator.translate("హలో", "te", ["hi", "mr"])
    assert result.success
    assert "hi" in result.translations
    assert "mr" in result.translations
    assert result.translations["hi"] == "hi: హలో"


def test_generate_srt(tmp_path):
    segments = [
        CaptionSegment(start=0.0, end=2.5, text="హలో"),
        CaptionSegment(start=2.5, end=5.0, text="ఎలా ఉన్నారు"),
    ]
    output = tmp_path / "test.srt"
    generate_srt(segments, output)
    content = output.read_text(encoding="utf-8")
    assert "1" in content
    assert "00:00:00,000 --> 00:00:02,500" in content
    assert "హలో" in content


def test_seconds_to_srt_time():
    assert seconds_to_srt_time(0.0) == "00:00:00,000"
    assert seconds_to_srt_time(3661.123) == "01:01:01,123"


def test_pipeline_with_mocks(sample_video, tmp_path):
    def mock_asr(audio_path, language):
        return {
            "text": "ఉప్పు ధర ఎక్కువగా ఉంది",
            "chunks": [
                {"timestamp": (0.0, 2.0), "text": "ఉప్పు ధర"},
                {"timestamp": (2.0, 4.0), "text": "ఎక్కువగా ఉంది"},
            ],
        }

    def mock_translate(text, src, tgt):
        return f"[{tgt}] {text}"

    asr = IndicConformerASR(model_pipeline=mock_asr)
    translator = IndicTrans2Translator(model=mock_translate, tokenizer=None)
    pipeline = SignalPipeline(asr=asr, translator=translator, output_dir=str(tmp_path / "out"))

    result = pipeline.run(
        video_path=str(sample_video),
        source_lang="te",
        target_langs=["hi", "mr"],
    )

    assert result.success
    assert result.source_language == "te"
    assert result.target_languages == ["hi", "mr"]
    assert "hi" in result.outputs
    assert "mr" in result.outputs
    assert "te" in result.outputs
    assert Path(result.outputs["hi"]).exists()
    assert Path(result.outputs["mr"]).exists()
