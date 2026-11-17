# Deployment

## Shape
FastAPI backend (`backend/`, uvicorn), Next.js frontend
(`web-application/`), PostgreSQL + Redis for Celery in the full
deployment (docker-compose.yml). Docker was **not available in the
build VM** (BLOCKERS B3-001), so compose boot is unverified here;
verify.sh/e2e.sh exercise the app via direct process/TestClient runs.

## Required environment
- `APP_ENV=production` in production (with DEMO_MODE unset/false —
  the app refuses to boot otherwise).
- `ADMIN_API_KEY` — protects admin surfaces; set it always.
- `DATABASE_URL`, `REDIS_URL` for DB/Celery features.

## Optional integrations (feature activates only when set)
- Marketplace/API keys: `SERPAPI_KEY`, `EBAY_CLIENT_ID/SECRET`,
  `ETSY_API_KEY`, affiliate tags `AFFILIATE_TAG_*`, EPC `AFFILIATE_EPC_*`.
- `OPENAI_API_KEY` (+ `AI_DAILY_BUDGET_USD`) — LLM assistant path.
- Paddle: `PADDLE_API_KEY`, `PADDLE_WEBHOOK_SECRET`, `PADDLE_PRICE_*`.
- Alerts: `SMTP_*`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`,
  `WHATSAPP_CLOUD_TOKEN` (official API only).
- `MCP_API_KEY` — enables /mcp.

## Run
```
./verify.sh   # tests + audit:truth
./eval.sh     # eval gates
./e2e.sh      # API smoke
cd web-application && npm run build
```
