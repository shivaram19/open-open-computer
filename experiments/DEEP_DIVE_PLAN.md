# Deep-Dive Plan: ComfyUI + Bernini + HyperFrames

**Goal:** Run each tool end-to-end, exercise its core features, and understand how they could integrate with ACN agents.

**Constraint:** Current machine has no GPU and no CUDA. ComfyUI/Bernini need GPU for real inference. HyperFrames works locally.

---

## Phase 1 — Local Pilot Checks (no cost)

These verify what we can do without spending money.

| # | Check | Expected outcome | Status |
|---|-------|------------------|--------|
| 1 | HyperFrames `npm run render` on default project | Produces a 10s MP4 | ✅ Done (24.9s render, 25.6 KB output) |
| 2 | HyperFrames `npm run check` (lint/validate/inspect) | Passes | ✅ Done (0 errors) |
| 3 | HyperFrames `npm run dev` (preview server) | Serves live preview | ✅ Done (serves HTML; port 3000 busy, use `--port`) |
| 4 | ComfyUI `python main.py --cpu` starts | Server starts, UI reachable | ✅ Done |
| 5 | ComfyUI no-model smoke test | Loads UI, shows no checkpoints | ✅ Done (`/system_stats` responds) |
| 6 | Bernini Python 3.11 venv imports | torch/diffusers/transformers/veomni import | ✅ Done |
| 7 | Bernini `--help` on inference scripts | Shows args without crashing | ❌ Hard blocker: `ValueError: 不能在fa2和fa3都不支持的情况下工作！！！！` |
| 8 | Document local limitations | Clear list of what cannot run here | ✅ Done below |

### Local limitations found

- **Bernini cannot run at all without GPU/CUDA.** It raises a `ValueError` at import time because neither FlashAttention-2 nor FlashAttention-3 is available. Even `--help` fails.
- **ComfyUI runs in CPU mode** but generating images/videos will be extremely slow and limited by 16 GB RAM.
- **HyperFrames is fully functional locally** because it renders with headless Chrome + FFmpeg on CPU.

### Extra dependency found for Bernini

`torchvision==0.20.1+cu124` was missing from `requirements.txt` and had to be installed manually. The VM setup script includes it.

---

## Phase 2 — GPU VM Plan (requires approval, costs money)

### Option A: Cost-effective exploration
- **Instance:** `gpu_1x_a6000` (1× RTX A6000, 48 GB VRAM)
- **Cost:** ~$0.57/hour
- **Can run:**
  - ComfyUI with SDXL / Flux / video models
  - Bernini-R 1.3B
  - HyperFrames (also works on CPU, but GPU helps preview)
- **Cannot run:** Bernini-R 14B or full Bernini 7B+14B (need 80 GB)

### Option B: Full feature coverage
- **Instance:** `gpu_1x_h100` (1× H100, 80 GB VRAM)
- **Cost:** ~$2.73/hour
- **Can run:**
  - Everything in Option A
  - Bernini-R 14B
  - Full Bernini (7B planner + 14B renderer)
  - FlashAttention-3

### Option C: Balanced
- **Instance:** `gpu_1x_l40s` (1× L40S, 48 GB VRAM)
- **Cost:** ~$0.88/hour
- Similar to A6000 but newer architecture.

### VM Setup Script (to be run after launch)

```bash
# System
sudo apt update && sudo apt install -y git-lfs ffmpeg build-essential

# Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Node 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repos
git clone https://github.com/comfyanonymous/ComfyUI.git
git clone https://github.com/bytedance/Bernini.git
git clone https://github.com/heygen-com/hyperframes.git

# ComfyUI setup
python3.11 -m venv ComfyUI/.venv
source ComfyUI/.venv/bin/activate
pip install -r ComfyUI/requirements.txt

# Bernini setup
python3.11 -m venv Bernini/.venv
source Bernini/.venv/bin/activate
pip install -r Bernini/requirements.txt
pip install flash-attn==2.8.3
pip install --no-deps git+https://github.com/ByteDance-Seed/VeOmni.git@v0.1.10

# HyperFrames setup
cd hyperframes
npx hyperframes init demo-video
```

---

## Phase 3 — Experiment Matrix on GPU

### ComfyUI experiments
1. Install a small checkpoint (SDXL or Flux-dev) and generate an image
2. Build a workflow with: Load Checkpoint → CLIP Encode → KSampler → VAE Decode → Save Image
3. Add ControlNet (canny edge) to control composition
4. Add LoRA to steer style
5. Load an SVD model and generate a short video
6. Use ComfyUI API (not just UI) to submit a workflow

### Bernini experiments
1. Download Bernini-R 1.3B
2. Run T2I case file
3. Run I2I editing case
4. Run T2V case
5. Run V2V editing case
6. Try full Bernini 7B+14B (if on H100)
7. Try prompt enhancer with OpenAI-compatible endpoint

### HyperFrames experiments
1. Render default project
2. Add GSAP animation, text, images
3. Add video and audio tracks
4. Use catalog blocks (transitions, captions, charts)
5. Render with different quality settings
6. Expose a simple HyperFrames project as an agent-callable function

### ACN integration experiment
1. Use `acn/src/generation/media_service.py` and `media_tools.py`
2. Register ComfyUI + Bernini + HyperFrames tools in `TwinToolRegistry`
3. Have a `ToolCallingTwin` agent plan which backend to use for a media task
4. Log all calls through `SecurityManager`

---

## Phase 4 — Deliverables

1. `experiments/RESULTS.md` — what worked, what failed, latencies, output samples
2. `experiments/INTEGRATION_NOTES.md` — how each tool fits into ACN
3. Updated `acn/src/generation/` with working adapters and tests
4. Demo video(s) rendered by HyperFrames and/or generated by ComfyUI/Bernini

---

## Approval needed

Before I launch any GPU VM, confirm:
1. Which GPU tier (A / B / C or none)
2. Approximate budget/hours you are comfortable with
3. Whether to proceed with Phase 1 pilot checks first
