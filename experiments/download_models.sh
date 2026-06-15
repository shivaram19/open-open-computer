#!/usr/bin/env bash
# Download the models we need on the GPU VM.
# Run this after vm_setup.sh finishes.

set -euo pipefail

LOG=/tmp/download_models.log
exec > >(tee -a "$LOG") 2>&1

echo "=== Model download started at $(date -Iseconds) ==="

# Use the Bernini venv which has huggingface-cli
export PATH="$HOME/.local/bin:$PATH"
cd /home/Ubuntu/deeptech/experiments/Bernini
source .venv/bin/activate

MODELS_DIR="$HOME/models"
mkdir -p "$MODELS_DIR"

# ── Bernini-R 1.3B ──
if [ ! -d "$MODELS_DIR/Bernini-R-1.3B-Diffusers" ]; then
    echo "Downloading Bernini-R 1.3B..."
    huggingface-cli download ByteDance/Bernini-R-1.3B-Diffusers \
        --local-dir "$MODELS_DIR/Bernini-R-1.3B-Diffusers" \
        --local-dir-use-symlinks False
else
    echo "Bernini-R 1.3B already present."
fi

# ── IndicConformer Telugu (AI4Bharat/IndicConformer) ──
# NeMo downloads models on first use; pre-fetch here if a direct URL is known.
# For now, we ensure the NeMo cache dir exists.
mkdir -p "$HOME/.cache/torch/NeMo"

# ── IndicTrans2 ──
# Try the public unrestricted variant first; fall back to gated default.
INDICTRANS_MODEL="${INDICTRANS_MODEL:-ai4bharat/indictrans2-indic-indic-1B}"
if [ ! -d "$MODELS_DIR/indictrans2" ]; then
    echo "Downloading IndicTrans2 ($INDICTRANS_MODEL)..."
    huggingface-cli download "$INDICTRANS_MODEL" \
        --local-dir "$MODELS_DIR/indictrans2" \
        --local-dir-use-symlinks False || echo "WARN: IndicTrans2 download failed (gated model?)"
else
    echo "IndicTrans2 already present."
fi

echo "=== Model download finished at $(date -Iseconds) ==="
echo "Models in: $MODELS_DIR"
ls -lh "$MODELS_DIR"
