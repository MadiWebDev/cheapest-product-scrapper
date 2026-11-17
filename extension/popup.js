// Popup flow: read the active tab URL -> extract the product with the
// backend's SSRF-guarded extractor -> search for the same product ->
// show the best landed price + trust, with the tracked /go buy link.
async function main() {
  const status = document.getElementById('status');
  const result = document.getElementById('result');
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) { status.textContent = 'No active tab URL.'; return; }
    const extracted = await window.PriceIntelApi.extractFromUrl(tab.url);
    const title = extracted.offers && extracted.offers[0] ? extracted.offers[0].title : '';
    if (!title) { status.textContent = 'No product data found on this page.'; return; }
    status.textContent = `Comparing: ${title}`;
    const res = await window.PriceIntelApi.search(title);
    const product = res.products && res.products[0];
    if (!product || !product.offers.length) { result.textContent = 'No comparison offers found.'; return; }
    const best = product.offers[0];
    const a = document.createElement('a');
    a.href = `${window.PriceIntelApi.API_BASE}${best.go_url}`;
    a.target = '_blank';
    a.textContent = 'Open best offer';
    result.innerHTML = '';
    const p = document.createElement('p');
    p.className = 'price';
    p.textContent = best.landed ? `${best.landed.currency} ${best.landed.total} landed` : 'No landed price';
    const t = document.createElement('p');
    t.textContent = `Trust ${best.trust_score}/100 — ${(best.trust_reasons || [])[0] || ''}`;
    result.append(p, t, a);
  } catch (e) {
    status.textContent = `Error: ${e.message} (is the API running?)`;
  }
}
main();
