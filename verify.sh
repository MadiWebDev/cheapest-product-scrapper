#!/usr/bin/env bash
# PriceIntel one-command verification (directive §1.13, stack-mapped per D-028).
# Runs: backend unit/integration tests, audit:truth, frontend production build.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ -x "$HOME/workspace/cpf-venv/bin/python" ]; then PY="$HOME/workspace/cpf-venv/bin/python"; fi
export PYTHON="$PY"
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy || true

echo "== backend tests =="
(cd backend && "$PY" -m pytest tests/ -q)

echo "== audit:truth =="
"$PY" tools/audit_truth.py

echo "== frontend build =="
(cd web-application && npm run build)

echo "verify: OK"
