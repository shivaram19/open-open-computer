#!/usr/bin/env bash
# Setup script to run on the GPU VM for ComfyUI + Bernini + HyperFrames + Signal Network.
# This script is idempotent and logs everything to /tmp/vm_setup.log.

set -euo pipefail

LOG=/tmp/vm_setup.log
exec > >(tee -a "$LOG") 2>&1

echo "=== VM setup started at $(date -Iseconds) ==="

# ── System packages ──
sudo apt-get update
sudo apt-get install -y \
    git git-lfs \
    ffmpeg \
    build-essential \
    python3 python3-venv python3-dev python3-pip \
    curl wget

# ── CUDA Toolkit 12.5 + cuDNN 9 (required for flash-attn and IndicConformer ONNX GPU) ──
if ! command -v nvcc &> /dev/null; then
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt-get update
    sudo apt-get install -y cuda-toolkit-12-5
fi
sudo apt-get install -y libcudnn9-cuda-12 cudnn9-cuda-12
export CUDA_HOME="/usr/local/cuda-12.5"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

# ── UV (fast Python package manager) ──
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv &> /dev/null; then
    mkdir -p "$HOME/.local/bin"
    curl -Lo "$HOME/.local/bin/uv" https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu
    chmod +x "$HOME/.local/bin/uv"
    curl -Lo "$HOME/.local/bin/uvx" https://github.com/astral-sh/uv/releases/latest/download/uvx-x86_64-unknown-linux-gnu
    chmod +x "$HOME/.local/bin/uvx"
fi

# ── Managed Python versions ──
# Ubuntu 24.04 does not ship python3.11/3.10 in default repos, so let uv install them.
uv python install 3.11 3.10

# ── Node 22 ──
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# ── Workspace (use the synced project directory) ──
WORKSPACE="/home/Ubuntu/deeptech/experiments"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# ── ComfyUI ──
if [ ! -d ComfyUI ]; then
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git
fi
cd ComfyUI
uv venv --clear --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
# Install a small model for quick smoke test
mkdir -p models/checkpoints
cd ..

# ── Bernini ──
if [ ! -d Bernini ]; then
    git clone --depth 1 https://github.com/bytedance/Bernini.git
fi
cd Bernini
uv venv --clear --python 3.11 .venv
source .venv/bin/activate
# Install torch first so flash-attn build can import it
uv pip install torch==2.5.1+cu124 --extra-index-url https://download.pytorch.org/whl/cu124
# flash-attn needs these build deps present when --no-build-isolation is used
uv pip install packaging setuptools wheel
uv pip install flash-attn==2.8.3 --no-build-isolation
# Install remaining requirements (skip flash-attn since it is already built)
grep -v '^flash-attn' requirements.txt > /tmp/bernini-requirements-no-flash.txt
uv pip install -r /tmp/bernini-requirements-no-flash.txt --no-build-isolation
uv pip install torchvision==0.20.1+cu124 --index-url https://download.pytorch.org/whl/cu124
uv pip install --no-deps git+https://github.com/ByteDance-Seed/VeOmni.git@v0.1.10
# Test + extras needed by ACN and IndicTrans2
uv pip install pytest sentencepiece mcp
cd ..

# ── HyperFrames ──
if [ ! -d hyperframes ]; then
    git clone --depth 1 https://github.com/heygen-com/hyperframes.git
fi
cd hyperframes
rm -rf demo-video
npx hyperframes init demo-video
cd demo-video
npm install
cd ../..

# ── Signal Network GPU dependencies ──
# Isolated Python 3.10 env matches the signal-network Dockerfile
if [ ! -d signal-env ]; then
    uv venv --clear --python 3.10 signal-env
fi
source signal-env/bin/activate
uv pip install \
    nemo-toolkit[asr] \
    transformers \
    torch \
    torchaudio \
    torchcodec \
    "onnxruntime==1.20.1" \
    "onnx==1.20.1" \
    "onnxruntime-gpu==1.20.1" \
    indic-nlp-library \
    fastapi uvicorn redis rq \
    pytest fakeredis \
    gtts \
    azure-storage-blob
# IndicTrans2 is used via HuggingFace transformers (no source install needed).
# IndicConformer ASR is gated; accept the HF license or use --asr-model to switch models.
mkdir -p "$HOME/models"

echo "=== VM setup finished at $(date -Iseconds) ==="
echo "Next: download models and run experiments."
