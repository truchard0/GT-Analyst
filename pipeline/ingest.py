#!/usr/bin/env python3
"""News ingestion. Sources (set keys in .env as available):
  NEWSAPI_KEY   -> newsapi.org top business headlines (polled every 3rd run)
  FINNHUB_KEY   -> finnhub.io market news             (polled every 3rd run)
  RSS (no key)  -> FEEDS below, every run
Dedups by URL sha1 against ledger/seen.db; APPENDS to inbox/latest.md.
Watchlist matches -> inbox/triggered/<ts>_<TICKERS>.md + detached trigger.py.
Designed to run headless under pythonw every 5 minutes; all output -> logs/ingest.log
Test hook: python ingest.py --feeds tests/fake_feed.xml  (local file instead of FEEDS)
"""
import datetime
import email.utils
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import traceback
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, load_env, load_json, log, utc_iso, utc_stamp

LOGFILE = ROOT / "logs" / "ingest.log"

# (url, label) — sector-spread macro tape. Liveness-checked at build time.
FEEDS = [
    # principal rhetoric — Trump Truth Social posts (doctrine §12.1: SENTIMENT layer,
    # discount as a thesis input; graduate to an event ONLY if capital-committed).
    ("https://trumpstruth.org/feed", "trump-truth"),
    # broad markets
    ("https://feeds.content.dowjones.io/public/rss/mw_topstories", "marketwatch"),
    ("https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "marketwatch-pulse"),
    ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "wsj-markets"),
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "cnbc-top"),
    ("https://news.google.com/rss/search?q=when:2h+site:reuters.com&hl=en-US&gl=US&ceid=US:en", "reuters-via-gnews"),
    # central banks / government
    ("https://www.federalreserve.gov/feeds/press_all.xml", "fed"),
    ("https://www.sec.gov/news/pressreleases.rss", "sec"),
    ("https://news.google.com/rss/search?q=when:7d+OFAC+sanctions&hl=en-US&gl=US&ceid=US:en", "ofac-sanctions-gnews"),
    ("https://www.ecb.europa.eu/rss/press.html", "ecb"),
    # defense
    ("https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=400&Site=945&max=20", "dod-contracts"),
    ("https://breakingdefense.com/feed/", "breaking-defense"),
    ("https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml", "defense-news"),
    # energy
    ("https://oilprice.com/rss/main", "oilprice"),
    ("https://www.eia.gov/rss/todayinenergy.xml", "eia"),
    # shipping / logistics (chokepoint watch, doctrine §11.4)
    ("https://gcaptain.com/feed/", "gcaptain"),
    ("https://splash247.com/feed/", "splash247"),
    ("https://www.freightwaves.com/news/feed", "freightwaves"),
    # semis / tech supply chain
    ("https://www.tomshardware.com/feeds/all", "tomshardware"),
    ("https://www.eetimes.com/feed/", "eetimes"),
    # ag / food inputs (doctrine §10.8 cascade)
    ("https://www.world-grain.com/rss/articles", "world-grain"),
    # ── war / OSINT / geopolitical (§2 escalation, §4 chessboard) ──
    ("https://www.aljazeera.com/xml/rss/all.xml", "aljazeera"),
    ("https://www.longwarjournal.org/feed", "long-war-journal"),
    ("https://news.usni.org/feed", "usni-naval"),
    ("https://www.twz.com/feed", "the-war-zone"),
    ("https://www.bellingcat.com/feed/", "bellingcat"),
    ("https://www.crisisgroup.org/rss.xml", "crisis-group"),
    ("https://news.google.com/rss/search?q=when:6h+Institute+for+the+Study+of+War+Iran&hl=en-US&gl=US&ceid=US:en", "isw-gnews"),
    ("https://news.google.com/rss/search?q=when:3h+Hormuz+OR+Houthi+tanker&hl=en-US&gl=US&ceid=US:en", "chokepoint-gnews"),
    # ── maritime security (chokepoint enforcement, §11.4) ──
    ("https://news.google.com/rss/search?q=when:6h+tanker+attack+OR+maritime+security+OR+naval&hl=en-US&gl=US&ceid=US:en", "maritime-gnews"),
    ("https://news.google.com/rss/search?q=when:6h+UKMTO+OR+%22maritime+advisory%22+Red+Sea&hl=en-US&gl=US&ceid=US:en", "ukmto-gnews"),
    # ── legislation / executive action / SCOTUS (§12.1 capital-committed; #49/#41) ──
    ("https://www.whitehouse.gov/presidential-actions/feed/", "wh-presidential-actions"),
    ("https://news.google.com/rss/search?q=when:12h+Supreme+Court+ruling+OR+SCOTUS+decision&hl=en-US&gl=US&ceid=US:en", "scotus-gnews"),
    ("https://news.google.com/rss/search?q=when:12h+%22signed+into+law%22+OR+%22executive+order%22&hl=en-US&gl=US&ceid=US:en", "law-signed-gnews"),
    # ── macro / rates (the 2y is the Branch-B discriminator; §13d nowcast) ──
    ("https://news.google.com/rss/search?q=when:4h+Treasury+yield+OR+CPI+OR+Federal+Reserve&hl=en-US&gl=US&ceid=US:en", "macro-gnews"),
    ("https://news.google.com/rss/search?q=when:8h+jobs+report+OR+%22Bureau+of+Labor+Statistics%22+OR+unemployment+rate&hl=en-US&gl=US&ceid=US:en", "bls-gnews"),
    # ── energy / commodity (more) ──
    ("https://news.google.com/rss/search?q=when:6h+Baker+Hughes+rig+count+OR+crude+inventory&hl=en-US&gl=US&ceid=US:en", "rigcount-gnews"),
    ("https://news.google.com/rss/search?q=when:4h+Brent+crude+OR+OPEC+production&hl=en-US&gl=US&ceid=US:en", "crude-gnews"),
]

ATOM = "{http://www.w3.org/2005/Atom}"

# Bare-symbol matching is disabled for these common words (and all len<=2 tickers);
# they still match with $SYM or (NYSE|NASDAQ: SYM) context, and via aliases.
SYMBOL_STOPWORDS = {
    "A", "ALL", "AN", "ANY", "ARE", "ARM", "BE", "BIG", "BY", "CAT", "CELL", "CEO",
    "CORE", "DAY", "DO", "EAT", "FAST", "FLY", "FOR", "GAS", "GO", "GOLD", "HAS",
    "HE", "HIVE", "HUT", "IT", "KEY", "LOW", "MAIN", "MAN", "MOD", "NET", "NEW",
    "NEXT", "NICE", "NOW", "ON", "ONE", "OPEN", "OR", "OUT", "PATH", "PLAY", "POET",
    "REAL", "RIDE", "ROOT", "RUN", "SAFE", "SEE", "SERV", "SO", "SOS", "TECH",
    "TELL", "TWO", "UP", "WELL", "WISE", "YOU",
}


def seen_db():
    p = ROOT / "ledger" / "seen.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(p, timeout=15)
    # the 5-min scheduled task + dashboard-triggered runs can collide on seen.db;
    # wait for the lock instead of erroring, and use WAL for concurrent readers.
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("CREATE TABLE IF NOT EXISTS seen(h TEXT PRIMARY KEY, ts TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS run_counter(k TEXT PRIMARY KEY, v INTEGER)")
    return c


def bump_run_counter(c):
    c.execute("INSERT INTO run_counter VALUES('runs',1) "
              "ON CONFLICT(k) DO UPDATE SET v=v+1")
    return c.execute("SELECT v FROM run_counter WHERE k='runs'").fetchone()[0]


def fetch(url, headers=None):
    if not url.startswith("http"):  # test hook: local file path
        return pathlib.Path(url).read_bytes()
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "gt-analyst/1.0"})
    return urllib.request.urlopen(req, timeout=20).read()


def parse_pub(raw_date):
    """RFC-822 (RSS pubDate) or ISO-8601 (Atom/APIs) -> 'YYYY-MM-DDTHH:MMZ' UTC, or ''.
    Timeliness is load-bearing for the analysis layer: every item carries its
    REPORTED time so stale/archival items are caught mechanically, not by vibes."""
    if not raw_date:
        return ""
    raw_date = str(raw_date).strip()
    dt = None
    try:
        dt = email.utils.parsedate_to_datetime(raw_date)
    except Exception:
        try:
            dt = datetime.datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except Exception:
            return ""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)
    return dt.astimezone(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")


def reported_note(pub):
    """Human-readable 'reported <ts>, <age>' annotation. No parens inside —
    the dashboard's (...) source capture must stay clean."""
    if not pub:
        return "reported unknown"
    try:
        dt = datetime.datetime.strptime(pub, "%Y-%m-%dT%H:%MZ").replace(tzinfo=datetime.UTC)
    except ValueError:
        return "reported unknown"
    hrs = (datetime.datetime.now(datetime.UTC) - dt).total_seconds() / 3600
    if hrs < 0:
        age = "future-dated"
    elif hrs < 1:
        age = f"{max(0, int(hrs * 60))}m ago"
    elif hrs <= 48:
        age = f"{hrs:.0f}h ago"
    else:
        age = f"STALE {hrs / 24:.0f}d old"
    return f"reported {pub}, {age}"


def parse_feed(raw, src_label):
    """Yield (title, desc, url, source, pub) from RSS 2.0 <item> or Atom <entry>."""
    out = []
    root = ET.fromstring(raw)
    for it in root.iter("item"):
        out.append(((it.findtext("title") or "").strip(),
                    (it.findtext("description") or "")[:300],
                    (it.findtext("link") or "").strip(), src_label,
                    parse_pub(it.findtext("pubDate") or it.findtext("date"))))
    for e in root.iter(f"{ATOM}entry"):
        link = ""
        for l in e.findall(f"{ATOM}link"):
            link = l.get("href") or link
            if l.get("rel") in (None, "alternate"):
                break
        out.append(((e.findtext(f"{ATOM}title") or "").strip(),
                    (e.findtext(f"{ATOM}summary") or e.findtext(f"{ATOM}content") or "")[:300],
                    link.strip(), src_label,
                    parse_pub(e.findtext(f"{ATOM}published") or e.findtext(f"{ATOM}updated"))))
    return out


def items(feeds, poll_apis):
    out, ok, total = [], 0, 0
    if poll_apis and os.getenv("NEWSAPI_KEY"):
        total += 1
        try:
            d = json.loads(fetch("https://newsapi.org/v2/top-headlines?category=business"
                                 f"&pageSize=50&apiKey={os.environ['NEWSAPI_KEY']}"))
            out += [(a["title"], a.get("description") or "", a["url"],
                     a.get("source", {}).get("name", "newsapi"),
                     parse_pub(a.get("publishedAt"))) for a in d.get("articles", [])]
            ok += 1
        except Exception as e:
            log(LOGFILE, f"newsapi fail: {e}")
    if poll_apis and os.getenv("FINNHUB_KEY"):
        total += 1
        try:
            d = json.loads(fetch("https://finnhub.io/api/v1/news?category=general"
                                 f"&token={os.environ['FINNHUB_KEY']}"))
            out += [(a["headline"], a.get("summary", ""), a["url"],
                     a.get("source", "finnhub"),
                     datetime.datetime.fromtimestamp(a["datetime"], datetime.UTC)
                     .strftime("%Y-%m-%dT%H:%MZ") if a.get("datetime") else "")
                    for a in d[:50]]
            ok += 1
        except Exception as e:
            log(LOGFILE, f"finnhub fail: {e}")
    # ── Federal Register (NO KEY): presidential documents (EOs) + significant rules.
    #    The capital-committed §12.1 instrument tracker — directly feeds #49/#41. ──
    if poll_apis:
        total += 1
        try:
            # presidential documents (EOs, proclamations, memoranda) = the high-signal
            # executive-action stream; plus SIGNIFICANT rules only (drop routine noise).
            u = ("https://www.federalregister.gov/api/v1/documents.json?per_page=30&order=newest"
                 "&conditions[type][]=PRESDOCU&conditions[type][]=RULE&conditions[significant]=1")
            d = json.loads(fetch(u))
            out += [(f"[{r.get('type', '?')}] {r.get('title', '')}", r.get("abstract") or "",
                     r.get("html_url", ""), "federal-register", parse_pub(r.get("publication_date")))
                    for r in d.get("results", []) if r.get("title")]
            ok += 1
        except Exception as e:
            log(LOGFILE, f"fedregister fail: {e}")
    # ── Polymarket (NO KEY): prediction-market implied odds. Surfaced so the analyst
    #    can compare MARKET-implied probability vs the ENGINE's (§12 calibration). ──
    if poll_apis:
        total += 1
        try:
            d = json.loads(fetch("https://gamma-api.polymarket.com/markets"
                                 "?closed=false&order=volume&ascending=false&limit=150"))
            rows = d if isinstance(d, list) else d.get("data", [])
            # keep only macro / geopolitical / political markets — skip the sports-betting flood.
            # word-boundary match so "war" doesn't hit inside "edWARd Gaming" (an esports team).
            rel_re = re.compile(
                r"\b(fed|rate hikes?|rate cuts?|iran|israel|wars?|ceasefire|elections?|trump|oil|"
                r"brent|crude|recession|china|taiwan|cpi|inflation|nuclear|hormuz|houthi|russia|"
                r"ukraine|opec|gdp|unemployment|shutdown|tariffs?|nvidia|nasdaq|bitcoin|supreme court|"
                r"congress|senate|powell|warsh|sanctions?|fomc|treasury|yields?|interest rate)\b", re.I)
            sports_re = re.compile(
                r"\b(vs\.?|handicap|spread|o/u|over/under|glove|winner|set \d|games?|goals?|"
                r"nba|nfl|mlb|nhl|episode|late show|podcast|host|soccer|tennis|gaming|series|match|award|champion|cup)\b", re.I)
            for m in rows:
                q = (m.get("question") or m.get("title") or "").strip()
                if not q or sports_re.search(q) or not rel_re.search(q):
                    continue
                pr = m.get("outcomePrices")
                try:
                    yes = round(float(json.loads(pr)[0]) * 100) if pr else None
                except (ValueError, TypeError, json.JSONDecodeError, IndexError):
                    yes = None
                if yes is not None:
                    out.append((f"PREDICTION MARKET ({yes}% YES): {q}", "",
                                "https://polymarket.com/event/" + str(m.get("slug", "")),
                                "polymarket", ""))
            ok += 1
        except Exception as e:
            log(LOGFILE, f"polymarket fail: {e}")
    # ── FRED (KEY: FRED_API_KEY): latest value of the series the engine watches most —
    #    the 2y (Branch-B discriminator), Brent, and gasoline. Surfaced as data-tape items. ──
    if poll_apis and os.getenv("FRED_API_KEY"):
        total += 1
        try:
            for sid, name in [("DGS2", "2yr Treasury %"), ("DGS10", "10yr Treasury %"),
                              ("DCOILBRENTEU", "Brent $/bbl"), ("GASREGW", "US reg gasoline $/gal")]:
                d = json.loads(fetch(
                    f"https://api.stlouisfed.org/fred/series/observations?series_id={sid}"
                    f"&sort_order=desc&limit=1&file_type=json&api_key={os.environ['FRED_API_KEY']}"))
                obs = d.get("observations", [])
                if obs and obs[0].get("value") not in (".", None):
                    out.append((f"MACRO DATA: {name} = {obs[0]['value']} ({obs[0].get('date')})",
                                "", f"https://fred.stlouisfed.org/series/{sid}", "fred", ""))
            ok += 1
        except Exception as e:
            log(LOGFILE, f"fred fail: {e}")
    # ── Congress.gov (KEY: CONGRESS_API_KEY from api.data.gov): recently-enacted laws. ──
    if poll_apis and os.getenv("CONGRESS_API_KEY"):
        total += 1
        try:
            d = json.loads(fetch("https://api.congress.gov/v3/law/119?limit=15&format=json"
                                 f"&api_key={os.environ['CONGRESS_API_KEY']}"))
            for b in d.get("bills", d.get("laws", [])):
                t = b.get("title") or ""
                if t:
                    out.append((f"LAW ENACTED: {t}", "", b.get("url", ""), "congress", ""))
            ok += 1
        except Exception as e:
            log(LOGFILE, f"congress fail: {e}")
    # ── EIA (KEY: EIA_API_KEY): weekly crude + gasoline stocks (supply-shock confirmation). ──
    if poll_apis and os.getenv("EIA_API_KEY"):
        total += 1
        try:
            d = json.loads(fetch(
                "https://api.eia.gov/v2/petroleum/stoc/wstk/data/?frequency=weekly"
                "&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&length=3"
                f"&api_key={os.environ['EIA_API_KEY']}"))
            for r in d.get("response", {}).get("data", [])[:3]:
                out.append((f"EIA STOCKS: {r.get('series-description', '')} = {r.get('value')} "
                            f"({r.get('period')})", "", "https://www.eia.gov/petroleum/", "eia-data", ""))
            ok += 1
        except Exception as e:
            log(LOGFILE, f"eia fail: {e}")
    for url, label in feeds:
        total += 1
        try:
            out += parse_feed(fetch(url), label)
            ok += 1
        except Exception as e:
            log(LOGFILE, f"feed fail {label}: {e}")
    return out, ok, total


# ── watchlist matching ──────────────────────────────────────────────────

def flatten_watchlist(data):
    """Support both the flat {"tickers":{...}} and themed
    {"themes":{name:{"index":..,"tickers":{...}}}} formats. Returns a flat
    {SYM: cfg} dict (later themes override earlier on symbol collision)."""
    out = {}
    out.update(data.get("tickers", {}) or {})
    for theme in (data.get("themes", {}) or {}).values():
        out.update((theme or {}).get("tickers", {}) or {})
    return out


def compile_watchlist():
    wl = flatten_watchlist(load_json(ROOT / "watchlist.json", {}))
    compiled = {}
    for sym, cfg in wl.items():
        cfg = cfg or {}
        allow_bare = cfg.get("symbol_match", True)
        if len(sym) <= 2 or sym.upper() in SYMBOL_STOPWORDS:
            allow_bare = False  # auto-guard against A/ALL/IT-style false positives
        pats = []
        if allow_bare:
            pats.append(("symbol", re.compile(
                rf"(?<![A-Za-z0-9])\$?{re.escape(sym)}(?![A-Za-z0-9])")))
        # $SYM or (NYSE: SYM) context always counts, even for guarded symbols
        pats.append(("symbol-ctx", re.compile(
            rf"(\${re.escape(sym)}(?![A-Za-z0-9])|[\(\s](?:NYSE|NASDAQ|AMEX)[:\s]+{re.escape(sym)}\b)")))
        for alias in sorted(cfg.get("aliases", []), key=len, reverse=True):
            pats.append(("alias", re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)))
        for kw in cfg.get("keywords", []):
            pats.append(("keyword", re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)))
        compiled[sym] = pats
    return compiled


def match_watchlist(compiled, fresh):
    """dict[ticker -> list[(item, kind, matched_text)]]"""
    hits = {}
    for item in fresh:
        text = f"{item[0]} {item[1]}"
        for sym, pats in compiled.items():
            for kind, pat in pats:
                m = pat.search(text)
                if m:
                    hits.setdefault(sym, []).append((item, kind, m.group(0)))
                    break  # one hit per ticker per item is enough
    return hits


def write_triggered_batch(hits):
    tickers = sorted(hits.keys())
    stamp = utc_stamp()
    path = ROOT / "inbox" / "triggered" / f"{stamp}_{'-'.join(tickers)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Watchlist trigger — {utc_iso()} ({', '.join(tickers)})\n\n")
        for sym in tickers:
            f.write(f"## {sym}\n")
            for item, kind, text in hits[sym]:
                t, d, u, s = item[0], item[1], item[2], item[3]
                p = item[4] if len(item) > 4 else ""
                f.write(f"- **{t}** ({s} | {reported_note(p)})\n  {d}\n  {u}\n"
                        f"  Matched: {sym} ({kind} \"{text}\")\n")
        f.write("\n")
    return path, tickers


def dispatch_trigger(batch_path, tickers):
    """Spawn trigger.py detached so the 5-min ingest cadence never blocks."""
    pyw = pathlib.Path(sys.executable)
    pythonw = pyw.parent / "pythonw.exe"
    exe = str(pythonw if pythonw.exists() else pyw)
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    subprocess.Popen(
        [exe, str(ROOT / "pipeline" / "trigger.py"),
         "--batch", str(batch_path), "--tickers", ",".join(tickers)],
        cwd=ROOT, creationflags=flags, close_fds=True)


# ── main ────────────────────────────────────────────────────────────────

def main():
    load_env()
    feeds = FEEDS
    if "--feeds" in sys.argv:  # test hook
        paths = sys.argv[sys.argv.index("--feeds") + 1:]
        feeds = [(p, f"test:{pathlib.Path(p).name}") for p in paths]

    c = seen_db()
    run_no = bump_run_counter(c)
    poll_apis = (run_no % 3 == 1)  # free-tier guard: APIs every 3rd run only

    all_items, ok, total = items(feeds, poll_apis)
    fresh = []
    for it in all_items:
        title, desc, url, src = it[0], it[1], it[2], it[3]
        pub = it[4] if len(it) > 4 else ""
        if not url:
            continue
        h = hashlib.sha1(url.encode()).hexdigest()
        if c.execute("SELECT 1 FROM seen WHERE h=?", (h,)).fetchone():
            continue
        c.execute("INSERT INTO seen VALUES(?,?)", (h, utc_iso()))
        fresh.append((title, desc, url, src, pub))
    c.commit()

    trigger_note = "none"
    if fresh:
        inbox = ROOT / "inbox"
        inbox.mkdir(exist_ok=True)
        with open(inbox / "latest.md", "a", encoding="utf-8") as f:  # APPEND
            f.write(f"## batch {utc_iso()} ({len(fresh)} new)\n\n")
            for t, d, u, s, p in fresh:
                f.write(f"- **{t}** ({s} | {reported_note(p)})\n  {d}\n  {u}\n")
            f.write("\n")

        hits = match_watchlist(compile_watchlist(), fresh)
        if hits:
            batch_path, tickers = write_triggered_batch(hits)  # ALL matches recorded
            # Tier gate: only auto-tier tickers dispatch a token-burning analysis.
            at = load_json(ROOT / "config.json", {}).get("auto_trigger", {})
            if at.get("tier_enabled", True) and at.get("auto_tickers"):
                auto = [t for t in tickers if t in set(at["auto_tickers"])]
            else:
                auto = tickers
            watch_only = [t for t in tickers if t not in auto]
            if auto:
                dispatch_trigger(batch_path, auto)
                trigger_note = f"dispatched {','.join(auto)}"
                if watch_only:
                    trigger_note += f" (watch-only: {','.join(watch_only)})"
                trigger_note += f" -> {batch_path.name}"
            else:
                trigger_note = f"watch-only {','.join(tickers)} -> {batch_path.name}"

    log(LOGFILE, f"run={run_no} feeds_ok={ok}/{total} apis={'y' if poll_apis else 'n'} "
                 f"new={len(fresh)} trigger={trigger_note}")
    print(f"{len(fresh)} new items -> inbox/latest.md (trigger: {trigger_note})")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(LOGFILE, "FATAL " + traceback.format_exc().replace("\n", " | "))
        raise
