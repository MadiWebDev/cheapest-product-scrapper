# Methodology

The public methodology page lives in the web app at `/methodology`
(web-application/app/methodology/page.tsx) and is the canonical
user-facing text. Engineering summary:

- Landed cost = item + shipping + duty + tax + handling, FX-converted
  with a disclosed margin; certainty labels per line (CONFIRMED /
  SELLER_ESTIMATE / PLATFORM_ESTIMATE with rule id+version / UNKNOWN).
- Fair-price band = median/IQR of current offers, hidden below 5.
- Price Confidence Index = band sample + shipping certainty + FX
  freshness + review evidence (components exposed).
- Trust (trust-v2.1) = decomposable seller/review/protection signals
  with stored inputs and warning categories (indicators only).
- Matching = hard variant separation first, explainable confidence
  second; human review overrides win.
- Ranking = landed + trust + delivery only; monetization data is
  architecturally excluded (tests).
