#!/usr/bin/env python3
"""Generate a complete Signal Network HTML slide deck via OpenAI directly."""

import os
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parent
OUTPUT = ROOT / "docs" / "Signal_Network_OpenDesign_Deck.html"

SYSTEM = """You are an expert frontend developer and presentation designer.
Your task is to produce a single, self-contained HTML file for a slide deck.
Rules:
- Output ONLY the complete HTML code. No markdown, no explanations, no code fences.
- The HTML must be fully self-contained: inline CSS, inline JavaScript, Google Fonts via CDN are allowed.
- Each slide is a full-screen 16:9 section with CSS scroll-snap.
- Use the exact color palette: background #0F172A, accent #06B6D4, text #F8FAFC, muted text #94A3B8.
- Include dot navigation on the right, keyboard arrow/PageDown/PageUp navigation, and a small footer on every slide with the repo link + share links (LinkedIn, X, WhatsApp, Telegram).
- Use large, bold typography and generous whitespace.
- Ensure all 9 slides are present and content-rich.
"""

USER = """Create a recruiting pitch deck for Signal Network.

Brand:
- Name: Signal Network
- Tagline: "Open-source hyper-local edutainment at scale — one video → N languages × M formats × P platforms."
- Tone: ambitious, inclusive, builder-friendly

Slides (exact content):

1. Title slide: Signal Network + tagline + "Open-source · Indic-languages · GPU-powered"
2. The Problem: India has 22 scheduled languages + thousands of dialects; civic/economic info rarely reaches people in their native tongue; manual translation, dubbing, and short-form editing don't scale; creators and NGOs need a deterministic, reusable pipeline.
3. The Solution: Drop one source video → get dozens of regional short-form clips; ASR, translation, clip extraction, caption burn, and publishing are automated; demographic engine matches topics to regions, languages, and best posting times; fully open-source.
4. How It Works: pipeline diagram — Ingest (yt-dlp + ffmpeg) → ASR (IndicConformer) → Translate (IndicTrans2) → Clip (Signal-aware extraction) → Render (Revideo / FFmpeg) → Publish (Azure Blob + platforms). Label: "One input → dozens of regional variants".
5. Built & Tested Stack: table with rows: GPU VM (Massed Compute A6000, CUDA 12.5), ASR (AI4Bharat IndicConformer 600M — 22-lang transcripts), Translation (AI4Bharat IndicTrans2 1B — Indic→Indic), Media Gen (Bernini-R 1.3B Diffusers — 20/20 tests), Pipeline (Signal Network spine + fan-out — 35/35 tests), Cloud Upload (Azure Blob Storage — ready). Use green badges for test passes.
6. Publish Everywhere: grid of 8 platforms — YouTube Shorts, Instagram Reels, TikTok, WhatsApp Status, Telegram Channels, X / Twitter, LinkedIn, Facebook — with one-line value prop each.
7. What's Already Working: GPU VM with CUDA 12.5 + cuDNN 9 deployed; IndicConformer ASR + IndicTrans2 translation on GPU; Signal Network spine, clip extraction, fan-out: 35/35 tests passing; Azure Blob Storage publisher implemented and ready for credentials.
8. Immediate Next Steps: Wire real Azure credentials and upload first batch of clips; replace FFmpeg subtitle burn with true Revideo 9:16 templates; add platform publishers (YouTube Shorts, Instagram Reels, TikTok); build a lightweight web dashboard for upload + monitoring; crowdsource demographic profiles and regional signal data sources.
9. Join the Build: roles — ML Engineers (GPU/ONNX/quantization), Video/Frontend devs (Revideo, caption styling, dashboard), Data/Linguists (Indic transcripts, hashtags, demographics), DevOps/Cloud (Azure, CI/CD, GPU scheduling), Community (testing, feedback, outreach). Footer repo: github.com/shivaram19/open-open-computer (Signal Network folder).

Technical requirements:
- Single HTML file, scroll-snap full-screen slides.
- Keyboard and dot navigation.
- Inline CSS/JS, Google Fonts allowed.
- Repo footer on every slide with share links.
"""


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ],
        temperature=0.7,
        max_tokens=4096,
    )
    html = resp.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    if html.startswith("```html"):
        html = html[7:]
    if html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]
    html = html.strip()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved deck to {OUTPUT}")


if __name__ == "__main__":
    main()
