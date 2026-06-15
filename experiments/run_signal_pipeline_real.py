#!/usr/bin/env python3
"""End-to-end Signal Network pipeline with real Whisper ASR + IndicTrans2."""

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/Ubuntu/deeptech/signal-network")

# Dependencies check
try:
    from gtts import gTTS
except ImportError:
    print("Installing gTTS for synthetic Telugu audio...")
    subprocess.check_call(
        ["uv", "pip", "install", "gtts"],
        env={**os.environ, "PATH": os.environ.get("PATH", "") + ":/home/Ubuntu/.local/bin"},
    )
    from gtts import gTTS

from src.asr import IndicConformerASR
from src.pipeline import SignalPipeline
from src.translate import IndicTrans2Translator

OUT_DIR = Path("/home/Ubuntu/deeptech/outputs/signal_network_e2e")
OUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_TEXT = (
    "ఉప్పు ధర ఎక్కువగా ఉంది. "
    "ప్రభుత్వం దాన్ని తగ్గించాలి. "
    "రైతులు ఇబ్బందులు పడుతున్నారు. "
    "ధరల పెరుగుదల కారణంగా సామాన్యులు కష్టాలో కొన్నారు."
)

# 1. Generate Telugu audio with gTTS.
audio_path = OUT_DIR / "sample_te.mp3"
print("Generating Telugu audio...")
gTTS(text=AUDIO_TEXT, lang="te", slow=False).save(str(audio_path))
print("Audio saved:", audio_path)

# 2. Create a video from the audio + a static frame.
video_path = OUT_DIR / "sample_te.mp4"
frame_path = OUT_DIR / "frame.jpg"
subprocess.run(
    [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        "color=c=blue:s=640x360:d=10",
        "-frames:v", "1", str(frame_path),
    ],
    check=True,
    capture_output=True,
)
subprocess.run(
    [
        "ffmpeg", "-y", "-loop", "1", "-i", str(frame_path),
        "-i", str(audio_path), "-c:v", "libx264",
        "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", str(video_path),
    ],
    check=True,
    capture_output=True,
)
print("Video saved:", video_path)

# 3. Build real pipeline with Whisper ASR + IndicTrans2 translator.
asr = IndicConformerASR(
    model_id=os.environ.get("ASR_MODEL_ID", "openai/whisper-medium"),
    device="cuda:0",
)
translator = IndicTrans2Translator(
    model_id="/home/Ubuntu/models/indictrans2",
    device="cuda:0",
)
pipeline = SignalPipeline(asr=asr, translator=translator, output_dir=str(OUT_DIR))

# 4. Run pipeline.
print("Running full pipeline: video -> ASR -> translate -> captions...")
result = pipeline.run(
    video_path=str(video_path),
    source_lang="te",
    target_langs=["ta", "hi"],
)

print("\n=== Result ===")
print("success:", result.success)
print("source_language:", result.source_language)
print("target_languages:", result.target_languages)
print("outputs:", result.outputs)
if result.error:
    print("error:", result.error)
    sys.exit(1)

# 5. Verify output files exist.
for lang, path in result.outputs.items():
    exists = Path(path).exists()
    size = Path(path).stat().st_size if exists else 0
    print(f"  {lang}: {path} exists={exists} size={size} bytes")

print("\nPipeline complete.")
