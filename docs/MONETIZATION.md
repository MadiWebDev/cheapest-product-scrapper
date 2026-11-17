# Monetization

- **Affiliate (primary)**: outbound clicks go through /go; a tag is
  appended only when configured (`AFFILIATE_TAG_<CONNECTOR>[_<COUNTRY>]`).
  Clicks are bot-filtered. Revenue analytics keep **estimated**
  (clicks × operator-configured EPC) and **confirmed** (imported,
  deduplicated network conversions) strictly separate — never summed.
- **Subscriptions**: Free / Pro ($9) / Business ($29) list prices via
  Paddle (BillingProvider abstraction). Webhook signature verification
  and idempotent event handling are implemented and tested; live
  checkout activates with Paddle keys (sandbox first).
- **Sponsored**: a separate, labelled list in the search response.
  Sponsored entries are never part of organic results or ranking
  (separation is test-enforced), consistent with the ranking-integrity
  rule (Phase 6).
- **Developer API**: quota'd keys (hashed at rest) — the paid API tier
  builds on the same accounting.
- No payment data touches this codebase: Paddle is the merchant of
  record for subscriptions; affiliate revenue is paid by networks.
