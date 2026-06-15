"""SRT generation and FFmpeg caption burn-in."""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union


@dataclass
class CaptionSegment:
    start: float
    end: float
    text: str


def seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments: List[CaptionSegment], output_path: Union[str, Path]) -> Path:
    """Write SRT file from caption segments."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            f.write(f"{idx}\n")
            f.write(f"{seconds_to_srt_time(seg.start)} --> {seconds_to_srt_time(seg.end)}\n")
            f.write(f"{seg.text}\n\n")
    return output_path


def escape_for_ffmpeg_drawtext(text: str) -> str:
    """Escape characters for FFmpeg drawtext text expression."""
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\\'")
    return text


def burn_captions_ffmpeg(
    video_path: Union[str, Path],
    srt_path: Union[str, Path],
    output_path: Union[str, Path],
    style: str = "default",
) -> dict:
    """Burn SRT captions into a video using FFmpeg subtitles filter."""
    video_path = Path(video_path)
    srt_path = Path(srt_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        return {"success": False, "error": f"Video not found: {video_path}"}
    if not srt_path.exists():
        return {"success": False, "error": f"SRT not found: {srt_path}"}

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={escape_for_ffmpeg_drawtext(str(srt_path))}",
        "-c:a", "copy",
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
        return {"success": True, "output_path": str(output_path)}
    except subprocess.CalledProcessError as exc:
        return {"success": False, "error": f"FFmpeg failed (code {exc.returncode}): {exc.stderr}"}
    except FileNotFoundError:
        return {"success": False, "error": "FFmpeg not found on PATH."}
