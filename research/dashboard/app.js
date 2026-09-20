/* STIR strip dashboard — dual curve, two-point slope, month labels */

const MONTHS = {
  F: "Jan", G: "Feb", H: "Mar", J: "Apr", K: "May", M: "Jun",
  N: "Jul", Q: "Aug", U: "Sep", V: "Oct", X: "Nov", Z: "Dec",
};
const MONTH_NUM = {
  F: 1, G: 2, H: 3, J: 4, K: 5, M: 6,
  N: 7, Q: 8, U: 9, V: 10, X: 11, Z: 12,
};

const state = {
  data: null,
  curve: "EURIBOR",
  sessionIdx: 0,
  selected: [], // up to 2 contract codes, chronologically sorted when pair locked
  playing: false,
  playTimer: null,
  pollTimer: null,
  lastMeta: null,
};

const el = (id) => document.getElementById(id);

const BASE = (() => {
  const parts = location.pathname.split("/").filter(Boolean);
  if (parts[0] === "STIR_trade_research") return "/STIR_trade_research/";
  return "./";
})();

function dataUrl(file, { bust = false } = {}) {
  const u = new URL(`data/${file}`, new URL(BASE, location.href));
  if (bust) u.searchParams.set("t", String(Date.now()));
  return u.toString();
}

function monthLabel(code) {
  if (!code || code.length < 2) return code;
  const m = code[0];
  const yy = code.slice(1);
  return `${MONTHS[m] || m} '${yy}`;
}

function contractKey(code) {
  return 2000 + Number(code.slice(1)) + MONTH_NUM[code[0]] / 100;
}

function fmtBp(x) {
  if (x == null || Number.isNaN(x)) return "—";
  const sign = x > 0 ? "+" : "";
  return `${sign}${x.toFixed(1)} bp`;
}

/** Format a rate-space differential (e.g. 0.47) as basis points. */
function rateDiffBp(x) {
  if (x == null || Number.isNaN(x)) return "—";
  return fmtBp(x * 100);
}

function pct(x) {
  if (x == null || Number.isNaN(x)) return "—";
  return `${x.toFixed(3)}%`;
}

function signedClass(x) {
  if (x == null || Number.isNaN(x)) return "";
  return x >= 0 ? "pos" : "neg";
}

function labelsFor(contracts) {
  return contracts.map(monthLabel);
}

function codeFromLabel(label, contracts) {
  const i = labelsFor(contracts).indexOf(label);
  return i >= 0 ? contracts[i] : null;
}

async function loadData({ bust = false } = {}) {
  const res = await fetch(dataUrl("curves.json", { bust }), { cache: "no-store" });
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

function histDate() {
  return currentCurve().sessions[state.sessionIdx];
}

function pairContracts() {
  if (state.selected.length < 2) return null;
  const [a, b] = state.selected;
  return contractKey(a) <= contractKey(b) ? [a, b] : [b, a];
}

/** Rate spread front − back in bp (positive = inverted). */
function slopeBp(rates, front, back) {
  if (!rates || rates[front] == null || rates[back] == null) return null;
  return (rates[front] - rates[back]) * 100;
}

function setTab(curve) {
  state.curve = curve;
  state.selected = [];
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
  render();
}

function clearSelection() {
  state.selected = [];
  render();
}

function onPointClick(labelOrCode) {
  const c = currentCurve();
  let code = c.contracts.includes(labelOrCode)
    ? labelOrCode
    : codeFromLabel(labelOrCode, c.contracts);
  if (!code) return;

  if (state.selected.includes(code)) {
    state.selected = state.selected.filter((x) => x !== code);
  } else if (state.selected.length >= 2) {
    state.selected = [code];
  } else {
    state.selected = [...state.selected, code];
  }
  render();
}

function updateSide() {
  const c = currentCurve();
  const hist = histDate();
  const pair = pairContracts();

  el("sideSingle").classList.add("hidden");
  el("sidePair").classList.add("hidden");

  if (pair) {
    const [front, back] = pair;
    const latestSlope = slopeBp(c.latest_rates, front, back);
    const histSlope = slopeBp(c.rates[hist], front, back);
    const diff =
      latestSlope != null && histSlope != null ? latestSlope - histSlope : null;

    el("sideHint").classList.add("hidden");
    el("sidePair").classList.remove("hidden");
    el("sideEyebrow").textContent = "Slope pair";
    el("sideTitle").textContent = `${monthLabel(front)} → ${monthLabel(back)}`;
    el("kvFront").textContent = `${monthLabel(front)} (${c.symbols[front]})`;
    el("kvBack").textContent = `${monthLabel(back)} (${c.symbols[back]})`;
    el("blkSlopeLatestDate").textContent = c.asof;
    el("blkSlopeHistDate").textContent = hist;
    el("mSlopeLatest").textContent = fmtBp(latestSlope);
    el("mSlopeLatest").className = signedClass(latestSlope);
    el("mSlopeHist").textContent = fmtBp(histSlope);
    el("mSlopeHist").className = signedClass(histSlope);
    el("mSlopeDiff").textContent = fmtBp(diff);
    el("mSlopeDiff").className = signedClass(diff);

    let note = "";
    if (diff == null) note = "Missing rate on one of the dates.";
    else if (Math.abs(diff) < 1e-9) note = "Same slope as on the historical date.";
    else if (diff > 0)
      note = "Latest is more inverted / less upward-sloping than the historical date.";
    else note = "Latest is less inverted / more upward-sloping than the historical date.";
    el("slopeNote").textContent = note;
    return;
  }

  if (state.selected.length === 1) {
    const contract = state.selected[0];
    const latestRate = c.latest_rates[contract];
    const histRate = c.rates[hist]?.[contract];
    const latestSpot = c.latest_spot;
    const histSpot = c.spot[hist];
    const latestCumul =
      latestRate != null && latestSpot != null ? latestRate - latestSpot : null;
    const histCumul = histRate != null && histSpot != null ? histRate - histSpot : null;
    const diff =
      latestCumul != null && histCumul != null ? latestCumul - histCumul : null;

    el("sideHint").classList.add("hidden");
    el("sideSingle").classList.remove("hidden");
    el("sideEyebrow").textContent = "Contract detail";
    el("sideTitle").textContent = monthLabel(contract);
    el("kvSymbol").textContent = c.symbols[contract];
    el("kvContract").textContent = monthLabel(contract);
    el("kvPolicy").textContent = c.policy_name;
    el("blkLatestDate").textContent = c.asof;
    el("blkHistDate").textContent = hist;
    el("mLatestRate").textContent = pct(latestRate);
    el("mLatestSpot").textContent = pct(latestSpot);
    el("mLatestCumul").textContent = rateDiffBp(latestCumul);
    el("mLatestCumul").className = signedClass(latestCumul);
    el("mHistRate").textContent = pct(histRate);
    el("mHistSpot").textContent = pct(histSpot);
    el("mHistCumul").textContent = rateDiffBp(histCumul);
    el("mHistCumul").className = signedClass(histCumul);
    el("mDiff").textContent = rateDiffBp(diff);
    el("mDiff").className = signedClass(diff);
    el("deltaNote").textContent =
      "Click a second month to lock a slope and see its history below.";
    return;
  }

  el("sideHint").classList.remove("hidden");
  el("sideEyebrow").textContent = "Selection";
  el("sideTitle").textContent = "Click one or two points";
}

function seriesFor(dateKey, ratesMap, contracts) {
  const rates = ratesMap[dateKey] || {};
  const codes = [];
  const y = [];
  for (const c of contracts) {
    if (rates[c] != null) {
      codes.push(c);
      y.push(rates[c]);
    }
  }
  return { codes, x: labelsFor(codes), y };
}

function markerStyle(codes, selectedSet, baseColor, activeColor) {
  return {
    size: codes.map((c) => (selectedSet.has(c) ? 13 : 8)),
    color: codes.map((c) => (selectedSet.has(c) ? activeColor : baseColor)),
  };
}

function renderStrip() {
  const c = currentCurve();
  const hist = histDate();
  el("sliderDate").textContent = hist;

  const latest = seriesFor(c.asof, c.rates, c.contracts);
  const historical = seriesFor(hist, c.rates, c.contracts);
  const selectedSet = new Set(state.selected);
  const latestMk = markerStyle(latest.codes, selectedSet, "#c45c26", "#5b4db8");
  const histMk = markerStyle(historical.codes, selectedSet, "#1a6b7a", "#5b4db8");

  const traces = [
    {
      x: latest.x,
      y: latest.y,
      name: `Latest ${c.asof}`,
      type: "scatter",
      mode: "lines+markers",
      line: { color: "#c45c26", width: 2.6 },
      marker: latestMk,
      customdata: latest.codes,
      hovertemplate: `%{x}<br>latest %{y:.3f}%<extra></extra>`,
    },
    {
      x: historical.x,
      y: historical.y,
      name: `History ${hist}`,
      type: "scatter",
      mode: "lines+markers",
      line: {
        color: "#1a6b7a",
        width: 2.2,
        dash: hist === c.asof ? "solid" : "dot",
      },
      marker: histMk,
      customdata: historical.codes,
      hovertemplate: `%{x}<br>${hist} %{y:.3f}%<extra></extra>`,
    },
  ];

  const pair = pairContracts();
  if (pair) {
    const [front, back] = pair;
    // Draw pair connectors on both curves when rates exist
    for (const [rates, name, color, dash] of [
      [c.latest_rates, "Latest pair", "#c45c26", "solid"],
      [c.rates[hist], "Hist pair", "#1a6b7a", "dot"],
    ]) {
      if (rates?.[front] == null || rates?.[back] == null) continue;
      traces.push({
        x: [monthLabel(front), monthLabel(back)],
        y: [rates[front], rates[back]],
        name,
        type: "scatter",
        mode: "lines+markers",
        line: { color: "#5b4db8", width: 3, dash },
        marker: { size: 11, color: "#5b4db8" },
        hoverinfo: "skip",
        showlegend: false,
      });
    }
  }

  const layout = {
    margin: { l: 52, r: 16, t: 8, b: 48 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(255,255,255,0.35)",
    font: { family: "Sora, sans-serif", color: "#12202c", size: 12 },
    xaxis: {
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
    legend: { orientation: "h", y: 1.12, x: 0, font: { size: 11 } },
    hovermode: "closest",
  };

  const node = el("chart");
  Plotly.react(node, traces, layout, { displayModeBar: false, responsive: true });
  if (!node._stirClickBound) {
    node.on("plotly_click", (ev) => {
      if (!ev?.points?.length) return;
      const pt = ev.points[0];
      const code = pt.customdata || codeFromLabel(pt.x, currentCurve().contracts);
      onPointClick(code);
    });
    node._stirClickBound = true;
  }
}

function renderSlopeHistory() {
  const c = currentCurve();
  const pair = pairContracts();
  const node = el("slopeChart");

  if (!pair) {
    el("slopeTitle").textContent = "Slope over time";
    el("slopeSub").textContent = "Select two contracts on the strip";
    Plotly.react(
      node,
      [],
      {
        margin: { l: 52, r: 16, t: 8, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(255,255,255,0.35)",
        xaxis: { visible: false },
        yaxis: { visible: false },
        annotations: [
          {
            text: "Click two months above to plot slope history",
            showarrow: false,
            font: { color: "#3d5160", size: 13, family: "Sora, sans-serif" },
            xref: "paper",
            yref: "paper",
            x: 0.5,
            y: 0.5,
          },
        ],
      },
      { displayModeBar: false, responsive: true }
    );
    return;
  }

  const [front, back] = pair;
  el("slopeTitle").textContent = `${monthLabel(front)} − ${monthLabel(back)}`;
  el("slopeSub").textContent = `Slope history (bp) · positive = inverted · vs latest ${c.asof}`;

  const xs = [];
  const ys = [];
  for (const d of c.sessions) {
    const s = slopeBp(c.rates[d], front, back);
    if (s == null) continue;
    xs.push(d);
    ys.push(s);
  }
  const latestSlope = slopeBp(c.latest_rates, front, back);
  const hist = histDate();

  const traces = [
    {
      x: xs,
      y: ys,
      type: "scatter",
      mode: "lines",
      name: "Slope history",
      line: { color: "#1a6b7a", width: 2 },
      hovertemplate: `%{x}<br>%{y:.1f} bp<extra></extra>`,
    },
  ];
  if (latestSlope != null) {
    traces.push({
      x: [xs[0], xs[xs.length - 1]],
      y: [latestSlope, latestSlope],
      type: "scatter",
      mode: "lines",
      name: `Latest ${latestSlope.toFixed(1)} bp`,
      line: { color: "#c45c26", width: 2, dash: "dash" },
      hoverinfo: "skip",
    });
  }
  // Marker for slider date
  const histSlope = slopeBp(c.rates[hist], front, back);
  if (histSlope != null) {
    traces.push({
      x: [hist],
      y: [histSlope],
      type: "scatter",
      mode: "markers",
      name: "Slider date",
      marker: { size: 11, color: "#5b4db8", symbol: "diamond" },
      hovertemplate: `Slider %{x}<br>%{y:.1f} bp<extra></extra>`,
    });
  }

  Plotly.react(
    node,
    traces,
    {
      margin: { l: 52, r: 16, t: 8, b: 40 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(255,255,255,0.35)",
      font: { family: "Sora, sans-serif", color: "#12202c", size: 12 },
      xaxis: {
        tickfont: { family: "IBM Plex Mono, monospace", size: 10 },
        gridcolor: "rgba(197,208,216,0.55)",
        fixedrange: true,
      },
      yaxis: {
        title: { text: "Slope (bp)", font: { size: 11, color: "#3d5160" } },
        tickfont: { family: "IBM Plex Mono, monospace", size: 11 },
        gridcolor: "rgba(197,208,216,0.55)",
        zeroline: true,
        zerolinecolor: "rgba(61,81,96,0.35)",
        fixedrange: true,
      },
      legend: { orientation: "h", y: 1.14, x: 0, font: { size: 11 } },
      hovermode: "x unified",
    },
    { displayModeBar: false, responsive: true }
  );
}

function render() {
  renderStrip();
  renderSlopeHistory();
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
    try {
      await fetch(new URL("api/rebuild", new URL(BASE, location.origin)).toString(), {
        method: "POST",
      });
    } catch (_) {
      /* static */
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
      const res = await fetch(dataUrl("meta.json", { bust: true }), { cache: "no-store" });
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
  el("clearSelBtn").addEventListener("click", () => {
    stopPlay();
    clearSelection();
  });

  await loadData();
  state.lastMeta = state.data.generated_at;
  setTab("EURIBOR");
  startPolling();
}

init().catch((err) => {
  console.error(err);
  el("sideHint").textContent =
    "Failed to load data/curves.json — run scripts/build_dashboard_data.py and serve research/dashboard.";
});
