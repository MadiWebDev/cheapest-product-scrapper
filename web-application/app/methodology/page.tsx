export const metadata = { title: 'Methodology — Cheapest Product Finder' };
export default function Methodology() {
  return <main className="mx-auto max-w-3xl p-4">
    <h1 className="text-3xl font-bold">How we calculate</h1>
    <section><h2 className="mt-4 text-xl font-semibold">Landed cost</h2>
      <p>The price you actually pay: item + shipping + customs duty + VAT/GST + handling, converted at a live FX rate with a small disclosed margin. The item price is CONFIRMED (as listed). Tax and duty are PLATFORM_ESTIMATEs from versioned rule tables (duty.json, vat_gst.json) — estimates, never a guarantee. When a mandatory component is unknown, we rank on the conservative computed total and say so.</p></section>
    <section><h2 className="mt-4 text-xl font-semibold">Fair price &amp; confidence</h2>
      <p>The fair-price band is the interquartile range of current offers for the same product; it is hidden when fewer than 5 offers exist. The Price Confidence Index (0–100) combines band sample size, shipping certainty, FX freshness and review evidence — its components are shown in every evidence drawer. A price more than 60% below the group median is quarantined as a possible glitch pending re-verification.</p></section>
    <section><h2 className="mt-4 text-xl font-semibold">Trust score</h2>
      <p>Trust (formula trust-v2.1) decomposes into seller history, review evidence adjusted for fake-review patterns, buyer protection, warranty, returns, official-store status and a counterfeit-risk indicator when a price sits far below the market median. Warnings are risk indicators, not accusations. The top reasons are printed on every card and the full inputs in the evidence drawer.</p></section>
    <section><h2 className="mt-4 text-xl font-semibold">Matching</h2>
      <p>Offers are grouped only when they agree on the hard variant axes — storage, RAM, colour, generation, condition, SIM, carrier lock, bundle and accessory-vs-device. Every grouped offer shows its match confidence and the reasons behind it.</p></section>
    <section><h2 className="mt-4 text-xl font-semibold">Ranking independence &amp; sources</h2>
      <p>Ranking uses landed cost, trust and delivery speed only. Commissions, campaigns and sponsored placements are never ranking inputs — this is enforced by automated tests, including a check that configuring affiliate tags cannot change any score or ordering. Sources run in live mode only with an approved, unexpired compliance review of their terms and robots rules; the rest stay disabled. Outbound links may earn a commission when an affiliate tag is configured; that never affects ranking.</p></section>
  </main>;
}
