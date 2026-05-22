# ACN Security Baseline

Generated: 2026-05-22

## Scope

- **Project:** Autonomous Cognitive Network (ACN)
- **Files scanned:** 348 files across `acn/` and `tests/` (~4.4MB)
- **Tools used:** GitLeaks v8.25.1, TruffleHog v3.95.3, pip-audit v2.10.0, Safety v3.7.0, OSV Scanner v2.3.8

---

## Secret Scanning Results

| Tool | Target | Verified Secrets | Unverified Secrets | Notes |
|------|--------|-----------------|-------------------|-------|
| GitLeaks | Git history + working tree | 0 | 0 | 1 false positive allowlisted (citation keys) |
| TruffleHog v3 | Filesystem | 0 | 0 | Deep entropy + regex scanning |
| TruffleHog v3 | Git history (18 commits) | 0 | 0 | Full commit history analyzed |
| Manual grep | All files | 0 | 0 | URLs with creds, base64, IPs, TODOs |

**Key finding:** API keys are handled via `os.environ.get()` (good practice). No hardcoded secrets detected.

---

## Dependency Scanning Results

### Direct Dependencies (requirements-acn.txt)

| Package | Version | Source |
|---------|---------|--------|
| openai | 2.32.0 | PyPI |
| plotly | 6.7.0 | PyPI |
| pydantic | 2.13.3 | PyPI |
| pytest | 9.0.3 | PyPI |
| requests | 2.34.2 | PyPI |
| streamlit | 1.57.0 | PyPI |

**CVE Status:** 0 known vulnerabilities (pip-audit + Safety both clear)

### Container Base Image (python:3.11-alpine)

| Package | Version | CVEs | Fix Available |
|---------|---------|------|---------------|
| wheel (Python) | 0.45.1 | 1 | ✅ Yes |
| xz (Alpine) | 5.8.2-r0 | 1 | ✅ Yes |

**Action:** Rebuild Docker images after base image update to pull patched versions.

---

## Infrastructure

### Security Scanning Files

- `.gitleaks.toml` — Allowlist for citation keys (AuthorYYYY format)
- `requirements-acn.txt` — Pinned dependency manifest
- `scripts/run-security-scan.sh` — One-command security audit

### How to Run Scans

```bash
cd /path/to/acn
./scripts/run-security-scan.sh
```

---

## Accepted Risks

1. **Transitive dependency coverage:** pip-audit and Safety scan direct dependencies only. Transitive deps of `openai`, `streamlit`, etc. are not independently audited in this baseline.
2. **Docker image lag:** Base image CVEs are fixed upstream but require image rebuild + redeploy.
3. **No CI pipeline:** Security scans are manual. Recommended: add GitHub Actions workflow.

---

## Remediation Timeline

| Priority | Item | ETA |
|----------|------|-----|
| LOW | Update python:3.11-alpine base image (wheel + xz patches) | Next deploy cycle |
| LOW | Add `pip-audit --desc` to CI for transitive dep visibility | Future sprint |
| INFO | Monitor moby/moby releases for docker/docker CVE fixes | Ongoing (external) |

