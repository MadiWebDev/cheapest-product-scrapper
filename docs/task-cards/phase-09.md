# Task card — Phase 9: monetization

- **Goal:** AffiliateService over /go, Paddle billing with verified
  webhooks, sponsored separation, honest revenue analytics.
- **Acceptance:** per-country tag resolution ✓; bot clicks filtered
  from estimates ✓; EPC only when operator-configured (never invented)
  ✓; estimated/confirmed never summed ✓; Paddle signature scheme
  verified incl. tamper + stale-ts rejection ✓; event idempotency ✓;
  sponsored separation test ✓; plan list prices are the product's own
  (Free/Pro $9/Business $29, config-overridable) — a product decision,
  recorded here.
- **Tests added:** test_monetization.py (8). Suite: 77 passed.
- **Review findings (pass 2):** is_bot_ua lives in go.py (click layer)
  and is re-exported by affiliate.py — putting it in affiliate.py would
  have created a circular import with the click store.
- **Red-team findings (pass 3):** webhook verification rejects stale
  timestamps (replay window) and uses compare_digest; checkout without
  keys returns an explicit not_configured mode instead of a fake URL.
- **Status:** VERIFIED — L-055…L-057, L-059; L-058 IMPLEMENTED-UNVERIFIED.
