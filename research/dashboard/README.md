# STIR strips dashboard

## Open it now

**Working live link** (Cloudflare tunnel to this agent):

https://selected-connection-would-teaches.trycloudflare.com/

Self-contained mirror on the same host (single file, no extra asset fetches):

https://selected-connection-would-teaches.trycloudflare.com/stir-strips.html

**Permanent preview** (no Pages setup; opens the bundled HTML via htmlpreview):

https://htmlpreview.github.io/?https://raw.githubusercontent.com/ALILODHI-cloud/STIR_trade_research/gh-pages/stir-strips.html

## Optional: GitHub Pages

`github.io` stays 404 until you enable Pages once:

1. https://github.com/ALILODHI-cloud/STIR_trade_research/settings/pages
2. Deploy from branch → **gh-pages** / root → Save
3. Then: https://alilodhi-cloud.github.io/STIR_trade_research/

## Why earlier links failed

- Absolute `<base href="/STIR_trade_research/">` broke tunnel/CDN asset paths (removed).
- jsDelivr serves `.html` as `text/plain` (browser shows source, not the app).
- Cloudflare quick tunnels expire — bookmark the htmlpreview URL instead.
- `*.github.io` needs the one-time Pages enable above.

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/pack_dashboard_bundle.py   # writes stir-strips.html
python3 scripts/serve_dashboard.py
```
