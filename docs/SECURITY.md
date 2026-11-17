# Security

See also docs/THREAT_MODEL.md (STRIDE). Controls implemented and tested:

- **SSRF**: the generic extractor resolves hosts and blocks private /
  loopback / link-local / reserved / multicast IPs, non-http(s)
  schemes, and credentials-in-URL (tests in test_connectors/test_adapters).
- **Open-redirect prevention**: /go resolves only server-registered
  offer ids and re-validates the destination against a per-marketplace
  host allowlist at click time (lookalike hosts rejected; tests).
- **Demo guard**: the app refuses to boot with DEMO_MODE=true when
  APP_ENV=production (tested by tools/audit_truth.py).
- **Keys at rest**: admin, developer and unsubscribe credentials are
  stored as SHA-256 hashes; raw keys are shown once at creation.
- **Webhooks**: Paddle signatures verified with HMAC-SHA256 over
  `ts:body`, constant-time compare, 300 s replay tolerance; Telegram
  webhook requires its secret header; both are idempotent/secret-gated.
- **RBAC**: admin console v2 enforces viewer < moderator < admin;
  legacy /api/admin/* requires ADMIN_API_KEY when configured (set it
  in every deployment — see DEPLOYMENT.md).
- **Headers**: API responses carry nosniff, X-Frame-Options DENY,
  Referrer-Policy no-referrer and a restrictive CSP (JSON API).
- **Rate limits**: slowapi on legacy routes; per-key quotas on the
  developer API; token-bucket on MCP.
- **Ranking integrity**: ranking cannot read monetization data
  (architectural + behavioral tests, Phase 6).

Known limits: no WAF; auth for end-users is the v1 JWT system
(unchanged); in-process stores in the skeleton are single-process by
design (see DATABASE.md).
