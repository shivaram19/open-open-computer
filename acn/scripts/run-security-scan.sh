#!/bin/bash
# ACN Security Audit Script
# Runs all enterprise scanners and generates a consolidated report

set -euo pipefail

ACN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_FILE="$ACN_DIR/security-report-$(date +%Y%m%d-%H%M%S).txt"

echo "========================================" | tee "$REPORT_FILE"
echo "ACN Security Audit — $(date -Iseconds)" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"

# 1. Secret Scanning
echo "" | tee -a "$REPORT_FILE"
echo "--- 1. GitLeaks ---" | tee -a "$REPORT_FILE"
gitleaks detect --source "$ACN_DIR" --config "$ACN_DIR/.gitleaks.toml" 2>&1 | tee -a "$REPORT_FILE" || true

echo "" | tee -a "$REPORT_FILE"
echo "--- 2. TruffleHog (filesystem) ---" | tee -a "$REPORT_FILE"
trufflehog filesystem "$ACN_DIR" --only-verified 2>&1 | tee -a "$REPORT_FILE" || true

# 2. Dependency Scanning
echo "" | tee -a "$REPORT_FILE"
echo "--- 3. pip-audit ---" | tee -a "$REPORT_FILE"
pip-audit --requirement "$ACN_DIR/requirements-acn.txt" 2>&1 | tee -a "$REPORT_FILE" || true

echo "" | tee -a "$REPORT_FILE"
echo "--- 4. Safety CLI ---" | tee -a "$REPORT_FILE"
safety check --file "$ACN_DIR/requirements-acn.txt" 2>&1 | tee -a "$REPORT_FILE" || true

# 3. Container Scanning (if docker available)
echo "" | tee -a "$REPORT_FILE"
echo "--- 5. Docker base image (optional) ---" | tee -a "$REPORT_FILE"
if command -v osv-scanner &> /dev/null && docker images python:3.11-alpine &> /dev/null; then
    osv-scanner scan image python:3.11-alpine 2>&1 | tee -a "$REPORT_FILE" || true
else
    echo "Skipping container scan (osv-scanner or image not available)" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "========================================" | tee -a "$REPORT_FILE"
