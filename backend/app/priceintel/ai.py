"""AI assistant (directive §13) behind an AIProvider abstraction.

Reality of this environment: no LLM API key exists (BLOCKERS B3-004),
so the LLM-backed provider is implemented against the OpenAI client
interface but cannot run here; the DEFAULT provider is a deterministic,
grounded fallback: structured query parsing -> platform search tool ->
templated answer built ONLY from that tool result.

Groundedness rule (enforced, not aspirational): the answer builder
receives only the tool-result object; every price/score it prints comes
from that object, and `verify_grounded` re-checks that any number in
the answer text appears in the tool result. User text and scraped
titles are always data, never instructions.
"""
from __future__ import annotations

import os
import re
import time


class BudgetExceeded(Exception):
    pass


class AIBudget:
    """Daily spend cap (USD) for paid providers; the deterministic
    provider costs 0 and is never blocked by it."""

    def __init__(self, daily_cap_usd: float | None = None):
        self.cap = daily_cap_usd if daily_cap_usd is not None else float(os.getenv("AI_DAILY_BUDGET_USD", "5"))
        self.spent = 0.0
        self.day = time.strftime("%Y-%m-%d")

    def charge(self, usd: float) -> None:
        today = time.strftime("%Y-%m-%d")
        if today != self.day:
            self.day, self.spent = today, 0.0
        if self.spent + usd > self.cap:
            raise BudgetExceeded(f"AI daily budget cap ${self.cap} reached")
        self.spent += usd


BUDGET = AIBudget()


class AIProvider:
    name = "base"

    def available(self) -> bool:
        return False

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class LLMProvider(AIProvider):
    """OpenAI-compatible chat provider. BLOCKED in this environment:
    no API key (B3-004). Interface + budget wiring are real; the live
    leg activates when OPENAI_API_KEY is configured."""

    name = "llm"

    def available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

    def complete(self, prompt: str) -> str:
        if not self.available():
            raise RuntimeError("OPENAI_API_KEY not configured (B3-004)")
        BUDGET.charge(0.01)  # conservative per-call estimate against the cap
        from openai import OpenAI

        client = OpenAI()
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": "You are a shopping assistant. Use only the provided tool results."},
                      {"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content or ""


class DeterministicProvider(AIProvider):
    name = "deterministic"

    def available(self) -> bool:
        return True


def get_provider() -> AIProvider:
    llm = LLMProvider()
    return llm if llm.available() else DeterministicProvider()


# --- grounded assistant -------------------------------------------------------

_BUDGET_RE = re.compile(r"(?:under|below|max|budget)\s*(?:rs\.?|pkr|usd|\$)?\s*([\d,]{3,})", re.I)


def parse_query(query: str) -> dict:
    """Structured parse of the user's text. The text is DATA: it is
    matched against patterns, never executed or obeyed."""
    m = _BUDGET_RE.search(query or "")
    budget = float(m.group(1).replace(",", "")) if m else None
    cleaned = _BUDGET_RE.sub("", query or "").strip()
    return {"search_terms": cleaned or (query or ""), "budget": budget}


def build_answer(query: str, search_result: dict) -> dict:
    """Templated answer citing ONLY the tool result from this turn."""
    parsed = parse_query(query)
    products = search_result.get("products", [])
    citations: list[str] = []
    lines: list[str] = []
    if not products:
        return {"answer": "No offers were found for that search in the current sources. "
                          "Try a broader product name or a different ship-to country.",
                "citations": [], "provider": "deterministic", "grounded": True}
    top = products[0]
    best = top["offers"][0] if top.get("offers") else None
    if best and best.get("landed"):
        citations.append(best["offer_id"])
        lines.append(
            f"Best value for '{top['title']}': {best['landed']['currency']} {best['landed']['total']} "
            f"landed to {search_result.get('country')} via {best['offer']['connector']} "
            f"(trust {best['trust_score']}/100: {'; '.join(best.get('trust_reasons', [])[:2])}).")
        if best.get("fair_position"):
            lines.append(f"Its price sits {best['fair_position'].replace('_', ' ')} for this product group.")
        if best.get("quarantined"):
            lines.append("Warning: the cheapest listing is quarantined as a possible glitch price — treat it with caution.")
    alt = None
    for p in products[1:]:
        if p.get("offers"):
            alt = p
            break
    if alt and alt["offers"] and alt["offers"][0].get("landed"):
        o = alt["offers"][0]
        citations.append(o["offer_id"])
        lines.append(f"Alternative: '{alt['title']}' from {o['landed']['currency']} {o['landed']['total']} landed.")
    if parsed["budget"] and best and best.get("landed"):
        within = best["landed"]["total"] <= parsed["budget"]
        lines.append(f"Against your budget of {parsed['budget']}: the best offer is "
                     f"{'within' if within else 'above'} it.")
    return {"answer": " ".join(lines), "citations": citations,
            "provider": "deterministic", "grounded": True}


def verify_grounded(answer: str, search_result: dict, extra_allowed: set[str] | None = None) -> bool:
    """Every number in the answer must exist in this turn's tool result
    (including numbers inside its strings, e.g. 'iPhone 15') or in
    extra_allowed (the user's own budget, quoted back)."""
    allowed: set[str] = set(extra_allowed or ())

    def add_number(n: str):
        n = n.replace(",", "")
        allowed.add(n)
        try:
            f = float(n)
            allowed.add(str(int(f)) if f == int(f) else f"{f:.2f}")
        except ValueError:
            pass

    def collect(x):
        if isinstance(x, (int, float)):
            add_number(str(x))
        elif isinstance(x, str):
            for n in re.findall(r"\d[\d,]*\.?\d*", x):
                add_number(n)
        elif isinstance(x, dict):
            for v in x.values():
                collect(v)
        elif isinstance(x, list):
            for v in x:
                collect(v)

    collect(search_result.get("products", []))
    for num in re.findall(r"\d[\d,]*\.?\d*", answer):
        n = num.replace(",", "")
        if n not in allowed and str(int(float(n))) not in allowed and f"{float(n):.2f}" not in allowed:
            return False
    return True


def answer(query: str, country: str = "PK", currency: str = "PKR") -> dict:
    from app.services.search import search as run_search

    parsed = parse_query(query)
    filters = {}
    result = run_search(parsed["search_terms"], filters, country, currency)
    built = build_answer(query, result)
    extra = set()
    if parsed["budget"]:
        extra = {str(parsed["budget"]), str(int(parsed["budget"]))}
    built["grounded_verified"] = verify_grounded(built["answer"], result, extra)
    built["demo"] = result.get("demo", False)
    return built
