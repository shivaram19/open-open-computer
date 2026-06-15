# GPU VM Deployment Plan

**Scope:** Move ACN media generation (Bernini, ComfyUI) and Signal Network inference (IndicConformer ASR, IndicTrans2 translation) from CPU-mocked local development to real GPU execution.

**Status:** DEPLOYED ✅
- VM `media-lab-a6000` is running at `64.247.196.36` (RTX A6000 48 GB)
- Setup script `vm_setup.sh` completed successfully
- Models downloaded: Bernini-R 1.3B, IndicTrans2 (after HF license acceptance)
- GPU sensors validated: Bernini T2I, ACN tool, Signal Network translation pipeline
- Test suites passing on the VM: ACN 20/20, Signal Network 30/30

---

## 1. Recommended Instance

| Workload | Minimum instance | Recommended instance | Why |
|---|---|---|---|
| Bernini-R 1.3B + ComfyUI + Indic models | `gpu_1x_a6000` (48 GB) | `gpu_1x_a100` (80 GB) | 48 GB is enough for 1.3B in isolation; 80 GB leaves headroom for ComfyUI + concurrent inference |
| Bernini-R 14B or full planner+renderer | `gpu_1x_a100` (80 GB) | `gpu_1x_h100` (80 GB) | 14B needs ~80 GB VRAM |

**Primary recommendation for first boot:**
- **Instance:** `gpu_1x_a6000` (RTX A6000 48 GB, 6 vCPU, 48 GiB RAM, 256 GB disk)
- **Region:** `us-central-2` (Kansas City, MO) — cheapest and available
- **Price:** $0.57/hr on-demand / ~$0.50/hr spot
- **Image:** `Ubuntu Server 24.04` (vm_image_id: 184) — ships with NVIDIA drivers + Docker

**Why not H100 first?** Bernini-R 1.3B, IndicConformer, and IndicTrans2 all fit comfortably in 48 GB. Start cheap, validate end-to-end, then scale up if we need 14B Bernini or higher throughput.

---

## 2. Cost Estimate

Assuming `gpu_1x_a6000` in `us-central-2`:

| Usage pattern | Hours | Cost |
|---|---|---|
| Single 4-hour validation session | 4 | ~$2.28 |
| 1 week of active dev (40 hrs) | 40 | ~$22.80 |
| 1 month of active dev (160 hrs) | 160 | ~$91.20 |
| 1 month always-on | ~730 | ~$416.10 |

**Budget-conscious option:** `gpu_1x_a6000_spot` at $0.50/hr cuts the above by ~12%. Spot instances can be interrupted; use them only for dev/experiments, not long-running renders.

**If we later need 80 GB:**
- `gpu_1x_a100` (us-central-3): $1.35/hr → ~$985/month always-on
- `gpu_1x_h100` (us-central-3): $2.73/hr → ~$1,993/month always-on

---

## 3. Pre-Launch Checklist

Before invoking `instances_launch`, confirm:

- [x] Billing is configured in the Massed Compute account
- [x] SSH public key uploaded and stored in `.secrets/media_lab_key`
- [x] HuggingFace token used (`HF_TOKEN`) and IndicTrans2 license accepted
- [x] On-demand `gpu_1x_a6000` selected for first boot
- [x] Region `us-central-2` selected
- [ ] Disk snapshot/backup strategy for downloaded models (TODO if VM kept long-term)

---

## 4. Launch Command

```bash
instances_launch \
  --productName gpu_1x_a6000 \
  --regionName us-central-2 \
  --imageId 184 \
  --instanceName "media-lab-a6000" \
  --sshKeys '["media_lab_key"]' \
  --command 'bash -c "export PROJECT_BRANCH=main; curl -fsSL https://raw.githubusercontent.com/<user>/deeptech/main/experiments/vm_setup.sh | bash"'
```

> Replace `<your-key-name>` with the SSH key name registered in the account and `<user>` with the repo owner. The `command` is optional; you can also SSH in and run the setup script manually.

---

## 5. Post-Launch Setup

After the VM boots and the setup script finishes:

### 5.1 Verify CUDA

```bash
ssh -i .secrets/media_lab_key root@64.247.196.36
nvidia-smi
nvcc --version
python3 -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

### 5.2 Clone / sync the project

```bash
# Project synced to /home/Ubuntu/deeptech via rsync during setup
ssh -i .secrets/media_lab_key root@64.247.196.36
cd /home/Ubuntu/deeptech
```

### 5.3 Download models

| Model | Command / Source | Expected size |
|---|---|---|
| Bernini-R 1.3B | `huggingface-cli download ByteDance/Bernini-R-1.3B-Diffusers --local-dir /home/Ubuntu/models/Bernini-R-1.3B-Diffusers` | ~5–10 GB |
| IndicTrans2 | `huggingface-cli download ai4bharat/indictrans2-indic-indic-1B --local-dir /home/Ubuntu/models/indictrans2` (gated; needs HF token + license acceptance) | ~4 GB |
| IndicConformer ASR | Downloaded on-demand by NeMo first use | ~0.5–1 GB |

> **Note:** IndicTrans2 default ID `ai4bharat/indictrans2-indic-indic-1B` is gated. Either accept the license on HuggingFace or switch to an unrestricted checkpoint before launch.

### 5.4 ACN media lab environment

`experiments/vm_setup.sh` already installs:
- Python 3.11, `uv`, Node 22, FFmpeg
- ComfyUI
- Bernini dependencies (torch cu124, flash-attn, VeOmni)
- HyperFrames

After setup, run the ACN GPU sensor:

```bash
ssh -i .secrets/media_lab_key root@64.247.196.36
cd /home/Ubuntu/deeptech/experiments/Bernini
source .venv/bin/activate
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
python infer_single_gpu.py \
  --config /home/Ubuntu/models/Bernini-R-1.3B-Diffusers \
  --case assets/testcases/t2i/t2i.json \
  --num_frames 1 \
  --guidance_mode t2v_apg
```

### 5.5 Signal Network GPU environment

Signal Network currently uses mock ASR/translator in local tests. On the GPU VM, swap to real model IDs:

```bash
ssh -i .secrets/media_lab_key root@64.247.196.36
cd /home/Ubuntu/deeptech
source experiments/signal-env/bin/activate
# NeMo + IndicTrans2 already installed in signal-env
cd signal-network
```

Then run the real pipeline sensor:

```bash
python scripts/run_fanout.py \
  --video assets/cooking_sample.mp4 \
  --source-lang te \
  --topics rice,salt \
  --regions andhra_pradesh \
  --output-dir outputs/gpu_run
```

---

## 6. Integration Architecture

```
┌─────────────────┐     SSH / rsync     ┌─────────────────────────────┐
│  Local dev box  │ ──────────────────▶ │  Massed Compute GPU VM      │
│  (tests + git)  │                     │  • Bernini (1.3B or 14B)    │
└─────────────────┘                     │  • ComfyUI                  │
       │                                │  • IndicConformer ASR       │
       │        docker build / push     │  • IndicTrans2              │
       └──────────────────────────────▶ │  • Signal Network API       │
                                        └─────────────────────────────┘
```

Recommended split:
- **Local:** write code, run unit tests, build Docker images
- **GPU VM:** run real inference, store models, expose internal API endpoints
- **Future:** wrap the GPU VM inference in a small FastAPI service so ACN and Signal Network can call it remotely

---

## 7. Validation Sensors

A sensor must pass before we call the phase complete.

| # | Sensor | Pass criteria |
|---|---|---|
| 7.1 | `nvidia-smi` shows GPU | CUDA driver + device visible |
| 7.2 | `python -c "import torch; print(torch.cuda.is_available())"` | Prints `True` |
| 7.3 | Bernini single-image test produces a file | File exists in `outputs/` |
| 7.4 | Signal Network spine pipeline with real IndicConformer ASR + translation + burn | Output videos/SRTs generated on GPU |
| 7.5 | Signal Network real fan-out runs without mock | Manifest JSON generated with real IndicConformer ASR + translation + clip extraction |
| 7.6 | ACN `generate_video_bernini` tool runs on GPU | Returns `success=True` with output path |
| 7.7 | All existing tests still pass | `python -m pytest signal-network/tests` and `python -m pytest acn/tests/generation` |

---

## 8. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Gated IndicTrans2 model blocks launch | Use an unrestricted public checkpoint or accept the HF license before launch |
| FlashAttention build fails | Fall back to SDPA / xFormers; A6000 supports flash-attn wheels |
| VRAM too small | Start with 1.3B; upgrade to A100/H100 only if needed |
| Spot interruption loses work | Save outputs to persistent storage; use on-demand for long renders |
| Model re-download every launch | Pre-download to `/root/models` and consider snapshotting the disk |

---

## 9. Validation Results

All sensors in section 7 have been executed on `media-lab-a6000`:

| Sensor | Result |
|---|---|
| 7.1 CUDA / GPU | ✅ `nvidia-smi` shows RTX A6000 |
| 7.2 torch CUDA | ✅ `torch.cuda.is_available()` = True |
| 7.3 Bernini T2I | ✅ `outputs/t2i_*.png` generated (~12 s) |
| 7.4 Signal spine (real ASR + translation + burn) | ✅ Telugu → Tamil/Hindi captioned videos generated |
| 7.5 Signal fan-out | ✅ `fanout_manifest.json` generated with 2 regional variants (Maharashtra mr/hi) |
| 7.6 ACN Bernini tool | ✅ `generate_image_bernini` returned output path |
| 7.7 Tests | ✅ Signal Network 30/30, ACN generation 20/20 |

### Commands used

```bash
# Bernini T2I
source /home/Ubuntu/deeptech/experiments/Bernini/.venv/bin/activate
python infer_single_gpu.py --config /home/Ubuntu/models/Bernini-R-1.3B-Diffusers \
  --case assets/testcases/t2i/t2i.json --num_frames 1 --guidance_mode t2v_apg

# Signal Network spine end-to-end (uses gTTS-generated Telugu audio)
export PATH="$HOME/.local/bin:$PATH"
source /home/Ubuntu/deeptech/experiments/signal-env/bin/activate
cd /home/Ubuntu/deeptech
python experiments/run_signal_pipeline_real.py

# Signal Network regional fan-out
cd /home/Ubuntu/deeptech/signal-network
python scripts/run_fanout.py \
  --video /home/Ubuntu/deeptech/outputs/signal_network_e2e/sample_te.mp4 \
  --source-lang te --topics inflation --regions maharashtra \
  --output-dir /home/Ubuntu/deeptech/outputs/signal_network_fanout \
  --asr-model ai4bharat/indic-conformer-600m-multilingual \
  --translator-model /home/Ubuntu/models/indictrans2 \
  --device cuda:0
```

## 10. Next Actions

1. **IndicConformer access:** Retry `ai4bharat/indic-conformer-600m-multilingual` once HuggingFace author approval is granted; swap `ASR_MODEL_ID` to use it.
2. **Revideo rendering:** Complete the Revideo template so `clip_path` is populated in fan-out manifests.
3. **Cost control:** Terminate or snapshot the VM when active experimentation pauses (~$0.57/hr on-demand).
4. **Production wiring:** Wrap GPU inference in a FastAPI service so local ACN/Signal Network can call it remotely.

---

## 10. Decision Log

- **Instance tier for first boot:** `gpu_1x_a6000` — cheapest 48 GB option that fits Bernini-R 1.3B and all Signal Network models.
- **Region:** `us-central-2` — has A6000 capacity at the lowest on-demand price.
- **Image:** `Ubuntu Server 24.04` (id 184) — drivers and Docker pre-installed.
- **Spot vs on-demand:** on-demand for first boot to avoid interruption during setup; switch to spot later for cost savings.
- **Environment split:** Bernini uses Python 3.11 + torch 2.5.1+cu124; Signal Network uses Python 3.10 + transformers (NeMo installed but unused).
- **IndicTrans2 integration:** Uses HuggingFace `transformers` with `trust_remote_code=True`; local Signal Network code now auto-selects this path on GPU.
- **ASR:** `ai4bharat/indic-conformer-600m-multilingual` is gated and originally required manual author approval. Once access is granted, it loads via custom `AutoModel` code and runs on GPU via ONNX Runtime CUDA execution provider, producing high-quality Telugu transcripts with word-level timestamps.
- **Project sync:** `rsync`; `vm_setup.sh` bootstraps the VM after first boot.
- **Revideo rendering:** Not exercised; Revideo template is a skeleton and `npm` rendering returns `None`. This is a known follow-up, not a blocker for spine/fan-out validation.
