'use client';
import {useEffect,useState} from 'react';
import {formatMoney} from '../lib/format';
const API=process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000';
type Offer={offer:any; landed:any; quality_score:number; quality_explanation:any; value_score:number; availability:string; badges?:string[]; go_url?:string; trust_score?:number; trust_reasons?:string[]; certainty?:any; checked_at?:string};
type Product={id:string; title:string; offers:Offer[]};
export default function SearchApp(){
 const [q,setQ]=useState('iPhone 15'); const [country,setCountry]=useState('US'); const [currency,setCurrency]=useState('USD');
 const [products,setProducts]=useState<Product[]>([]); const [loading,setLoading]=useState(false); const [demo,setDemo]=useState(false); const [err,setErr]=useState(''); const [compare,setCompare]=useState<Product[]>([]);
 // Location intelligence (§5): a remembered manual choice is restored on
 // load and always wins; changing the selects updates the memory.
 useEffect(()=>{ try{ const c=localStorage.getItem('pi_country'); const cur=localStorage.getItem('pi_currency'); if(c) setCountry(c); if(cur) setCurrency(cur); }catch{} },[]);
 useEffect(()=>{ try{ localStorage.setItem('pi_country',country); localStorage.setItem('pi_currency',currency); }catch{} },[country,currency]);
 async function go(){
  setLoading(true); setErr('');
  try{ const r=await fetch(`${API}/api/search`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q,country,currency})}); const d=await r.json(); setProducts(d.products||[]); setDemo(!!d.demo); }
  catch(e){ setErr('Search failed — is the API running?'); } setLoading(false);
 }
 return <main className="mx-auto max-w-6xl p-4">
  <h1 className="text-3xl font-bold">Cheapest Product Finder</h1>
  <p className="text-sm opacity-70">Global price comparison ranked by landed price, quality and delivery. Tax/duty figures are estimates unless marked exact. Affiliate links may earn a commission — disclosed here.</p>
  {demo && <div role="alert" className="my-2 rounded bg-yellow-200 p-2 text-black">Demo mode: showing demo data (DEMO_MODE=true).</div>}
  <div className="my-4 flex flex-wrap gap-2">
   <input aria-label="Search products" className="min-w-64 flex-1 rounded border p-3 text-black" value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&go()}/>
   <select aria-label="Ship-to country" className="rounded border p-3 text-black" value={country} onChange={e=>setCountry(e.target.value)}>{['US','GB','DE','FR','AE','SA','IN','PK','AU','JP','CA','BR','TR','ZA','NG','SG'].map(c=><option key={c}>{c}</option>)}</select>
   <select aria-label="Currency" className="rounded border p-3 text-black" value={currency} onChange={e=>setCurrency(e.target.value)}>{['USD','EUR','GBP','PKR','INR','AED','SAR','JPY','AUD','CAD'].map(c=><option key={c}>{c}</option>)}</select>
   <button className="rounded bg-blue-600 px-5 py-3 text-white" onClick={go}>Search</button>
  </div>
  {loading && <div aria-busy="true">Loading offers… (skeleton)</div>}
  {err && <div role="alert" className="text-red-600">{err}</div>}
  {!loading && products.length===0 && <p>No results yet — try a search.</p>}
  <div className="grid gap-4 md:grid-cols-2">
   {products.map(p=>{const best=p.offers[0]; if(!best) return null; return <article key={p.id} className="rounded border p-4">
    <h2 className="font-semibold">{p.title}</h2>
    <p className="text-2xl">{best.landed?formatMoney(best.landed.total, best.landed.currency):'—'} <span className="text-sm">landed</span></p>
    {best.certainty && <p className="text-xs">Item price: {best.certainty.labels.item} · Tax/duty: {best.certainty.labels.tax.replaceAll('_',' ')} (estimate)</p>}
    {best.trust_reasons && best.trust_reasons.length>0 && <p className="text-sm">Trust {best.trust_score}/100 — {best.trust_reasons[0]}</p>}
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
