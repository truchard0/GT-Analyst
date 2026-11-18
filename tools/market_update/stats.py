"""Measured base rates for the market update (our own data only; every figure returns its n and window).

1. Morning-band record: on each session with a 09:30 Skylit SPXW map, the "morning band" is the span between the
   largest positive-gamma same-day (0DTE) strike at or below the open and the largest one at or above it, within
   +-1.5% of spot. The descriptive statement scored each day is "SPX closes inside the morning band" (endpoint, never
   touch). The control is the MIRROR band (the same band reflected through the open: same width, same geometry).
   If positioning carried information, the real band would contain the close more often than its mirror.
2. Next-session routes: close-to-close SPX moves measured against the options-implied 1-day move, split into
   "beyond the priced move up / inside / beyond it down", unconditional and for sessions whose 30-day implied vol
   (Skylit svx30, a VIX-like index) sat near today's. These are shares of past sessions, not forecasts.

Cache: data/market_update/history_spxw.json (incremental; one entry per live session).
"""
import datetime as dt
import json
import statistics as st

import numpy as np

try:
    from . import data as D
except ImportError:  # run as a script
    import data as D

BAND_PCT = 0.015
CACHE = D.MU_DATA / "history_spxw.json"


def morning_band(m, expiry, pct=BAND_PCT):
    """(lo, hi, lo_val, hi_val) from one SymMap's `expiry` column, or None."""
    col = m.col(expiry)
    if col is None:
        return None
    spot = m.spot
    w = m.window(pct)
    below = [(col[i], m.strikes[i]) for i in range(len(col)) if w[i] and m.strikes[i] <= spot and col[i] > 0]
    above = [(col[i], m.strikes[i]) for i in range(len(col)) if w[i] and m.strikes[i] >= spot and col[i] > 0]
    if not below or not above:
        return None
    lv, lo = max(below)
    hv, hi = max(above)
    return float(lo), float(hi), float(lv), float(hv)


def _session_entry(date):
    mins = D.live_minutes(date)
    if not mins or mins[0][0] != "0930":
        return None
    snap = D.load_live(date, "0930")
    m = snap.get("SPXW")
    if m is None or not m.expiries or m.expiries[0] != date:
        return None
    band = morning_band(m, date)
    spots, vix = [], None
    sample = mins[::5]
    if mins[-1] not in sample:
        sample.append(mins[-1])
    for h, p in sample:
        j = D._jload(p)
        for s in j.get("body", j).get("data", {}).get("symbols", []):
            if s["symbol"] == "SPXW":
                spots.append(float(s["spot"]))
            elif s["symbol"] == "VIX" and h == mins[-1][0]:
                vix = float(s["spot"])
    if not spots:
        return None
    return {"open": m.spot, "close": spots[-1], "close_slot": mins[-1][0], "hi5": max(spots), "lo5": min(spots),
            "band": band, "vix_close": vix}


def build_history(refresh=False, verbose=False):
    hist = {}
    if CACHE.exists() and not refresh:
        hist = json.loads(CACHE.read_text())
    root = D.SKYLIT / "live"
    days = sorted(d for d in D.os.listdir(root) if d[:2] == "20")
    new = 0
    for d in days:
        if d in hist:
            continue
        try:
            e = _session_entry(d)
        except Exception as ex:  # a malformed day is skipped, not fatal
            e = {"error": str(ex)[:200]}
        hist[d] = e
        new += 1
        if verbose and new % 20 == 0:
            print("  history:", d)
    if new:
        D.MU_DATA.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(hist))
    return hist


def band_record(hist, before=None):
    """Containment of the close by the morning band vs its mirror, over sessions strictly before `before`."""
    n = real = mirror = 0
    days = []
    for d, e in sorted(hist.items()):
        if before and d >= str(before):
            continue
        if not e or "error" in e or not e.get("band") or e.get("close_slot", "0000") < "1555":
            continue
        lo, hi = e["band"][0], e["band"][1]
        o, c = e["open"], e["close"]
        mlo, mhi = 2 * o - hi, 2 * o - lo
        n += 1
        real += lo <= c <= hi
        mirror += mlo <= c <= mhi
        days.append(d)
    if not n:
        return None
    # day-block bootstrap of the difference
    rng = np.random.default_rng(7)
    rr = np.array([1.0 if (e["band"][0] <= e["close"] <= e["band"][1]) else 0.0 for d, e in sorted(hist.items()) if d in days])
    mm = np.array([1.0 if (2 * e["open"] - e["band"][1] <= e["close"] <= 2 * e["open"] - e["band"][0]) else 0.0
                   for d, e in sorted(hist.items()) if d in days])
    diffs = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        diffs.append(rr[idx].mean() - mm[idx].mean())
    lo_ci, hi_ci = np.percentile(diffs, [2.5, 97.5])
    return {"n": n, "real": real, "mirror": mirror, "real_pct": 100 * real / n, "mirror_pct": 100 * mirror / n,
            "diff_ci": (100 * lo_ci, 100 * hi_ci), "first": days[0], "last": days[-1]}


def em_ratio(rows):
    """Median ratio em_1d_pct / svx1d_adj where both exist (to give history days an implied 1-day move)."""
    r = [em / sv for _, _, _, sv, em in rows if em and sv]
    return st.median(r) if r else None


def route_rates(rows, today_svx30=None, band=2.5, upto=None):
    """Next-session close-to-close move vs the priced 1-day move. Returns dict with unconditional and conditional
    shares {up, inside, down, n, window}. Pairs across data gaps (> 4 calendar days) are skipped."""
    k = em_ratio(rows)
    pairs = []
    for (d1, c1, v1, s1, e1), (d2, c2, v2, s2, e2) in zip(rows, rows[1:]):
        if upto and d2 > str(upto):
            continue
        if (D.d_(d2) - D.d_(d1)).days > 4:
            continue
        em = e1 if e1 else (k * s1 if (k and s1) else None)
        if not em or not c1 or not c2:
            continue
        r = 100 * (c2 / c1 - 1)
        pairs.append((d1, v1, r, em))

    def tally(ps):
        if not ps:
            return None
        up = sum(1 for _, _, r, em in ps if r > em)
        dn = sum(1 for _, _, r, em in ps if r < -em)
        n = len(ps)
        return {"n": n, "up": 100 * up / n, "down": 100 * dn / n, "inside": 100 * (n - up - dn) / n,
                "n_up": up, "n_down": dn, "first": ps[0][0], "last": ps[-1][0],
                "abs_med": st.median(abs(r) for _, _, r, _ in ps)}

    out = {"all": tally(pairs), "k": k}
    if today_svx30 is not None:
        cond = [p for p in pairs if p[1] is not None and abs(p[1] - today_svx30) <= band]
        out["cond"] = tally(cond)
        out["cond_band"] = (today_svx30 - band, today_svx30 + band)
    return out


def score_band(lo, hi, close):
    if close is None:
        return "pending"
    return "inside" if lo <= close <= hi else ("above" if close > hi else "below")


if __name__ == "__main__":
    h = build_history(verbose=True)
    print(band_record(h))
    rows = D.load_vol_history("SPXW")
    print(len(rows), rows[0][0], rows[-1][0])
    print(route_rates(rows, today_svx30=rows[-1][2]))
