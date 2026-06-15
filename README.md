# Open Open Computer 🌐🤖🎬

> **We are building the open infrastructure for a multilingual, agent-native internet.**

One source video. Twenty-two languages. Dozens of platform-ready clips. Zero black boxes.

[![Signal Network Tests](https://img.shields.io/badge/Signal%20Network-35%2F35%20passing-brightgreen)](#signal-network)
[![ACN Tests](https://img.shields.io/badge/ACN-media%20tools%20%2B%20MCP%20bridge-blue)](#acn)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange)](#)

---

## 🎯 The Intention

Most of the world’s knowledge is trapped in a handful of languages. In India alone, **22 scheduled languages** and thousands of dialects mean that civic, economic, and educational content rarely reaches people in the tongue they understand best.

We think that’s fixable — and that the fix should be **open, inspectable, and forkable**.

**Open Open Computer** is an umbrella project for agent-native tools that let creators, NGOs, journalists, and developers:

- Turn one piece of source media into **hyper-local variants** automatically.
- Run everything on **open-source models** and their own infrastructure.
- Orchestrate the whole flow through **collaborative AI agents** with security, audit, and access control built in.
- Publish everywhere people already watch — from YouTube Shorts to WhatsApp Status.

We are not building a closed SaaS. We are building a **public utility** for regional media.

---

## 🧱 What’s Inside

This repo is a set of composable building blocks. See [`UNIFIED_BUILD_PLAN.md`](UNIFIED_BUILD_PLAN.md) for the full map.

| Block | What it does | Entry point |
|---|---|---|
| **🧠 ACN** — Agent Collaboration Network | Secure multi-agent runtime with RBAC, audit, and an MCP bridge for media tools. | `acn/src/` |
| **📡 Signal Network** | End-to-end pipeline: video → ASR → translation → clip extraction → caption burn → publish. | `signal-network/` |
| **🛠️ Experiments** | GPU VM setup, model downloads, and validation scripts for Bernini, IndicConformer, IndicTrans2. | `experiments/` |
| **🚀 Landing Pages** | Lightweight public demos and product entry points. | `open-computer-use-landing/`, `picocloth-landing/` |
| **📢 Pitch Decks** | Recruitment and share assets (HTML, PPTX, Markdown) for social media. | `docs/share.html` |

---

## ⚡ The Magic in 30 Seconds

```
One Telugu video about inflation
        │
        ▼
┌─────────────────┐
│  Signal Network │
│  ingest → ASR   │  IndicConformer
│  → translate    │  IndicTrans2
│  → clip → render│  Revideo / FFmpeg
│  → publish      │  Azure Blob + socials
└─────────────────┘
        │
        ▼
  Marathi clip for Maharashtra
  Hindi clip for Telangana
  SRTs, manifests, thumbnails
```

All happening inside an agent runtime that logs who asked for what, checks permissions, and routes the work to the right GPU worker.

---

## 🌍 Why This Matters

- **Scale:** Manual dubbing and editing cannot serve a billion people in their own languages.
- **Access:** Regional audiences deserve news, education, and opportunities in their native tongue.
- **Ownership:** Open-source means no API lock-in, no surprise pricing, no opaque algorithms deciding what gets said.
- **Agency:** Any community can fork the pipeline and adapt it to their language, culture, and platforms.

---

## 🚦 Current Status

- ✅ GPU VM running CUDA 12.5 + cuDNN 9
- ✅ IndicConformer ASR and IndicTrans2 translation on GPU
- ✅ Signal Network spine + fan-out: **35/35 tests passing**
- ✅ Azure Blob Storage publisher implemented
- 🔄 Real platform publishers (YouTube, Instagram, TikTok) in progress
- 🔄 True Revideo 9:16 template rendering in progress
- 🔄 Web dashboard for monitoring uploads in progress

---

## 🤝 Join the Build

We are actively looking for builders who care about open AI and multilingual access.

- **ML Engineers** — optimize ASR/translation on GPU, ONNX, quantization.
- **Video / Frontend Devs** — Revideo templates, caption styling, web dashboard.
- **Data & Linguists** — improve Indic transcripts, region hashtags, demographic profiles.
- **DevOps / Cloud** — Azure deployments, CI/CD, cost-efficient GPU scheduling.
- **Community** — content testing, feedback loops, regional outreach.

**Repo:** [github.com/shivaram19/open-open-computer](https://github.com/shivaram19/open-open-computer)

**Quick entry points:**
- Read the plan: [`UNIFIED_BUILD_PLAN.md`](UNIFIED_BUILD_PLAN.md)
- Explore the pipeline: [`signal-network/README.md`](signal-network/README.md)
- View the pitch deck: [`docs/share.html`](docs/share.html)

---

## 📜 License

Apache 2.0 — fork it, run it, improve it, share it.

*Built in public. For everyone who speaks a language the internet forgot.*
