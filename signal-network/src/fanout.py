"""End-to-end regional fan-out: source → clips → regional plans → publish manifests."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.clip_pipeline import ClipPipeline
from src.demographics import ContentPlan, DemographicEngine
from src.publishers import AzureBlobPublisher, FilePublisher, MultiPlatformPublisher


@dataclass
class RegionalVariant:
    region_id: str
    language: str
    clip_start: float
    clip_end: float
    clip_path: str
    srt_path: str
    plan: ContentPlan
    caption: str
    manifest_path: Optional[str] = None


@dataclass
class FanOutResult:
    success: bool
    variants: List[RegionalVariant] = field(default_factory=list)
    manifests: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


class RegionalFanOut:
    """Orchestrates clip generation + demographic targeting + publishing manifests."""

    def __init__(
        self,
        clip_pipeline: ClipPipeline,
        demographics: Optional[DemographicEngine] = None,
        publisher: Optional[MultiPlatformPublisher] = None,
        output_dir: str = "outputs",
        max_clips_per_region: int = 2,
    ):
        self.clip_pipeline = clip_pipeline
        self.demographics = demographics or DemographicEngine()
        self.publisher = publisher or MultiPlatformPublisher({
            "file_manifest": FilePublisher(output_dir),
            "azure_blob": AzureBlobPublisher(),
        })
        self.output_dir = Path(output_dir)
        self.max_clips_per_region = max_clips_per_region

    def run(
        self,
        video_path: str,
        source_lang: str,
        topics: List[str],
        price_overlay: str,
        region_ids: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
    ) -> FanOutResult:
        """Generate regional variants and publishing manifests."""
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            return FanOutResult(success=False, error=f"Input video not found: {video_path}")

        # Determine target regions.
        if region_ids:
            regions = [self.demographics.profiles[r] for r in region_ids if r in self.demographics.profiles]
        else:
            regions = self.demographics.rank_regions(topics)

        if not regions:
            return FanOutResult(success=False, error="No matching regions found")

        # Run spine once and extract clips once.
        spine_result = self.clip_pipeline.spine.run(
            video_path=str(video_path_obj),
            source_lang=source_lang,
            target_langs=[],  # translations happen per-region
        )
        if not spine_result.success:
            return FanOutResult(success=False, error=f"Spine pipeline failed: {spine_result.error}")

        audio_path = self.clip_pipeline.spine.last_audio_path or video_path_obj
        asr_result = self.clip_pipeline.spine.asr.transcribe(audio_path, source_lang)
        clips = self.clip_pipeline.clipper.extract_clips(asr_result.segments)
        if not clips:
            return FanOutResult(success=True, variants=[], manifests=spine_result.outputs)

        variants: List[RegionalVariant] = []
        manifests: Dict[str, str] = {}

        for region in regions:
            plan = self.demographics.generate_plan(
                region_id=region.id,
                source_lang=source_lang,
                available_languages=region.languages,
                platforms=platforms,
            )

            target_langs = plan.languages
            top_clips = clips[: self.max_clips_per_region]
            renders = self.clip_pipeline.render_clips(
                source_video_path=str(video_path_obj),
                clips=top_clips,
                source_lang=source_lang,
                target_langs=target_langs,
                price_overlay=price_overlay,
                region_tag=region.name,
            )

            for render in renders:
                caption = f"{render.clip.hook_sentence} " + " ".join(plan.hashtags)
                variant = RegionalVariant(
                    region_id=region.id,
                    language=render.target_lang,
                    clip_start=render.clip.start,
                    clip_end=render.clip.end,
                    clip_path=str(render.video_path) if render.video_path else "",
                    srt_path=str(render.srt_path),
                    plan=plan,
                    caption=caption,
                )

                if render.video_path:
                    pub_results = self.publisher.publish_all(
                        video_path=str(render.video_path),
                        caption=caption,
                        hashtags=plan.hashtags,
                        platforms=plan.platforms,
                        schedule_time=plan.schedule_time,
                    )
                    for pub in pub_results:
                        if pub.success:
                            variant.manifest_path = pub.url
                            manifests[f"{region.id}_{render.clip.start:.0f}_{render.target_lang}_{pub.platform}"] = pub.url

                variants.append(variant)

        # Write a master manifest.
        master_manifest = self.output_dir / "fanout_manifest.json"
        master_manifest.write_text(
            json.dumps(
                {
                    "regions": [v.region_id for v in variants],
                    "variants": [
                        {
                            "region_id": v.region_id,
                            "language": v.language,
                            "clip_start": v.clip_start,
                            "clip_end": v.clip_end,
                            "clip_path": v.clip_path,
                            "srt_path": v.srt_path,
                            "caption": v.caption,
                            "manifest_path": v.manifest_path,
                        }
                        for v in variants
                    ],
                },
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        manifests["master"] = str(master_manifest)

        return FanOutResult(success=True, variants=variants, manifests=manifests)
