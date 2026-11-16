# RISKS — PRICEINTEL v3 (directive §3)

Each risk: likelihood / impact / mitigation / owner / review date.
Owner for all rows is the project maintainer unless noted. Review date
for all rows: 2027-02-17 (90-day cadence, aligned with compliance
re-review).

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Legal: a marketplace's terms prohibit the access method used | Medium | High | Compliance gate (Phase 1): no approved, unexpired COMPLIANCE_REVIEW → adapter disabled for live mode; takedown workflow; official APIs preferred |
| R-02 | Legal: affiliate program rule breach (redirect/cloaking/cookie rules) | Medium | Medium | Per-program redirect policy stored with the compliance record; disclosure near every outbound action; /go allowlist only |
| R-03 | Legal: consumer-protection / advertising disclosure failures | Medium | Medium | Sponsored always separated + labelled; estimates labelled; legal review flagged as owner action in FINAL_REPORT (Appendix F) |
| R-04 | Data: selector drift silently degrades a source | High | Medium | Drift detector (v1) wired to adapter health + admin (Phase 3); implausible-value rejection; graceful degradation |
| R-05 | Data: stale prices shown as live | Medium | High | checkedAt + freshness labels everywhere; stale-price guardrail metric; FX stale flag (v1) |
| R-06 | Cost: LLM / data-provider spend overruns | Medium | Medium | Spend caps + kill switches (Phase 7/9); deterministic fallback; cost-per-search published in PERFORMANCE.md |
| R-07 | Security: SSRF via URL extractor / adapters | Medium | High | assert_public_url (v1, tested); egress allowlist per adapter manifest (Phase 3); private-IP blocking |
| R-08 | Security: open redirect via /go | Medium | High | Per-marketplace destination allowlist, re-validation at click time (Phase 1) |
| R-09 | Reputational: wrong match (false merge) shows a wrong "cheapest" | Medium | High | Hard separation rules + false-merge gate <1% on the labeled set (Phase 4); prefer missed match; match-review queue (Phase 11) |
| R-10 | Reputational: fraud flag read as an accusation against a seller | Medium | Medium | Indicators-only language; seller right of reply (Phase 11); false-positive tracking |
| R-11 | Platform dependency: a marketplace revokes API/affiliate access | Medium | Medium | Multi-source design; compliance expiry auto-disable; no single source is load-bearing for the skeleton |
| R-12 | Privacy: PII leaks into logs/LLM prompts | Low | High | PII scrubbing rule for assistant (Phase 7); no raw IP retention in location service (Phase 2) |
