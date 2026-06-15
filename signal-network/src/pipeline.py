"""End-to-end spine pipeline: video → ASR → translate → captioned outputs."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.ingest import extract_audio
from src.asr import IndicConformerASR, ASRSegment
from src.translate import IndicTrans2Translator
from src.captions import CaptionSegment, generate_srt, burn_captions_ffmpeg


@dataclass
class PipelineResult:
    success: bool
    source_language: str
    target_languages: List[str]
    outputs: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


class SignalPipeline:
    """Orchestrates ingestion, ASR, translation, and caption burn."""

    def __init__(
        self,
        asr: Optional[IndicConformerASR] = None,
        translator: Optional[IndicTrans2Translator] = None,
        output_dir: str = "outputs",
    ):
        self.asr = asr or IndicConformerASR()
        self.translator = translator or IndicTrans2Translator()
        self.output_dir = Path(output_dir)
        self.last_audio_path: Optional[str] = None

    def run(
        self,
        video_path: str,
        source_lang: str,
        target_langs: List[str],
    ) -> PipelineResult:
        """Run the full spine pipeline."""
        video_path = Path(video_path)
        if not video_path.exists():
            return PipelineResult(
                success=False,
                source_language=source_lang,
                target_languages=target_langs,
                error=f"Input video not found: {video_path}",
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        stem = video_path.stem

        # 1. Extract audio.
        audio_path = self.output_dir / f"{stem}_{source_lang}.wav"
        self.last_audio_path = str(audio_path)
        audio_result = extract_audio(video_path, audio_path)
        if not audio_result.success:
            return PipelineResult(
                success=False,
                source_language=source_lang,
                target_languages=target_langs,
                error=f"Audio extraction failed: {audio_result.error}",
            )

        # 2. Transcribe.
        asr_result = self.asr.transcribe(audio_path, language=source_lang)
        if not asr_result.success:
            return PipelineResult(
                success=False,
                source_language=source_lang,
                target_languages=target_langs,
                error=f"ASR failed: {asr_result.error}",
            )

        outputs: Dict[str, str] = {}

        # 3. For each target language, translate segments and burn captions.
        for tgt_lang in target_langs:
            translated_segments: List[CaptionSegment] = []
            for seg in asr_result.segments:
                trans_result = self.translator.translate(seg.text, source_lang, [tgt_lang])
                if not trans_result.success:
                    translated_text = f"[translation error: {trans_result.error}]"
                else:
                    translated_text = trans_result.translations.get(tgt_lang, "")
                translated_segments.append(
                    CaptionSegment(
                        start=seg.start,
                        end=seg.end,
                        text=translated_text,
                    )
                )

            srt_path = self.output_dir / f"{stem}_{source_lang}_{tgt_lang}.srt"
            generate_srt(translated_segments, srt_path)

            out_video = self.output_dir / f"{stem}_{tgt_lang}.mp4"
            burn_result = burn_captions_ffmpeg(video_path, srt_path, out_video)
            if burn_result["success"]:
                outputs[tgt_lang] = str(out_video)
            else:
                outputs[tgt_lang] = f"error: {burn_result['error']}"

        # Also save source-language SRT.
        source_srt = self.output_dir / f"{stem}_{source_lang}.srt"
        generate_srt(
            [CaptionSegment(start=s.start, end=s.end, text=s.text) for s in asr_result.segments],
            source_srt,
        )
        outputs[source_lang] = str(source_srt)

        return PipelineResult(
            success=True,
            source_language=source_lang,
            target_languages=target_langs,
            outputs=outputs,
        )
