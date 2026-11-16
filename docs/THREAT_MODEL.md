# THREAT MODEL — PRICEINTEL v3 (directive §3, STRIDE summary)

Scope: auth, /go redirects, source adapters, billing webhooks, admin,
public/developer API, MCP endpoint, AI assistant, browser extension.

| Surface | Threat (STRIDE) | Control in place / planned |
|---|---|---|
| Auth | Spoofing — credential stuffing, weak hashing | bcrypt via passlib (D-013 lineage); JWT with rotation on refresh (v1); rate limits (slowapi); 2FA for admins PLANNED (Phase 11 hardening list) |
| Auth | Elevation — plan/role tampering from client | Plans server-assigned (v1 D-012); RBAC tests (Phase 11) |
| /go redirect | Tampering — open redirect to phishing | Per-marketplace host allowlist; destination re-validated at click time; no user-supplied target URLs (Phase 1) |
| Adapters | Tampering/SSRF — extractor fetches internal addresses | `assert_public_url` blocks private/loopback IPs (v1, tested); egress allowlist in manifests (Phase 3); response schema validation |
| Adapters | Info disclosure — scraped pages carry third-party PII | Never store personal data from scraped pages (v1 rule); payload minimisation in raw-payload store |
| Billing webhooks | Spoofing/Tampering — forged Paddle events | Signature verification + idempotency keys before any state change (Phase 9); replay window |
| Admin | Elevation — unprotected admin routes | Admin router behind auth + role check; sensitive actions audit-logged (Phase 11); admin responses never publicly cacheable |
| Public/developer API | DoS — quota abuse | Hashed API keys, per-key quotas + rate limiting (Phase 11); slowapi on public routes |
| MCP endpoint | Spoofing — unauthenticated agent access | Same API-key auth + rate limits as developer API (Phase 7) |
| AI assistant | Tampering — prompt injection via product titles / pasted ads | Scraped/pasted text delimited as data, never instructions; tools callable only by the platform layer; hostile-string regression tests (Phase 7) |
| AI assistant | Info disclosure — PII in prompts/logs | PII scrub before logging; conversation memory user-scoped + deletable (Phase 7 design) |
| Extension | Elevation — excessive host permissions | Least-privilege manifest, supported-sites only, no form/keystroke access (Phase 12 scaffold + COMPLIANCE checklist) |
| All | Repudiation — disputed admin/billing actions | Immutable audit log with actor, target, before/after, request id (Phase 11) |
| All | DoS — search fan-out abuse | Per-IP rate limits; connector concurrency caps; user searches outrank background jobs |

Residual risks accepted for this program: no WAF, no SOC monitoring,
single-region deployment (see RISKS.md R-07/R-08 for the two highest).
