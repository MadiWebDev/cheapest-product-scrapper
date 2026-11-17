# Runbooks

- **Adapter drift suspected** (admin health shows drift_runs > 0):
  check the adapter's fixture contract test, inspect the source's
  page structure change, update the extractor, regenerate manifests.
- **Compliance record expiring**: gate closes automatically at expiry.
  Re-review terms/robots, record via POST /api/admin/compliance/{id},
  regenerate manifests.
- **FX stale** (fx_stale=true in responses): both providers failed;
  check egress to frankfurter/open.er-api. Prices still compute from
  the flagged fallback table — never silently fresh.
- **Paddle webhook failures**: verify PADDLE_WEBHOOK_SECRET matches
  the dashboard; check the 300 s timestamp tolerance; events are
  idempotent, so redelivery is safe.
- **Alert delivery failing**: notify() returns the reason
  (SMTP/Telegram not configured or rejected); alerts are not marked
  notified on failure, so they retry on the next evaluation.
- **Push reconciliation (B3-007)**: before any new push, list_commits;
  if the phase-4 commit is already on main, mark it confirmed and
  continue from Phase 5 — never force-push, never re-push blindly.
