#!/usr/bin/env python3
"""Download and smoke-test AI4Bharat IndicConformer ASR."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/Ubuntu/deeptech/signal-network")

from src.asr import IndicConformerASR

model_id = "ai4bharat/indic-conformer-600m-multilingual"
cache_dir = Path("/home/Ubuntu/models/indicconformer")

# IndicConformer's custom from_pretrained only accepts a HuggingFace repo_id and
# downloads to the HF cache internally. We keep a local mirror for bookkeeping.
if not cache_dir.exists() or not any(cache_dir.iterdir()):
    cache_dir.mkdir(parents=True, exist_ok=True)
    print("Downloading model:", model_id)
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id=model_id,
        local_dir=str(cache_dir),
        local_dir_use_symlinks=False,
        token=os.environ.get("HF_TOKEN"),
    )
    print("Download complete. Size:", sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()) / 1e9, "GB")
else:
    print("Model already present at:", cache_dir)

# Create synthetic Telugu audio: 3 seconds of 1kHz tone (not speech, but tests pipeline load)
audio_path = Path("/home/Ubuntu/deeptech/outputs/indicconformer_test.wav")
audio_path.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
    "-ar", "16000", "-ac", "1", str(audio_path)
], check=True, capture_output=True)

print("Loading ASR model...")
asr = IndicConformerASR(model_id=model_id, device="cuda:0")

print("Transcribing...")
result = asr.transcribe(str(audio_path), language="te")
print("ASR success:", result.success)
print("Segments:", result.segments)
if result.error:
    print("Error:", result.error)
