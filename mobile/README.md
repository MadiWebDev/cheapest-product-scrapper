# PriceIntel mobile (Expo scaffold)

Status: IMPLEMENTED-UNVERIFIED — code-complete scaffold; no device or
emulator runtime exists in the build environment, so nothing here has
been run on a device and no app-store claims are made.

- Search, landed price, trust and /go buy links work against the same
  backend as the web app (`lib/api.ts`, EXPO_PUBLIC_API_URL).
- Deep links: scheme `priceintel://` (see app.json); web cards link
  here from "Open in app".
- Barcode / snap-to-search: entry points exist behind flags in
  `lib/features.ts`, disabled until a device-verified build.
