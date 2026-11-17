#!/usr/bin/env node
// Missing-key check: every locale in lib/i18n.ts must define exactly
// the same key set as English. Exits 1 on any drift.
import { readFileSync } from 'node:fs';

const src = readFileSync(new URL('../lib/i18n.ts', import.meta.url), 'utf8');

function keysOf(name) {
  const m = src.match(new RegExp(`export const ${name} = \\{([\\s\\S]*?)\\};`));
  if (!m) throw new Error(`locale block ${name} not found`);
  return [...m[1].matchAll(/^\s*([a-z_]+):/gm)].map((x) => x[1]).sort();
}

const en = keysOf('en');
let failed = false;
for (const loc of ['ur', 'ar']) {
  const keys = keysOf(loc);
  const missing = en.filter((k) => !keys.includes(k));
  const extra = keys.filter((k) => !en.includes(k));
  if (missing.length || extra.length) {
    failed = true;
    console.error(`${loc}: missing=[${missing}] extra=[${extra}]`);
  } else {
    console.log(`${loc}: ${keys.length}/${en.length} keys OK`);
  }
}
if (failed) process.exit(1);
console.log('i18n: all locales complete');
