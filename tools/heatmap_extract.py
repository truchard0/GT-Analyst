"""Extract strike x expiry dealer-gamma heatmaps from our own Skylit universe maps (stdlib only).

Reads the Skylit single-name universe snapshots in Trading Bot (read-only) and writes a compact JSON with,
per ticker: spot, the expiries shown, a strike window around spot, the per-cell dealer gamma grid, and the
largest cell ("king") within the shown window.

Source rules (house hygiene):
  - Only Skylit universe maps are read (`heatmap.meta.metric == "gamma"`). Vanna maps are skipped.
  - Never reads Unusual Whales data or the cached option-chain files: any path containing "whales",
    "unusual" or "cards" is refused.
  - Prefers the 16:00 ET end-of-day batch (`eod_HHMMSS_*.json.gz`, not `eod_vanna_*`). A ticker missing
    from the EOD batches falls back to the 09:30 ET `ndx_093000_*` batch, then `open_*`, and says so.
  - The filename symbol is only the first symbol of a batch of ~10, so every file is opened and searched.

Units: the vendor's per-cell `matrix` value (net dealer gamma per strike and expiry; Skylit's row `value` is
the sum of the row across all expiries). Skylit does not publish the normalization, so values are comparable
within one ticker only, never across tickers. Positive = dealers long gamma, negative = short gamma.

Usage:
  python tools/heatmap_extract.py --date 2026-11-17 \
      --out data/ai_technical/heatmaps_20261117.json
"""
import argparse
import datetime as dt
import gzip
import json
import os
import sys

DEFAULT_UNIVERSE = r"C:\Users\hudso\Downloads\Trading Bot\tradingview\_skylit\universe"
DEFAULT_TICKERS = ["NVDA", "AVGO", "MU", "META", "AMZN", "SMH", "CRWV"]
BANNED_PATH_PARTS = ("whales", "unusual", "cards")
# Row grid per ticker: strikes that are multiples of this step are shown (off-grid strikes are dropped and the
# dropped share of |gamma| is reported). None = every native strike. Chosen so ~16-22 rows cover about +-12%.
DEFAULT_STEP = {"NVDA": 2.5, "AVGO": 5, "MU": 5, "META": 5, "AMZN": 2.5, "SMH": 5, "CRWV": None}
# Wider window where the row grid is coarse relative to spot (NVDA has only 12 grid strikes inside +-12%).
WINDOW = {"NVDA": 0.15}
# Event context the map cannot know about (company-confirmed or calendar facts as of the snapshot).
EVENT_STALE = {"NVDA": "NVDA reported after the 17 Nov 2026 close; this 16:00 ET map predates the report "
                       "and is EVENT-STALE from the release onward (show no levels from it)."}
BATCH_PREF = [("eod_", "16:00 ET end-of-day batch"), ("ndx_093000_", "09:30 ET open batch (ndx list)"),
              ("open_", "09:30 ET open batch")]


def is_banned(path):
    low = path.replace("\\", "/").lower()
    return any(p in low for p in BANNED_PATH_PARTS)


def load_symbols(path):
    j = json.load(gzip.open(path))
    hm = j.get("heatmap", {}) if isinstance(j, dict) else {}
    meta = hm.get("meta", {})
    syms = hm.get("data", {}).get("symbols", [])
    return meta, syms


def find_map(day_dir, ticker):
    files = sorted(os.listdir(day_dir))
    for prefix, label in BATCH_PREF:
        cands = [f for f in files if f.startswith(prefix) and f.endswith(".json.gz") and "vanna" not in f]
        for f in reversed(cands):  # latest batch first
            p = os.path.join(day_dir, f)
            if is_banned(p):
                continue
            try:
                meta, syms = load_symbols(p)
            except Exception:
                continue
            if meta.get("metric") != "gamma":
                continue
            for s in syms:
                if s.get("symbol") == ticker:
                    return p, label, meta, s
    return None, None, None, None


def on_grid(k, step):
    if step is None:
        return True
    q = k / step
    return abs(q - round(q)) < 1e-9


def pick_expiries(exps, after, n_max=6, monthly="2026-12-18"):
    """The Friday expiries after `after` out to the monthly OPEX, capped at n_max (monthly kept).

    `after` is the next session's date: its same-day column lapses at that close, so it is left out."""
    chosen = [e for e in exps if after < e <= monthly and dt.date.fromisoformat(e).weekday() == 4]
    if monthly in exps and monthly not in chosen:
        chosen.append(monthly)
    while len(chosen) > n_max:
        drop = [e for e in chosen if e != monthly][-1]
        chosen.remove(drop)
    return sorted(chosen)


def next_weekday(d):
    d = d + dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def extract(ticker, day_dir, step, win_pct, max_rows, monthly):
    path, label, meta, s = find_map(day_dir, ticker)
    if path is None:
        return None, "%s: no Skylit gamma map found in %s" % (ticker, day_dir)
    spot = float(s["spot"])
    exps = s["expirations"]
    snap_day = dt.date.fromisoformat(s["asOf"][:10])
    skip_day = next_weekday(snap_day).isoformat()
    shown = pick_expiries(exps, skip_day, monthly=monthly)
    cols = [exps.index(e) for e in shown]
    mat = s["matrix"]
    rows_all = [(i, r["strike"]) for i, r in enumerate(s["strikes"]) if abs(r["strike"] / spot - 1) <= win_pct]
    grid = [(i, k) for i, k in rows_all if on_grid(k, step)]
    grid.sort(key=lambda t: abs(t[1] - spot))
    grid = grid[:max_rows]
    lo0, hi0 = min(k for _, k in grid), max(k for _, k in grid)
    # off-grid strikes inside the span that hold a big cell (>= 30% of the grid's largest) are added back
    gmax = max(abs(mat[i][c]) for i, _ in grid for c in cols)
    extra = [(i, k) for i, k in rows_all if lo0 <= k <= hi0 and not on_grid(k, step)
             and max(abs(mat[i][c]) for c in cols) >= 0.30 * gmax]
    grid = sorted(grid + extra, key=lambda t: t[1])
    lo, hi = grid[0][1], grid[-1][1]
    gamma = [[round(float(mat[i][c]), 1) for c in cols] for i, _ in grid]
    strikes = [k for _, k in grid]
    skipped = [c for c, e in enumerate(exps) if e == skip_day]

    # what the row grid drops, within the same strike span and shown expiries
    span = [(i, k) for i, k in rows_all if lo <= k <= hi]
    tot = sum(abs(mat[i][c]) for i, _ in span for c in cols)
    kept = sum(abs(v) for row in gamma for v in row)
    dropped_share = 0.0 if tot == 0 else 1 - kept / tot
    # share of the window's |gamma| (first 10 expiries) that the shown expiries carry
    ten = list(range(min(10, len(exps))))
    tot10 = sum(abs(mat[i][c]) for i, _ in span for c in ten if exps[c] <= monthly)
    exp_share = 0.0 if tot10 == 0 else tot / tot10

    # king = largest |cell| in the shown window
    best = max(((abs(v), strikes[r], shown[c], v) for r, row in enumerate(gamma) for c, v in enumerate(row)))
    king = {"strike": best[1], "expiry": best[2], "value": best[3]}
    # off-grid cells larger than the king would be hidden by the row grid: flag them
    hidden = [(k, exps[c], mat[i][c]) for i, k in span if not on_grid(k, step) for c in cols
              if abs(mat[i][c]) > 0.5 * best[0]]
    # net gamma within +-2% of spot over the shown expiries (regime read)
    near = sum(mat[i][c] for i, k in rows_all if abs(k / spot - 1) <= 0.02 for c in cols)
    regime = "positive" if near > 0.05 * best[0] else ("negative" if near < -0.05 * best[0] else "flat")
    # per-strike sum across the 10 expiries to the monthly (the levels-file convention) for comparison
    rowsum10 = [(abs(sum(mat[i][c] for c in ten if exps[c] <= monthly)), k, sum(mat[i][c] for c in ten if exps[c] <= monthly))
                for i, k in rows_all]
    sk = max(rowsum10)

    notes = []
    notes.append("Map: %s, %s (asOf %s). %d of %d expiries shown; they carry %.0f%% of the |gamma| in the strike span "
                 "across every expiry to %s (the omitted next-session and Monday/Wednesday expiries hold the rest)." % (os.path.basename(path), label, s.get("asOf"), len(shown), len(exps),
                                                 100 * exp_share, monthly))
    notes.append("Rows: %s strikes %s-%s (%.1f%% to +%.1f%% of spot)%s%s; the strikes left out carry %.1f%% of the "
                 "|gamma| in that span." % (len(strikes), lo, hi, 100 * (lo / spot - 1), 100 * (hi / spot - 1),
                                            "" if step is None else ", every %g" % step,
                                            "" if not extra else " plus %s (large off-grid nodes)" %
                                            ", ".join("%g" % k for _, k in extra),
                                            max(0.0, 100 * dropped_share)))
    if skipped:
        c0 = skipped[0]
        sk_abs = sum(abs(mat[i][c0]) for i, _ in span)
        notes.append("The %s expiry (the session after the snapshot) is left out: it lapses at that close. It held "
                     "%.0f%% of the span's |gamma| including it." % (skip_day, 100 * sk_abs / (sk_abs + tot10)))
    if hidden:
        notes.append("WARNING: off-grid cells over half the king's size were dropped: %s" %
                     ", ".join("%s/%s %.0f" % h for h in hidden[:5]))
    notes.append("Largest shown cell %s / %s (%+.0f). Summed over the expiries to %s the largest strike is %s (%+.0f)." %
                 (king["strike"], king["expiry"], king["value"], monthly, sk[1], sk[2]))
    notes.append("Net gamma within +-2%% of spot over the shown expiries: %+.0f (%s)." % (near, regime))
    if label != BATCH_PREF[0][1]:
        notes.append("No end-of-day map for this name: this is the open map, about 6.5 hours before the close.")
    if ticker in EVENT_STALE:
        notes.append(EVENT_STALE[ticker])
    out = {
        "ticker": ticker,
        "snapshot_ts": s.get("asOf"),
        "source_file": path,
        "source_batch": label,
        "metric": meta.get("metric"),
        "spot": round(spot, 2),
        "expiries": shown,
        "strikes": strikes,
        "gamma": gamma,
        "king": king,
        "regime_pm2pct": regime,
        "event_stale": ticker in EVENT_STALE,
        "notes": notes,
    }
    return out, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", default="2026-11-17", help="snapshot day folder (YYYY-MM-DD)")
    ap.add_argument("--universe", default=DEFAULT_UNIVERSE, help="Skylit universe folder (read-only)")
    ap.add_argument("--tickers", default=",".join(DEFAULT_TICKERS))
    ap.add_argument("--window", type=float, default=0.12, help="strike window as a fraction of spot")
    ap.add_argument("--max-rows", type=int, default=22)
    ap.add_argument("--monthly", default="2026-12-18", help="monthly OPEX that must be shown")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    day_dir = os.path.join(a.universe, a.date)
    if is_banned(day_dir):
        sys.exit("refused: banned source path")
    res, errs = [], []
    for t in [x.strip().upper() for x in a.tickers.split(",") if x.strip()]:
        r, e = extract(t, day_dir, DEFAULT_STEP.get(t), WINDOW.get(t, a.window), a.max_rows, a.monthly)
        (res.append(r) if r else errs.append(e))
    doc = {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Skylit single-name universe maps (Trading Bot tradingview/_skylit/universe/%s), read-only" % a.date,
        "units": "Skylit per-cell dealer gamma ('matrix' value): net dealer gamma for one strike and one expiry. "
                 "Positive = dealers long gamma, negative = short gamma. The vendor does not publish the "
                 "normalization; compare within a ticker only, never across tickers.",
        "king_definition": "largest |cell| within the strikes and expiries shown",
        "excluded": "No Unusual Whales data and no cached option-chain files of unclear source were read.",
        "tickers": res,
        "errors": errs,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    for r in res:
        print(r["ticker"], r["snapshot_ts"], r["spot"], r["expiries"], len(r["strikes"]), "king", r["king"])
        for n in r["notes"]:
            print("   ", n)
    for e in errs:
        print("ERR", e)


if __name__ == "__main__":
    main()
