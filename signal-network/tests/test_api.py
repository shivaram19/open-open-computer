"""Tests for the Signal Network FastAPI service."""

import sys
from pathlib import Path

import fakeredis
import pytest
from fastapi.testclient import TestClient

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.api import create_app
from src.asr import IndicConformerASR
from src.pipeline import SignalPipeline
from src.translate import IndicTrans2Translator


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def sample_video(tmp_path):
    import subprocess
    output = tmp_path / "sample_input.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "testsrc=duration=2:size=320x240:rate=1",
        "-f", "lavfi",
        "-i", "sine=frequency=1000:duration=2",
        "-pix_fmt", "yuv420p",
        str(output),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output


@pytest.fixture
def client(fake_redis, sample_video, tmp_path):
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

    app = create_app(redis_client=fake_redis, pipeline=pipeline)
    with TestClient(app) as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job(client):
    response = client.post(
        "/jobs",
        json={
            "file_path": "/tmp/video.mp4",
            "source_lang": "te",
            "target_langs": ["hi", "mr"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["source_lang"] == "te"
    assert data["target_langs"] == ["hi", "mr"]


def test_create_job_requires_source(client):
    response = client.post(
        "/jobs",
        json={
            "source_lang": "te",
            "target_langs": ["hi"],
        },
    )
    assert response.status_code == 400


def test_get_job(client):
    create_response = client.post(
        "/jobs",
        json={
            "file_path": "/tmp/video.mp4",
            "source_lang": "te",
            "target_langs": ["hi"],
        },
    )
    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_job_not_found(client):
    response = client.get("/jobs/nonexistent")
    assert response.status_code == 404


def test_run_job_sync(client, sample_video):
    create_response = client.post(
        "/jobs",
        json={
            "file_path": str(sample_video),
            "source_lang": "te",
            "target_langs": ["hi", "mr"],
        },
    )
    job_id = create_response.json()["id"]

    response = client.post(f"/jobs/{job_id}/run")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "hi" in data["outputs"]
    assert "mr" in data["outputs"]
    assert Path(data["outputs"]["hi"]).exists()
