# BLOCKERS — PRICEINTEL v3 (directive §1.5)

Format: what / why / what is needed / fallback in place. Three genuine
attempts maximum per blocker; never loop, never fake past one.

## B3-001 — Docker Compose boot cannot be verified in the build VM
- **What:** §1.6/§42E gate "app starts via Docker Compose".
- **Why:** `docker: command not found` in this VM (checked 2026-11-17).
- **Needed:** a Docker-capable environment (the owner's machine or CI).
- **Fallback:** app boot + full request journeys verified via direct
  process/TestClient runs (TRUTH_LEDGER evidence); compose file kept
  under review; GitHub Actions (Docker-capable) runs the same test suite.

## B3-002 — `.github/workflows/*` cannot be pushed (403)
- **What:** CI workflow updates cannot land on GitHub from this program.
- **Why:** the Muse GitHub App installation lacks the Workflows
  permission; `push_files` on `.github/workflows/ci.yml` returned
  `403 Resource not accessible by integration` in v1 (2026-11-16).
- **Needed:** owner grants the App the Workflows permission, or uploads
  the file once via github.com.
- **Fallback:** CI file kept correct locally and in the delivery zip;
  all other files push normally. Not retried per phase (§ task rule).

## B3-003 — No live marketplace/API credentials exist in this environment
- **What:** live connector calls (Amazon PA-API, eBay, Etsy, …), live FX
  fetch verification against paid tiers, SerpApi/Zyte-class providers.
- **Why:** no API keys are configured in this environment.
- **Needed:** owner-created accounts/keys (list in RUN_AND_KEYS.md).
- **Fallback:** connectors fixture-tested; live mode additionally gated
  by the compliance gate (Phase 1). Statuses stay BLOCKED for live legs.

## B3-004 — No LLM API key (AI assistant live leg)
- **What:** directive §15 LLM-backed assistant answers.
- **Why:** no provider key configured.
- **Needed:** an LLM provider API key + spend cap approval.
- **Fallback:** AIProvider abstraction + deterministic grounded fallback
  (structured parsing → platform tools → cited templated answer),
  Phase 7. LLM path flag-off.

## B3-005 — No Paddle live keys / no Telegram bot token / no SMTP creds
- **What:** live checkout, bot delivery, email delivery.
- **Why:** credentials not configured.
- **Needed:** Paddle sandbox/vendor keys, Telegram bot token, SMTP creds.
- **Fallback:** billing abstraction + webhook verification tested with
  documented test patterns and fixtures; channels env-gated and honest
  about not-configured state (Phases 9–10).

## B3-006 — Playwright not installed in the build VM
- **What:** browser-level E2E (§1.7, §38).
- **Why:** no Playwright/browser binaries in this VM.
- **Needed:** Playwright install on a capable machine or CI.
- **Fallback:** API-level journey tests via TestClient against the real
  app (marked as such in the ledger — never described as Playwright).

## B3-007 — Push approval channel timed out (2026-11-17)
- **Symptom:** the Phase 4 push_files call was interrupted by a service
  restart; the follow-up verification call's egress approval timed out
  ("action was not performed").
- **Impact:** Phase 4 push outcome UNVERIFIED — it may or may not have
  landed. Phases 4+ pushes are PENDING until the channel is used again.
- **Reconciliation (do this first when pushes resume):** list_commits —
  if a phase-4 commit sits on top of 2000846d, Phase 4 landed; mark it
  confirmed and do NOT re-push. If head is still 2000846d, push Phase 4,
  then continue per-phase. Never force-push.
- **Program state:** local commits continue; nothing is blocked locally.
