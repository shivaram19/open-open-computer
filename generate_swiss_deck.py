#!/usr/bin/env python3
"""Generate a Signal Network deck using the Open Design Swiss International template."""

import os
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parent
OUTPUT = ROOT / "docs" / "Signal_Network_Swiss_Deck.html"

SYSTEM = """You are an elite frontend developer and presentation designer.
You must apply the **Swiss International Deck** design system exactly.

Design system rules (strict):
- Theme: **Klein Blue (IKB)** — accent `#002FA7`, paper `#fafaf8`, ink `#0a0a0a`.
- 16-column grid: `grid-template-columns: repeat(16, 1fr); gap: 0`.
- All corners are sharp: `border-radius: 0` everywhere.
- 1px hairline borders only (black or accent). No shadows, gradients, or blur.
- Fonts: Inter Tight for display, Inter for body, JetBrains Mono for data. Load via Google Fonts.
- Extreme type contrast: cover headline 9.6vw display, body 14-16px, labels 11px uppercase with letter-spacing 0.08em.
- Keyboard left/right arrow navigation plus hash sync (`#slide-N`).
- Fixed chrome: `№N/N` bottom-right, topic label bottom-left on every slide.
- No external images. Decorative geometry (ASCII dot matrix, concentric rings) must be inline SVG or pure CSS.
- Output a single self-contained HTML file with inline CSS and JS.
- Use the provided 22 layouts where appropriate; pick the best layout for each slide's content.

Output ONLY the complete HTML. No markdown, no explanation, no code fences.
"""

USER = """Create a recruiting pitch deck for Signal Network using the Swiss International Deck system.

Content:

Slide 1 — S01 Cover
- Title: Signal Network
- Subtitle: Open-source hyper-local edutainment at scale
- Tagline: One video → N languages × M formats × P platforms
- Date: 2026
- Topic: OPEN SOURCE / INDIC AI

Slide 2 — S03 Statement
- Big centered statement: "Most Indians cannot access civic and economic information in their own language."
- Footnote: 22 scheduled languages, thousands of dialects, manual localization doesn't scale.

Slide 3 — S18 Why Now
- 3 columns:
  1. SCALE — India creates content mainly in Hindi/English; regional audiences are underserved.
  2. COST — Manual dubbing, translation, and short-form editing are too slow and expensive.
  3. TECH — Open Indic ASR and translation models are now fast and accurate enough to automate this.

Slide 4 — S04 Six Cells (pipeline overview)
- 6 cells in 2×3 grid:
  1. INGEST — ffmpeg + yt-dlp → clean audio
  2. ASR — IndicConformer → word-level transcripts
  3. TRANSLATE — IndicTrans2 → 22 Indic languages
  4. CLIP — signal-aware viral moment extraction
  5. RENDER — Revideo / FFmpeg captions
  6. PUBLISH — Azure Blob + social platforms

Slide 5 — S06 KPI Tower
- 4 KPIs with heights proportional to impact:
  1. 22 — languages supported
  2. 35/35 — pipeline tests passing
  3. 1 → 100s — videos generated per input
  4. 0 — vendor lock-in (open source)

Slide 6 — S19 Four Cards
- Headline: Publish everywhere people already watch
- 4 cards: YouTube Shorts, Instagram Reels, TikTok, WhatsApp Status, Telegram, X, LinkedIn, Facebook — pick the top 4 or show 8 as two rows of four.

Slide 7 — S13 Three Forces Cards
- Headline: Built, tested, and running on GPU
- 3 cards:
  1. GPU — CUDA 12.5 + cuDNN 9 A6000 VM deployed.
  2. MODELS — IndicConformer ASR + IndicTrans2 translation on GPU.
  3. CLOUD — Azure Blob Storage publisher implemented.

Slide 8 — S09 Closing Manifesto
- Left block: ASCII dot matrix +宣言 "Open infrastructure for a multilingual internet."
- Right white block with 3 points:
  1. Transparent models and code.
  2. Forkable for any region or language.
  3. No vendor lock-in, no black box.

Slide 9 — S22 Image Hero or S01 Cover variant
- Headline: Build the multilingual future with us.
- 3-column roles: ML Engineers / Video + Frontend / Data + Linguists / DevOps + Cloud / Community.
- CTA: Star the repo · Open an issue · Share this deck.
- Repo: github.com/shivaram19/open-open-computer

Use real data and content from above. Do not use lorem ipsum. Make it visually stunning and immediately understandable.
"""


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ],
        temperature=0.5,
        max_tokens=4096,
    )
    html = resp.choices[0].message.content.strip()
    for fence in ["```html", "```"]:
        if html.startswith(fence):
            html = html[len(fence):]
        if html.endswith("```"):
            html = html[:-3]
    html = html.strip()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved Swiss deck to {OUTPUT}")


if __name__ == "__main__":
    main()
