"""Extended pipeline: spine + clip extraction + Revideo template rendering."""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.asr import ASRSegment
from src.captions import CaptionSegment, generate_srt
from src.clipper import Clip, SignalClipper
from src.pipeline import SignalPipeline


@dataclass
class ClipRenderResult:
    clip: Clip
    target_lang: str
    srt_path: Path
    video_path: Optional[Path] = None
    rendered: bool = False
    error: Optional[str] = None


@dataclass
class ClipPipelineResult:
    success: bool
    clips: List[Clip]
    renders: List[ClipRenderResult] = field(default_factory=list)
    outputs: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


class ClipPipeline:
    """Pipeline that extracts signal clips and renders them via Revideo."""

    def __init__(
        self,
        spine_pipeline: SignalPipeline,
        clipper: Optional[SignalClipper] = None,
        template_dir: str = "templates/cooking_signal",
        output_dir: str = "outputs",
        revideo_cmd: str = "npm",
    ):
        self.spine = spine_pipeline
        self.clipper = clipper or SignalClipper()
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.revideo_cmd = revideo_cmd

    def run(
        self,
        video_path: str,
        source_lang: str,
        target_langs: List[str],
        price_overlay: str,
        region_tag: str,
    ) -> ClipPipelineResult:
        """Run spine, extract clips, translate clip captions, render template."""
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            return ClipPipelineResult(
                success=False,
                clips=[],
                error=f"Input video not found: {video_path}",
            )

        # Run spine pipeline to get ASR segments.
        spine_result = self.spine.run(
            video_path=str(video_path_obj),
            source_lang=source_lang,
            target_langs=target_langs,
        )
        if not spine_result.success:
            return ClipPipelineResult(
                success=False,
                clips=[],
                error=f"Spine pipeline failed: {spine_result.error}",
            )

        # Extract clips from source segments.
        audio_path = self.spine.last_audio_path or video_path_obj
        asr_result = self.spine.asr.transcribe(audio_path, source_lang)
        clips = self.clipper.extract_clips(asr_result.segments)
        if not clips:
            return ClipPipelineResult(success=True, clips=[], outputs=spine_result.outputs)

        renders = self.render_clips(
            source_video_path=str(video_path_obj),
            clips=clips,
            source_lang=source_lang,
            target_langs=target_langs,
            price_overlay=price_overlay,
            region_tag=region_tag,
        )

        outputs = {
            **spine_result.outputs,
            **{
                f"clip_{r.clip.start:.0f}_{r.clip.end:.0f}_{r.target_lang}": str(r.video_path)
                for r in renders
                if r.video_path
            },
        }

        return ClipPipelineResult(success=True, clips=clips, renders=renders, outputs=outputs)

    def render_clips(
        self,
        source_video_path: str,
        clips: List[Clip],
        source_lang: str,
        target_langs: List[str],
        price_overlay: str,
        region_tag: str,
    ) -> List[ClipRenderResult]:
        """Translate and render a pre-extracted list of clips."""
        renders: List[ClipRenderResult] = []
        for clip in clips:
            for tgt_lang in target_langs:
                trans_result = self.spine.translator.translate(clip.text, source_lang, [tgt_lang])
                translated_text = trans_result.translations.get(tgt_lang, clip.text) if trans_result.success else clip.text

                srt_path = self.output_dir / f"clip_{clip.start:.0f}_{clip.end:.0f}_{tgt_lang}.srt"
                generate_srt(
                    [CaptionSegment(start=0.0, end=clip.end - clip.start, text=translated_text)],
                    srt_path,
                )

                render_result = ClipRenderResult(
                    clip=clip,
                    target_lang=tgt_lang,
                    srt_path=srt_path,
                )

                stem = f"clip_{clip.start:.0f}_{clip.end:.0f}_{tgt_lang}"
                if shutil.which(self.revideo_cmd):
                    render_result.video_path = self._render_revideo(
                        clip=clip,
                        translated_text=translated_text,
                        price_overlay=price_overlay,
                        region_tag=region_tag,
                        language=tgt_lang,
                        stem=stem,
                    )
                    render_result.rendered = render_result.video_path is not None

                # Fallback to FFmpeg trim + caption burn if Revideo is unavailable or failed.
                if not render_result.video_path:
                    render_result.video_path = self._render_ffmpeg(
                        source_video_path=source_video_path,
                        clip=clip,
                        srt_path=srt_path,
                        stem=stem,
                    )
                    render_result.rendered = render_result.video_path is not None
                    if not render_result.rendered:
                        render_result.error = "Both Revideo and FFmpeg rendering failed"

                renders.append(render_result)
        return renders

    def _render_revideo(
        self,
        clip: Clip,
        translated_text: str,
        price_overlay: str,
        region_tag: str,
        language: str,
        stem: str,
    ) -> Optional[Path]:
        """Shell out to Revideo to render a single clip."""
        output_path = self.output_dir / f"{stem}.mp4"
        variables = {
            "captionTrack": [{"start": 0.0, "end": clip.end - clip.start, "text": translated_text}],
            "priceOverlay": price_overlay,
            "regionTag": region_tag,
            "language": language,
        }

        cmd = [
            self.revideo_cmd,
            "run",
            "render",
            "--projectFile", str(self.template_dir / "src" / "scenes" / "scene.tsx"),
            "--variables", json.dumps(variables),
            "--outFile", str(output_path),
        ]

        try:
            subprocess.run(
                cmd,
                cwd=str(self.template_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            # Rendering is optional; return None on failure.
            return None

    def _render_ffmpeg(
        self,
        source_video_path: str,
        clip: Clip,
        srt_path: Path,
        stem: str,
    ) -> Optional[Path]:
        """Trim source video to clip bounds and burn in translated captions via FFmpeg."""
        output_path = self.output_dir / f"{stem}.mp4"
        duration = clip.end - clip.start
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(clip.start),
            "-i", str(source_video_path),
            "-t", str(duration),
            "-vf", "subtitles=" + str(srt_path).replace(":", "\\:"),
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
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
