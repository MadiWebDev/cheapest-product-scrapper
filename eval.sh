#!/usr/bin/env bash
# Evaluation suites (directive §1.13/§38): matching, relevance, landed-cost
# golden cases, trust, scam-ad, assistant groundedness. Datasets live in
# eval/ and are enforced by tools/run_evals.py once present.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ -x "$HOME/workspace/cpf-venv/bin/python" ]; then PY="$HOME/workspace/cpf-venv/bin/python"; fi
export PYTHON="$PY"
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy || true
"$PY" tools/run_evals.py
