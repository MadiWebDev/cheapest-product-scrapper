# Task card — Phase 7: AI assistant, scam checker, MCP

- **Goal:** provider-abstracted assistant with enforced groundedness,
  scam-ad checker with a labeled eval, authenticated MCP endpoint.
- **Acceptance:** deterministic provider serves with no key; LLM path
  present but BLOCKED (B3-004) ✓; answers built only from same-turn
  tool results, verified numerically ✓; injection text treated as data
  ✓; scam eval recall 1.000 / false-flag 0.000 on synthetic ads ✓; MCP
  503-unconfigured / 401-wrong-key / rate-limited ✓.
- **Tests added:** test_ai_mcp.py (9). Suite: 69 passed.
- **Review findings (pass 2):** the first groundedness verifier failed
  on legitimate answers — numbers inside tool-result strings ("iPhone
  15", "128GB") are grounded data too, and the user's own budget may be
  quoted back. Verifier now collects string-embedded numbers and takes
  an explicit extra-allowed set; fabricated prices still fail.
- **Red-team findings (pass 3):** MCP history tool must not fabricate —
  it returns available:false with the reason. Scam checker language is
  indicators-only everywhere, including the API note field.
- **Status:** VERIFIED (L-044, L-046…L-048); LLM path BLOCKED (L-045).
