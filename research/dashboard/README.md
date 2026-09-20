# STIR strips dashboard

## Open it now

Cloudflare quick tunnel (works from phone/laptop while this cloud agent is up;
URL changes if the tunnel restarts):

- https://representing-depot-misc-cpu.trycloudflare.com/
- https://representing-depot-misc-cpu.trycloudflare.com/stir-strips.html

`stir-strips.html` is a single-file bundle (CSS/JS/curves inlined).
As-of strip data: **2026-09-18**.

## Permanent hosting

GitHub Pages is the durable host. Enable once (agent cannot flip this switch):

1. https://github.com/ALILODHI-cloud/STIR_trade_research/settings/pages
2. Source: **Deploy from a branch** → **gh-pages** / `(root)` → Save
3. Site: https://alilodhi-cloud.github.io/STIR_trade_research/

Until then `*.github.io` returns 404. Do **not** use jsDelivr for the HTML
(it serves `text/plain`, so the browser shows source).

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/pack_dashboard_bundle.py
python3 scripts/serve_dashboard.py
# http://127.0.0.1:8765/
```
