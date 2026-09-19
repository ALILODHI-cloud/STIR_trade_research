#!/usr/bin/env python3
"""Serve the STIR strip dashboard with live data rebuild.

  python3 scripts/serve_dashboard.py

Then open http://127.0.0.1:8765/

Endpoints:
  GET  /              dashboard
  GET  /data/*        curves.json / meta.json
  POST /api/rebuild   re-run build_dashboard_data.py from cache
  GET  /api/health
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "research" / "dashboard"
BUILD = ROOT / "scripts" / "build_dashboard_data.py"
HOST = "127.0.0.1"
PORT = 8765

_rebuild_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASH), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:
        if self.path.startswith("/api/health"):
            self._json(200, {"ok": True, "asof": _asof()})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.startswith("/api/rebuild"):
            ok, detail = rebuild()
            self._json(200 if ok else 500, {"ok": ok, "detail": detail, "asof": _asof()})
            return
        self.send_error(404)

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def _asof() -> str | None:
    meta = DASH / "data" / "meta.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text()).get("asof")
    except Exception:
        return None


def rebuild() -> tuple[bool, str]:
    with _rebuild_lock:
        try:
            r = subprocess.run(
                [sys.executable, str(BUILD)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode != 0:
                return False, (r.stderr or r.stdout or "rebuild failed")[-500:]
            return True, (r.stdout or "ok")[-300:]
        except Exception as e:
            return False, str(e)


def main() -> None:
    if not (DASH / "data" / "curves.json").exists():
        ok, detail = rebuild()
        if not ok:
            print("initial rebuild failed:", detail, file=sys.stderr)
            sys.exit(1)
    httpd = ThreadingHTTPServer((HOST, PORT), partial(Handler))
    print(f"STIR dashboard  http://{HOST}:{PORT}/")
    print("POST /api/rebuild to refresh from data/cache/stir_curves/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
