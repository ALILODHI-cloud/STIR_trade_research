"""Fetch fixed-contract STIR futures history from Barchart (browser session).

Requires a real Chrome that can clear the AWS WAF challenge (headed).
Writes data/raw/stir_futures/{histories_raw,histories_meta,latest_quotes}.json

Symbols: SQ (3M SOFR), IM (3M Euribor), J8 (3M SONIA) — fixed contracts only.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "stir_futures"

BASE_PARAMS = {
    "fields": (
        "tradeTime.format(m/d/Y),openPrice,highPrice,lowPrice,lastPrice,"
        "priceChange,percentChange,volume,openInterest,symbolCode,symbolType"
    ),
    "type": "eod",
    "orderBy": "tradeTime",
    "orderDir": "desc",
    "maxRecords": "500",
    "startDate": "01012026",
}


def symbols() -> list[str]:
    out: list[str] = []
    for root in ("SQ", "IM", "J8"):
        for y in ("26", "27", "28", "29"):
            for m in ("H", "M", "U", "Z"):
                out.append(f"{root}{m}{y}")
    for m in ("F", "G", "J", "K", "N", "Q", "V", "X"):
        out.append(f"SQ{m}26")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    syms = symbols()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_context().new_page()
        page.goto(
            "https://www.barchart.com/futures/quotes/J8Z26",
            wait_until="domcontentloaded",
            timeout=120_000,
        )
        for _ in range(40):
            html = page.content()
            if "challenge-container" not in html and "J8Z26" in html:
                break
            time.sleep(1)

        all_rows: dict = {}
        meta: dict = {}
        for i, sym in enumerate(syms):
            params = dict(BASE_PARAMS)
            params["symbol"] = sym
            r = page.evaluate(
                """async (params) => {
                const url='https://www.barchart.com/proxies/core-api/v1/historical/get?'
                  + new URLSearchParams(params);
                const resp=await fetch(url,{credentials:'include',
                  headers:{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}});
                return {status:resp.status, text:await resp.text()};
            }""",
                params,
            )
            if r["status"] != 200:
                meta[sym] = {"ok": False, "status": r["status"]}
                continue
            data = json.loads(r["text"])
            rows = data.get("data") or []
            all_rows[sym] = rows
            meta[sym] = {"ok": True, "n": len(rows), "total": data.get("total")}
            print(f"{i+1}/{len(syms)} {sym} n={len(rows)}")
            time.sleep(0.12)

        quotes: list = []
        for i in range(0, len(syms), 30):
            chunk = syms[i : i + 30]
            rq = page.evaluate(
                """async (syms) => {
                const url='https://www.barchart.com/proxies/core-api/v1/quotes/get?'
                  + new URLSearchParams({
                    symbols: syms.join(','),
                    fields: 'symbol,contractName,lastPrice,priceChange,previousPrice,tradeTime,volume,openInterest,highPrice,lowPrice,openPrice'
                  });
                const resp=await fetch(url,{credentials:'include',
                  headers:{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}});
                return {status:resp.status, text:await resp.text()};
            }""",
                chunk,
            )
            if rq["status"] == 200:
                quotes.extend(json.loads(rq["text"]).get("data") or [])
        browser.close()

    (OUT / "histories_raw.json").write_text(json.dumps(all_rows))
    (OUT / "histories_meta.json").write_text(json.dumps(meta, indent=2))
    (OUT / "latest_quotes.json").write_text(json.dumps(quotes, indent=2))
    print("wrote", OUT, "symbols", len(all_rows), "quotes", len(quotes))


if __name__ == "__main__":
    main()
