#!/usr/bin/env python3
"""CLI entrypoint for Signal Network regional fan-out."""

import argparse
import os
import sys
from pathlib import Path

# Ensure src/ is on path when running directly.
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.asr import IndicConformerASR
from src.clip_pipeline import ClipPipeline
from src.clipper import SignalClipper
from src.demographics import DemographicEngine
from src.fanout import RegionalFanOut
from src.pipeline import SignalPipeline
from src.publishers import AzureBlobPublisher, FilePublisher, MultiPlatformPublisher
from src.signal_injector import SignalInjector
from src.translate import IndicTrans2Translator


def main():
    parser = argparse.ArgumentParser(description="Signal Network regional fan-out")
    parser.add_argument("--video", required=True, help="Path to source video")
    parser.add_argument("--source-lang", default="te", help="Source language code")
    parser.add_argument("--target-langs", nargs="+", default=["ta"], help="Target language codes")
    parser.add_argument("--topics", nargs="+", default=["inflation"], help="Signal topics")
    parser.add_argument("--regions", nargs="+", help="Target region IDs")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument(
        "--asr-model",
        default=os.environ.get("ASR_MODEL_ID", "ai4bharat/indic-conformer-600m-multilingual"),
        help="ASR model id or local path (env: ASR_MODEL_ID)",
    )
    parser.add_argument(
        "--translator-model",
        default=os.environ.get("TRANSLATOR_MODEL_ID", "ai4bharat/indictrans2-indic-indic-1B"),
        help="Translation model id or local path (env: TRANSLATOR_MODEL_ID)",
    )
    parser.add_argument(
        "--device",
        default=os.environ.get("INFERENCE_DEVICE", "cpu"),
        help="PyTorch device for models (env: INFERENCE_DEVICE)",
    )
    parser.add_argument(
        "--price-overlay",
        help="Override price overlay text (auto-generated if omitted)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock ASR/translator so no GPU/model downloads are needed",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["file_manifest", "azure_blob"],
        help="Publishing platforms to use",
    )

    args = parser.parse_args()

    # Build pipeline.
    if args.mock:
        def mock_asr(audio_path, language):
            return {
                "text": "ఉప్పు ధర ఎక్కువగా ఉంది",
                "chunks": [
                    {"timestamp": (0.0, 2.0), "text": "ఉప్పు ధర"},
                    {"timestamp": (2.0, 7.0), "text": "ఎక్కువగా ఉంది Government inflation reason"},
                ],
            }

        def mock_translate(text, src, tgt):
            return f"[{tgt}] {text}"

        asr = IndicConformerASR(model_pipeline=mock_asr)
        translator = IndicTrans2Translator(model=mock_translate, tokenizer=None)
    else:
        asr = IndicConformerASR(model_id=args.asr_model, device=args.device)
        translator = IndicTrans2Translator(model_id=args.translator_model, device=args.device)

    spine = SignalPipeline(asr=asr, translator=translator, output_dir=args.output_dir)
    clipper = SignalClipper(min_duration=2.0, max_duration=90.0, target_duration=45.0)
    clip_pipeline = ClipPipeline(
        spine_pipeline=spine,
        clipper=clipper,
        output_dir=args.output_dir,
    )

    publisher = MultiPlatformPublisher({
        "file_manifest": FilePublisher(args.output_dir),
        "azure_blob": AzureBlobPublisher(),
    })
    fanout = RegionalFanOut(
        clip_pipeline=clip_pipeline,
        demographics=DemographicEngine(),
        publisher=publisher,
        output_dir=args.output_dir,
    )

    # Auto-generate price overlay if not provided.
    price_overlay = args.price_overlay
    if not price_overlay:
        injector = SignalInjector()
        overlay = injector.generate_overlay(" ".join(args.topics), args.source_lang)
        price_overlay = overlay.overlay_text if overlay else "Signal overlay"

    print(f"Running fan-out for: {args.video}")
    print(f"Topics: {args.topics}")
    print(f"Price overlay: {price_overlay}")

    result = fanout.run(
        video_path=args.video,
        source_lang=args.source_lang,
        topics=args.topics,
        price_overlay=price_overlay,
        region_ids=args.regions,
        platforms=args.platforms,
    )

    if not result.success:
        print(f"Fan-out failed: {result.error}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated {len(result.variants)} regional variants")
    print(f"Master manifest: {result.manifests.get('master')}")
    for v in result.variants:
        print(f"  - {v.region_id}/{v.language}: {v.clip_path or '(no clip)'}")
        if v.manifest_path:
            print(f"      manifest: {v.manifest_path}")


if __name__ == "__main__":
    main()
