'use client';
import {useEffect,useState} from 'react';
import {formatMoney} from '../lib/format';
import {t, dirFor, type Locale} from '../lib/i18n';
const API=process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000';
type Offer={offer:any; landed:any; quality_score:number; quality_explanation:any; value_score:number; availability:string; badges?:string[]; go_url?:string; trust_score?:number; trust_reasons?:string[]; trust?:any; certainty?:any; checked_at?:string; match_confidence?:number; match_reasons?:string[]; fair_position?:string|null; pci?:any; quarantined?:boolean; quarantine_reason?:string; ranking?:any};
type Product={id:string; title:string; offers:Offer[]; fair_price_band?:any};
function freshness(iso:string|undefined, locale:Locale): string{
 if(!iso) return '';
 const mins=Math.max(0, Math.round((Date.now()-new Date(iso).getTime())/60000));
 return mins<=1?`${t(locale,'checked')} just now`:`${t(locale,'checked')} ${mins} min ago`;
}
export default function SearchApp(){
 const [q,setQ]=useState('iPhone 15'); const [country,setCountry]=useState('US'); const [currency,setCurrency]=useState('USD');
 const [products,setProducts]=useState<Product[]>([]); const [loading,setLoading]=useState(false); const [demo,setDemo]=useState(false); const [err,setErr]=useState(''); const [compare,setCompare]=useState<Product[]>([]);
 // Location intelligence (§5): a remembered manual choice is restored on
 // load and always wins; changing the selects updates the memory.
 useEffect(()=>{ try{ const c=localStorage.getItem('pi_country'); const cur=localStorage.getItem('pi_currency'); if(c) setCountry(c); if(cur) setCurrency(cur); }catch{} },[]);
 useEffect(()=>{ try{ localStorage.setItem('pi_country',country); localStorage.setItem('pi_currency',currency); }catch{} },[country,currency]);
 const [locale,setLocale]=useState<Locale>('en'); const [lite,setLite]=useState(false);
 useEffect(()=>{ try{ const l=localStorage.getItem('pi_locale') as Locale|null; if(l&&(l==='en'||l==='ur'||l==='ar')) setLocale(l); setLite(localStorage.getItem('pi_lite')==='1'); }catch{} },[]);
 useEffect(()=>{ try{ localStorage.setItem('pi_locale',locale); localStorage.setItem('pi_lite',lite?'1':'0'); }catch{} document.documentElement.lang=locale; document.documentElement.dir=dirFor(locale); },[locale,lite]);
 async function go(){
  setLoading(true); setErr('');
  try{ const r=await fetch(`${API}/api/search`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q,country,currency})}); const d=await r.json(); setProducts(d.products||[]); setDemo(!!d.demo); }
  catch(e){ setErr('Search failed — is the API running?'); } setLoading(false);
 }
 return <main className="mx-auto max-w-6xl p-4">
  <h1 className="text-3xl font-bold">Cheapest Product Finder</h1>
  <p className="text-sm opacity-70">Global price comparison ranked by landed price, quality and delivery. Tax/duty figures are estimates unless marked exact. Affiliate links may earn a commission — disclosed here. <a className="underline" href="/methodology">{t(locale,'methodology')}</a></p>
  {demo && <div role="alert" className="my-2 rounded bg-yellow-200 p-2 text-black">{t(locale,'demo_banner')}</div>}
  <div className="my-4 flex flex-wrap gap-2">
   <input aria-label={t(locale,'search_label')} className="min-w-64 flex-1 rounded border p-3 text-black" value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&go()}/>
   <select aria-label={t(locale,'ship_to')} className="rounded border p-3 text-black" value={country} onChange={e=>setCountry(e.target.value)}>{['US','GB','DE','FR','AE','SA','IN','PK','AU','JP','CA','BR','TR','ZA','NG','SG'].map(c=><option key={c}>{c}</option>)}</select>
   <select aria-label={t(locale,'currency')} className="rounded border p-3 text-black" value={currency} onChange={e=>setCurrency(e.target.value)}>{['USD','EUR','GBP','PKR','INR','AED','SAR','JPY','AUD','CAD'].map(c=><option key={c}>{c}</option>)}</select>
   <select aria-label={t(locale,'language')} className="rounded border p-3 text-black" value={locale} onChange={e=>setLocale(e.target.value as Locale)}>{(['en','ur','ar'] as Locale[]).map(l=><option key={l} value={l}>{l==='en'?'English':l==='ur'?'اردو':'العربية'}</option>)}</select>
   <label className="flex items-center gap-1 text-sm"><input type="checkbox" checked={lite} onChange={e=>setLite(e.target.checked)}/> {t(locale,'lite_mode')}</label>
   <button className="rounded bg-blue-600 px-5 py-3 text-white" onClick={go}>{t(locale,'search_button')}</button>
  </div>
  {loading && <div aria-busy="true">Loading offers… (skeleton)</div>}
  {err && <div role="alert" className="text-red-600">{err}</div>}
  {!loading && products.length===0 && <p>No results yet — try a search.</p>}
  <div className="grid gap-4 md:grid-cols-2">
   {products.map(p=>{const best=p.offers[0]; if(!best) return null; return <article key={p.id} className="rounded border p-4">
    <h2 className="font-semibold">{p.title}</h2>
    <p className="text-2xl">{best.landed?formatMoney(best.landed.total, best.landed.currency):'—'} <span className="text-sm">landed</span></p>
    {best.certainty && <p className="text-xs">Item price: {best.certainty.labels.item} · Tax/duty: {best.certainty.labels.tax.replaceAll('_',' ')} (estimate)</p>}
    {best.trust_reasons && best.trust_reasons.length>0 && <p className="text-sm">{t(locale,'trust')} {best.trust_score}/100 — {best.trust_reasons[0]}</p>}
    <p className="text-xs opacity-80">{best.fair_position && <>Fair price: {best.fair_position.replaceAll('_',' ')} · </>}{best.match_confidence!=null && <>{t(locale,'match')} {best.match_confidence}% · </>}{best.pci && <>PCI {best.pci.index}/100 · </>}{freshness(best.checked_at, locale)}</p>
    {best.quarantined && <p role="alert" className="text-sm text-red-600">{best.quarantine_reason}</p>}
    {best.trust?.warnings?.length>0 && <p className="text-xs text-amber-700">⚠ {best.trust.warnings[0].text}</p>}
    {!lite && <details><summary className="cursor-pointer text-sm">{t(locale,'evidence')}</summary>
     <div className="text-xs">
      {p.fair_price_band && !p.fair_price_band.hidden && <p>Fair-price band ({p.fair_price_band.window}, n={p.fair_price_band.sample_size}): {p.fair_price_band.low} – {p.fair_price_band.high}, median {p.fair_price_band.median}</p>}
      {p.fair_price_band?.hidden && <p>Fair-price band hidden: {p.fair_price_band.reason}</p>}
      {best.pci && <p>Price Confidence Index {best.pci.index}/100 — components: {JSON.stringify(best.pci.components)}</p>}
      {best.certainty && <p>Certainty rules: tax {best.certainty.rules.tax}, duty {best.certainty.rules.duty}. {best.certainty.note}</p>}
      {best.match_reasons && <p>Match: {best.match_reasons.join('; ')}</p>}
      {best.ranking && <p>Ranking: position {best.ranking.position} — {best.ranking.basis}</p>}
     </div></details>}
    {best.landed && <details><summary className="cursor-pointer text-sm">Price breakdown</summary><pre className="text-xs">{JSON.stringify(best.landed,null,1)}</pre></details>}
    <p>Quality: {best.quality_score}/100 · Value: {best.value_score} · {best.availability} · via {best.offer.connector}</p>
    <details><summary className="cursor-pointer text-sm">Why this quality score?</summary><pre className="text-xs">{JSON.stringify(best.quality_explanation,null,1)}</pre></details>
    <details><summary className="cursor-pointer text-sm">Compare all {p.offers.length} offers</summary>{p.offers.map((o,i)=><p key={i} className="text-sm">{o.offer.connector}: {o.landed?o.landed.total:'—'} (Q {o.quality_score}) {(o.badges||[]).join(', ')}</p>)}</details>
    <div className="mt-2 flex gap-2"><a className="rounded bg-green-600 px-3 py-1 text-white" href={best.go_url?`${API}${best.go_url}`:best.offer.url} target="_blank" rel="noreferrer">Buy</a>
    <button className="rounded border px-3 py-1" onClick={()=>compare.length<4&&setCompare([...compare,p])}>Compare</button>
    <button className="rounded border px-3 py-1" onClick={()=>alert('Alert/watchlist: use POST /api alerts in the API (Phase 8)')}>Set price alert</button></div>
   </article>})}
  </div>
  {compare.length>0 && <section className="mt-6"><h2 className="font-bold">Compare ({compare.length}/4)</h2>{compare.map(p=><p key={p.id}>{p.title} — best landed {p.offers[0]?.landed?.total}</p>)}</section>}
 </main>;
}
