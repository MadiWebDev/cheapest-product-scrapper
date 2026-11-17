# Task card — Phase 10: alerts + watchlists completion

- **Goal:** re-evidence v1 alerts, add quiet hours, dedupe, one-click
  unsubscribe; Telegram webhook behind a flag; WhatsApp official-only.
- **Acceptance:** v1 notify() re-evidenced (real SMTP/Telegram when
  configured, explicit not_configured otherwise) ✓; quiet hours with
  per-alert timezone ✓; dedupe rule (<1% / 24h) ✓; unsubscribe token
  stored hashed, one-click GET endpoint ✓; watchlist isolation ✓;
  Telegram webhook secret-gated with fixture tests ✓; WhatsApp
  official channel BLOCKED honestly ✓.
- **Tests added:** test_alerts.py (7). Suite: 84 passed.
- **Review findings (pass 2):** evaluate() must not mark an alert
  notified when delivery fails — otherwise a user silently loses the
  alert during an SMTP outage. Tested explicitly.
- **Red-team findings (pass 3):** unsubscribe tokens are stored as
  SHA-256 hashes and compared in constant time; the token is the
  credential for exactly one action (deactivate), nothing else.
- **Status:** VERIFIED — L-060…L-063; L-064 BLOCKED (credentials).
