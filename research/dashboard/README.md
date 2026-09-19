# STIR strips dashboard

Live tabbed view of Euribor / SOFR / SONIA 3M futures strips.

## Public URL (any device)

**Permanent (after Pages is enabled + this workflow runs):**  
https://alilodhi-cloud.github.io/STIR_trade_research/

One-time setup: repo **Settings → Pages → Source: GitHub Actions**.  
Then merge this branch / run the **Deploy STIR dashboard** workflow.

Auto-updates: weekday schedule at 21:30 UTC (refreshes FRED spots + rebuilds
the JSON from the latest committed futures panel). Trigger manually via
Actions → Deploy STIR dashboard → Run workflow.

**Ephemeral tunnel** (only while the cloud agent VM is up): ask the agent for
the current `*.trycloudflare.com` link.

## Local

```bash
python3 scripts/build_dashboard_data.py
python3 scripts/serve_dashboard.py   # http://127.0.0.1:8765/
```

## Features

- Tabs per curve
- Latest curve fixed (amber); historical overlay via slider (teal)
- Click a contract: cumul vs policy at latest vs slider date, and the delta
- Client polls `data/meta.json` every 15s so a new deploy shows up without refresh
