/* STIR strip dashboard — tabs, dual curve, slider, click side panel */

const state = {
  data: null,
  curve: "EURIBOR",
  sessionIdx: 0,
  selected: null,
  playing: false,
  playTimer: null,
  pollTimer: null,
  lastMeta: null,
};

const el = (id) => document.getElementById(id);

function bp(x) {
  if (x == null || Number.isNaN(x)) return "—";
  const v = x * 100;
  const sign = v > 0 ? "+" : "";
  return `${sign}${v.toFixed(1)} bp`;
}

function pct(x) {
  if (x == null || Number.isNaN(x)) return "—";
  return `${x.toFixed(3)}%`;
}

function signedClass(x) {
  if (x == null || Number.isNaN(x)) return "";
  return x >= 0 ? "pos" : "neg";
}

async function loadData({ bust = false } = {}) {
  const q = bust ? `?t=${Date.now()}` : "";
  const res = await fetch(`data/curves.json${q}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`curves.json ${res.status}`);
  const data = await res.json();
  state.data = data;
  el("asofPill").textContent = `as-of ${data.asof}`;
  el("footUpdated").textContent = `generated ${new Date(data.generated_at).toLocaleString()}`;
  return data;
}

function currentCurve() {
  return state.data.curves[state.curve];
}

function setTab(curve) {
  state.curve = curve;
  state.selected = null;
  document.querySelectorAll(".tab").forEach((t) => {
    const on = t.dataset.curve === curve;
    t.classList.toggle("active", on);
    t.setAttribute("aria-selected", on ? "true" : "false");
  });
  const c = currentCurve();
  el("curveTitle").textContent = c.label;
  el("curveSub").textContent = `${c.root}* 3M futures · vs ${c.policy_name}`;
  const sessions = c.sessions;
  const slider = el("dateSlider");
  slider.max = String(sessions.length - 1);
  slider.value = String(sessions.length - 1);
  state.sessionIdx = sessions.length - 1;
  el("sliderStart").textContent = sessions[0];
  el("sliderEnd").textContent = sessions[sessions.length - 1];
  clearSide();
  render();
}

function histDate() {
  return currentCurve().sessions[state.sessionIdx];
}

function clearSide() {
  el("sideTitle").textContent = "Click a point";
  el("sideHint").classList.remove("hidden");
  el("sideBody").classList.add("hidden");
}

function updateSide() {
  const c = currentCurve();
  const contract = state.selected;
  if (!contract) {
    clearSide();
    return;
  }
  const asof = c.asof;
  const hist = histDate();
  const sym = c.symbols[contract];

  const latestRate = c.latest_rates[contract];
  const histRate = c.rates[hist]?.[contract];
  const latestSpot = c.latest_spot;
  const histSpot = c.spot[hist];

  const latestCumul = latestRate != null && latestSpot != null ? latestRate - latestSpot : null;
  const histCumul = histRate != null && histSpot != null ? histRate - histSpot : null;
  const diff =
    latestCumul != null && histCumul != null ? latestCumul - histCumul : null;

  el("sideHint").classList.add("hidden");
  el("sideBody").classList.remove("hidden");
  el("sideTitle").textContent = contract;
  el("kvSymbol").textContent = sym;
  el("kvContract").textContent = contract;
  el("kvPolicy").textContent = c.policy_name;

  el("blkLatestDate").textContent = asof;
  el("blkHistDate").textContent = hist;

  el("mLatestRate").textContent = pct(latestRate);
  el("mLatestSpot").textContent = pct(latestSpot);
  el("mLatestCumul").textContent = bp(latestCumul);
  el("mLatestCumul").className = signedClass(latestCumul);

  el("mHistRate").textContent = pct(histRate);
  el("mHistSpot").textContent = pct(histSpot);
  el("mHistCumul").textContent = bp(histCumul);
  el("mHistCumul").className = signedClass(histCumul);

  el("mDiff").textContent = bp(diff);
  el("mDiff").className = signedClass(diff);

  let note = "";
  if (diff != null) {
    if (Math.abs(diff) < 1e-9) note = "Same priced change vs policy as on the historical date.";
    else if (diff > 0)
      note = "Latest prices more tightening (or less easing) into this tenor than the historical date.";
    else note = "Latest prices less tightening (or more easing) into this tenor than the historical date.";
  } else {
    note = "Missing rate or spot for this date/contract.";
  }
  el("deltaNote").textContent = note;
}

function seriesFor(dateKey, ratesMap, contracts) {
  const rates = ratesMap[dateKey] || {};
  const x = [];
  const y = [];
  for (const c of contracts) {
    if (rates[c] != null) {
      x.push(c);
      y.push(rates[c]);
    }
  }
  return { x, y };
}

function render() {
  const c = currentCurve();
  const hist = histDate();
  el("sliderDate").textContent = hist;

  const latest = seriesFor(c.asof, c.rates, c.contracts);
  const historical = seriesFor(hist, c.rates, c.contracts);

  const selected = state.selected;
  const latestColors = latest.x.map((ct) => (ct === selected ? "#8a3510" : "#c45c26"));
  const histColors = historical.x.map((ct) => (ct === selected ? "#0d4a55" : "#1a6b7a"));
  const latestSizes = latest.x.map((ct) => (ct === selected ? 12 : 8));
  const histSizes = historical.x.map((ct) => (ct === selected ? 12 : 8));

  const traces = [
    {
      x: latest.x,
      y: latest.y,
      name: `Latest ${c.asof}`,
      type: "scatter",
      mode: "lines+markers",
      line: { color: "#c45c26", width: 2.6, shape: "linear" },
      marker: { size: latestSizes, color: latestColors, line: { width: 0 } },
      hovertemplate: `%{x}<br>latest %{y:.3f}%<extra></extra>`,
      customdata: latest.x.map(() => "latest"),
    },
    {
      x: historical.x,
      y: historical.y,
      name: `History ${hist}`,
      type: "scatter",
      mode: "lines+markers",
      line: { color: "#1a6b7a", width: 2.2, dash: hist === c.asof ? "solid" : "dot" },
      marker: { size: histSizes, color: histColors },
      hovertemplate: `%{x}<br>${hist} %{y:.3f}%<extra></extra>`,
      customdata: historical.x.map(() => "hist"),
    },
  ];

  const layout = {
    margin: { l: 55, r: 20, t: 10, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(255,255,255,0.35)",
    font: { family: "Sora, sans-serif", color: "#12202c", size: 12 },
    xaxis: {
      title: "",
      tickfont: { family: "IBM Plex Mono, monospace", size: 11 },
      gridcolor: "rgba(197,208,216,0.55)",
      zeroline: false,
      fixedrange: true,
    },
    yaxis: {
      title: { text: "Implied 3M rate (%)", font: { size: 11, color: "#3d5160" } },
      tickfont: { family: "IBM Plex Mono, monospace", size: 11 },
      gridcolor: "rgba(197,208,216,0.55)",
      zeroline: false,
      fixedrange: true,
    },
    legend: { orientation: "h", y: 1.08, x: 0, font: { size: 11 } },
    hovermode: "closest",
    separators: ".,",
  };

  const config = {
    displayModeBar: false,
    responsive: true,
  };

  const node = el("chart");
  Plotly.react(node, traces, layout, config);
  if (!node._stirClickBound) {
    node.on("plotly_click", (ev) => {
      if (!ev?.points?.length) return;
      state.selected = ev.points[0].x;
      updateSide();
      render();
    });
    node._stirClickBound = true;
  }
  updateSide();
}

function onSliderInput() {
  state.sessionIdx = Number(el("dateSlider").value);
  render();
}

function togglePlay() {
  if (state.playing) {
    stopPlay();
    return;
  }
  state.playing = true;
  el("playBtn").textContent = "Pause";
  const c = currentCurve();
  state.playTimer = setInterval(() => {
    let next = state.sessionIdx + 1;
    if (next >= c.sessions.length) next = 0;
    state.sessionIdx = next;
    el("dateSlider").value = String(next);
    render();
  }, 90);
}

function stopPlay() {
  state.playing = false;
  el("playBtn").textContent = "Play";
  if (state.playTimer) clearInterval(state.playTimer);
  state.playTimer = null;
}

async function refresh() {
  const btn = el("refreshBtn");
  btn.disabled = true;
  try {
    // Ask local server to rebuild if available; ignore failure for static open
    try {
      await fetch("/api/rebuild", { method: "POST" });
    } catch (_) {
      /* static file mode */
    }
    await loadData({ bust: true });
    setTab(state.curve);
    el("livePill").classList.remove("stale");
  } catch (err) {
    console.error(err);
    el("livePill").classList.add("stale");
  } finally {
    btn.disabled = false;
  }
}

function startPolling() {
  if (state.pollTimer) clearInterval(state.pollTimer);
  state.pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`data/meta.json?t=${Date.now()}`, { cache: "no-store" });
      if (!res.ok) return;
      const meta = await res.json();
      if (state.lastMeta && meta.generated_at !== state.lastMeta) {
        await loadData({ bust: true });
        const c = currentCurve();
        const sessions = c.sessions;
        const slider = el("dateSlider");
        const wasAtEnd = Number(slider.value) === Number(slider.max);
        slider.max = String(sessions.length - 1);
        if (wasAtEnd) {
          slider.value = slider.max;
          state.sessionIdx = sessions.length - 1;
        }
        el("sliderStart").textContent = sessions[0];
        el("sliderEnd").textContent = sessions[sessions.length - 1];
        el("asofPill").textContent = `as-of ${state.data.asof}`;
        render();
      }
      state.lastMeta = meta.generated_at;
      el("livePill").classList.remove("stale");
    } catch (_) {
      el("livePill").classList.add("stale");
    }
  }, 15000);
}

async function init() {
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => {
      stopPlay();
      setTab(t.dataset.curve);
    })
  );
  el("dateSlider").addEventListener("input", onSliderInput);
  el("playBtn").addEventListener("click", togglePlay);
  el("toLatestBtn").addEventListener("click", () => {
    stopPlay();
    const c = currentCurve();
    state.sessionIdx = c.sessions.length - 1;
    el("dateSlider").value = String(state.sessionIdx);
    render();
  });
  el("refreshBtn").addEventListener("click", refresh);

  await loadData();
  state.lastMeta = state.data.generated_at;
  setTab("EURIBOR");
  startPolling();
}

init().catch((err) => {
  console.error(err);
  el("sideHint").textContent = `Failed to load data/curves.json — run scripts/build_dashboard_data.py and serve research/dashboard.`;
});
