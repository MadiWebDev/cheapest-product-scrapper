// MV3 service worker: intentionally minimal — the popup does the work.
// Kept as the registered entry point for future context-menu actions.
chrome.runtime.onInstalled.addListener(() => {
  console.log('PriceIntel extension installed');
});
