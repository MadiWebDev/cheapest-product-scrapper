# API (v3 surface; v1 endpoints unchanged)

## Public
- `POST /api/search`, `GET /api/search`, `GET /api/search/stream` (SSE)
- `GET /go/{offer_id}` — tracked redirect (allowlist re-validated)
- `GET /api/compliance`, `GET /api/compliance/{source_id}`
- `GET /api/adapters`, `GET /api/adapters/{id}` — manifest + health
- `GET /api/countries`, `GET /api/countries/{code}`, `GET /api/location/resolve`
- `GET /api/format/money?amount=&currency=`
- `POST /api/assistant` — grounded assistant (deterministic provider;
  LLM path activates with OPENAI_API_KEY)
- `POST /api/scam-check` — indicators-only ad analysis
- `GET /api/sponsored`
- Features (`/api/features/*`, flag-gated): used-phone-kit,
  compatibility, budget-plan, outcomes (+`/{seller}`), evidence-pack,
  alternatives, deal-passport, digest/run
- Alerts/watchlists: `POST /api/alerts`, `GET /api/alerts/unsubscribe`,
  `POST /api/alerts/evaluate`, `POST/GET /api/watchlist`
- Billing: `GET /api/billing/plans`, `POST /api/billing/checkout`,
  `POST /api/billing/webhook/paddle`
- `POST /api/telegram/webhook` (secret-gated)
- `POST /mcp` — JSON-RPC tools; requires MCP_API_KEY (503 when unset)

## Developer API (X-API-Key, quota'd)
- `GET /api/v1/search`, `GET /api/v1/usage`

## Admin
- v2 console (`X-Admin-Key`, RBAC): `/api/admin/v2/users`, `audit-log`,
  `match-review` (+`/scan`, `/{id}/decision`), `sellers/{seller}/scorecard|reply|undercuts`,
  `devkeys`
- v1 admin (`/api/admin/*`): connectors, tax-tables, metrics,
  compliance (+update), revenue, conversions, sponsored.
  Requires ADMIN_API_KEY when configured.

Health/observability: `/api/health`, `/ready`, `/metrics`.
