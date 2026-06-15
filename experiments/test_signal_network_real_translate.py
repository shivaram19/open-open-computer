"""End-to-end Signal Network sensor with real IndicTrans2 translator."""
import sys
sys.path.insert(0, "/home/Ubuntu/deeptech/signal-network")

from pathlib import Path
from src.pipeline import SignalPipeline
from src.translate import IndicTrans2Translator

# Synthetic video: 3 sec black frame with silent audio
out_dir = Path("/home/Ubuntu/deeptech/outputs/signal_network_test")
out_dir.mkdir(parents=True, exist_ok=True)
video_path = out_dir / "sample_te.mp4"

import subprocess
subprocess.run([
    "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x480:d=3",
    "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
    "-shortest", "-c:v", "libx264", "-c:a", "aac", str(video_path)
], check=True, capture_output=True)

# Mock ASR returning Telugu segments
class MockASR:
    def __init__(self):
        self._pipeline = None
    def load(self):
        pass
    def transcribe(self, audio_path, language="te"):
        from src.asr import ASRResult, ASRSegment
        return ASRResult(
            success=True,
            segments=[ASRSegment(start=0.0, end=2.0, text="ఇది ఒక పరీక్ష.", lang="te")],
            language="te",
        )

# Map our short lang code to IndicTrans2 flores codes
translator = IndicTrans2Translator(
    model_id="/home/Ubuntu/models/indictrans2",
    device="cuda",
)

pipeline = SignalPipeline(asr=MockASR(), translator=translator, output_dir=str(out_dir))
result = pipeline.run(str(video_path), source_lang="te", target_langs=["ta"])

print("success:", result.success)
print("outputs:", result.outputs)
if result.error:
    print("error:", result.error)
