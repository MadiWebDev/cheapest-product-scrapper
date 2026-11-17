# Database

## Persistent models (v1, SQLAlchemy — unchanged by v3)
- `products` / `suppliers` (catalog), `price_history` (per-product
  price points), `watchlist_items`, `alerts` (app/models/catalog.py),
  plus the v1 user/auth models. Migrations: Alembic (backend/alembic).
- Money is stored as NUMERIC(19,4) (decision D-007 line); tax/duty/FX
  rule data are versioned JSON in backend/app/data/ (vat_gst.json,
  duty.json, countries.json, compliance/, manifests/).

## v3 in-process stores (walking-skeleton scope)
The v3 services keep runtime state in process-local stores with small,
explicit interfaces so a DB backing can replace them without API
changes: OfferStore + clicks (priceintel/go.py), AdapterHealth,
AlertService, MatchReviewQueue overrides, OutcomeStore, ConversionLedger,
SellerIntel observations, DevKeys/AdminAuth key stores.

**Deployment consequence (honest):** in multi-process deployments
these stores are per-process until the DB-backed implementations land;
the API shapes already match the DB models where they exist (alerts,
watchlists, price history).
