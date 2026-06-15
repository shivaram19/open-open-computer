# Bernini End-to-End Setup Checklist

Repo: `https://github.com/bytedance/Bernini.git`  
Paper: *Bernini: Latent Semantic Planning for Video Diffusion* (arXiv:2605.22344)

Use this checklist to go from a fresh machine to a working Bernini inference pipeline.

---

## 1. Hardware

- [ ] **NVIDIA GPU with CUDA compute capability ≥ 8.0** (Ampere or newer)
  - Minimum: RTX 3090 / A100 / A6000 (for 1.3B or smaller tasks)
  - Recommended: **H100 / H800 / H200** (for 14B model + FlashAttention-3)
- [ ] **VRAM:**
  - Bernini-R 1.3B: ~24 GB
  - Bernini-R 14B: ~80 GB (H100/A100 80 GB)
  - Full Bernini (7B planner + 14B renderer): ~80–100 GB
- [ ] **System RAM:** ≥ 64 GB recommended
- [ ] **Disk:** ≥ 100 GB free for code, conda env, and model weights
- [ ] **OS:** Linux (Ubuntu 22.04+ tested). Windows/macOS not officially supported.

---

## 2. System Software

- [ ] **CUDA Toolkit 12.4** installed and on `PATH`/`LD_LIBRARY_PATH`
  - Minimum: CUDA 12.3 if building FlashAttention-3 from source
- [ ] **NVIDIA Driver** ≥ 535 (matches CUDA 12.4)
- [ ] **Git** with LFS support (some test assets use LFS)
- [ ] **Conda** or **pyenv** for isolated Python 3.11.2 environment

Verify:
```bash
nvidia-smi
nvcc --version
python --version  # should be 3.11.2
```

---

## 3. Python Environment

- [ ] Create a Python 3.11.2 environment:
  ```bash
  conda create -n bernini python=3.11.2 -y
  conda activate bernini
  ```
- [ ] Clone the repo:
  ```bash
  git clone https://github.com/bytedance/Bernini.git
  cd Bernini
  ```

---

## 4. Python Dependencies

- [ ] Install base requirements:
  ```bash
  pip install -r requirements.txt
  ```
  This pins:
  - `torch==2.5.1+cu124`
  - `diffusers==0.35.2`
  - `accelerate==0.34.2`
  - `transformers==4.57.3`

- [ ] Install **Open-VeOmni** (required, all inference paths import it):
  ```bash
  pip install --no-deps git+https://github.com/ByteDance-Seed/VeOmni.git@v0.1.10
  ```
  > Use `--no-deps` so it does not override the pinned torch build.

- [ ] Install **FlashAttention** (pick one):
  - [ ] General CUDA GPUs (A100, A6000, RTX 3090/4090):
    ```bash
    pip install flash-attn==2.8.3
    ```
  - [ ] Hopper GPUs (H100/H800/H200) for FlashAttention-3:
    ```bash
    git clone https://github.com/Dao-AILab/flash-attention.git
    cd flash-attention && git checkout v2.8.3
    cd hopper && MAX_JOBS=$(nproc) python setup.py install --user
    ```

---

## 5. Model Weights

Choose one pipeline:

### Option A: Bernini-R (renderer-only, simpler)

- [ ] **Bernini-R 1.3B** (lightweight):
  ```bash
  # HuggingFace repo: ByteDance/Bernini-R-1.3B-Diffusers
  export BERNINI_R_MODEL="ByteDance/Bernini-R-1.3B-Diffusers"
  ```
- [ ] **Bernini-R 14B** (best quality):
  ```bash
  export BERNINI_R_MODEL="ByteDance/Bernini-R-Diffusers"
  ```

### Option B: Full Bernini (planner + renderer)

- [ ] Download full weights:
  ```bash
  export BERNINI_MODEL="ByteDance/Bernini-Diffusers"
  ```

> Weights are downloaded automatically on first run via `diffusers` if `HF_HOME` has space and network access. For offline/air-gapped use, pre-download with `huggingface-cli`.

---

## 6. Optional: Prompt Enhancer (recommended)

- [ ] Set an OpenAI-compatible endpoint for prompt enhancement:
  ```bash
  export BERNINI_PE_API_KEY="sk-..."
  export BERNINI_PE_BASE_URL="https://api.openai.com/v1"
  export BERNINI_PE_MODEL="gpt-4o-mini"  # or any vision-capable chat model
  ```
- [ ] Or set `OPENAI_API_KEY` / `OPENAI_BASE_URL` as fallbacks.

---

## 7. Verify Installation

- [ ] Import check (catches missing VeOmni / torch mismatch):
  ```bash
  python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
  python -c "from bernini import ..."  # or run the actual inference import
  ```
- [ ] Download Bernini-R weights (diffusers format):
  ```bash
  pip install -U huggingface_hub
  hf download ByteDance/Bernini-R-1.3B-Diffusers \
      --local-dir pretrained_models/Bernini-R-1.3B-Diffusers
  ```
- [ ] Run a minimal single-GPU text-to-image test:
  ```bash
  python infer_single_gpu.py \
      --config pretrained_models/Bernini-R-1.3B-Diffusers \
      --case assets/testcases/t2i/t2i.json \
      --num_frames 1 \
      --guidance_mode t2v_apg
  ```
- [ ] Or use the task-specific helper script:
  ```bash
  export BERNINI_R_CONFIG=./pretrained_models/Bernini-R-1.3B-Diffusers
  bash scripts/bernini_r/run_t2i.sh
  ```

---

## 8. Run a Bundled Case File

- [ ] Inspect example case files:
  ```bash
  ls assets/testcases/
  ```
- [ ] Run one example:
  ```bash
  python run_case.py --case assets/testcases/t2v/example.json
  ```
  (Script names vary — check `docs/bernini.md` or `docs/bernini_r.md`.)

---

## 9. Gradio Demo (optional)

- [ ] Launch the UI:
  ```bash
  python gradio_demo.py --config pretrained_models/Bernini-R-1.3B-Diffusers --port 7860
  ```
- [ ] Open the printed local URL in a browser.

---

## 10. Common Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `CUDA out of memory` | Model too large for GPU | Use 1.3B, enable CPU offloading, or use a larger GPU |
| `No module named 'veomni'` | VeOmni not installed | Re-run the VeOmni install step |
| `flash_attn` import error | FlashAttention not built for your CUDA/PyTorch | Install matching `flash-attn` wheel or use SDPA fallback |
| `torch` CPU-only build | Wrong torch index / overwritten by dep | Re-install `torch==2.5.1+cu124` from the CUDA index |
| Download hangs / 403 | HuggingFace auth or rate limit | `huggingface-cli login` or set `HF_TOKEN` |
| Python 3.10 runtime errors | Bernini requires Python 3.11.2 | Use conda/pyenv with exact Python version |

---

## Current Environment Gap

The local machine where this checklist was written has:
- Python 3.10.12 (Bernini needs 3.11.2)
- No NVIDIA GPU / CUDA visible
- Node 22 + FFmpeg (fine for HyperFrames, irrelevant for Bernini)

**Conclusion:** Bernini inference cannot run here. Use this checklist on a CUDA-equipped workstation or cloud instance (e.g., NVIDIA H100 on Massed Compute / Lambda / RunPod).
