#!/usr/bin/env bash
# End-to-end journeys (directive §1.13). Playwright is not installed in the
# build VM (see docs/BLOCKERS.md); the API-level journey runs through
# FastAPI TestClient against the real app, plus the boot smoke.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ -x "$HOME/workspace/cpf-venv/bin/python" ]; then PY="$HOME/workspace/cpf-venv/bin/python"; fi
export PYTHON="$PY"
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy || true

echo "== boot smoke =="
"$PY" tools/smoke.py

if [ -f backend/tests/test_journey.py ]; then
  echo "== API journey tests =="
  (cd backend && "$PY" -m pytest tests/test_journey.py -q)
fi
echo "e2e: OK"
