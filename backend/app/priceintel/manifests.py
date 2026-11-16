"""Adapter manifests (directive §8): one versioned JSON per adapter in
app/data/manifests/, generated from the registry by tools/gen_manifests.py."""
from __future__ import annotations

import json
import pathlib

DATA = pathlib.Path(__file__).parent.parent / "data" / "manifests"


def load_manifests() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if DATA.exists():
        for p in sorted(DATA.glob("*.json")):
            m = json.loads(p.read_text())
            out[m["id"]] = m
    return out


MANIFESTS = load_manifests()


def manifest_for(connector: str) -> dict | None:
    return MANIFESTS.get(connector)
