#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if [ -x "$HOME/workspace/cpf-venv/bin/python" ]; then PY="$HOME/workspace/cpf-venv/bin/python"; fi
export PYTHON="$PY"
"$PY" tools/audit_truth.py
