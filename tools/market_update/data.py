"""Loaders for the market-update engine. Read-only on Trading Bot; every loader returns a snapshot time and a stale flag.

Sources (all under Trading Bot/tradingview/_skylit unless stated):
  live/<date>/HHMM_heatmap.json.gz    per-minute Skylit gamma maps, 09:30-16:00 ET (SPY, SPXW, QQQ, NDXP, NDX, SMH, VIX;
                                      5 expiries each; spot is a 1-minute sample, not OHLC)
  live/<date>/HHMM_levels.json.gz     half-hourly Skylit level summaries (king, walls, top nodes; 5-expiry row sums)
  live/<date>/overnight_heatmap.json.gz + overnight_levels.json.gz   one 17:30 ET snapshot per night
  vol/daily/<date>.json, vol/history_*.json   daily IV, expected 1-day move, VIX-like svx30, closes
  universe/<date>/<batch>_HHMMSS_*.json.gz    single-name gamma maps (pre/open/five/ten/twenty/mid/eod batches);
                                      eod_vanna_* = single-name vanna maps (16:00 ET only)
  dealer_flow/<date>/fut_ES.json, fut_NQ.json  ES/NQ 1-minute bars (minute-of-day keys 360-974 = 06:00-16:14 ET)
  moves/<session>.json, moves/cal/<session>.json   earnings list, past reaction moves, gap-chance base rate
  GT data/market_update/events/<date>.json      curated world-event lead lines with reported times (ours)

Hygiene: never Unusual Whales data and never the cached option chains of unclear source - any path containing
'whales', 'unusual' or 'cards' is refused. Nothing here writes to Trading Bot.
"""
import datetime as dt
import glob
import gzip
import json
import os
import pathlib
from zoneinfo import ZoneInfo

import numpy as np

ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
REPO = pathlib.Path(__file__).resolve().parents[2]
SKYLIT = pathlib.Path(os.environ.get("GT_SKYLIT_ROOT",
                                     r"C:\Users\hudso\Downloads\Trading Bot\tradingview\_skylit"))
MU_DATA = REPO / "data" / "market_update"
BANNED_PATH_PARTS = ("whales", "unusual", "cards")
INDEX_SYMBOLS = ("SPY", "SPXW", "QQQ", "NDXP", "NDX", "SMH", "VIX")


class BannedSource(Exception):
    pass


def check_path(p):
    low = str(p).replace("\\", "/").lower()
    if any(b in low for b in BANNED_PATH_PARTS):
        raise BannedSource("refused banned source path: %s" % p)
    return p


def _jload(p):
    check_path(p)
    p = str(p)
    if p.endswith(".gz"):
        with gzip.open(p) as f:
            return json.load(f)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- dates and staleness
def d_(s):
    return s if isinstance(s, dt.date) else dt.date.fromisoformat(str(s)[:10])


def weekdays_between(a, b):
    """Weekdays after a up to and including b (0 if b <= a). Exchange holidays are not modelled."""
    a, b = d_(a), d_(b)
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def next_weekday(d):
    d = d_(d) + dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def prev_weekday(d):
    d = d_(d) - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def to_et(iso):
    if iso is None:
        return None
    t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=UTC)
    return t.astimezone(ET)


def stale_flag(snap_date, edition_date, event_after=None, max_lag=2):
    """(stale: bool, show: bool, note). Same-day or T-1 = fresh; up to max_lag weekdays = STALE (shown, flagged);
    older = not shown. event_after = an ET datetime of a release after the snapshot: EVENT-STALE, levels not shown."""
    lag = weekdays_between(snap_date, edition_date)
    if event_after is not None:
        return True, False, "EVENT-STALE: map predates the %s release" % event_after.strftime("%d %b %H:%M ET")
    if lag == 0:
        return False, True, "fresh (same day)"
    if lag == 1:
        return False, True, "fresh (T-1)"
    if lag <= max_lag:
        return True, True, "STALE %d weekdays" % lag
    return True, False, "STALE %d weekdays: not shown" % lag


# ---------------------------------------------------------------- symbol maps
class SymMap:
    """One symbol's strike x expiry map from a Skylit snapshot."""

    def __init__(self, s, metric, source, batch=None):
        self.symbol = s["symbol"]
        self.metric = metric
        self.asof = to_et(s.get("asOf"))
        self.spot = float(s["spot"])
        self.prev_close = s.get("previousClose")
        self.expiries = list(s.get("expirations", []))
        self.strikes = np.array([float(r["strike"]) for r in s.get("strikes", [])])
        self.nodes = {float(r["strike"]): r.get("nodeType") for r in s.get("strikes", [])}
        m = s.get("matrix") or []
        self.matrix = np.array(m, dtype=float) if m else np.zeros((len(self.strikes), len(self.expiries)))
        self.source = source
        self.batch = batch

    def col(self, expiry):
        if expiry not in self.expiries:
            return None
        return self.matrix[:, self.expiries.index(expiry)]

    def rowsum(self, expiries=None):
        if expiries is None:
            return self.matrix.sum(axis=1)
        idx = [self.expiries.index(e) for e in expiries if e in self.expiries]
        return self.matrix[:, idx].sum(axis=1)

    def window(self, pct):
        return np.abs(self.strikes / self.spot - 1) <= pct


class Snapshot:
    def __init__(self, kind, path, slot_et, maps, fetched=None, extra=None):
        self.kind = kind
        self.path = str(path)
        self.slot_et = slot_et            # the slot time the file stands for (ET)
        self.maps = maps                  # {symbol: SymMap}
        self.fetched = fetched
        self.extra = extra or {}
        self.stale = False
        self.show = True
        self.stale_note = ""

    def __getitem__(self, sym):
        return self.maps[sym]

    def get(self, sym):
        return self.maps.get(sym)

    @property
    def label(self):
        return self.slot_et.strftime("%d %b %Y %H:%M ET") if self.slot_et else "unknown time"


def _parse_maps(j, source):
    body = j.get("body", j.get("heatmap", j))
    meta = body.get("meta", {})
    metric = meta.get("metric", "gamma")
    syms = body.get("data", {}).get("symbols", [])
    return metric, {s["symbol"]: SymMap(s, metric, source) for s in syms}


def live_dir(date):
    return SKYLIT / "live" / str(date)


def live_minutes(date):
    """Sorted [(HHMM str, path)] of the per-minute heatmaps for a session."""
    d = live_dir(date)
    if not d.is_dir():
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith("_heatmap.json.gz") and f[:4].isdigit():
            out.append((f[:4], d / f))
    return out


def load_live(date, hhmm="1600", edition_date=None):
    """The per-minute map at or before hhmm (ET). Returns a Snapshot or None."""
    mins = [(h, p) for h, p in live_minutes(date) if h <= hhmm]
    if not mins:
        return None
    h, p = mins[-1]
    j = _jload(p)
    metric, maps = _parse_maps(j, "Skylit live map")
    slot = dt.datetime.combine(d_(date), dt.time(int(h[:2]), int(h[2:])), tzinfo=ET)
    snap = Snapshot("live", p, slot, maps, j.get("fetched"))
    snap.stale, snap.show, snap.stale_note = stale_flag(date, edition_date or date)
    return snap


def load_live_levels(date, hhmm="1600"):
    d = live_dir(date)
    fs = sorted(f for f in os.listdir(d) if f.endswith("_levels.json.gz") and f[:4].isdigit() and f[:4] <= hhmm) \
        if d.is_dir() else []
    if not fs:
        return None
    j = _jload(d / fs[-1])
    syms = j["body"]["data"]["symbols"]
    return {"path": str(d / fs[-1]), "slot": fs[-1][:4], "symbols": {s["symbol"]: s for s in syms}}


def load_overnight(date, edition_date=None):
    """The 17:30 ET overnight map for the night after `date` (heatmap + levels)."""
    p = live_dir(date) / "overnight_heatmap.json.gz"
    if not p.exists():
        return None
    j = _jload(p)
    metric, maps = _parse_maps(j, "Skylit overnight map")
    fetched = to_et(j.get("fetched"))
    slot = fetched.replace(second=0, microsecond=0) if fetched else dt.datetime.combine(d_(date), dt.time(17, 30), tzinfo=ET)
    lv = live_dir(date) / "overnight_levels.json.gz"
    extra = {}
    if lv.exists():
        jl = _jload(lv)
        extra["levels"] = {s["symbol"]: s for s in jl["body"]["data"]["symbols"]}
    snap = Snapshot("overnight", p, slot, maps, j.get("fetched"), extra)
    snap.stale, snap.show, snap.stale_note = stale_flag(date, edition_date or date)
    return snap


def latest_overnight_date(on_or_before=None):
    root = SKYLIT / "live"
    days = sorted(d for d in os.listdir(root) if d[:2] == "20" and (root / d / "overnight_heatmap.json.gz").exists())
    if on_or_before:
        days = [d for d in days if d <= str(on_or_before)]
    return days[-1] if days else None


def spot_path(date, symbol="SPXW", until="1600", cache=True):
    """[(datetime ET, spot)] from every per-minute map up to `until`. Cached in data/market_update/cache/."""
    cdir = MU_DATA / "cache"
    cpath = cdir / ("spots_%s.json" % date)
    data = None
    if cache and cpath.exists():
        data = json.loads(cpath.read_text())
    mins = live_minutes(date)
    if data is None or len(data.get("minutes", [])) < len(mins):
        data = {"minutes": [], "spots": {}}
        for h, p in mins:
            j = _jload(p)
            body = j.get("body", j)
            data["minutes"].append(h)
            for s in body.get("data", {}).get("symbols", []):
                data["spots"].setdefault(s["symbol"], {})[h] = [s["spot"], s.get("asOf")]
        if cache:
            cdir.mkdir(parents=True, exist_ok=True)
            cpath.write_text(json.dumps(data))
    out = []
    for h in data["minutes"]:
        if h > until:
            break
        v = data["spots"].get(symbol, {}).get(h)
        if v is None:
            continue
        t = dt.datetime.combine(d_(date), dt.time(int(h[:2]), int(h[2:])), tzinfo=ET)
        out.append((t, float(v[0])))
    return out


# ---------------------------------------------------------------- vol / IV / expected move
def load_vol_daily(date):
    """{symbol: {close, atm_iv_30, em_1d_pct, svx30, svx1d_adj, ...}} for one session, with 'published' and stale."""
    p = SKYLIT / "vol" / "daily" / ("%s.json" % date)
    if not p.exists():
        return None
    j = _jload(p)
    out = {}
    for s in j["data"]["symbols"]:
        out[s["symbol"]] = {k: (v[0] if isinstance(v, list) and v else None) for k, v in s["columns"].items()}
    meta = j.get("meta", {})
    return {"symbols": out, "published": to_et(meta.get("publishedAt")), "path": str(p), "session": date}


def load_vol_history(symbol="SPXW"):
    """Daily [(date, close, svx30, svx1d_adj, em_1d_pct or None)] merged from vol/history_* and vol/daily/*."""
    rows = {}
    for p in sorted(glob.glob(str(SKYLIT / "vol" / "history_*.json"))):
        j = _jload(p)
        for s in j["data"]["symbols"]:
            if s["symbol"] != symbol:
                continue
            c = s["columns"]
            for i, d in enumerate(s["dates"]):
                rows[d] = (d, c["close"][i], c["svx30"][i], c.get("svx1d_adj", [None] * len(s["dates"]))[i], None)
    for p in sorted(glob.glob(str(SKYLIT / "vol" / "daily" / "*.json"))):
        j = _jload(p)
        for s in j["data"]["symbols"]:
            if s["symbol"] != symbol:
                continue
            c = s["columns"]
            for i, d in enumerate(s["dates"]):
                rows[d] = (d, c["close"][i], c["svx30"][i], c.get("svx1d_adj", [None])[i], c.get("em_1d_pct", [None])[i])
    return [rows[d] for d in sorted(rows) if rows[d][1] is not None]


# ---------------------------------------------------------------- single-name universe maps
BATCH_TIMES = ("pre", "open", "five", "ten", "twenty", "mid", "eod", "ndx", "confirm")


def universe_batches(date, metric="gamma"):
    """[(HHMMSS, prefix, path)] of single-name batches for a day, gamma or vanna."""
    d = SKYLIT / "universe" / str(date)
    if not d.is_dir():
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json.gz"):
            continue
        parts = f.split("_")
        is_vanna = parts[1] == "vanna" if len(parts) > 2 else False
        if (metric == "vanna") != is_vanna:
            continue
        hhmmss = parts[2] if is_vanna else parts[1]
        if not hhmmss.isdigit():
            continue
        out.append((hhmmss, parts[0], d / f))
    return sorted(out)


def load_universe_map(date, ticker, metric="gamma", asof="235959", edition_date=None, event_after=None):
    """The latest single-name map for `ticker` at or before `asof` (HHMMSS or HHMM) on `date`. Every batch file is
    opened (the filename symbol is only the batch's first name). Returns SymMap with .stale/.show/.stale_note."""
    asof = (asof + "00")[:6] if len(asof) == 4 else asof
    for hhmmss, prefix, p in reversed(universe_batches(date, metric)):
        if hhmmss > asof:
            continue
        try:
            j = _jload(p)
        except BannedSource:
            raise
        except Exception:
            continue
        hm = j.get("heatmap", j.get("body", j))
        if hm.get("meta", {}).get("metric") != metric:
            continue
        for s in hm.get("data", {}).get("symbols", []):
            if s.get("symbol") == ticker:
                m = SymMap(s, metric, "Skylit universe %s batch" % prefix, batch="%s_%s" % (prefix, hhmmss))
                m.path = str(p)
                ev = event_after if (event_after is not None and m.asof and m.asof < event_after) else None
                m.stale, m.show, m.stale_note = stale_flag(date, edition_date or date, ev)
                return m
    return None


# ---------------------------------------------------------------- futures bars
def load_futures(date, sym="ES"):
    """ES/NQ 1-minute bars [(datetime ET, o, h, l, c, v)]; keys are minute-of-day ET (06:00-16:14)."""
    p = SKYLIT / "dealer_flow" / str(date) / ("fut_%s.json" % sym)
    if not p.exists():
        return None
    j = _jload(p)
    bars = []
    for k, v in sorted(j["bars"].items(), key=lambda kv: int(kv[0])):
        m = int(k)
        t = dt.datetime.combine(d_(date), dt.time(m // 60, m % 60), tzinfo=ET)
        bars.append((t, *v))
    return {"contract": j.get("contract"), "bars": bars, "path": str(p)}


def latest_futures_date(on_or_before):
    root = SKYLIT / "dealer_flow"
    days = sorted(d for d in os.listdir(root) if d[:2] == "20" and (root / d / "fut_ES.json").exists()
                  and d <= str(on_or_before))
    return days[-1] if days else None


# ---------------------------------------------------------------- earnings
def load_earnings(session):
    """Earnings list for `session` (YYYY-MM-DD): moves rows (past reactions, gap chance) + the calendar (times)."""
    out = {"session": str(session), "rows": [], "cal": [], "note": ""}
    p = SKYLIT / "moves" / ("%s.json" % session)
    if p.exists():
        j = _jload(p)
        out.update({"rows": j.get("rows", []), "note": j.get("note", ""), "built": j.get("built"),
                    "base": j.get("base", {}), "path": str(p)})
    c = SKYLIT / "moves" / "cal" / ("%s.json" % session)
    if c.exists():
        out["cal"] = _jload(c).get("rows", [])
    return out


def release_time(row, default_after=dt.time(16, 0), default_before=dt.time(8, 0)):
    """ET datetime of an earnings release from a moves row ('tonight after the close' / 'tomorrow before the open')."""
    d = d_(row.get("report_day"))
    w = (row.get("when") or "").lower()
    if "after" in w:
        return dt.datetime.combine(d, default_after, tzinfo=ET)
    if "before" in w:
        return dt.datetime.combine(d, default_before, tzinfo=ET)
    return None


# ---------------------------------------------------------------- events (ours)
def load_events(date, asof_et=None):
    """Curated world-event lead lines for the edition (GT data/market_update/events/<date>.json). Items reported after
    the edition's as-of time are dropped, so a back-dated edition never knows the future."""
    p = MU_DATA / "events" / ("%s.json" % date)
    if not p.exists():
        return []
    items = json.loads(p.read_text(encoding="utf-8")).get("items", [])
    def et(s):
        return dt.datetime.fromisoformat(s).replace(tzinfo=ET) if s else None

    out = []
    for it in items:
        t = to_et(it.get("reported_utc")) if it.get("reported_utc") else None
        known = t or et(it.get("known_from_et"))
        until = et(it.get("until_et"))
        if asof_et is not None:
            if known is not None and known > asof_et:
                continue
            if until is not None and asof_et >= until:
                continue
        it = dict(it)
        it["reported_et"] = t
        it["when"] = et(it.get("when_et"))
        out.append(it)
    return out
