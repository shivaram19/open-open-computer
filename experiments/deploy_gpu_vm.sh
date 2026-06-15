#!/usr/bin/env bash
# GPU VM deployment helper for the media / Signal Network lab.
# This script only PLANs and PRINTs the launch command by default.
# Pass --launch to actually invoke the Massed Compute MCP / API.

set -euo pipefail

PRODUCT="gpu_1x_a6000"
REGION="us-central-2"
IMAGE_ID=184
INSTANCE_NAME="media-lab-a6000"
SSH_KEY_NAME="${SSH_KEY_NAME:-}"
SETUP_URL="https://raw.githubusercontent.com/$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]//;s/\.git$//' || echo '<user>/deeptech')/main/experiments/vm_setup.sh"

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --launch              Actually launch the VM (default is dry-run)
  --product NAME        GPU product (default: $PRODUCT)
  --region NAME         Region (default: $REGION)
  --image-id ID         VM image ID (default: $IMAGE_ID)
  --name NAME           Instance name (default: $INSTANCE_NAME)
  --ssh-key NAME        SSH key name registered in Massed Compute (required for launch)
  --setup-url URL       Post-boot setup script URL
  -h, --help            Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --launch) LAUNCH=1 ;;
    --product) PRODUCT="$2"; shift ;;
    --region) REGION="$2"; shift ;;
    --image-id) IMAGE_ID="$2"; shift ;;
    --name) INSTANCE_NAME="$2"; shift ;;
    --ssh-key) SSH_KEY_NAME="$2"; shift ;;
    --setup-url) SETUP_URL="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

cat <<EOF
=== GPU VM Deployment Plan ===
Product:    $PRODUCT
Region:     $REGION
Image ID:   $IMAGE_ID
Name:       $INSTANCE_NAME
Setup URL:  $SETUP_URL

Estimated cost (on-demand):
  4 hours:  ~\$$(python3 -c "print(f'{$PRODUCT#gpu_}: not priced here')" 2>/dev/null || echo "see GPU_VM_DEPLOYMENT_PLAN.md")
EOF

if [[ "${LAUNCH:-0}" != "1" ]]; then
  cat <<EOF

Dry-run mode. To launch, run:

  SSH_KEY_NAME=<your-key> $0 --launch

EOF
  exit 0
fi

if [[ -z "$SSH_KEY_NAME" ]]; then
  echo "ERROR: --ssh-key or SSH_KEY_NAME env var is required for launch."
  exit 1
fi

cat <<EOF

Launching VM...
EOF

# This command uses the massed-compute MCP tool. If running outside Kimi CLI,
# replace with the equivalent REST API call or use the MCP client.
instances_launch \
  --productName "$PRODUCT" \
  --regionName "$REGION" \
  --imageId "$IMAGE_ID" \
  --instanceName "$INSTANCE_NAME" \
  --sshKeys "[\"$SSH_KEY_NAME\"]" \
  --command "bash -c 'curl -fsSL $SETUP_URL | bash'"
