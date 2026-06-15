"""ASR wrapper around AI4Bharat IndicConformer and compatible HF models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ASRSegment:
    start: float
    end: float
    text: str
    lang: str = "unknown"


@dataclass
class ASRResult:
    success: bool
    segments: List[ASRSegment] = field(default_factory=list)
    language: str = "unknown"
    error: Optional[str] = None


class IndicConformerASR:
    """Wrapper for AI4Bharat IndicConformer multilingual ASR.

    Supports:
    - The custom-code IndicConformer checkpoint (ai4bharat/indic-conformer-600m-multilingual)
    - Standard HuggingFace automatic-speech-recognition pipelines (e.g. Whisper)
    - Dependency injection of a mock callable for testing
    """

    def __init__(
        self,
        model_id: str = "ai4bharat/indic-conformer-600m-multilingual",
        device: str = "cpu",
        model_pipeline: Optional[Any] = None,
        return_timestamps: bool = True,
    ):
        self.model_id = model_id
        self.device = device
        self._pipeline = model_pipeline
        self.return_timestamps = return_timestamps
        self._injected = model_pipeline is not None
        self._is_indicconformer = self._detect_indicconformer(model_id)

    @staticmethod
    def _detect_indicconformer(model_id: str) -> bool:
        """Heuristic to detect the custom-code IndicConformer checkpoint."""
        lowered = model_id.lower()
        return "indic-conformer" in lowered or "indicconformer" in lowered

    def load(self) -> None:
        """Load the model. Skipped if a pipeline was injected."""
        if self._pipeline is not None:
            return
        try:
            if self._is_indicconformer:
                from transformers import AutoModel
                self._pipeline = AutoModel.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                )
                if self.device != "cpu":
                    self._pipeline = self._pipeline.to(self.device)
            else:
                from transformers import pipeline
                self._pipeline = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_id,
                    device=self.device,
                    trust_remote_code=True,
                )
        except Exception as exc:
            raise RuntimeError(f"Failed to load ASR model {self.model_id}: {exc}") from exc

    def _load_audio(self, audio_path: Path) -> Tuple[Any, int]:
        """Load audio to mono 16 kHz tensor."""
        import torch
        import torchaudio

        wav, sr = torchaudio.load(str(audio_path))
        if wav.shape[0] > 1:
            wav = torch.mean(wav, dim=0, keepdim=True)
        if sr != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
            wav = resampler(wav)
        return wav, 16000

    def _transcribe_indicconformer(
        self,
        audio_path: Path,
        language: str,
    ) -> ASRResult:
        """Run the custom IndicConformer forward method."""
        wav, _ = self._load_audio(audio_path)
        model = self._pipeline

        if self.return_timestamps:
            text, timestamps = model(
                wav,
                language,
                decoding="ctc",
                compute_timestamps="w",
            )
            segments = [
                ASRSegment(
                    start=float(start),
                    end=float(end),
                    text=str(word).strip(),
                    lang=language,
                )
                for word, start, end in timestamps[0]
            ]
        else:
            text = model(wav, language, decoding="ctc")
            segments = [ASRSegment(start=0.0, end=0.0, text=str(text).strip(), lang=language)]

        return ASRResult(success=True, segments=segments, language=language)

    def _transcribe_pipeline(
        self,
        audio_path: Path,
        language: str,
    ) -> ASRResult:
        """Run a standard HuggingFace ASR pipeline."""
        raw = self._pipeline(
            str(audio_path),
            language=language,
            return_timestamps=self.return_timestamps,
        )

        # Normalize output.
        if isinstance(raw, str):
            text = raw
            segments = [ASRSegment(start=0.0, end=0.0, text=text.strip(), lang=language)]
        elif isinstance(raw, dict):
            text = raw.get("text", "")
            chunks = raw.get("chunks", [])
            if chunks:
                segments = [
                    ASRSegment(
                        start=chunk.get("timestamp", (0.0, 0.0))[0] or 0.0,
                        end=chunk.get("timestamp", (0.0, 0.0))[1] or 0.0,
                        text=chunk.get("text", "").strip(),
                        lang=language,
                    )
                    for chunk in chunks
                ]
            else:
                segments = [ASRSegment(start=0.0, end=0.0, text=text.strip(), lang=language)]
        elif isinstance(raw, list):
            segments = [
                ASRSegment(
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    text=seg.get("text", "").strip(),
                    lang=language,
                )
                for seg in raw
            ]
        else:
            segments = [ASRSegment(start=0.0, end=0.0, text=str(raw).strip(), lang=language)]

        return ASRResult(success=True, segments=segments, language=language)

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "te",
    ) -> ASRResult:
        """Transcribe an audio file to timestamped segments."""
        audio_path = Path(audio_path)
        if not audio_path.exists():
            return ASRResult(success=False, error=f"Audio file not found: {audio_path}")

        self.load()

        try:
            # If a mock pipeline was injected, call it (without model-specific kwargs).
            if self._injected:
                raw = self._pipeline(str(audio_path), language=language)
                # Normalize injected output the same way as the dict branch.
                if isinstance(raw, dict):
                    text = raw.get("text", "")
                    chunks = raw.get("chunks", [])
                    if chunks:
                        segments = [
                            ASRSegment(
                                start=chunk.get("timestamp", (0.0, 0.0))[0] or 0.0,
                                end=chunk.get("timestamp", (0.0, 0.0))[1] or 0.0,
                                text=chunk.get("text", "").strip(),
                                lang=language,
                            )
                            for chunk in chunks
                        ]
                    else:
                        segments = [ASRSegment(start=0.0, end=0.0, text=text.strip(), lang=language)]
                elif isinstance(raw, str):
                    segments = [ASRSegment(start=0.0, end=0.0, text=raw.strip(), lang=language)]
                else:
                    segments = [ASRSegment(start=0.0, end=0.0, text=str(raw).strip(), lang=language)]
                return ASRResult(success=True, segments=segments, language=language)

            if self._is_indicconformer:
                return self._transcribe_indicconformer(audio_path, language)
            return self._transcribe_pipeline(audio_path, language)
        except Exception as exc:
            return ASRResult(success=False, error=f"Transcription failed: {exc}")
