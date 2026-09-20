# STIR strips dashboard

## Open it (pick one)

### Permanent static mirror (no Pages setup)

https://cdn.jsdelivr.net/gh/ALILODHI-cloud/STIR_trade_research@gh-pages/index.html

Assets and `data/curves.json` load from the same CDN path. After each
`gh-pages` publish, jsDelivr may cache the branch tip for up to ~12h; append
`?t=` or pin a commit SHA if you need an instant refresh.

### Live tunnel (this cloud agent VM only)

Ephemeral `*.trycloudflare.com` URL — ask the agent for the current hostname.
Old tunnel links die; do not bookmark them.

### GitHub Pages (optional, auto weekday refresh)

One-time enable:

1. https://github.com/ALILODHI-cloud/STIR_trade_research/settings/pages  
2. Source: **Deploy from a branch** → **gh-pages** / root → Save  
3. Site: https://alilodhi-cloud.github.io/STIR_trade_research/

Workflow: `.github/workflows/deploy-dashboard.yml` (push + weekdays 21:30 UTC).

## Why links failed

- Absolute `<base href="/STIR_trade_research/">` broke every host except
  project Pages (CDN/tunnel asset paths 404). Removed.
- Cloudflare quick tunnels expire.
- `github.io` stays 404 until Pages is enabled once.

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/serve_dashboard.py
# http://127.0.0.1:8765/
```
