#!/usr/bin/env python3
"""audit:truth — PriceIntel directive §1.13.

Fails (exit 1) when:
  1. A TRUTH_LEDGER.md row claims VERIFIED without evidence text.
  2. Production code contains stub/fake markers (TODO, FIXME, lorem,
     standalone 'mock'/'fake', placeholder prices) outside the allowed
     demo/fixture locations.
  3. The app can boot with DEMO_MODE=true under APP_ENV=production
     (the §1.14 guard must reject it).

Run from the repo root:  python3 tools/audit_truth.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []

# --- 1. Ledger evidence check -------------------------------------------------
ledger = ROOT / "docs" / "TRUTH_LEDGER.md"
if not ledger.exists():
    failures.append("docs/TRUTH_LEDGER.md is missing")
else:
    for i, line in enumerate(ledger.read_text().splitlines(), 1):
        if "| VERIFIED |" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # columns: id | claim | module | status | evidence | re-verified | notes
            evidence = cells[4] if len(cells) > 4 else ""
            if len(evidence) < 12 or "evidence needed" in evidence.lower():
                failures.append(f"TRUTH_LEDGER.md:{i} VERIFIED row lacks evidence: {line[:80]}")

# --- 2. Stub / fake marker scan ------------------------------------------------
# Phrase-level markers: the domain legitimately contains identifiers like
# fake_discount / fake_review_penalty (fraud-detection features), so bare
# words would false-positive. We flag fabricated-data phrasing instead.
MARKERS = [
    (re.compile(r"\bTODO\b"), "TODO"),
    (re.compile(r"\bFIXME\b"), "FIXME"),
    (re.compile(r"lorem", re.I), "lorem"),
    (re.compile(r"mock\s+(data|response|result|offer|price)", re.I), "mock data"),
    (re.compile(r"fake\s+(data|price|offer|result|review\s+text)", re.I), "fake data"),
    (re.compile(r"placeholder\s+price", re.I), "placeholder price"),
    (re.compile(r"hardcoded\s+price", re.I), "hardcoded price"),
]
SCAN_DIRS = [ROOT / "backend" / "app", ROOT / "web-application" / "app",
             ROOT / "web-application" / "components"]
ALLOWED = {"demo.py"}  # the env-gated demo connector is labelled demo data


def _scan(path: Path) -> None:
    if path.name in ALLOWED or "fixtures" in path.parts or "__pycache__" in path.parts:
        return
    if path.suffix not in (".py", ".ts", ".tsx", ".js"):
        return
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return
    for rx, label in MARKERS:
        for m in rx.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            failures.append(f"marker '{label}' in production code: {path.relative_to(ROOT)}:{line_no}")


for d in SCAN_DIRS:
    if d.exists():
        for p in d.rglob("*"):
            if p.is_file():
                _scan(p)

# --- 3. Demo-mode production guard ---------------------------------------------
py = os.environ.get("PYTHON", sys.executable)
env = {k: v for k, v in os.environ.items()
       if k.lower() not in ("http_proxy", "https_proxy", "all_proxy", "no_proxy")}
env.update({"DEMO_MODE": "true", "APP_ENV": "production", "PYTHONPATH": str(ROOT / "backend")})
proc = subprocess.run([py, "-c", "import app.main"], capture_output=True, text=True, env=env)
if proc.returncode == 0:
    failures.append("DEMO_MODE=true booted under APP_ENV=production — §1.14 guard missing")
elif "DEMO_MODE" not in (proc.stderr or ""):
    failures.append("app failed to boot in production-demo check for an unexpected reason: "
                    + (proc.stderr or "")[-300:])

if failures:
    print("audit:truth FAILED")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("audit:truth OK — ledger evidence present, no stub/fake markers in production code, demo guard rejects production boot")
