// Money formatting (directive §7). PKR/INR use lakh/crore phrasing with
// South-Asian digit grouping, mirroring the backend formatter
// (app/priceintel/location.py) so web and API agree.
const SOUTH_ASIAN = new Set(['PKR', 'INR']);

function groupSouthAsian(n: number): string {
  const neg = n < 0; const s = String(Math.abs(Math.trunc(n)));
  if (s.length <= 3) return (neg ? '-' : '') + s;
  const head = s.slice(0, -3); const tail = s.slice(-3);
  const parts: string[] = []; let h = head;
  while (h.length > 2) { parts.unshift(h.slice(-2)); h = h.slice(0, -2); }
  if (h) parts.unshift(h);
  return (neg ? '-' : '') + parts.join(',') + ',' + tail;
}

function trim(x: number): string {
  return x.toFixed(2).replace(/\.?0+$/, '');
}

export function formatMoney(amount: number, currency: string): string {
  const cur = (currency || '').toUpperCase();
  const n = Math.round(amount);
  if (SOUTH_ASIAN.has(cur) && Math.abs(n) >= 100000) {
    if (Math.abs(n) >= 10000000) return `${cur} ${trim(n / 10000000)} crore (${cur} ${groupSouthAsian(n)})`;
    return `${cur} ${trim(n / 100000)} lakh (${cur} ${groupSouthAsian(n)})`;
  }
  if (SOUTH_ASIAN.has(cur)) return `${cur} ${groupSouthAsian(n)}`;
  return `${cur} ${n.toLocaleString('en-US')}`;
}
