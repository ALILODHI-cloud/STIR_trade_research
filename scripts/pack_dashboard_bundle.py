#!/usr/bin/env python3
"""Pack research/dashboard into a single stir-strips.html (embedded curves)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "research" / "dashboard"


def main() -> None:
    html = (DASH / "index.html").read_text()
    css = (DASH / "styles.css").read_text()
    js = (DASH / "app.js").read_text()
    curves = (DASH / "data" / "curves.json").read_text()

    html = re.sub(r'\s*<link rel="stylesheet" href="styles\.css"\s*/?>', "", html)
    html = re.sub(r'\s*<script src="app\.js"></script>', "", html)
    html = html.replace("</head>", f"<style>\n{css}\n</style>\n</head>", 1)

    js_patched = re.sub(
        r"async function loadData\(\{ bust = false \} = \{\}\) \{.*?\n\}",
        '''async function loadData({ bust = false } = {}) {
  const node = document.getElementById("embedded-curves");
  if (!node) throw new Error("missing embedded-curves");
  const data = JSON.parse(node.textContent);
  state.data = data;
  el("asofPill").textContent = `as-of ${data.asof}`;
  el("footUpdated").textContent = `generated ${new Date(data.generated_at).toLocaleString()} (bundled)`;
  return data;
}''',
        js,
        count=1,
        flags=re.S,
    )
    js_patched = js_patched.replace(
        'await fetch(new URL("api/rebuild", new URL(BASE, location.origin)).toString(), {\n        method: "POST",\n      });',
        "/* bundled: no rebuild API */",
    )
    js_patched = re.sub(
        r"function startPolling\(\) \{.*?\n\}",
        "function startPolling() { /* bundled: no polling */ }",
        js_patched,
        count=1,
        flags=re.S,
    )
    # Mark live pill as static
    js_patched = js_patched.replace(
        'el("livePill").classList.remove("stale");',
        'el("livePill").classList.remove("stale"); el("livePill").title = "bundled snapshot";',
        1,
    )

    boot = (
        f'<script type="application/json" id="embedded-curves">{curves}</script>\n'
        f"<script>\n{js_patched}\n</script>\n"
    )
    html = html.replace("</body>", boot + "</body>", 1)
    out = DASH / "stir-strips.html"
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
