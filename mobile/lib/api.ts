// PriceIntel API client — talks to the same backend as the web app.
// Base URL is configured with EXPO_PUBLIC_API_URL (no secrets in code).
const BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export interface Landed { total: number; currency: string }
export interface OfferResult {
  offer: { connector: string; title: string; url: string; price: number; currency: string };
  landed: Landed | null;
  trust_score: number;
  trust_reasons: string[];
  go_url: string;
  fair_position: string | null;
  quarantined?: boolean;
}
export interface ProductResult { id: string; title: string; offers: OfferResult[]; fair_price_band?: unknown }
export interface SearchResponse {
  products: ProductResult[];
  sponsored: Array<{ title: string; url: string; label: string }>;
  demo: boolean;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API ${path} failed: ${r.status}`);
  return (await r.json()) as T;
}

export function searchProducts(query: string, country = 'PK', currency = 'PKR'): Promise<SearchResponse> {
  return post<SearchResponse>('/api/search', { query, country, currency });
}

export function createAlert(userRef: string, query: string, targetPrice: number, destination: string) {
  return post('/api/alerts', { user_ref: userRef, query, target_price: targetPrice, channel: 'email', destination });
}

export function goUrl(goPath: string): string {
  return `${BASE}${goPath}`;
}
