# Unified Build Plan — Building Blocks & How They Fit

This repo is a collection of **composable building blocks** that, wired together, become an open-source, agent-native platform for regional media generation and distribution.

---

## 1. The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER / COMMUNITY                            │
│   (creators, NGOs, journalists, contributors)                       │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
    ┌──────────────▼──────────────┐     ┌──────────────────────────┐
    │   Landing Pages / Demos     │     │   Pitch Decks / Docs     │
    │   • open-computer-use       │     │   • Swiss deck           │
    │   • picocloth               │     │   • PPTX / Markdown      │
    └──────────┬──────────────────┘     └────────────┬─────────────┘
               │                                      │
               └──────────────┬───────────────────────┘
                              │
            ┌─────────────────▼──────────────────────┐
            │   ACN — Agent Collaboration Network    │
            │   (control plane + multi-agent runtime) │
            │                                         │
            │  • Security, RBAC, Audit               │
            │  • TwinTool registry                   │
            │  • MCP server bridge                   │
            │  • Planner / orchestrator agents       │
            └─────────────────┬──────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐   ┌──────────▼──────────┐  ┌──────▼──────┐
│  ACN Media   │   │   Signal Network    │  │  Experiment │
│    Tools     │   │   (content pipeline)│  │   Runners   │
│              │   │                     │  │             │
│ • ComfyUI    │   │ • ingest / ASR      │  │ • GPU VM    │
│ • Bernini    │   │ • translate / clip  │  │   setup     │
│ • HyperFrames│   │ • render / publish  │  │ • Model     │
└──────┬───────┘   └──────────┬──────────┘  │   download  │
       │                      │             └──────┬──────┘
       │                      │                    │
       └──────────────────────┼────────────────────┘
                              │
               ┌──────────────▼──────────────┐
               │   Cloud Storage + Social    │
               │   • Azure Blob Storage      │
               │   • YouTube / Reels / TikTok│
               │   • WhatsApp / Telegram / X │
               └─────────────────────────────┘
```

---

## 2. Building Blocks

### 2.1 ACN — Agent Collaboration Network (`acn/`)

**What it is:** A secure, multi-agent runtime that can plan tasks, enforce permissions, audit actions, and expose tools over MCP.

**Key pieces:**
| Piece | File(s) | Role |
|---|---|---|
| Security baseline | `acn/src/security/audit.py`, `rbac.py` | Authentication, authorization, audit logging for every tool call. |
| Media service | `acn/src/generation/media_service.py` | Adapters for ComfyUI, HyperFrames, and Bernini backends. |
| Media tools | `acn/src/generation/media_tools.py` | `TwinTool` wrappers that add tenant/agent context and RBAC. |
| MCP bridge | `acn/src/generation/mcp_server.py` | Exposes ACN tools to any MCP-compatible client (Kimi, Claude Code, Cursor, etc.). |
| Tests | `acn/tests/generation/` | Validates the MCP bridge and media tools. |

**Where it fits:** ACN is the **control plane**. It decides *what* to build, *who* can invoke it, and *what happened*. Signal Network and the media backends are the *workers* it orchestrates.

---

### 2.2 Signal Network (`signal-network/`)

**What it is:** A deterministic pipeline that turns one source video into dozens of language-specific, platform-ready short-form clips.

**Key pieces:**
| Piece | File(s) | Role |
|---|---|---|
| Spine | `src/pipeline.py`, `src/asr.py`, `src/translate.py` | Extract audio → transcribe with IndicConformer → translate with IndicTrans2. |
| Clip extraction | `src/clipper.py`, `src/clip_pipeline.py` | Find viral moments and render per-language clip variants. |
| Targeting | `src/demographics.py` | Match topics to regions, languages, and posting times. |
| Publishing | `src/publishers.py` | Upload to Azure Blob Storage; stubs for YouTube, Instagram, TikTok. |
| API + jobs | `src/api.py`, `src/jobs.py`, `src/worker.py` | FastAPI + Redis queue for async pipeline runs. |
| Tests | `tests/` | 35/35 passing unit tests with mock models. |

**Where it fits:** Signal Network is the **content factory**. ACN agents can call it as a tool when the goal is “make a Telugu inflation video for Maharashtra.”

---

### 2.3 Experiments (`experiments/`)

**What it is:** Infrastructure-as-code, model downloaders, and validation scripts for the GPU VM and the models both ACN and Signal Network depend on.

**Key pieces:**
| Piece | File(s) | Role |
|---|---|---|
| VM setup | `vm_setup.sh`, `deploy_gpu_vm.sh`, `validate_gpu_vm.sh` | Idempotent CUDA/cuDNN/Python environment setup. |
| Model download | `download_models.sh`, `download_indicconformer.py` | Pull Bernini, IndicTrans2, IndicConformer. |
| Validation | `test_indictrans2_gpu.py`, `test_signal_network_real_translate.py`, `test_acn_bernini_real.py`, `run_signal_pipeline_real.py` | Prove each component works on real GPU hardware. |
| Plans | `GPU_VM_DEPLOYMENT_PLAN.md`, `BERNINI_SETUP_CHECKLIST.md`, `DEEP_DIVE_PLAN.md`, `FOUNDATION_BUILD_PLAN.md` | Human-readable runbooks. |

**Where it fits:** Experiments are the **provisioning layer**. They prepare the machine and models that ACN media tools and Signal Network consume at runtime.

---

### 2.4 Landing Pages (`open-computer-use-landing/`, `picocloth-landing/`)

**What it is:** Lightweight public HTML pages that explain specific product angles and collect interest.

**Where it fits:** Landing pages are the **front door**. They convert visitors into users or contributors and can embed demo videos produced by Signal Network.

---

### 2.5 Community / Recruitment Assets (`docs/`, `create_pitch_deck.py`, `generate_swiss_deck.py`)

**What it is:** Pitch decks (HTML, PPTX, Markdown) and scripts to regenerate them via Open Design / OpenAI.

**Where it fits:** These are the **growth layer**. They explain the project, attract contributors, and can be posted to LinkedIn, X, WhatsApp, Telegram, etc.

---

## 3. How the Blocks Work Together

### Scenario: “Generate and publish a regional video about salt prices.”

1. **ACN planner agent** receives the request: topic = `inflation`, source = Telugu video, target = Maharashtra & Telangana.
2. **ACN SecurityManager** checks the caller’s roles and logs the intent.
3. **Signal Network pipeline** is invoked:
   - `ingest.py` downloads/extracts audio.
   - `asr.py` (IndicConformer) transcribes Telugu speech.
   - `translate.py` (IndicTrans2) translates to Marathi and Hindi.
   - `clipper.py` extracts the strongest 45-second clip.
   - `clip_pipeline.py` burns translated captions and a price overlay.
4. **ACN media tools** optionally generate a thumbnail/B-roll via ComfyUI or Bernini.
5. **Publishers** upload the clip + SRT + manifest to **Azure Blob Storage**.
6. **Future platform publishers** post to YouTube Shorts, Instagram Reels, TikTok, etc.
7. **Landing pages** and **pitch decks** drive the next contributor or user to the repo.

---

## 4. Integration Points

| From | To | Mechanism |
|---|---|---|
| ACN agents | Signal Network | Function/tool call or MCP tool wrapper around `run_fanout.py`. |
| ACN agents | Media backends | `TwinTool` → `media_service.py` → ComfyUI / Bernini / HyperFrames. |
| Signal Network | Cloud storage | `AzureBlobPublisher` via `azure-storage-blob`. |
| Signal Network | Social platforms | Future `YouTubePublisher`, `InstagramPublisher`, etc. |
| Experiments | ACN + Signal Network | Pre-installed models and GPU VM ready for inference. |
| Landing pages / decks | Repo | Links to `github.com/shivaram19/open-open-computer`. |

---

## 5. Next Steps to Wire Everything

1. **ACN → Signal Network tool wrapper:** expose `run_fanout.py` as a TwinTool so ACN agents can invoke the pipeline with RBAC + audit.
2. **ACN → Azure upload:** reuse `AzureBlobPublisher` inside ACN’s media service for cloud storage of any generated asset.
3. **Signal Network platform publishers:** implement real YouTube/Instagram/TikTok uploaders behind ACN’s security layer.
4. **Experiments → reproducible environment:** turn `vm_setup.sh` into a Docker/Packer image so ACN can spin up workers anywhere.
5. **Landing pages → live demos:** add an embedded Signal Network output gallery and a contributor CTA.
6. **CI/CD:** run `signal-network` tests and `acn` tests in GitHub Actions on every push.

---

## 6. Repositories & Entry Points

- Main repo: `github.com/shivaram19/open-open-computer`
- Signal Network code: `signal-network/src/`
- ACN code: `acn/src/`
- GPU/infrastructure scripts: `experiments/`
- Live pitch deck: served via `docs/share.html` (temporary ngrok) or deploy `docs/` to a static host.
