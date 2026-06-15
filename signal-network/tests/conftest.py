"""Shared fixtures for signal-network tests."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def sample_video(tmp_path: Path) -> Path:
    """Generate a tiny test video with synthetic audio."""
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
