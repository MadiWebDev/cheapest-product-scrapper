# Transparency

- **Estimates are labelled**: tax/duty lines carry PLATFORM_ESTIMATE
  with the rule table version; nothing estimated is presented as exact.
- **Demo data is labelled**: DEMO_MODE responses carry demo:true and
  the UI shows a banner; production refuses demo mode at boot.
- **Affiliate disclosure**: search responses and the UI state that
  outbound links may earn a commission and that commissions never
  affect ranking (test-enforced).
- **Sponsored is labelled** and kept out of organic results.
- **Source status is public**: /api/compliance shows every reviewed
  source's status, including blocked ones and why.
- **Scores are explainable**: trust, PCI, match confidence and ranking
  all expose their inputs/reasons in the API and the evidence drawer.
- **Truth ledger**: docs/TRUTH_LEDGER.md records every capability with
  its status (VERIFIED / IMPLEMENTED-UNVERIFIED / STUBBED / BLOCKED /
  PLANNED) and the evidence behind it; docs/BLOCKERS.md records what
  could not be done here and why.
