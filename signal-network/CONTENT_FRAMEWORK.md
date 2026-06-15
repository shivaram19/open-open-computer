# Signal Network Content Framework

A walk-through of the pipeline dimensions: **purpose → prepare → structure → language → content → purpose selection**.

---

## 1. Purpose

**Why the pipeline exists.**

Signal Network turns one source video into **N languages × M formats × P platforms** of hyper-local edutainment content without manual editing.

Primary purposes:
- **Awareness:** Explain civic/economic issues (inflation, health, water, jobs) in local languages.
- **Engagement:** Format as short-form vertical video (Reels/Shorts/WhatsApp status) for regional audiences.
- **Scale:** Automate so a single input fans out to dozens of regional variants.

Example purpose for the GPU run:
> Inform Maharashtra audiences about salt/inflation in their local language with a price overlay and translated captions.

---

## 2. Prepare

**What must be ready before running the pipeline.**

### Infrastructure
- GPU VM with CUDA 12.5 + cuDNN 9 (e.g. Massed Compute `gpu_1x_a6000`).
- Two Python environments:
  - Bernini env (3.11) for image/video generation.
  - Signal env (3.10) for ASR, translation, pipeline API.

### Models
| Model | Location / ID | Role |
|---|---|---|
| Bernini-R 1.3B | `ByteDance/Bernini-R-1.3B-Diffusers` | Media generation (ACN) |
| IndicConformer 600M | `ai4bharat/indic-conformer-600m-multilingual` | ASR for 22 Indic languages |
| IndicTrans2 1B | `ai4bharat/indictrans2-indic-indic-1B` | Indic→Indic translation |

### Inputs
- Source video with clear speech in the source language.
- Topic keywords (e.g. `inflation`, `salt`).
- Target region(s) or auto-ranked regions.

---

## 3. Structure

**The end-to-end pipeline architecture.**

```
Source Video
    │
    ▼
┌─────────────┐
│  Ingest     │  ffmpeg → 16 kHz mono WAV
└─────────────┘
    │
    ▼
┌─────────────┐
│  ASR        │  IndicConformer → word-level Telugu segments
└─────────────┘
    │
    ▼
┌─────────────┐
│  Translate  │  IndicTrans2 → mr, hi, ta, ...
└─────────────┘
    │
    ▼
┌─────────────┐
│  Clip       │  SignalClipper extracts 2–90 s signal windows
└─────────────┘
    │
    ▼
┌─────────────┐
│  Render     │  Revideo / FFmpeg caption burn
└─────────────┘
    │
    ▼
┌─────────────┐
│  Publish    │  File manifest (+ future platform publishers)
└─────────────┘
```

Output structure per run:
- `{stem}_{src}.srt` — source-language transcript
- `{stem}_{src}_{tgt}.srt` — translated captions
- `{stem}_{tgt}.mp4` — captioned output video
- `fanout_manifest.json` — regional variants metadata

---

## 4. Language

**How languages are handled.**

- **Source language:** Short code (`te`, `hi`, `mr`, ...).
- **ASR:** IndicConformer accepts the same short code directly.
- **Translation:** IndicTrans2 uses FLORES-style codes mapped internally:
  - `te` → `tel_Telu`
  - `ta` → `tam_Taml`
  - `hi` → `hin_Deva`
  - `mr` → `mar_Deva`
- **Target languages:** Determined by region profile (`demographics.py`) or CLI `--target-langs`.

Current supported source/target pairs follow IndicTrans2’s Indic→Indic coverage (22 scheduled languages).

---

## 5. Content

**What gets generated.**

### Spine outputs
- **Source SRT:** Telugu word-level timestamps from IndicConformer.
- **Translated SRTs:** Hindi, Marathi, Tamil, etc.
- **Captioned videos:** Source video with burned translated subtitles.

### Fan-out outputs
- **Regional variants:** Per-region, per-language clip SRTs.
- **Price overlay:** Auto-generated from signal data (e.g. `Salt ధర: ₹45/kg (+12%)`).
- **Captions/hashtags:** Hook sentence + region-specific hashtags.
- **Manifest JSON:** Maps every variant to region, language, clip timing, and file paths.

### Example manifest entry
```json
{
  "region_id": "maharashtra",
  "language": "hi",
  "clip_start": 2.24,
  "clip_end": 6.88,
  "clip_path": "",
  "srt_path": "/home/Ubuntu/.../clip_2_7_hi.srt",
  "caption": "ప్రభుత్వం దాన్ని తగ్గించాలి రైతులు ఇబ్బందులు పడుతున్నారు #maharashtra #te #inflation"
}
```

---

## 6. Purpose Selection

**How the pipeline decides what to produce for whom.**

`DemographicEngine` (`src/demographics.py`) selects targets based on:

1. **Topics** — user-provided keywords (`inflation`, `salt`).
2. **Region profiles** — each region has:
   - `languages` spoken there
   - `topics` it cares about
   - `best_time_ist` for posting
   - `format` (reels_9_16, whatsapp_status_friendly)
3. **Ranking** — regions are scored by topic overlap and ranked.
4. **Language filtering** — target languages are intersected with the region’s languages.

Example selection:
- Input topics: `inflation`
- Ranked region: `maharashtra` (topics include `inflation`)
- Maharashtra languages: `mr`, `hi`
- Generated variants: `maharashtra/mr`, `maharashtra/hi`

Manual override via CLI:
```bash
python scripts/run_fanout.py \
  --video sample.mp4 --source-lang te --topics inflation \
  --regions maharashtra telangana \
  --asr-model ai4bharat/indic-conformer-600m-multilingual \
  --translator-model /home/Ubuntu/models/indictrans2 \
  --device cuda:0
```

---

## Quick Reference

| Word | Pipeline mapping |
|---|---|
| Purpose | Hyper-local edutainment at scale |
| Prepare | GPU VM + models + source video |
| Structure | Ingest → ASR → Translate → Clip → Render → Publish |
| Language | 22 Indic languages via IndicConformer + IndicTrans2 |
| Content | SRTs, captioned videos, overlays, fan-out manifest |
| Purpose Selection | DemographicEngine matches topics → regions → languages |
