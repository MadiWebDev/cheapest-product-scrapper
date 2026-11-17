// i18n scaffolding (directive §21): core flows in en / ur / ar with RTL
// for ur+ar. Full-string coverage grows incrementally; the missing-key
// check (scripts/check-i18n.mjs) guarantees every locale carries every
// key the UI can request — a missing key is a build-time failure, not a
// silent English fallback.
export const en = {
  search_label: 'Search products',
  ship_to: 'Ship-to country',
  currency: 'Currency',
  search_button: 'Search',
  landed: 'landed',
  trust: 'Trust',
  demo_banner: 'Demo mode: showing demo data (DEMO_MODE=true).',
  no_results: 'No results yet — try a search.',
  loading: 'Loading offers…',
  methodology: 'How we calculate',
  lite_mode: 'Lite mode',
  language: 'Language',
  evidence: 'Why am I seeing this?',
  checked: 'checked',
  match: 'match',
  buy: 'Buy',
  compare: 'Compare',
  set_alert: 'Set price alert',
};
export const ur = {
  search_label: 'پروڈکٹس تلاش کریں',
  ship_to: 'ترسیل کا ملک',
  currency: 'کرنسی',
  search_button: 'تلاش کریں',
  landed: 'کل لاگت',
  trust: 'اعتماد',
  demo_banner: 'ڈیمو موڈ: ڈیمو ڈیٹا دکھایا جا رہا ہے۔',
  no_results: 'ابھی کوئی نتیجہ نہیں — تلاش کر کے دیکھیں۔',
  loading: 'آفرز لوڈ ہو رہی ہیں…',
  methodology: 'ہم حساب کیسے لگاتے ہیں',
  lite_mode: 'لائٹ موڈ',
  language: 'زبان',
  evidence: 'مجھے یہ کیوں دکھایا جا رہا ہے؟',
  checked: 'جانچا گیا',
  match: 'مماثلت',
  buy: 'خریدیں',
  compare: 'موازنہ',
  set_alert: 'قیمت الرٹ لگائیں',
};
export const ar = {
  search_label: 'ابحث عن المنتجات',
  ship_to: 'بلد الشحن',
  currency: 'العملة',
  search_button: 'بحث',
  landed: 'التكلفة الكلية',
  trust: 'الثقة',
  demo_banner: 'وضع العرض: يتم عرض بيانات تجريبية.',
  no_results: 'لا توجد نتائج بعد — جرّب البحث.',
  loading: 'جارٍ تحميل العروض…',
  methodology: 'كيف نحسب',
  lite_mode: 'الوضع الخفيف',
  language: 'اللغة',
  evidence: 'لماذا أرى هذا؟',
  checked: 'تم التحقق',
  match: 'تطابق',
  buy: 'اشترِ',
  compare: 'قارن',
  set_alert: 'تنبيه السعر',
};
export type Locale = 'en' | 'ur' | 'ar';
export const LOCALES: Record<Locale, Record<string, string>> = { en, ur, ar };
export const RTL_LOCALES: Locale[] = ['ur', 'ar'];
export function dirFor(locale: Locale): 'rtl' | 'ltr' {
  return RTL_LOCALES.includes(locale) ? 'rtl' : 'ltr';
}
export function t(locale: Locale, key: keyof typeof en): string {
  return LOCALES[locale][key] ?? en[key];
}
