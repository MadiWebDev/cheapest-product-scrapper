# Compliance

## The gate
A source may run in **live mode** only when a COMPLIANCE_REVIEW record
exists for it, has status `approved`, and is unexpired
(`backend/app/priceintel/compliance.py`). Records are versioned JSON in
`backend/app/data/compliance/` with the Appendix-C fields: terms and
robots URLs + review dates + summaries, access method, rate-limit
policy, data-use rules, affiliate status, takedown contact/SLA,
reviewer, sign-off and expiry (90-day review cadence).

Demo/fixture mode is unaffected by the gate and is always labelled.

## Current records (2026-11-17)
| Source | Status | Basis |
|---|---|---|
| daraz | **blocked** | Terms §2E prohibit collection/use of product listings and prices and data-mining/robot extraction without written consent; robots also disallows /catalog/. Approved route: official API/affiliate credentials only. |
| priceoye | pending | robots.txt reviewed 2026-11-17 (query-string URLs disallowed for `*`); terms not yet reviewed. |
| telemart | pending | robots.txt reviewed 2026-11-17 (Shopify storefront defaults); terms not yet reviewed. |
| all other adapters | unreviewed | No record → gate closed in live mode. |

## Process
1. Reviewer fetches the source's terms + robots and records evidence
   (never conclusions without the pages).
2. Admin records the decision via `POST /api/admin/compliance/{id}`
   (approval requires a named reviewer and an expiry date).
3. Manifests are regenerated (`tools/gen_manifests.py`) so adapter
   compliance_status matches the records.
4. Takedown: on a verified request, disable the source (status →
   blocked) and purge stored offers for it within 7 days.

This document is an engineering record, not legal advice.
