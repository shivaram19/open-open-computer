#!/usr/bin/env python3
"""Regenerate the Signal Network deck with clearer, punchier messaging."""

import os
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parent
OUTPUT = ROOT / "docs" / "Signal_Network_OpenDesign_Deck.html"

SYSTEM = """You are a senior presentation designer and copywriter for open-source developer recruitment.
Create a single, self-contained HTML slide deck.
Rules:
- Output ONLY complete HTML. No markdown, no explanations.
- Self-contained: inline CSS/JS, Google Fonts allowed.
- 16:9 full-screen slides with CSS scroll-snap.
- One big idea per slide. Headlines must be short and punchy. Body text must be 3-5 bullets max, plain English.
- Use a strong visual hierarchy: huge headline, short subtitle, minimal body.
- Colors: background #0F172A, accent #06B6D4, text #F8FAFC, muted #94A3B8.
- Include dot navigation, keyboard arrow/PageDown navigation, and a footer on every slide with repo link + share links.
- Add simple entrance animations (fade/slide up) when navigating.
"""

USER = """Rewrite the Signal Network recruiting deck to communicate clearly and persuasively.

Project facts:
- Signal Network is an open-source pipeline that turns ONE source video into dozens of regional short-form clips automatically.
- It works for India’s 22 scheduled languages and thousands of dialects.
- It uses AI4Bharat IndicConformer for speech-to-text, AI4Bharat IndicTrans2 for translation, Bernini for media generation, and publishes to Azure Blob Storage + social platforms.
- Current status: GPU VM running, ASR + translation working on GPU, Signal Network pipeline has 35/35 tests passing, Azure publisher implemented.
- It is built for YouTube Shorts, Instagram Reels, TikTok, WhatsApp Status, Telegram Channels, X/Twitter, LinkedIn, and Facebook.
- Repo: github.com/shivaram19/open-open-computer (Signal Network folder)

Slide plan (8 slides):

1. Hook slide
   - Headline: "One video. Every language. Automatically."
   - Sub: Signal Network turns a single source video into hyper-local short-form content for India's regional audiences.
   - Footer tag: "Open-source · Indic-languages · GPU-powered"

2. The gap
   - Headline: "Most Indians can't access information in their own language."
   - Bullets: 22 official languages, thousands of dialects; civic and economic news stays in English/Hindi; manual dubbing and editing don't scale.

3. The product
   - Headline: "Signal Network fans out one video into N languages × M formats × P platforms."
   - Bullets: upload one video; get transcripts, translations, clips, captions, and publish manifests; choose regions or let the engine rank them.

4. How it works (4 steps, visual)
   - Headline: "Ingest → Understand → Localize → Publish"
   - Steps: 1. Extract clean audio, 2. Transcribe with IndicConformer, 3. Translate with IndicTrans2 + extract clips, 4. Burn captions and publish to Azure + social platforms.

5. Proof it works
   - Headline: "Built, tested, and running on GPU."
   - Bullets: CUDA 12.5 + cuDNN 9 GPU VM deployed; IndicConformer ASR + IndicTrans2 translation on GPU; 35/35 pipeline tests passing; Azure Blob Storage upload ready.

6. Where the content goes
   - Headline: "Publish everywhere people already watch."
   - Grid: YouTube Shorts, Instagram Reels, TikTok, WhatsApp Status, Telegram, X, LinkedIn, Facebook.

7. Why open-source
   - Headline: "Open infrastructure for a multilingual internet."
   - Bullets: transparent models and code; forkable for any region or language; no vendor lock-in, no black box.

8. Join us
   - Headline: "Build the multilingual future with us."
   - Roles: ML Engineers, Video/Frontend devs, Data & Linguists, DevOps/Cloud, Community.
   - CTA buttons: Star the repo, Open an issue, Share this deck.

Make the design feel premium and startup-pitch quality. Use gradients subtly, large type, and clear spacing.
"""


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER},
        ],
        temperature=0.6,
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
    print(f"Saved clearer deck to {OUTPUT}")


if __name__ == "__main__":
    main()
