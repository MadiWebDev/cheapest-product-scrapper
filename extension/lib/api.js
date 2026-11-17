// Shared API client for the extension. The API base is the user's own
// backend (default localhost in this scaffold build); no data leaves
// for anywhere else.
const API_BASE = 'http://localhost:8000';

async function extractFromUrl(url) {
  const r = await fetch(`${API_BASE}/api/extract?url=${encodeURIComponent(url)}`);
  if (!r.ok) throw new Error(`extract failed: ${r.status}`);
  return r.json();
}

async function search(query, country = 'PK', currency = 'PKR') {
  const r = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, country, currency }),
  });
  if (!r.ok) throw new Error(`search failed: ${r.status}`);
  return r.json();
}

// Exposed for popup.js (MV3 popup pages cannot use ES modules without a bundler).
window.PriceIntelApi = { extractFromUrl, search, API_BASE };
