# Signal Network

Deterministic, open-source pipeline for regional edutainment and hyper-local content automation.

One source video fans out into **N languages × M formats × P platforms** without manual editing.

## Phase 1: The Spine ✅ COMPLETE

Core pipeline: **video → audio → ASR → translation → captioned outputs**.

**Sensor:** `python3 -m pytest tests/test_spine.py -v` → 6 passed.

## Phase 2: FastAPI + Redis Job Queue ✅ COMPLETE

- `POST /jobs` — create job with `source_url` or `file_path`
- `GET /jobs/{id}` — poll status + outputs
- `POST /jobs/{id}/run` — synchronous run for testing
- Redis-backed queue + worker (`SpineWorker`)
- `yt-dlp` ingestion support

**Sensor:** `python3 -m pytest tests -v` → 12 passed.

## Phase 3: Clip Extraction + Revideo Templates ✅ COMPLETE

- `src/clipper.py` — signal-aware clip extraction (keywords, sentiment shift, duration)
- `src/clip_pipeline.py` — spine + clips + per-clip SRTs + Revideo rendering hook
- `templates/cooking_signal/` — 9:16 Revideo template with price overlay + captions

**Sensor:** `python3 -m pytest tests -v` → 16 passed.

## Phase 4: Demographic Targeting + Publishing ✅ COMPLETE

- `src/demographics.py` — region profiles + topic matching + content plans
- `src/publishers.py` — pluggable publishers (file manifest stub + OpenShorts stub)
- `src/fanout.py` — end-to-end regional fan-out

**Sensor:** `python3 -m pytest tests -v` → 22 passed.

## Phase 5: Signal Data Integration ✅ COMPLETE

- `src/signal_data/`
  - `commodity_prices.py` — CSV/API price fetcher with overlay formatting
  - `census.py` — district-level demographics stub
  - `news_rss.py` — regional news RSS stub
- `src/signal_injector.py` — topic → signal overlay generator
- `scripts/run_fanout.py` — single CLI entrypoint

**Sensor:** `python3 -m pytest tests -v` → 34 passed.

## Phase 6: Azure Blob Storage Publishing ✅ COMPLETE

- `src/publishers.py` — added `AzureBlobPublisher` using `azure-storage-blob`
- `scripts/run_fanout.py` — `--platforms` flag to publish to `file_manifest` and/or `azure_blob`
- `src/fanout.py` — default publisher includes Azure Blob when configured

**Sensor:** `python3 -m pytest tests -v` → 34 passed.

## CLI Usage

```bash
# Mock run (no model downloads)
python3 scripts/run_fanout.py \
  --video assets/sample.mp4 \
  --source-lang te \
  --topics inflation \
  --regions maharashtra telangana \
  --mock

# Production run (requires ASR + IndicTrans2 models)
python3 scripts/run_fanout.py \
  --video assets/sample.mp4 \
  --source-lang te \
  --topics inflation \
  --asr-model ai4bharat/indic-conformer-600m-multilingual \
  --translator-model ai4bharat/indictrans2-indic-indic-1B \
  --device cuda:0

# GPU VM example with Whisper fallback
python3 scripts/run_fanout.py \
  --video assets/sample.mp4 \
  --source-lang te \
  --topics inflation \
  --regions maharashtra \
  --asr-model openai/whisper-medium \
  --translator-model /home/Ubuntu/models/indictrans2 \
  --device cuda:0

# Publish rendered clips to Azure Blob Storage
export AZURE_STORAGE_CONNECTION_STRING="..."
export AZURE_STORAGE_CONTAINER="signal-network"
python3 scripts/run_fanout.py \
  --video assets/sample.mp4 \
  --source-lang te \
  --topics inflation \
  --platforms file_manifest azure_blob \
  --device cuda:0
```

### Model configuration

- `ASR_MODEL_ID` / `--asr-model` — ASR backend.
  - `ai4bharat/indic-conformer-600m-multilingual` (recommended) — gated; accept the license on HuggingFace first. Loads via custom `AutoModel` code and produces high-quality Indic transcripts with word-level timestamps.
  - `openai/whisper-medium` — public fallback that supports timestamps.
- `TRANSLATOR_MODEL_ID` / `--translator-model` — local path or HuggingFace id for IndicTrans2.
- `INFERENCE_DEVICE` / `--device` — `cpu`, `cuda`, or `cuda:0`.

### Azure publishing configuration

- `AZURE_STORAGE_CONNECTION_STRING` — Storage account connection string from `az storage account show-connection-string`.
- `AZURE_STORAGE_CONTAINER` — Destination container name (created beforehand with `az storage container create`).
- Uploaded blobs are prefixed with `signal-network/` by default.

## Refined Architecture (from research)

| Layer | Tool | License | Role |
|-------|------|---------|------|
| Ingestion | `yt-dlp` + `ffmpeg` | Open | Download/convert any source |
| ASR | AI4Bharat IndicConformer 600M | MIT | 22-language speech-to-text |
| Translation | AI4Bharat IndicTrans2 | Open | Direct Indic→Indic |
| Clip Extraction | AI-Youtube-Shorts-Generator / OpenShorts | MIT | Viral moment detection + crop |
| Templates | Revideo | MIT | Programmatic 9:16 video assembly |
| Caption Burn | FFmpeg + Subtitle Edit | Open | Deterministic subtitle rendering |
| Demographics | Indian Census GeoJSON + custom API | Open | Region/language targeting |
| Publishing | Azure Blob Storage + OpenShorts API / custom publishers | Open | Cloud upload + auto-post to Reels/Shorts/TikTok |
| Signal Logic | Custom FastAPI service | Open | Entertainment hook + embedded data |

## Repository layout

```
signal-network/
  src/
    ingest.py      # yt-dlp + ffmpeg audio extraction
    asr.py         # IndicConformer wrapper
    translate.py   # IndicTrans2 wrapper
    captions.py    # SRT + FFmpeg burn
    pipeline.py    # end-to-end orchestration
    api.py         # FastAPI service
    jobs.py        # Redis queue + worker
    schemas.py     # Pydantic models
  tests/           # unit tests with mock models
  deployment/      # Docker/VM deploy configs
  templates/       # Revideo templates (Phase 3)
  assets/          # sample inputs
  outputs/         # generated files
```

## Run the API locally

```bash
cd signal-network
# Requires Redis running on localhost:6379, or use fakeredis for tests
python3 -m uvicorn src.api:app --reload
```

## Roadmap

- Phase 1: Spine ✅
- Phase 2: FastAPI + Redis job queue + yt-dlp ingestion ✅
- Phase 3: Clip extraction + Revideo templates
- Phase 4: Demographic targeting + OpenShorts publishing
- Phase 5: Signal data integration (prices, census, news) ✅
- Phase 6: Azure Blob Storage publishing ✅
