# PriceIntel browser extension (MV3 scaffold)

Status: IMPLEMENTED-UNVERIFIED — no browser runtime is available in
the build environment to load-test the extension; the code is complete
and syntax-checked, and its API calls target the same backend as web.

Flow: popup reads the active tab URL -> backend `/api/extract`
(SSRF-guarded) identifies the product -> `/api/search` compares ->
best landed price + trust shown with the tracked `/go` link.
Permissions are minimal (`activeTab` + the API host only).
