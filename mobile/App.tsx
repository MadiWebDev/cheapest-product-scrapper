import React, { useState } from 'react';
import { Button, FlatList, Linking, SafeAreaView, Text, TextInput, View } from 'react-native';
import { searchProducts, goUrl, type ProductResult } from './lib/api';
import { FEATURE_BARCODE_SCAN, assertFeatureEnabled } from './lib/features';

// PriceIntel mobile (Expo scaffold). Search + landed price + trust are
// live against the backend; barcode entry is behind a disabled flag.
export default function App() {
  const [q, setQ] = useState('iPhone 15');
  const [items, setItems] = useState<ProductResult[]>([]);
  const [err, setErr] = useState('');
  async function run() {
    setErr('');
    try { const r = await searchProducts(q); setItems(r.products); }
    catch (e) { setErr('Search failed — is the API reachable?'); }
  }
  return (
    <SafeAreaView style={{ padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: '700' }}>PriceIntel</Text>
      <TextInput value={q} onChangeText={setQ} accessibilityLabel="Search products"
        style={{ borderWidth: 1, padding: 10, marginVertical: 8 }} />
      <Button title="Search" onPress={run} />
      <Button title="Scan barcode (disabled in this build)" onPress={() => {
        try { assertFeatureEnabled('barcode', FEATURE_BARCODE_SCAN); } catch (e) { setErr(String(e)); }
      }} />
      {!!err && <Text style={{ color: 'red' }}>{err}</Text>}
      <FlatList data={items} keyExtractor={(p) => p.id} renderItem={({ item }) => {
        const best = item.offers[0];
        return (
          <View style={{ borderWidth: 1, padding: 10, marginTop: 8 }}>
            <Text style={{ fontWeight: '600' }}>{item.title}</Text>
            {best?.landed && <Text>{best.landed.currency} {best.landed.total} landed · Trust {best.trust_score}/100</Text>}
            {!!best?.trust_reasons?.[0] && <Text>{best.trust_reasons[0]}</Text>}
            {!!best && <Button title="Buy" onPress={() => Linking.openURL(goUrl(best.go_url))} />}
          </View>
        );
      }} />
    </SafeAreaView>
  );
}
