"""Ingestion utilities: download, extract and normalize audio/video sources."""

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class AudioExtractResult:
    success: bool
    output_path: Path
    sample_rate: int = 16000
    channels: int = 1
    error: str | None = None


@dataclass
class DownloadResult:
    success: bool
    output_path: Path
    error: Optional[str] = None


def download_video(
    url: str,
    output_path: Union[str, Path],
    format_code: str = "best[ext=mp4]/best",
) -> DownloadResult:
    """Download a video from a URL using yt-dlp.

    Supports YouTube and 1000+ sites supported by yt-dlp.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ytdlp = shutil.which("yt-dlp") or shutil.which("youtube-dl")
    if ytdlp is None:
        return DownloadResult(
            success=False,
            output_path=output_path,
            error="yt-dlp not found. Install with: pip install yt-dlp",
        )

    cmd = [
        ytdlp,
        "--no-playlist",
        "-f", format_code,
        "-o", str(output_path),
        url,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return DownloadResult(success=True, output_path=output_path)
    except subprocess.CalledProcessError as exc:
        return DownloadResult(
            success=False,
            output_path=output_path,
            error=f"yt-dlp failed (code {exc.returncode}): {exc.stderr}",
        )


def extract_audio(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    sample_rate: int = 16000,
    channels: int = 1,
) -> AudioExtractResult:
    """Extract audio from a video file into a normalized WAV.

    Uses FFmpeg to resample to mono 16kHz 16-bit PCM by default.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(output_path),
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return AudioExtractResult(
            success=True,
            output_path=output_path,
            sample_rate=sample_rate,
            channels=channels,
        )
    except subprocess.CalledProcessError as exc:
        return AudioExtractResult(
            success=False,
            output_path=output_path,
            sample_rate=sample_rate,
            channels=channels,
            error=f"FFmpeg failed (code {exc.returncode}): {exc.stderr}",
        )
    except FileNotFoundError:
        return AudioExtractResult(
            success=False,
            output_path=output_path,
            error="FFmpeg not found. Install FFmpeg and ensure it is on PATH.",
        )
