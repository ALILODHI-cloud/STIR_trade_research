# STIR strips dashboard

## Open it now

**Fresh Cloudflare link** (works from phone/laptop; only while the cloud agent VM is up — the old `*.trycloudflare.com` URLs die):

Ask the agent for the current tunnel, or check the latest chat message.

**Permanent URL** (any device, auto-updates weekdays):

1. Open https://github.com/ALILODHI-cloud/STIR_trade_research/settings/pages
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / root → Save
4. Site: https://alilodhi-cloud.github.io/STIR_trade_research/

The GitHub Actions workflow publishes `research/dashboard` to `gh-pages` and
refreshes FRED spots on weekdays at 21:30 UTC. Manual: Actions → Deploy STIR
dashboard → Run workflow.

## Why links failed before

- Cloudflare quick tunnels expire; old URLs return errors.
- `github.io` 404s until Pages is enabled in repo Settings (one-time).

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/serve_dashboard.py
```
