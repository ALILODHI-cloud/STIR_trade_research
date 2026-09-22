# STIR strips dashboard

## Stable link

Use the branch-backed single-file dashboard:

- https://raw.githack.com/ALILODHI-cloud/STIR_trade_research/gh-pages/stir-strips.html

This URL does not change when the dashboard is republished. Raw.githack shows
a safety confirmation the first time a browser opens HTML from this repository;
continue once and the interactive dashboard loads. It is the working fallback
until GitHub Pages is enabled.

Latest RV workbook:

- https://raw.githubusercontent.com/ALILODHI-cloud/STIR_trade_research/gh-pages/peak_rv_universe_latest.xlsx

`stir-strips.html` is a single-file bundle (CSS/JS/curves inlined).
The current as-of date is shown in the dashboard header.

## Permanent hosting

GitHub Pages is the durable first-party host. The publishing workflow already
keeps the `gh-pages` branch current. Enable the site once:

1. https://github.com/ALILODHI-cloud/STIR_trade_research/settings/pages
2. Source: **Deploy from a branch** → **gh-pages** / `(root)` → Save
3. Site: https://alilodhi-cloud.github.io/STIR_trade_research/

Until step 2 is done, `*.github.io` returns 404. Cloudflare quick tunnels are
deliberately not listed here because they expire. Do not use jsDelivr for the
HTML (it serves `text/plain`, so the browser shows source).

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/pack_dashboard_bundle.py
python3 scripts/serve_dashboard.py
# http://127.0.0.1:8765/
```
