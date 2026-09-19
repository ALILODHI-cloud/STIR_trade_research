"""Data access: local-first, with a clear message when egress is blocked.

This session's network policy blocks the public data hosts, so every loader
looks on disk first. Drop files into data/raw/ (anything you export) or
data/manual/ (levels you paste), and they are picked up without a fetch. If
the host is allowlisted later, `fetch=True` starts working with no other
change to call sites.
"""
from __future__ import annotations

import io
import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
CACHE = ROOT / "data" / "cache"
MANUAL = ROOT / "data" / "manual"


class DataUnavailable(RuntimeError):
    """Raised when a series is neither on disk nor reachable."""


@dataclass(frozen=True)
class Source:
    key: str
    description: str
    url: str
    host: str


SOURCES: dict[str, Source] = {
    "SOFR": Source("SOFR", "Secured Overnight Financing Rate",
                   "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR", "fred.stlouisfed.org"),
    "EFFR": Source("EFFR", "Effective Fed Funds Rate",
                   "https://fred.stlouisfed.org/graph/fredgraph.csv?id=EFFR", "fred.stlouisfed.org"),
    "SONIA": Source("SONIA", "SONIA fixing (BoE IADB)",
                    "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp", "www.bankofengland.co.uk"),
    "ESTR": Source("ESTR", "Euro short-term rate (ECB Data Portal)",
                   "https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT?format=csvdata",
                   "data-api.ecb.europa.eu"),
    "CPIAUCSL": Source("CPIAUCSL", "US CPI, all items, SA",
                       "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL", "fred.stlouisfed.org"),
    "PAYEMS": Source("PAYEMS", "US nonfarm payrolls",
                     "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PAYEMS", "fred.stlouisfed.org"),
    "UNRATE": Source("UNRATE", "US unemployment rate",
                     "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE", "fred.stlouisfed.org"),
}


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    return pd.read_csv(path, sep=sep)


def find_local(key: str) -> Path | None:
    """First file in data/cache/ or data/raw/ whose stem matches `key`."""
    for folder in (CACHE, RAW):
        if not folder.exists():
            continue
        exact = [p for p in folder.iterdir() if p.stem.lower() == key.lower()]
        if exact:
            return exact[0]
        loose = [p for p in folder.iterdir()
                 if p.is_file() and key.lower() in p.stem.lower()]
        if loose:
            return sorted(loose)[0]
    return None


def load_series(key: str, fetch: bool = True, date_col: str | None = None,
                value_col: str | None = None) -> pd.Series:
    """Load a named series as a date-indexed float Series."""
    path = find_local(key)
    if path is not None:
        df = _read_any(path)
        dcol = date_col or df.columns[0]
        vcol = value_col or df.columns[1]
        s = pd.Series(
            pd.to_numeric(df[vcol], errors="coerce").values,
            index=pd.to_datetime(df[dcol], errors="coerce"),
            name=key,
        ).dropna()
        return s.sort_index()

    if fetch and key.upper() in SOURCES:
        src = SOURCES[key.upper()]
        try:
            import requests

            r = requests.get(src.url, timeout=30)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            out = CACHE / f"{key}.csv"
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False)
            return load_series(key, fetch=False)
        except Exception as exc:  # noqa: BLE001 - surface the real cause
            raise DataUnavailable(
                f"{key} is not on disk and {src.host} could not be reached "
                f"({type(exc).__name__}: {exc}).\n"
                f"  - This session's egress policy blocks that host. Either "
                f"allowlist it in the environment's network settings, or\n"
                f"  - export the series and drop it in {RAW.relative_to(ROOT)}/ "
                f"as {key}.csv (first column dates, second column values)."
            ) from exc

    raise DataUnavailable(
        f"No local file for {key!r} in data/cache/ or data/raw/, and no fetch "
        f"source registered. Known sources: {sorted(SOURCES)}."
    )


def load_manual(name: str) -> dict:
    """Load a pasted-levels file from data/manual/ (YAML)."""
    import yaml

    for ext in (".yaml", ".yml"):
        p = MANUAL / f"{name}{ext}"
        if p.exists():
            return yaml.safe_load(p.read_text())
    available = sorted(p.name for p in MANUAL.glob("*.y*ml")) if MANUAL.exists() else []
    raise DataUnavailable(f"No manual file {name!r} in data/manual/. Available: {available}")


def manual_strip(name: str) -> "tuple[list[str], list[float]]":
    """Read a pasted strip: {asof, root, contracts: {SYMBOL: price}}."""
    blob = load_manual(name)
    contracts = blob["contracts"]
    symbols = list(contracts)
    return symbols, [float(contracts[s]) for s in symbols]
