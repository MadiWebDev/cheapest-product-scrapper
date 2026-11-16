"""Adapter health: runtime record of connector runs, including the
drift-detector output (directive §8 — drift must reach health + admin,
not just the per-search response)."""
from __future__ import annotations

import time


class AdapterHealth:
    def __init__(self) -> None:
        self._state: dict[str, dict] = {}

    def record(self, connector: str, offers: int, drift_suspected: bool,
               error: str | None = None, latency_ms: int = 0) -> None:
        s = self._state.setdefault(connector, {"runs": 0, "total_offers": 0,
                                               "drift_runs": 0, "errors": 0,
                                               "last_drift_suspected": False,
                                               "last_error": None, "last_run_at": None,
                                               "last_latency_ms": 0})
        s["runs"] += 1
        s["total_offers"] += offers
        s["errors"] += 1 if error else 0
        s["drift_runs"] += 1 if drift_suspected else 0
        s["last_drift_suspected"] = drift_suspected
        s["last_error"] = error
        s["last_run_at"] = time.time()
        s["last_latency_ms"] = latency_ms

    def snapshot(self) -> dict[str, dict]:
        return {k: dict(v) for k, v in sorted(self._state.items())}

    def for_connector(self, connector: str) -> dict:
        return dict(self._state.get(connector, {"runs": 0, "total_offers": 0,
                                                "drift_runs": 0, "errors": 0,
                                                "last_drift_suspected": False,
                                                "last_error": None, "last_run_at": None,
                                                "last_latency_ms": 0}))


HEALTH = AdapterHealth()
