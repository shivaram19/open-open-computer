#!/usr/bin/env bash
# Validation script for the GPU VM. Run after vm_setup.sh and download_models.sh.

set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
export CUDA_HOME=/usr/local/cuda-12.5
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

echo "=== GPU VM Validation ==="

# 1. CUDA
ssh-command() { true; }
nvidia-smi

# 2. Bernini env + import check
cd /home/Ubuntu/deeptech/experiments/Bernini
source .venv/bin/activate
python -c "import torch; print('torch:', torch.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
python -c "import flash_attn; print('flash-attn OK')"

# 3. Bernini single image test
python infer_single_gpu.py \
  --config /home/Ubuntu/models/Bernini-R-1.3B-Diffusers \
  --case assets/testcases/t2i/t2i.json \
  --num_frames 1 --guidance_mode t2v_apg
ls -lh assets/testcases/t2i/t2i_out.png

# 4. ACN tests
export PYTHONPATH=/home/Ubuntu/deeptech/acn/src:/home/Ubuntu/deeptech
cd /home/Ubuntu/deeptech
python -m pytest acn/tests/generation -q

# 5. Signal Network tests
cd /home/Ubuntu/deeptech/signal-network
source /home/Ubuntu/deeptech/experiments/signal-env/bin/activate
python -m pytest tests/ -q

# 6. Signal Network real translation sensor
cd /home/Ubuntu/deeptech/experiments
python test_signal_network_real_translate.py

echo "=== All validations passed ==="
