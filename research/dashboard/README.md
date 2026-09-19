# STIR strips dashboard

Live tabbed view of Euribor / SOFR / SONIA 3M futures strips.

## Run

```bash
python3 scripts/build_dashboard_data.py   # from data/cache/stir_curves
python3 scripts/serve_dashboard.py        # http://127.0.0.1:8765/
```

## Features

- Tabs per curve
- Full strip in rate space
- History slider: latest curve stays fixed (amber); historical overlays (teal)
- Click a contract: side panel shows
  - cumulative change vs policy at latest
  - cumulative change vs policy on the slider date
  - difference between those two priced changes
- Refresh button + 15s poll of `data/meta.json` for live updates after rebuilds
- `POST /api/rebuild` regenerates JSON from the cache

Policy spots: SOFR overnight, ECB DFR (Euribor tab), SONIA overnight.
