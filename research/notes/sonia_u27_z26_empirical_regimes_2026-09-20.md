# Empirical: does U27−Z26 flatten? Rally vs selloff

**Contracts:** J8Z26 = **Dec’26**, J8U27 = **Sep’27**.  
**Spread:** U27 − Z26 (bp), desk = back − front. As-of **2026-09-18**.  
**Source:** `data/cache/stir_curves/sonia_u27_minus_z26_timeseries.csv` (2021-09-21 → 2026-09-18).

Figure: `research/notes/figures/sonia_u27_z26_rally_selloff_2026-09-18.png`

---

## 1. Has this gap ever flattened?

**Yes — often historically; once hard YTD.**

| Fact | Number |
|---|---|
| Full-sample range | **−31** to **+63** bp |
| Days spread **&lt; 0** (Sep’27 below Dec’26) | **640 / 1274** (~50%) |
| Days spread **&lt; 5** | **916 / 1274** |
| YTD min | **−20.5** on **2026-03-20** |
| YTD max / last | **+63.0** on **2026-09-18** |

### Big flatten episodes (peak ≥ +10 → drop ≥ 15 bp)

| Peak | Peak bp | Trough | Trough bp | Drop | Sessions | Δ Z26 over flatten |
|---|---:|---|---:|---:|---:|---:|
| 2022-03-01 | +14.0 | 2022-08-15 | −1.5 | **15.5** | 118 | **+79.5** (selloff) |
| 2025-11-14 | +12.5 | 2026-03-20 | −20.5 | **33.0** | 87 | **+118.5** (selloff) |

YTD inversion spell: **2026-03-18 → 2026-05-12** (min −20.5). That was **not** a bull-flatten: Dec’26 sold off *through* Sep’27 (Z26 peaked ~4.625% while U27 ~4.42%) — front led, spread went negative.

### Recent micro-flatten (still elevated)

| Date | Z26 % | U27 % | Spread |
|---|---:|---:|---:|
| 2026-09-14 | 4.345 | 4.940 | **59.5** |
| 2026-09-16 | 4.225 | 4.725 | **50.0** (−9.5 in 2 sessions) |
| 2026-09-18 | 4.250 | 4.880 | **63.0** (fully retraced + more) |

So: the strip **can** and **has** flattened this gap — including all the way through zero. It has **not** flattened from a +60 handle before; +40 was first printed **2026-09-02**, and the only forward window after that went **higher** (to +63), not lower.

---

## 2. What happens in a selloff? (Z26 rates up)

Condition: daily **Δ Z26 &gt; +0.5 bp**.

| Sample | n | Mean ΔZ | Mean ΔU | Mean Δ(U27−Z26) | % spread up | β(ΔU\|ΔZ) |
|---|---:|---:|---:|---:|---:|---:|
| **YTD 2026** | 81 | +5.8 | +6.9 | **+1.13** | 65% | 0.75 |
| **Since Aug** | 19 | +2.7 | +6.2 | **+3.53** | 79% | **2.00** |
| Full 2021–26 | 602 | +5.7 | +5.7 | **−0.02** | 42% | 0.89 |

**YTD / since-Aug answer:** selloffs **steepen** U27−Z26. The peak **outruns** Dec’26. Short flattener **loses** on the average selloff day (+1.1 YTD, +3.5 since Aug).

**Full-sample answer:** roughly **flat** — no reliable selloff→flatten rule over 2021–26.

The March 2026 mega-flatten is the exception that proves the regime point: that selloff had **β &lt; 1** (front sold more than back). August–September has **β ≈ 2** (back sells more). Same “selloff,” opposite spread sign.

Largest steepening days YTD were mostly selloffs with U outrunning Z (e.g. 10-Sep ΔZ +11.5 / ΔU +23 → spread +11.5; 18-Sep ΔZ +2 / ΔU +15 → spread +13).

---

## 3. What happens in a rally? (Z26 rates down)

Condition: daily **Δ Z26 &lt; −0.5 bp**.

| Sample | n | Mean ΔZ | Mean ΔU | Mean Δ(U27−Z26) | % spread down | β(ΔU\|ΔZ) |
|---|---:|---:|---:|---:|---:|---:|
| **YTD 2026** | 82 | −4.6 | −5.3 | **−0.67** | 66% | 0.89 |
| **Since Aug** | 12 | −3.3 | −6.0 | **−2.71** | 83% | **2.04** |
| Full 2021–26 | 558 | −5.6 | −5.5 | **+0.10** | 45% | 0.94 |

**YTD / since-Aug answer:** rallies **flatten** the gap. Short flattener **makes** money on the average rally day (−0.7 YTD, −2.7 since Aug). Same β≈2: U27 falls ~2× Z26 → spread compresses.

**Full-sample answer:** again ~no edge (+0.1 mean).

5-day windows YTD (same sign):

| Window | n | Mean Δ spread over 5d | % flatten |
|---|---:|---:|---:|
| 5d Z26 selloff &gt; +5 bp | 57 | **+1.9** | 33% |
| 5d Z26 rally &lt; −5 bp | 48 | **−0.1** | 48% |
| 5d Z26 selloff &gt; +10 | 44 | **+0.9** | 41% |
| 5d Z26 rally &lt; −10 | 24 | **−0.8** | 54% |

---

## 4. Mechanism in one line

\[
\Delta(\mathrm{U27}-\mathrm{Z26}) \approx (\beta - 1)\,\Delta\mathrm{Z26}
\]

| Regime | β(ΔU\|ΔZ) | Implied | Empirically |
|---|---:|---|---|
| YTD pre-Aug | ~0.92 | selloff **flattens** slightly | mixed / March front-led |
| **Since Aug** | **~2.03** | selloff **steepens**, rally **flattens** | matches tables above |
| Full sample | ~0.9 | near zero | matches ~0 mean ΔS |

Of YTD days where spread fell: **67%** were Z26 rallies.  
Of YTD days where spread rose: **67%** were Z26 selloffs.  
Since Aug those shares are **83% / 80%**.

---

## 5. Bottom line for the short U27−Z26

1. **Flattening is real** — half the history was ≤0; YTD went to **−20.5**. The gap is not structurally stuck steep.
2. **In the live (Aug–Sep) regime, flatten = rally, steepen = selloff.** A short is a **bull-flatten / path-extension-fade**, not a hedge that pays when the strip sells.
3. **The big 2026 flatten was a selloff with β&lt;1** (Dec’26 became the peak). That is the *opposite* beta from today. Do not bank on “another hike scare → automatic flatten” unless the peak migrates *forward* of Sep’27 again.
4. **No full-sample free lunch** — over 2021–26, average selloff/rally days barely move this spread. The YTD skew is regime-dependent.
5. From **+63**, history gives **no prior analogue** of mean-reversion from this level; the only prior &gt;+40 prints are this month and they went higher.

JSON dump of tables: `data/cache/stir_curves/sonia_u27_z26_empirical_regimes.json`
