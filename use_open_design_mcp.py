#!/usr/bin/env python3
"""Generate a Signal Network pitch deck via the Open Design MCP server."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT = ROOT / "docs" / "Signal_Network_OpenDesign_Deck.html"

PROMPT = """Create a polished, single-file HTML slide deck for recruiting open-source contributors to Signal Network.

Brand:
- Name: Signal Network
- Tagline: "Open-source hyper-local edutainment at scale — one video → N languages × M formats × P platforms."
- Tone: ambitious, inclusive, builder-friendly
- Colors: deep slate (#0F172A) background, cyan accent (#06B6D4), clean white text

Slides to include (one per slide, 16:9 aspect):
1. Title slide: Signal Network + tagline + "Open-source · Indic-languages · GPU-powered"
2. The Problem: 22 languages, info gap, manual editing doesn't scale
3. The Solution: one source video → dozens of regional short-form clips, fully automated
4. How It Works: pipeline diagram — Ingest → ASR (IndicConformer) → Translate (IndicTrans2) → Clip → Render (Revideo/FFmpeg) → Publish (Azure Blob + platforms)
5. Built & Tested Stack: table with GPU VM, IndicConformer, IndicTrans2, Bernini, Signal Network pipeline, Azure Blob Storage; include test pass badges (20/20, 35/35)
6. Publish Everywhere: YouTube Shorts, Instagram Reels, TikTok, WhatsApp Status, Telegram, X, LinkedIn, Facebook
7. What's Already Working: CUDA 12.5 VM validated, ASR + translation on GPU, 35/35 tests passing, Azure publisher ready
8. Immediate Next Steps: wire Azure creds, true Revideo templates, platform publishers, web dashboard, crowdsource demographics
9. Join the Build: roles for ML Engineers, Video/Frontend devs, Data/Linguists, DevOps/Cloud, Community; GitHub repo link: github.com/shivaram19/open-open-computer (Signal Network folder)

Requirements:
- Use a modern, clean design with large typography and generous whitespace.
- Each slide should be a full-screen section with smooth CSS scroll-snap behavior.
- Include keyboard navigation (arrow keys / page down) and clickable dot navigation.
- Export-ready: self-contained HTML with inline CSS and no external dependencies except optional Google Fonts loaded from CDN.
- Add a small footer on each slide with the repo URL and "Share on LinkedIn · X · WhatsApp · Telegram".
"""


def mcp_call(server_proc, method, params):
    req = {"jsonrpc": "2.0", "id": server_proc["id"], "method": method, "params": params}
    server_proc["id"] += 1
    server_proc["proc"].stdin.write((json.dumps(req) + "\n").encode())
    server_proc["proc"].stdin.flush()
    # Read until matching id response
    while True:
        line = server_proc["proc"].stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed stdout")
        try:
            msg = json.loads(line.decode())
        except json.JSONDecodeError:
            continue
        if msg.get("id") == req["id"]:
            return msg


def main():
    env = os.environ.copy()
    env.update({
        "OD_DAEMON_URL": "http://localhost:7456",
        "BYOK_BASE_URL": "https://api.openai.com/v1",
        "BYOK_API_KEY": env.get("OPENAI_API_KEY", ""),
        "BYOK_MODEL": "gpt-4o",
        "BYOK_PROVIDER": "openai",
    })

    if not env["BYOK_API_KEY"]:
        print("OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    proc = subprocess.Popen(
        ["npx", "-y", "open-design-mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/tmp",
        env=env,
        text=False,
    )

    server = {"proc": proc, "id": 1}

    # Initialize
    init = mcp_call(server, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "kimi", "version": "1.0"},
    })
    if "result" not in init:
        print("MCP initialize failed:", init, file=sys.stderr)
        proc.terminate()
        sys.exit(1)

    print("MCP initialized, generating deck (this may take 1–3 minutes)...")

    result = mcp_call(server, "tools/call", {
        "name": "od_generate_design",
        "arguments": {
            "kind": "deck",
            "prompt": PROMPT,
            "maxTokens": 4096,
        },
    })

    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()

    if result.get("error"):
        print("Generation error:", result["error"], file=sys.stderr)
        sys.exit(1)

    content = result["result"]["content"]
    if isinstance(content, list) and len(content) > 0:
        html = content[0].get("text", "")
    else:
        html = str(content)

    if not html.strip():
        print("Empty response from Open Design", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved Open Design deck to {OUTPUT}")


if __name__ == "__main__":
    main()
