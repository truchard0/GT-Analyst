#!/usr/bin/env python3
"""Build one edition of the GT-Analyst US market update from our own Skylit maps.

  python -I tools/market_update/build.py --date 2026-11-17 --edition preclose [--asof 1545] [--tickers NVDA,MU]
  python -I tools/market_update/build.py --date 2026-11-17 --edition overnight --tickers NVDA,MU,SMH
  python -I tools/market_update/build.py --date 2026-11-18 --edition morning
  python -I tools/market_update/build.py --date 2026-11-17 --score-only      # score the morning band at the close

Writes reports/market_update/<date>_<edition>/: the PNG charts, update.md, update.pdf and update.docx.
Logs each morning-map base case to data/market_update/scorecard.csv and scores it at the close.

Rules baked in: events first; levels are positioning, never targets; price direction is a no-call; no trades, hedges,
sizes or payoff charts; scenario odds only from a measured base rate with its n; every number carries a snapshot time
and stale flag; never Unusual Whales data; nothing is written to Trading Bot.
"""
import argparse
import csv
import datetime as dt
import pathlib
import statistics as st
import sys

TOOLS = pathlib.Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import market_update  # noqa: E402,F401  (path bootstrap for numpy)
import numpy as np  # noqa: E402

from market_update import charts as C  # noqa: E402
from market_update import chartstyle as cs  # noqa: E402
from market_update import data as D  # noqa: E402
from market_update import stats as S  # noqa: E402

REPO = D.REPO
SCORECARD = D.MU_DATA / "scorecard.csv"
SC_FIELDS = ["statement_id", "date", "symbol", "statement", "map_snapshot", "band_lo", "band_hi", "open",
             "logged_by", "logged_at", "close", "close_slot", "outcome", "scored_at", "note"]
F = cs.fmt_big
L = cs.fmt_level
MINUS = cs.MINUS

RECORD = {
    "node": "Our record: price closed nearer the largest node than a mirror level 46.7% of the time (n = 165). "
            "Positioning, not destinations.",
    "gamma_sign": "Our record: negative-gamma days were not consistently wider (range ratios 1.28, 0.96, 0.80 for "
                  "SPX, SPY, QQQ).",
    "overnight": "Our record: the overnight node rule scored 51.2% vs 51.1% placebo on ~370 unseen nights. "
                 "No reversal edge at these levels overnight.",
    "vanna": "Our record: vanna splits passed 12 of 42 tests against 12.6 expected by chance. "
             "Vanna is shown as a description of the book only.",
    "heat": "Our record: the largest cell as a magnet tested null (46.7% vs mirror, n = 165). "
            "It shows the book, not a path.",
    "change": "Our record: rolling ceilings and floors follow price rather than lead it. "
              "A changed book describes positioning, not direction.",
    "vix": "Our record: no VIX-positioning rule has passed a pre-registered test in our registry. "
           "VIX levels are shown as context only.",
}


# ================================================================ small utils
def et_label(t):
    return t.strftime("%d %b %Y %H:%M ET") if t else "unknown time"


def hm(t):
    return t.strftime("%H:%M")


def pct(a, b):
    return 100.0 * (a / b - 1.0)


def day_name(d):
    return D.d_(d).strftime("%A")


def short_day(d):
    return D.d_(d).strftime("%a %d %b")


class Doc:
    """Edition content as blocks, rendered to markdown, PDF (pymupdf Story) and docx."""

    def __init__(self, title, deck):
        self.title, self.deck, self.blocks, self.charts = title, deck, [], []

    def h(self, text):
        self.blocks.append(("h2", text))

    def p(self, text):
        self.blocks.append(("p", text))

    def bullets(self, items):
        self.blocks.append(("ul", items))

    def table(self, header, rows):
        self.blocks.append(("table", header, rows))

    def img(self, path, caption):
        self.blocks.append(("img", pathlib.Path(path).name, caption))
        self.charts.append(pathlib.Path(path).name)

    def box(self, text):
        self.blocks.append(("box", text))

    def small(self, text):
        self.blocks.append(("small", text))

    def mark(self):
        self._mark = len(self.blocks)

    def insert_key_calls(self, rows, bottom_line):
        """Key-calls table (call, odds, resolves, what flips it) right after the event lead."""
        at = getattr(self, "_mark", 0)
        blk = [("h2", "Key calls"), ("p", bottom_line),
               ("table", ["Call", "Odds", "Resolves", "What flips it"], rows)]
        self.blocks[at:at] = blk

    # ---- markdown
    def markdown(self, footer):
        out = ["# %s" % self.title, "", "*%s*" % self.deck, ""]
        for b in self.blocks:
            k = b[0]
            if k == "h2":
                out += ["## %s" % b[1], ""]
            elif k == "p":
                out += [b[1], ""]
            elif k == "small":
                out += ["<sub>%s</sub>" % b[1], ""]
            elif k == "ul":
                out += ["- %s" % i for i in b[1]] + [""]
            elif k == "table":
                out.append("| " + " | ".join(b[1]) + " |")
                out.append("|" + "|".join("---" for _ in b[1]) + "|")
                out += ["| " + " | ".join(str(c) for c in r) + " |" for r in b[2]]
                out.append("")
            elif k == "img":
                out += ["![%s](%s)" % (b[2], b[1]), "", "*%s*" % b[2], ""]
            elif k == "box":
                out += ["> **%s**" % b[1], ""]
        out += ["---", footer, ""]
        return "\n".join(out)

    # ---- html for the PDF
    def html(self, footer):
        import html as H
        e = H.escape
        css = """
        body { font-family: sans-serif; font-size: 10pt; color: #1a1a1a; }
        h1 { font-size: 19pt; margin: 0 0 4pt 0; }
        h2 { font-size: 13pt; margin: 14pt 0 4pt 0; color: #111; }
        p { margin: 0 0 6pt 0; line-height: 1.35; }
        .deck { color: #555; font-style: italic; margin-bottom: 10pt; }
        .cap { color: #555; font-size: 8.5pt; font-style: italic; margin: 2pt 0 10pt 0; }
        .box { border: 1px solid #d9a400; background-color: #fff8e1; padding: 6pt; margin: 6pt 0 10pt 0;
               font-weight: bold; color: #5c4300; }
        .small { color: #666; font-size: 8pt; }
        table { border-collapse: collapse; margin: 4pt 0 10pt 0; font-size: 8.5pt; }
        th, td { border: 1px solid #cccccc; padding: 2pt 4pt; text-align: left; }
        th { background-color: #f0f0f0; }
        li { margin-bottom: 2pt; }
        .foot { color: #777; font-size: 8pt; margin-top: 12pt; }
        """
        parts = ["<html><head><style>%s</style></head><body>" % css, "<h1>%s</h1>" % e(self.title),
                 "<p class='deck'>%s</p>" % e(self.deck)]
        for b in self.blocks:
            k = b[0]
            if k == "h2":
                parts.append("<h2>%s</h2>" % e(b[1]))
            elif k == "p":
                parts.append("<p>%s</p>" % e(b[1]))
            elif k == "small":
                parts.append("<p class='small'>%s</p>" % e(b[1]))
            elif k == "ul":
                parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % e(i) for i in b[1]))
            elif k == "table":
                parts.append("<table><tr>%s</tr>%s</table>" % (
                    "".join("<th>%s</th>" % e(h) for h in b[1]),
                    "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % e(str(c)) for c in r) for r in b[2])))
            elif k == "img":
                parts.append("<p><img src='%s' width='504' height='315'/></p><p class='cap'>%s</p>" % (b[1], e(b[2])))
            elif k == "box":
                parts.append("<p class='box'>%s</p>" % e(b[1]))
        parts.append("<p class='foot'>%s</p></body></html>" % e(footer))
        return "".join(parts)


def write_pdf(doc, out_dir, footer):
    """Letter PDF. ReportLab (flowables keep charts full width and push them to the next page whole); pymupdf
    Story is the fallback when ReportLab is missing."""
    try:
        return _write_pdf_reportlab(doc, out_dir, footer)
    except ImportError:
        pass
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    html = doc.html(footer)
    story = pymupdf.Story(html=html, archive=pymupdf.Archive(str(out_dir)))
    path = out_dir / "update.pdf"
    writer = pymupdf.DocumentWriter(str(path))
    mediabox = pymupdf.paper_rect("letter")
    where = mediabox + (54, 54, -54, -54)
    more = True
    while more:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    return path


def _write_pdf_reportlab(doc, out_dir, footer):
    import html as H
    import matplotlib
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
                                    Spacer, Table, TableStyle)
    fdir = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for name, f in (("DV", "DejaVuSans.ttf"), ("DVB", "DejaVuSans-Bold.ttf"), ("DVI", "DejaVuSans-Oblique.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fdir / f)))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")
    base = ParagraphStyle("b", fontName="DV", fontSize=9.5, leading=13.2, textColor=colors.HexColor("#1a1a1a"),
                          alignment=TA_LEFT, spaceAfter=5)
    sty = {
        "h1": ParagraphStyle("h1", parent=base, fontName="DVB", fontSize=16.5, leading=20, spaceAfter=3),
        "deck": ParagraphStyle("deck", parent=base, fontName="DVI", textColor=colors.HexColor("#555555"),
                               spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base, fontName="DVB", fontSize=12, leading=15, spaceBefore=9,
                             spaceAfter=4),
        "p": base,
        "cap": ParagraphStyle("cap", parent=base, fontName="DVI", fontSize=8, leading=10.5,
                              textColor=colors.HexColor("#555555"), spaceAfter=9),
        "small": ParagraphStyle("small", parent=base, fontSize=7.5, leading=10, textColor=colors.HexColor("#666666")),
        "box": ParagraphStyle("box", parent=base, fontName="DVB", textColor=colors.HexColor("#5c4300"),
                              backColor=colors.HexColor("#fff8e1"), borderColor=colors.HexColor("#d9a400"),
                              borderWidth=0.8, borderPadding=6, spaceBefore=4, spaceAfter=10),
        "cell": ParagraphStyle("cell", parent=base, fontSize=8, leading=10, spaceAfter=0),
        "foot": ParagraphStyle("foot", parent=base, fontSize=7.5, textColor=colors.HexColor("#777777")),
    }
    e = H.escape
    W = letter[0] - 1.5 * inch
    flow = [Paragraph(e(doc.title), sty["h1"]), Paragraph(e(doc.deck), sty["deck"])]
    for b in doc.blocks:
        k = b[0]
        if k == "h2":
            flow.append(Paragraph(e(b[1]), sty["h2"]))
        elif k in ("p", "small"):
            flow.append(Paragraph(e(b[1]), sty[k]))
        elif k == "box":
            flow.append(Paragraph(e(b[1]), sty["box"]))
        elif k == "ul":
            flow.append(ListFlowable([ListItem(Paragraph(e(i), base), leftIndent=10) for i in b[1]],
                                     bulletType="bullet", start="•", leftIndent=10, bulletFontName="DV"))
        elif k == "table":
            data = [[Paragraph("<b>%s</b>" % e(h), sty["cell"]) for h in b[1]]] + \
                   [[Paragraph(e(str(c)), sty["cell"]) for c in r] for r in b[2]]
            n = len(b[1])
            widths = [W * 0.36, W * 0.18, W * 0.14, W * 0.32] if n == 4 else [W / n] * n
            t = Table(data, colWidths=widths, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            flow += [t, Spacer(1, 8)]
        elif k == "img":
            img = Image(str(out_dir / b[1]), width=W, height=W / 1.6)
            flow.append(KeepTogether([img, Spacer(1, 2), Paragraph(e(b[2]), sty["cap"])]))
    flow.append(Paragraph(e(footer), sty["foot"]))

    def on_page(canvas, d):
        canvas.saveState()
        canvas.setFont("DV", 7)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(0.75 * inch, 0.45 * inch, "GT-Analyst · not investment advice")
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.45 * inch, "page %d" % d.page)
        canvas.restoreState()

    path = out_dir / "update.pdf"
    SimpleDocTemplate(str(path), pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.75 * inch, title=doc.title,
                      author="GT-Analyst").build(flow, onFirstPage=on_page, onLaterPages=on_page)
    return path


def write_docx(doc, out_dir, footer):
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
    except ImportError:
        return None
    d = docx.Document()
    st_ = d.styles["Normal"]
    st_.font.name = "Calibri"
    st_.font.size = Pt(10.5)
    d.add_heading(doc.title, level=1)
    para = d.add_paragraph(doc.deck)
    para.runs[0].italic = True
    for b in doc.blocks:
        k = b[0]
        if k == "h2":
            d.add_heading(b[1], level=2)
        elif k == "p":
            d.add_paragraph(b[1])
        elif k == "small":
            r = d.add_paragraph().add_run(b[1])
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        elif k == "ul":
            for i in b[1]:
                d.add_paragraph(i, style="List Bullet")
        elif k == "table":
            t = d.add_table(rows=1, cols=len(b[1]))
            t.style = "Light Grid Accent 1"
            for j, h in enumerate(b[1]):
                t.rows[0].cells[j].text = h
            for r in b[2]:
                cells = t.add_row().cells
                for j, c in enumerate(r):
                    cells[j].text = str(c)
            d.add_paragraph()
        elif k == "img":
            d.add_picture(str(out_dir / b[1]), width=Inches(6.5))
            c = d.add_paragraph(b[2])
            c.runs[0].italic = True
            c.runs[0].font.size = Pt(9)
        elif k == "box":
            r = d.add_paragraph().add_run(b[1])
            r.bold = True
            r.font.color.rgb = RGBColor(0x8a, 0x64, 0x00)
    r = d.add_paragraph().add_run(footer)
    r.font.size = Pt(8)
    path = out_dir / "update.docx"
    d.save(str(path))
    return path


# ================================================================ scorecard
def sc_read():
    if not SCORECARD.exists():
        return []
    with open(SCORECARD, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sc_write(rows):
    D.MU_DATA.mkdir(parents=True, exist_ok=True)
    with open(SCORECARD, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SC_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in SC_FIELDS})


def sc_log_band(date, band, open_spot, snap_label, logged_by):
    rows = sc_read()
    sid = "%s-SPX-morning-band" % date
    if any(r["statement_id"] == sid for r in rows):
        return sid
    lo, hi = band[0], band[1]
    rows.append({"statement_id": sid, "date": str(date), "symbol": "SPX",
                 "statement": "SPX closes inside the morning band %s-%s (largest positive same-day gamma strikes "
                              "either side of the 09:30 open, within 1.5%%)" % (L(lo), L(hi)),
                 "map_snapshot": snap_label, "band_lo": lo, "band_hi": hi, "open": open_spot, "logged_by": logged_by,
                 "logged_at": dt.datetime.now(D.ET).strftime("%Y-%m-%d %H:%M ET"), "outcome": "pending"})
    sc_write(rows)
    return sid


def sc_score(date):
    """Score the morning-band row for `date` against the 16:00 ET map close. Returns the row or None."""
    rows = sc_read()
    sid = "%s-SPX-morning-band" % date
    mins = D.live_minutes(date)
    if not mins or mins[-1][0] < "1555":
        return None
    path = D.spot_path(date, "SPXW", "1600")
    close = path[-1][1]
    for r in rows:
        if r["statement_id"] == sid:
            r["close"] = "%.2f" % close
            r["close_slot"] = path[-1][0].strftime("%H:%M ET")
            r["outcome"] = S.score_band(float(r["band_lo"]), float(r["band_hi"]), close)
            r["scored_at"] = dt.datetime.now(D.ET).strftime("%Y-%m-%d %H:%M ET")
            r["note"] = "scored on the Skylit 16:00 ET spot sample"
            sc_write(rows)
            return r
    return None


def sc_tally(upto):
    """Scored morning bands for dates up to and including `upto` (a back-dated edition never sees later scores)."""
    rows = [r for r in sc_read() if r.get("outcome") not in ("", "pending", None) and r["date"] <= str(upto)]
    hit = sum(1 for r in rows if r["outcome"] == "inside")
    return hit, len(rows)


# ================================================================ shared sections
def events_section(doc, events):
    leads = [e for e in events if e.get("kind") == "lead"]
    doc.h("The day's events")
    if not leads:
        doc.p("No curated event lines for this date (data/market_update/events/<date>.json is missing).")
        return
    for e in leads:
        when = ("reported %s" % e["reported_et"].strftime("%d %b %H:%M ET")) if e.get("reported_et") else \
            "time not given"
        doc.p("%s (%s; %s)" % (e["text"], e.get("source", ""), when))


def watch_section(doc, events, extra=()):
    w = [e for e in events if e.get("kind") == "watch" and e.get("when")]
    items = ["%s: %s" % (e["when"].strftime("%a %d %b %H:%M ET") if e["when"].hour or e["when"].minute else
                         e["when"].strftime("%a %d %b"), e["text"]) for e in sorted(w, key=lambda x: x["when"])]
    items = list(extra) + items
    if items:
        doc.h("Dated watch-list")
        doc.bullets(items)


def band_record_line(rec):
    if not rec:
        return "Morning-band record: not enough sessions yet."
    return ("Morning band held the close on %.0f%% of %d sessions vs %.0f%% for its mirror (in-sample, %s to %s)."
            % (rec["real_pct"], rec["n"], rec["mirror_pct"], D.d_(rec["first"]).strftime("%b %Y"),
               D.d_(rec["last"]).strftime("%d %b %Y")))


def route_block(doc, out_dir, fname, *, label_day, close_txt, vix_now, em, rates, title_suffix, snapshot,
                event_note=None):
    """Route tree on the next session's close-to-close move vs the priced move, with measured shares and n."""
    a, c = rates["all"], rates.get("cond")
    use = c if (c and c["n"] >= 20) else a
    lo_b, hi_b = rates.get("cond_band", (None, None))
    cond_txt = ("sessions with 30-day implied vol %.0f-%.0f" % (lo_b, hi_b)) if use is c else "all sessions"
    br = []
    for key, lab, sub, col in (("up", "Up more than priced", "> +%.2f%%" % em, "green"),
                               ("inside", "Inside the priced move", "within ±%.2f%%" % em, "yellow"),
                               ("down", "Down more than priced", "< %s%.2f%%" % (MINUS, em), "red")):
        br.append(dict(label=lab, sub=sub, colour=col,
                       leaf=("%.0f%% of %d past sessions" % (use[key], use["n"]),
                             "%s\n(all sessions: %.0f%% of %d)" % (cond_txt, a[key], a["n"]))))
    aside = event_note or "No call on direction. Shares of past sessions, not forecasts."
    title = "%s: %.0f%% of similar sessions closed inside the priced ±%.2f%%" % (title_suffix, use["inside"], em)
    sub = ("Next-session SPX close-to-close move vs the options-implied 1-day move. %d %s (%s to %s); "
           "unconditional %d sessions." % (use["n"], cond_txt, use["first"], use["last"], a["n"]))
    C.route_tree(out_dir / fname, title=title, subtitle=sub,
                 root=(label_day.upper(), close_txt),
                 question=("How big is %s's close-to-close move?" % day_name_from(title_suffix), None),
                 branches=br, aside=(aside, None),
                 callout="Odds are shares of past sessions with n, not a forecast. Direction stays a no-call.",
                 footer_right="Skylit vol history (SPXW close, svx30, implied 1-day move), %s to %s" %
                              (a["first"], a["last"]), snapshot=snapshot)
    doc.img(out_dir / fname, "Routes for %s's session. Inside the priced move: %.0f%% of %d %s; beyond it up %.0f%%, "
            "down %.0f%%." % (day_name_from(title_suffix), use["inside"], use["n"], cond_txt, use["up"], use["down"]))
    return use, cond_txt


def day_name_from(label):
    for d in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
        if d.lower() in label.lower():
            return d
    return "the next session"


def single_names(doc, out_dir, date, tickers, asof_hhmmss, edition_date, releases, snapshot_txt, prefix,
                 with_vanna=True):
    notes = []
    for t in tickers:
        ev = releases.get(t)
        asof_dt = dt.datetime.combine(D.d_(edition_date), dt.time(int(asof_hhmmss[:2]), int(asof_hhmmss[2:4])),
                                      tzinfo=D.ET)
        released = ev is not None and ev <= asof_dt
        g = D.load_universe_map(date, t, "gamma", asof_hhmmss, edition_date, event_after=ev if released else None)
        if g is None:
            notes.append("%s: no Skylit single-name gamma map on %s at or before %s:%s ET." % (t, date, asof_hhmmss[:2],
                                                                                         asof_hhmmss[2:4]))
            continue
        if not g.show:
            notes.append("%s: %s (map %s); no levels shown." % (t, g.stale_note, et_label(g.asof)))
            continue
        exps = [e for e in g.expiries if e > str(edition_date)][:8]
        cols = [g.expiries.index(e) for e in exps]
        M = g.matrix[:, cols]
        win = 0.12 if t != "NVDA" else 0.15
        pre_note = ""
        if ev is not None and not released:
            pre_note = " Pre-report map: it becomes EVENT-STALE at the %s release." % ev.strftime("%d %b")
        fname = "%s_%s_gamma_heatmap.png" % (prefix, t.lower())
        sel = np.abs(g.strikes / g.spot - 1) <= win
        Msel = M[sel]
        r0, c0 = np.unravel_index(np.argmax(np.abs(Msel)), Msel.shape)
        kk, ke, kv = g.strikes[sel][r0], exps[c0], Msel[r0, c0]
        near = float(M[np.abs(g.strikes / g.spot - 1) <= 0.02].sum())
        regime = "long" if near > 0 else "short"
        title = "%s: the largest cell is %s %s on %s (%s)" % (t, "a long-gamma" if kv > 0 else "a short-gamma",
                                                               L(kk, 1 if kk != round(kk) else 0),
                                                               D.d_(ke).strftime("%d %b"), F(kv))
        sub = ("Dealer gamma by strike and expiry, %s map %s, spot %s. Net within ±2%% of spot over the %d "
               "expiries shown: %s (dealers %s gamma).%s" % (g.batch.split("_")[0], et_label(g.asof), L(g.spot, 2),
                                                             len(exps), F(near), regime, pre_note))
        C.gamma_heatmap(out_dir / fname, g.strikes, exps, M, g.spot, title=title, subtitle=sub,
                        callout=RECORD["heat"], footer_right="Skylit %s universe map %s, %d expiries %s to %s" %
                        (t, g.batch, len(exps), exps[0], exps[-1]), snapshot=snapshot_txt, window_pct=win,
                        decimals=1 if t in ("NVDA", "AMZN", "SMH") else 0,
                        unit_note="Values in Skylit units (compare within %s only)." % t,
                        tag=("%s GAMMA  STRIKE X EXPIRY" % t, "cyan"))
        doc.p("%s's %s map (%s, spot %s): the largest cell is %s on %s (%s), and net gamma within 2%% of spot over "
              "the %d expiries shown is %s, so dealers are net %s gamma around the price.%s" %
              (t, g.batch.split("_")[0], et_label(g.asof), L(g.spot, 2), L(kk, 1 if kk != round(kk) else 0),
               short_day(ke), F(kv), len(exps), F(near), regime, pre_note))
        doc.img(out_dir / fname, "%s dealer gamma across %d expiries (%s). Largest cell %s on %s, %s." %
                (t, len(exps), et_label(g.asof), L(kk, 1 if kk != round(kk) else 0), ke, F(kv)))
        if with_vanna:
            v = D.load_universe_map(date, t, "vanna", asof_hhmmss, edition_date,
                                    event_after=ev if released else None)
            if v is None:
                notes.append("%s vanna: no Skylit vanna map at or before %s:%s ET (the vanna batch runs at 16:00 ET "
                             "only)." % (t, asof_hhmmss[:2], asof_hhmmss[2:4]))
            elif not v.show:
                notes.append("%s vanna: %s; not shown." % (t, v.stale_note))
            else:
                vex = [e for e in v.expiries if e > str(edition_date)][:10]
                vals = v.rowsum(vex)
                fn = "%s_%s_vanna.png" % (prefix, t.lower())
                w = np.abs(v.strikes / v.spot - 1) <= 0.15
                kp = v.strikes[w][np.argmax(vals[w])]
                kn = v.strikes[w][np.argmin(vals[w])]
                above = float(vals[(v.strikes > v.spot) & w].sum())
                below = float(vals[(v.strikes < v.spot) & w].sum())
                res = C.vanna_bars(
                    out_dir / fn, v.strikes, vals, v.spot, ticker=t,
                    title="%s vanna: largest positive strike %s, largest negative %s" % (t, L(kp, 1 if kp != round(kp) else 0), L(kn, 1 if kn != round(kn) else 0)),
                    subtitle="Dealer vanna by strike, summed over %d expiries %s to %s, map %s, spot %s.\n"
                             "Net above spot %s, below spot %s (within ±15%%)." %
                             (len(vex), vex[0], vex[-1], et_label(v.asof), L(v.spot, 2), F(above), F(below)),
                    callout=RECORD["vanna"], footer_right="Skylit %s vanna map %s" % (t, v.batch),
                    snapshot=snapshot_txt, expiry_note="Summed over %d expiries %s to %s. Skylit units, compare "
                                                       "within %s only." % (len(vex), vex[0], vex[-1], t),
                    how_to=[("Green bars", "Positive vanna in Skylit's dealer sign.\nUnder that convention, a fall in\n"
                                           "implied vol has dealers buy here."),
                            ("Red bars", "Negative vanna: a fall in implied vol\nhas dealers sell here."),
                            ("What it is not", "A path. Vanna says what a vol move\nforces, not whether vol moves."),
                            ("Our record", "12 of 42 vanna splits passed,\nabout the 12.6 expected by chance.")])
                doc.img(out_dir / fn, "%s vanna by strike (%s): largest positive %s, largest negative %s; net "
                                     "above spot %s, below %s." % (t, et_label(v.asof), L(kp, 1 if kp != round(kp) else 0), L(kn, 1 if kn != round(kn) else 0),
                                                                   F(above), F(below)))
    return notes


def earnings_block(doc, out_dir, fname, session, vol, snapshot_txt, asof_dt, focus_syms=None):
    e = D.load_earnings(session)
    if not e["rows"]:
        return None
    rows, vcache, used_vol = [], {}, set()
    for r in e["rows"][:8]:
        when = r["when"].replace("tonight ", "").replace("tomorrow ", "")
        rel = D.release_time(r)
        if rel is not None and rel < asof_dt:
            when = "reported " + when
        # the implied move that covers the reaction session: the vol file from the close before that session,
        # and only if it was published before this edition's as-of time
        implied = None
        w = (r.get("when") or "").lower()
        rd = r.get("report_day")
        react = str(D.next_weekday(rd)) if "after" in w else (rd if "before" in w else None)
        if react:
            vd = str(D.prev_weekday(react))
            if vd not in vcache:
                vcache[vd] = D.load_vol_daily(vd)
            v = vcache[vd]
            if v and r["sym"] in v["symbols"] and v["published"] and v["published"] <= asof_dt:
                implied = v["symbols"][r["sym"]].get("em_1d_pct")
                used_vol.add(vd)
        rows.append(dict(sym=r["sym"], name=r.get("name", ""), when=when, past=r.get("typical") or [],
                         implied=implied, gap_chance=r.get("est")))
    pr = [r for r in rows if r["implied"] and r["past"]]
    focus = [r for r in rows if r["sym"] in (focus_syms or ()) and r["past"]]
    if pr:
        r = max(pr, key=lambda x: x["implied"])
        med = st.median(r["past"])
        title = "%s: options price a %.1f%% move, %.1fx the median of its last %d report days" % (
            r["sym"], r["implied"], r["implied"] / med, len(r["past"]))
    elif focus:
        r = focus[0]
        title = "%s reports %s: its last %d report days moved a median %.1f%% (%.1f%% to %.1f%%)" % (
            r["sym"], r["when"], len(r["past"]), st.median(r["past"]), min(r["past"]), max(r["past"]))
    else:
        title = "%d names report around %s" % (len(rows), short_day(session))
    vtxt = ("the options market's 1-day move from the %s close" % ", ".join(sorted(used_vol))) if used_vol else \
        "none yet (the price covering each report sets at the close before it)"
    sub = ("Reports touching the %s session. Past report-day moves are absolute; implied move: %s." %
           (short_day(session), vtxt))
    C.earnings_strip(out_dir / fname, rows, title=title, subtitle=sub,
                     callout="Implied moves are market prices, not our forecast. Gap chance: share of 10%+ open "
                             "gaps over a year (both halves); direction is a coin flip.",
                     footer_right="Skylit moves list %s; implied move: Skylit vol %s" %
                                  (session, ", ".join(sorted(used_vol)) or "none yet"),
                     snapshot=snapshot_txt, session_label=short_day(session).upper())
    doc.img(out_dir / fname, title + ".")
    return rows


# ================================================================ editions
def preclose(a, out_dir):
    date = a.date
    asof = a.asof or "1545"
    now = D.load_live(date, asof)
    am = D.load_live(date, "0930")
    if now is None or am is None:
        sys.exit("no live maps for %s" % date)
    asof_dt = now.slot_et
    snap_txt = et_label(asof_dt)
    m, m0 = now["SPXW"], am["SPXW"]
    nxt = [e for e in m.expiries if e > date][0]
    events = D.load_events(date, asof_dt)
    path = D.spot_path(date, "SPXW", asof)
    vpath = D.spot_path(date, "VIX", asof)
    prev = m.prev_close
    vol_prev = D.load_vol_daily(str(D.prev_weekday(date)))
    em_today = vol_prev["symbols"]["SPXW"]["em_1d_pct"] if vol_prev else None
    band = S.morning_band(m0, date)
    hist = S.build_history()
    rec = S.band_record(hist, before=date)

    hi_t, hi_p = max(path, key=lambda x: x[1])
    lo_t, lo_p = min(path, key=lambda x: x[1])
    now_p = path[-1][1]
    chg = pct(now_p, prev)
    vix_open, vix_now = vpath[0][1], vpath[-1][1]
    vix_hi_t, vix_hi = max(vpath, key=lambda x: x[1])
    exit_t = None
    if band:
        for t, p in path:
            if not (band[0] <= p <= band[1]):
                exit_t = (t, p)
                break
        sc_log_band(date, band, m0.spot, et_label(am.slot_et), "preclose (09:30 map, logged on build)")
    inside_now = band and band[0] <= now_p <= band[1]

    title = "US market update · %s · before the close (%s ET)" % (D.d_(date).strftime("%A %d %B %Y"),
                                                                            hm(asof_dt))
    deck = ("SPX %s %.2f%% at %s with the VIX at %.2f; tomorrow's book changed under the price." %
            ("down" if chg < 0 else "up", abs(chg), L(now_p, 2), vix_now))
    doc = Doc(title, deck)
    events_section(doc, events)
    doc.mark()

    # --- what happened today
    doc.h("What happened today")
    em_txt = (" Options had priced a ±%.2f%% day from the prior close; the move so far is %.2f%%, %s that." %
              (em_today, abs(chg), "inside" if abs(chg) <= em_today else "beyond")) if em_today else ""
    if band:
        verdict = ("still inside it (provisional until the close)" if inside_now else
                   "outside it at %s" % hm(asof_dt))
        band_txt = ("This morning's map put the band between %s and %s, the largest long-gamma same-day strikes "
                    "either side of the %s open. Our logged base case was a close inside that band. Price left the "
                    "band at %s (%s) and is %s." % (L(band[0]), L(band[1]), L(m0.spot, 2),
                                                    hm(exit_t[0]) if exit_t else "-", L(exit_t[1], 2) if exit_t else "-",
                                                    verdict))
    else:
        band_txt = "This morning's map had no long-gamma strike on one side of the open, so no band was logged."
    doc.p("SPX opened at %s, made its high of %s at %s and its low of %s at %s, and stands at %s (%s%.2f%% on the "
          "prior close of %s). The VIX went from %.2f at the open to a %.2f high at %s and %.2f now.%s" %
          (L(m0.spot, 2), L(hi_p, 2), hm(hi_t), L(lo_p, 2), hm(lo_t), L(now_p, 2), "+" if chg >= 0 else MINUS,
           abs(chg), L(prev, 2), vix_open, vix_hi, hm(vix_hi_t), vix_now, em_txt))
    doc.p(band_txt)
    col0 = m0.col(date)
    f1 = "01_spx_today_on_morning_map.png"
    res = C.levels_ladder(
        out_dir / f1, m0, col0,
        title=("SPX left the 09:30 band at %s; the low was %s at %s" % (hm(exit_t[0]), L(lo_p, 2), hm(lo_t))
               if exit_t and lo_p < band[0] else
               "SPX today on the 09:30 map: high %s at %s, low %s at %s" % (L(hi_p, 2), hm(hi_t), L(lo_p, 2),
                                                                         hm(lo_t))),
        subtitle="1-minute SPX samples on this morning's same-day (%s) dealer-gamma map. Prior close %s, now %s "
                 "(%s%.2f%%). VIX %.2f → %.2f." % (short_day(date), L(prev, 2), L(now_p, 2),
                                                      "+" if chg >= 0 else MINUS, abs(chg), vix_open, vix_now),
        tag=("SPX TODAY ON THE 09:30 MAP", "white"), callout=RECORD["gamma_sign"],
        footer_right="Skylit SPXW map 09:30 ET (same-day expiry); SPX spot 1-min samples to %s ET" % hm(asof_dt),
        snapshot=snap_txt, unit_note="Skylit gamma units", window_pct=0.02, path=path, prev_close=prev,
        last_label="now", mini=[("same-day gamma", col0)], morning_band=band[:2] if band else None,
        roles={band[0]: "band floor", band[1]: "band top"} if band else None, must=band[:2] if band else ())
    doc.img(out_dir / f1, "SPX today on this morning's map: high %s at %s, low %s at %s, now %s." %
            (L(hi_p, 2), hm(hi_t), L(lo_p, 2), hm(lo_t), L(now_p, 2)))

    # --- tomorrow's expiry, this morning vs now
    b = np.array([m0.col(nxt)[list(m0.strikes).index(k)] if k in set(m0.strikes) else 0.0 for k in m.strikes])
    n_ = m.col(nxt)
    w3 = np.abs(m.strikes / now_p - 1) <= 0.03
    up3 = (m.strikes > now_p) & w3
    net_b, net_n = float(b[w3].sum()), float(n_[w3].sum())
    upb, upn = float(b[up3].sum()), float(n_[up3].sum())
    ch = n_ - b
    gain_i, loss_i = int(np.argmax(np.where(w3, ch, -np.inf))), int(np.argmin(np.where(w3, ch, np.inf)))
    doc.h("%s's expiry: this morning vs now" % day_name(nxt))
    doc.p("Net dealer gamma on the %s expiry within 3%% of the price went from %s at 09:30 to %s now; above the price "
          "it went from %s to %s. The biggest gain was at %s (%s → %s) and the biggest loss at %s (%s → %s). "
          "A book that turns net short above the price means fewer brakes in that direction; our tests could not "
          "turn that into a forecast." % (short_day(nxt), F(net_b), F(net_n), F(upb), F(upn), L(m.strikes[gain_i]),
                                         F(b[gain_i]), F(n_[gain_i]), L(m.strikes[loss_i]), F(b[loss_i]),
                                         F(n_[loss_i])))
    f2 = "02_next_expiry_morning_vs_now.png"
    C.before_after(out_dir / f2, m.strikes, b, n_, now_p,
                   title="%s's expiry: net gamma above the price went %s → %s" % (day_name(nxt), F(upb), F(upn)),
                   subtitle="Dealer gamma by strike on the %s expiry, 09:30 (grey) vs %s ET (colour). Net within "
                            "±3%%: %s → %s." % (short_day(nxt), hm(asof_dt), F(net_b), F(net_n)),
                   callout=RECORD["change"], footer_right="Skylit SPXW maps 09:30 and %s ET, %s expiry" %
                                                          (hm(asof_dt), nxt),
                   snapshot=snap_txt, label_before="09:30", label_now=hm(asof_dt), window_pct=0.03)
    doc.img(out_dir / f2, "%s's expiry, 09:30 vs %s: net within 3%% %s → %s; above the price %s → %s." %
            (day_name(nxt), hm(asof_dt), F(net_b), F(net_n), F(upb), F(upn)))

    # --- the map across expiries (heatmap layer)
    exps = [e for e in m.expiries if e > date]
    cols = [m.expiries.index(e) for e in exps]
    M = m.matrix[:, cols]
    doc.h("The map across expiries")
    f3 = "03_spx_strike_expiry_heatmap.png"
    hres = C.gamma_heatmap(out_dir / f3, m.strikes, exps, M, now_p,
                           title="SPX book after today: the largest cell is %s on %s",
                           subtitle="", callout=RECORD["heat"], footer_right="", snapshot=snap_txt)
    kk, ke, kv = hres["king"]
    near = float(M[np.abs(m.strikes / now_p - 1) <= 0.01].sum())
    C.gamma_heatmap(out_dir / f3, m.strikes, exps, M, now_p,
                    title="SPX book after today: the largest cell is %s on %s (%s)" % (L(kk), short_day(ke), F(kv)),
                    subtitle="Dealer gamma by strike and expiry at %s ET, today's expiring column left out. Net within "
                             "±1%% of %s across the %d expiries: %s." % (hm(asof_dt), L(now_p, 2), len(exps),
                                                                             F(near)),
                    callout=RECORD["heat"], footer_right="Skylit SPXW map %s ET, expiries %s to %s" %
                                                         (hm(asof_dt), exps[0], exps[-1]),
                    snapshot=snap_txt, unit_note="Skylit units.", window_pct=0.02)
    doc.p("Leaving out today's expiring column, the biggest single cell in the book is %s on the %s expiry (%s). "
          "Net gamma within 1%% of the price across the %d remaining expiries is %s, so dealers are net %s gamma "
          "around the price going into the night." % (L(kk), short_day(ke), F(kv), len(exps), F(near),
                                                       "long" if near > 0 else "short"))
    doc.img(out_dir / f3, "SPX dealer gamma by strike and expiry at %s ET; largest cell %s on %s (%s)." %
            (hm(asof_dt), L(kk), short_day(ke), F(kv)))

    # --- tomorrow's map (levels)
    doc.h("%s's map as it stands" % day_name(nxt))
    f4 = "04_next_expiry_levels.png"
    rest = [e for e in m.expiries if e > date]
    lres = C.levels_ladder(
        out_dir / f4, m, n_,
        title="%s's expiry as it stands" % day_name(nxt), subtitle="", tag=("%s EXPIRY LEVELS" %
                                                                           short_day(nxt).upper(), "cyan"),
        callout=RECORD["node"], footer_right="", snapshot=snap_txt, unit_note="Skylit gamma units",
        window_pct=0.025, last=now_p, prev_close=None, mini=[("%s gamma" % short_day(nxt), n_),
                                                             ("all %d expiries" % len(rest), m.rowsum(rest))])
    lv = lres["levels"]
    pos = [x for x in lv if x[1] > 0]
    big = max(pos, key=lambda x: x[1]) if pos else max(lv, key=lambda x: abs(x[1]))
    below_neg = [x for x in lv if x[0] < now_p and x[1] < 0]
    above_pos = [x for x in lv if x[0] > now_p and x[1] > 0]
    title4 = "%s's expiry: %s is the largest long-gamma strike (%s)" % (day_name(nxt), L(big[0]), F(big[1]))
    sub4 = ("Dealer gamma by strike on the %s expiry at %s ET; price %s. Levels in cash index points." %
            (short_day(nxt), hm(asof_dt), L(now_p, 2)))
    C.levels_ladder(out_dir / f4, m, n_, title=title4, subtitle=sub4,
                    tag=("%s EXPIRY LEVELS" % short_day(nxt).upper(), "cyan"), callout=RECORD["node"],
                    footer_right="Skylit SPXW map %s ET, %s expiry; mini columns: that expiry and all %d" %
                                 (hm(asof_dt), nxt, len(rest)),
                    snapshot=snap_txt, unit_note="Skylit gamma units", window_pct=0.025, last=now_p,
                    mini=[("%s gamma" % short_day(nxt), n_), ("all %d expiries" % len(rest), m.rowsum(rest))])
    txt = "On the %s expiry the largest long-gamma strike is %s (%s)." % (short_day(nxt), L(big[0]), F(big[1]))
    if below_neg:
        bn = max(below_neg, key=lambda x: x[0])
        txt += " Below the price, %s is short gamma (%s): the book offers less damping under it." % (L(bn[0]),
                                                                                                    F(bn[1]))
    if above_pos:
        txt += " Above, the long-gamma strikes are %s." % ", ".join("%s (%s)" % (L(k), F(v)) for k, v in above_pos)
    doc.p(txt + " These describe positioning at %s; the overnight edition re-reads them at 17:30 ET." % hm(asof_dt))
    doc.img(out_dir / f4, title4 + ".")

    # --- VIX
    vix_block(doc, out_dir, "05_vix_levels.png", now["VIX"], snap_txt, "Skylit VIX map %s ET" % hm(asof_dt))

    # --- single names and earnings
    tickers = [t.strip().upper() for t in (a.tickers or "NVDA").split(",") if t.strip()]
    session_next = str(D.next_weekday(date))
    releases = {}
    for r in D.load_earnings(session_next)["rows"] + D.load_earnings(date)["rows"]:
        rt = D.release_time(r)
        if rt and r["sym"] in tickers and rt >= dt.datetime.combine(D.d_(date), dt.time(0), tzinfo=D.ET):
            releases[r["sym"]] = rt
    doc.h("Single names into tonight's reports")
    notes = single_names(doc, out_dir, date, tickers, asof + "00", date, releases, snap_txt, "06")
    erows = earnings_block(doc, out_dir, "07_earnings_strip.png", session_next, vol_prev, snap_txt, asof_dt, tickers)
    if erows:
        rr = [r for r in erows if r["implied"]]
        if rr:
            r = rr[0]
            doc.p("%s's options price a %.1f%% move against a median of %.1f%% on its last %d report days. That ratio "
                  "is a market price, not our forecast; we log realised against implied after each report." %
                  (r["sym"], r["implied"], st.median(r["past"]), len(r["past"])))
    for n in notes:
        doc.small(n)

    # --- routes
    doc.h("Routes into %s" % day_name(session_next))
    rows = D.load_vol_history("SPXW")
    rates = S.route_rates([r for r in rows if r[0] < date], today_svx30=vix_now)
    em = em_today or rates["all"]["abs_med"]
    use, cond_txt = route_block(doc, out_dir, "08_routes.png", label_day="%s %s" % (day_name(date), hm(asof_dt)),
                                close_txt="SPX %s · VIX %.2f · %s priced ±%.2f%% (%s's prices set at the close)" %
                                          (L(now_p, 2), vix_now, day_name(date), em, day_name(session_next)),
                                vix_now=vix_now, em=em, rates=rates,
                                title_suffix="Into %s" % day_name(session_next), snapshot=snap_txt,
                                event_note="Report-night odds (Nvidia tonight): no measured odds; we hold no "
                                           "report-night sample.")
    doc.p("In %d past %s, the next close landed inside the priced move %.0f%% of the time, beyond it on the upside "
          "%.0f%% and on the downside %.0f%%. These are shares of past sessions with their n, not a forecast, and they "
          "do not condition on tonight's report. Direction stays a no-call." %
          (use["n"], cond_txt, use["inside"], use["up"], use["down"]))

    # --- what would change the picture
    doc.h("What would change the picture")
    items = []
    if big:
        items.append("The overnight map (17:30 ET) moves the largest long-gamma strike on the %s expiry away from %s, "
                     "or its size falls below half of %s." % (short_day(nxt), L(big[0]), F(big[1])))
    items.append("Net gamma above the price on the %s expiry turns back positive (now %s)." % (short_day(nxt),
                                                                                              F(upn)))
    items.append("The VIX closes back under %.0f (now %.2f): the vol-bracket base rates above would then be read from "
                 "a different bucket." % (np.floor(vix_now) - 2, vix_now))
    doc.bullets(items)
    watch_section(doc, events)

    # --- key calls (inserted after the event lead)
    kc = []
    if band:
        kc.append(["Base case logged at 09:30: SPX closes inside %s-%s" % (L(band[0]), L(band[1])),
                   "%.0f%% of %d past sessions" % (rec["real_pct"], rec["n"]) if rec else "no record yet",
                   "%s 16:00 ET" % short_day(date),
                   "a 16:00 close outside the band (now %s: %s)" % (L(now_p, 2), "inside" if inside_now else "outside")])
    kc.append(["%s's close lands inside its priced 1-day move" % day_name(session_next),
               "%.0f%% of %d past sessions" % (use["inside"], use["n"]), "%s 16:00 ET" % short_day(session_next),
               "a close-to-close move beyond the priced move (set at today's close)"])
    kc.append(["Direction of SPX into %s" % day_name(session_next), "No call", "n/a", "n/a"])
    doc.insert_key_calls(kc, "SPX is %s%.2f%% at %s. This morning's band %s, and %s's book lost most of its long "
                             "gamma above the price (%s → %s). Odds below are measured base rates with their n; "
                             "direction is a no-call." % ("+" if chg >= 0 else MINUS, abs(chg), L(now_p, 2),
                                                          "broke at %s" % hm(exit_t[0]) if exit_t else "is holding",
                                                          day_name(nxt), F(upb), F(upn)))

    # --- record
    doc.h("Our record")
    hit, nsc = sc_tally(str(D.prev_weekday(date)))
    doc.box(band_record_line(rec) + (" Logged editions so far: %d of %d morning bands held the close." % (hit, nsc)
                                     if nsc else " No logged edition has been scored yet."))
    doc.p("Bootstrap 95%% interval for the gap between the band and its mirror: %+.1f to %+.1f points. It is "
          "in-sample and was not pre-registered, so it stays a lead, not a rule. Our other measured results are "
          "null: the largest node as a magnet (46.7%% vs mirror, n = 165), the gamma-sign range test (1.28 / 0.96 / "
          "0.80) and vanna splits at chance (12 of 42)." % rec["diff_ci"] if rec else "No band record yet.")
    return doc, now, asof_dt


def vix_block(doc, out_dir, fname, v, snap_txt, src):
    vals = v.rowsum()
    w = np.abs(v.strikes / v.spot - 1) <= 0.3
    kn = v.strikes[w][np.argmin(vals[w])]
    kp = v.strikes[w][np.argmax(vals[w])]
    near = float(vals[np.abs(v.strikes / v.spot - 1) <= 0.1].sum())
    title = "VIX %.2f: dealers net %s gamma near spot (%s); largest short strike %s" % (
        v.spot, "long" if near > 0 else "short", F(near), L(kn, 1))
    sub = ("Dealer gamma on VIX options by strike, summed over the %d listed expiries %s to %s. Largest long strike "
           "%s (%s), largest short %s (%s)." % (len(v.expiries), v.expiries[0], v.expiries[-1], L(kp, 1),
                                               F(vals[list(v.strikes).index(kp)]), L(kn, 1),
                                               F(vals[list(v.strikes).index(kn)])))
    doc.h("VIX positioning")
    C.levels_ladder(out_dir / fname, v, vals, title=title, subtitle=sub, tag=("VIX LEVELS", "orange"),
                    callout=RECORD["vix"], footer_right="%s, %d expiries summed" % (src, len(v.expiries)),
                    snapshot=snap_txt, unit_note="Skylit gamma units", window_pct=0.3, max_levels=7, decimals=1,
                    last=v.spot, prev_close=v.prev_close, min_gap_pct=0.035, min_frac=0.12,
                    mini=[("all expiries", vals)])
    doc.p("Across all listed VIX expiries dealers are net %s gamma within 10%% of the VIX (%s). The largest short-gamma "
          "strike is %s and the largest long-gamma strike %s. %s We hold no tested rule for VIX positioning, so it "
          "is context." % ("long" if near > 0 else "short", F(near), L(kn, 1), L(kp, 1),
                           "In principle net long VIX gamma near spot damps the VIX's own moves."
                           if near > 0 else "In principle net short VIX gamma near spot lets a vol spike feed "
                                            "itself."))
    doc.img(out_dir / fname, title + ".")


def overnight(a, out_dir):
    date = a.date or D.latest_overnight_date()
    snap = D.load_overnight(date)
    if snap is None:
        sys.exit("no overnight map for %s" % date)
    asof_dt = snap.slot_et
    snap_txt = et_label(asof_dt)
    m = snap["SPXW"]
    nxt = m.expiries[0]
    events = D.load_events(date, asof_dt)
    vol = D.load_vol_daily(date)
    close = vol["symbols"]["SPXW"]["close"] if vol else None
    em = vol["symbols"]["SPXW"]["em_1d_pct"] if vol else None
    svx = vol["symbols"]["SPXW"]["svx30"] if vol else None
    path = D.spot_path(date, "SPXW", "1600")
    vpath = D.spot_path(date, "VIX", "1600")
    prev = m.prev_close
    hi_t, hi_p = max(path, key=lambda x: x[1])
    lo_t, lo_p = min(path, key=lambda x: x[1])
    close = close or path[-1][1]
    chg = pct(close, prev)
    vix_close = vpath[-1][1] if vpath else None
    am = D.load_live(date, "0930")
    band = S.morning_band(am["SPXW"], date) if am else None
    if band:
        sc_log_band(date, band, am["SPXW"].spot, et_label(am.slot_et), "overnight (09:30 map, logged on build)")
    scored = sc_score(date)
    hist = S.build_history()
    rec = S.band_record(hist, before=str(D.next_weekday(date)))

    title = "US market update · overnight into %s (map %s ET)" % (D.next_weekday(date).strftime("%A %d %B %Y"),
                                                                      hm(asof_dt))
    deck = ("SPX closed %s%.2f%% at %s; options price ±%.2f%% for %s." %
            ("+" if chg >= 0 else MINUS, abs(chg), L(close, 2), em, day_name(nxt)) if em else
            "SPX closed at %s." % L(close, 2))
    doc = Doc(title, deck)
    events_section(doc, events)
    doc.mark()

    doc.h("How the day closed, and how this morning's map scored")
    doc.p("SPX closed at %s (%s%.2f%% on %s), after a high of %s at %s and a low of %s at %s. The VIX finished at "
          "%.2f." % (L(close, 2), "+" if chg >= 0 else MINUS, abs(chg), L(prev, 2), L(hi_p, 2), hm(hi_t), L(lo_p, 2),
                     hm(lo_t), vix_close or float("nan")))
    if scored:
        res = scored["outcome"]
        doc.p("Score: this morning's base case was a close inside the %s-%s band from the 09:30 map. The 16:00 sample "
              "was %s, %s the band. %s" % (L(float(scored["band_lo"])), L(float(scored["band_hi"])),
                                            L(float(scored["close"]), 2),
                                            "inside" if res == "inside" else res + " (outside)",
                                            "A hit." if res == "inside" else
                                            "A miss: the band described where gamma sat at the open, and price left "
                                            "it once the morning's long-gamma strikes were behind it."))
    # overnight ladder
    rows = D.load_vol_history("SPXW")
    rates = S.route_rates([r for r in rows if r[0] <= date], today_svx30=svx)
    c = rates.get("cond") or rates["all"]
    col = m.col(nxt)
    rest = m.expiries
    fut_d = D.latest_futures_date(date)
    basis_txt = ""
    if fut_d:
        fu = D.load_futures(fut_d, "ES")
        hcl = hist.get(fut_d, {}) or {}
        b16 = [b for b in fu["bars"] if b[0].hour == 16 and b[0].minute == 0]
        if b16 and hcl.get("close"):
            basis = b16[0][4] - hcl["close"]
            lag = D.weekdays_between(fut_d, date)
            basis_txt = (" Futures traded about %.0f points %s cash at the %s close (front ES contract; %s)." %
                         (abs(basis), "above" if basis >= 0 else "below", D.d_(fut_d).strftime("%d %b"),
                          "same day" if lag == 0 else "STALE: our bars end T-%d" % lag))
    lb = C.levels_ladder(out_dir / "01_overnight_map.png", m, col, title="x", subtitle="", tag=("X", "cyan"),
                         callout="", footer_right="", snapshot="", unit_note="", window_pct=0.025, last=m.spot)
    lv = lb["levels"]
    pos = [x for x in lv if x[1] > 0]
    big = max(pos, key=lambda x: x[1]) if pos else max(lv, key=lambda x: abs(x[1]))
    below = sorted([x for x in lv if x[0] < m.spot], key=lambda x: -x[0])
    above = sorted([x for x in lv if x[0] > m.spot], key=lambda x: x[0])
    table = ("Next close vs the priced move\npast sessions with\nVIX-like vol %.0f-%.0f" % rates["cond_band"]) if \
        rates.get("cond") else "Next close vs the priced move\nall past sessions"
    side = (table, [("inside ±%.2f%%: %.0f%%" % (em, c["inside"]), "n = %d sessions" % c["n"], "yellow"),
                    ("beyond, up: %.0f%%" % c["up"], "%d of %d" % (c["n_up"], c["n"]), "green"),
                    ("beyond, down: %.0f%%" % c["down"], "%d of %d" % (c["n_down"], c["n"]), "red"),
                    ("all sessions", "inside %.0f%% of %d\nup %.0f%% · down %.0f%%" %
                     (rates["all"]["inside"], rates["all"]["n"], rates["all"]["up"], rates["all"]["down"]),
                     "subtitle")])
    title1 = "Overnight into %s: %s is the largest long-gamma strike (%s)" % (day_name(nxt), L(big[0]), F(big[1]))
    sub1 = ("Dealer gamma by strike on the %s expiry, overnight map %s ET; map spot %s, close %s. Levels in cash "
            "index points." % (short_day(nxt), hm(asof_dt), L(m.spot, 2), L(close, 2)))
    C.levels_ladder(out_dir / "01_overnight_map.png", m, col, title=title1, subtitle=sub1,
                    tag=("OVERNIGHT MAP · %s EXPIRY" % short_day(nxt).upper(), "cyan"), callout=RECORD["overnight"],
                    footer_right="Skylit SPXW overnight map %s ET, %s expiry; vol history to %s" %
                                 (hm(asof_dt), nxt, date),
                    snapshot=snap_txt, unit_note="Skylit gamma units", window_pct=0.025, last=m.spot,
                    last_label="map spot", prev_close=None, mini=[("%s gamma" % short_day(nxt), col)], side_table=side)
    doc.h("The overnight map")
    txt = "Levels are cash.%s On the %s expiry the largest long-gamma strike is %s (%s)." % (basis_txt,
                                                                                              short_day(nxt),
                                                                                              L(big[0]), F(big[1]))
    if below:
        txt += " Below the map spot of %s the drawn strikes are %s." % (L(m.spot, 2), ", ".join(
            "%s (%s)" % (L(k), F(v)) for k, v in below[:3]))
    if above:
        txt += " Above it: %s." % ", ".join("%s (%s)" % (L(k), F(v)) for k, v in above[:4])
    doc.p(txt + " Our overnight node rule did not survive its holdout, so these are positioning, not stopping points.")
    doc.img(out_dir / "01_overnight_map.png", title1 + ".")

    # heatmap
    M = m.matrix
    f2 = "02_spx_strike_expiry_heatmap.png"
    h = C.gamma_heatmap(out_dir / f2, m.strikes, m.expiries, M, m.spot, title="x", subtitle="", callout="",
                        footer_right="", snapshot="")
    kk, ke, kv = h["king"]
    near = float(M[np.abs(m.strikes / m.spot - 1) <= 0.01].sum())
    C.gamma_heatmap(out_dir / f2, m.strikes, m.expiries, M, m.spot,
                    title="SPX overnight book: the largest cell is %s on %s (%s)" % (L(kk), short_day(ke), F(kv)),
                    subtitle="Dealer gamma by strike and expiry, overnight map %s ET. Net within ±1%% of %s "
                             "across the %d expiries: %s." % (hm(asof_dt), L(m.spot, 2), len(m.expiries), F(near)),
                    callout=RECORD["heat"], footer_right="Skylit SPXW overnight map %s ET, expiries %s to %s" %
                                                         (hm(asof_dt), m.expiries[0], m.expiries[-1]),
                    snapshot=snap_txt, unit_note="Skylit units.")
    doc.h("The map across expiries")
    doc.p("Across the next %d expiries the biggest cell is %s on %s (%s); net gamma within 1%% of the price is %s, so "
          "dealers are net %s gamma around the price into the open." % (len(m.expiries), L(kk), short_day(ke),
                                                                         F(kv), F(near),
                                                                         "long" if near > 0 else "short"))
    doc.img(out_dir / f2, "SPX dealer gamma by strike and expiry, overnight map %s ET." % hm(asof_dt))

    # this morning vs tonight for the next expiry
    if am:
        m0 = am["SPXW"]
        b = np.array([m0.col(nxt)[list(m0.strikes).index(k)] if (m0.col(nxt) is not None and k in set(m0.strikes))
                      else 0.0 for k in m.strikes])
        w3 = np.abs(m.strikes / m.spot - 1) <= 0.03
        up3 = (m.strikes > m.spot) & w3
        f3 = "03_next_expiry_morning_vs_tonight.png"
        C.before_after(out_dir / f3, m.strikes, b, col, m.spot,
                       title="%s's expiry since this morning: net within 3%% %s → %s" %
                             (day_name(nxt), F(float(b[w3].sum())), F(float(col[w3].sum()))),
                       subtitle="Dealer gamma by strike on the %s expiry, 09:30 (grey) vs overnight %s ET (colour). "
                                "Above the price: %s → %s." % (short_day(nxt), hm(asof_dt),
                                                                   F(float(b[up3].sum())), F(float(col[up3].sum()))),
                       callout=RECORD["change"], footer_right="Skylit SPXW maps 09:30 and overnight %s ET, %s expiry"
                                                              % (hm(asof_dt), nxt),
                       snapshot=snap_txt, label_before="09:30", label_now="overnight", window_pct=0.025)
        doc.h("%s's expiry: this morning vs tonight" % day_name(nxt))
        doc.p("Net gamma on the %s expiry within 3%% of the price went from %s this morning to %s tonight; above the "
              "price from %s to %s." % (short_day(nxt), F(float(b[w3].sum())), F(float(col[w3].sum())),
                                        F(float(b[up3].sum())), F(float(col[up3].sum()))))
        doc.img(out_dir / f3, "%s's expiry, 09:30 vs overnight." % day_name(nxt))

    vix_block(doc, out_dir, "04_vix_levels.png", snap["VIX"], snap_txt, "Skylit VIX overnight map %s ET" %
              hm(asof_dt))

    tickers = [t.strip().upper() for t in (a.tickers or "NVDA,MU").split(",") if t.strip()]
    session_next = str(D.next_weekday(date))
    releases = {}
    for r in D.load_earnings(session_next)["rows"]:
        rt = D.release_time(r)
        if rt and r["sym"] in tickers:
            releases[r["sym"]] = rt
    doc.h("Single names")
    notes = single_names(doc, out_dir, date, tickers, "235959", date, releases, snap_txt, "05")
    for n in notes:
        doc.small(n)
    erows = earnings_block(doc, out_dir, "07_earnings_strip.png", session_next, vol, snap_txt, asof_dt, tickers)
    if erows:
        rr = [r for r in erows if r["implied"]]
        if rr:
            r = rr[0]
            doc.p("%s reported after the close; its options had priced a %.1f%% move against a median %.1f%% on its "
                  "last %d report days. We log the realised move against that price after %s's close." %
                  (r["sym"], r["implied"], st.median(r["past"]), len(r["past"]), day_name(nxt)))

    doc.h("Routes into %s" % day_name(nxt))
    use, cond_txt = route_block(doc, out_dir, "08_routes.png", label_day="%s close" % day_name(date),
                                close_txt="SPX %s · VIX %.2f · options price ±%.2f%% for %s" %
                                          (L(close, 2), vix_close, em, day_name(nxt)),
                                vix_now=svx, em=em, rates=rates, title_suffix="Into %s" % day_name(nxt),
                                snapshot=snap_txt,
                                event_note="Report-night odds: no measured odds; we hold no report-night sample. "
                                           "Direction is a no-call.")
    doc.p("In %d past %s the next close landed inside the priced ±%.2f%% %.0f%% of the time; beyond it up "
          "%.0f%%, down %.0f%%. Shares of past sessions, not a forecast." % (use["n"], cond_txt, em, use["inside"],
                                                                            use["up"], use["down"]))
    watch_section(doc, events)
    kc = []
    if scored:
        kc.append(["Today's base case: SPX closed inside %s-%s" % (L(float(scored["band_lo"])),
                                                                  L(float(scored["band_hi"]))),
                   "%.0f%% of %d past sessions" % (rec["real_pct"], rec["n"]) if rec else "no record yet",
                   "scored at 16:00 ET", "%s (close %s)" % ("HIT" if scored["outcome"] == "inside" else "MISS",
                                                          L(float(scored["close"]), 2))])
    kc.append(["%s's close lands inside the priced ±%.2f%%" % (day_name(nxt), em),
               "%.0f%% of %d past sessions" % (use["inside"], use["n"]), "%s 16:00 ET" % short_day(nxt),
               "a close beyond %s or %s" % (L(close * (1 + em / 100), 0), L(close * (1 - em / 100), 0))])
    kc.append(["Direction of SPX into %s" % day_name(nxt), "No call", "n/a", "n/a"])
    doc.insert_key_calls(kc, "SPX closed %s%.2f%% at %s. Options price ±%.2f%% for %s; in %d similar past sessions "
                             "the next close stayed inside the priced move %.0f%% of the time. Direction is a no-call."
                         % ("+" if chg >= 0 else MINUS, abs(chg), L(close, 2), em, day_name(nxt), use["n"],
                            use["inside"]))
    doc.h("Our record")
    hit, nsc = sc_tally(date)
    doc.box(band_record_line(rec) + (" Logged editions so far: %d of %d morning bands held the close." % (hit, nsc)
                                     if nsc else " No logged edition has been scored yet."))
    if rec:
        doc.p("Bootstrap 95%% interval for the band-minus-mirror gap: %+.1f to %+.1f points; in-sample, not "
              "pre-registered, so a lead only. The overnight node rule was null on ~370 unseen nights." %
              rec["diff_ci"])
    return doc, snap, asof_dt


def morning(a, out_dir):
    date = a.date
    am = D.load_live(date, "0930")
    if am is None:
        sys.exit("no 09:30 map for %s yet: the morning edition needs the first live map of the session" % date)
    asof_dt = am.slot_et
    snap_txt = et_label(asof_dt)
    m = am["SPXW"]
    prevd = str(D.prev_weekday(date))
    events = D.load_events(date, asof_dt) + D.load_events(prevd, asof_dt)
    vol_prev = D.load_vol_daily(prevd)
    em = vol_prev["symbols"]["SPXW"]["em_1d_pct"] if vol_prev else None
    col = m.col(date)
    band = S.morning_band(m, date)
    title = "US market update · %s · morning (09:30 ET map)" % D.d_(date).strftime("%A %d %B %Y")
    doc = Doc(title, "SPX opened at %s against a prior close of %s." % (L(m.spot, 2), L(m.prev_close, 2)))
    events_section(doc, events)
    doc.h("Overnight")
    on = D.load_overnight(prevd)
    if on:
        g = pct(m.spot, on["SPXW"].spot)
        doc.p("Last night's map put SPX at %s at %s; it opened at %s, %s%.2f%% from there." %
              (L(on["SPXW"].spot, 2), on.label, L(m.spot, 2), "+" if g >= 0 else MINUS, abs(g)))
    doc.small("Overnight futures path: GAP. Our ES/NQ bars cover 06:00-16:14 ET only and lag the live maps.")
    doc.h("Today's map")
    if band:
        sid = sc_log_band(date, band, m.spot, et_label(asof_dt), "morning")
        doc.p("Base case logged (%s): SPX closes inside %s-%s, the largest long-gamma same-day strikes either side of "
              "the open. Scored at the close." % (sid, L(band[0]), L(band[1])))
    f1 = "01_today_map.png"
    C.levels_ladder(out_dir / f1, m, col, title="Today's map: band %s-%s around the %s open" %
                    (L(band[0]), L(band[1]), L(m.spot, 2)) if band else "Today's map at the open",
                    subtitle="Same-day dealer gamma by strike, 09:30 ET.%s" %
                             (" Options priced ±%.2f%% for today." % em if em else ""),
                    tag=("SPX TODAY'S MAP", "cyan"), callout=RECORD["node"],
                    footer_right="Skylit SPXW map 09:30 ET, %s expiry" % date, snapshot=snap_txt,
                    unit_note="Skylit gamma units", window_pct=0.02, prev_close=m.prev_close,
                    mini=[("same-day gamma", col), ("all 5 expiries", m.rowsum())],
                    roles={band[0]: "band floor", band[1]: "band top"} if band else None,
                    must=band[:2] if band else ())
    doc.img(out_dir / f1, "Today's same-day map at 09:30 ET.")
    vix_block(doc, out_dir, "02_vix_levels.png", am["VIX"], snap_txt, "Skylit VIX map 09:30 ET")
    tickers = [t.strip().upper() for t in (a.tickers or "").split(",") if t.strip()]
    if tickers:
        doc.h("Single names")
        notes = single_names(doc, out_dir, prevd, tickers, "235959", date, {}, snap_txt, "03")
        for n in notes:
            doc.small(n)
    earnings_block(doc, out_dir, "05_earnings_strip.png", date, vol_prev, snap_txt, asof_dt)
    rows = D.load_vol_history("SPXW")
    svx = vol_prev["symbols"]["SPXW"]["svx30"] if vol_prev else None
    rates = S.route_rates([r for r in rows if r[0] < date], today_svx30=svx)
    doc.h("Routes for today")
    route_block(doc, out_dir, "06_routes.png", label_day="%s open" % day_name(date),
                close_txt="SPX %s · priced ±%.2f%%" % (L(m.spot, 2), em or 0), vix_now=svx,
                em=em or rates["all"]["abs_med"], rates=rates, title_suffix="Today, %s" % day_name(date), snapshot=snap_txt)
    watch_section(doc, events)
    return doc, am, asof_dt


# ================================================================ main
def data_notes(edition, date, snap, asof_dt):
    notes = [
        "Index maps: Skylit per-minute gamma maps (5 expiries per symbol); spot is a 1-minute sample, so highs and "
        "lows are sampled, not exchange OHLC.",
        "Gamma values are Skylit's per-strike units; compare within one symbol only.",
        "Charm by strike: GAP (not in our Skylit maps). Index vanna (SPX/SPY/QQQ): GAP. Dealer net contracts: GAP.",
        "Overnight futures: ES/NQ bars cover 06:00-16:14 ET and end %s; the night-turn clock needs years of full "
        "overnight bars (GAP)." % (D.latest_futures_date(date) or "n/a"),
        "Macro calendar consensus and prior values: GAP. DXY, yields, metals panels: GAP.",
        "Never used: Unusual Whales data or cached option chains of unclear source.",
    ]
    if snap is not None:
        notes.insert(0, "Snapshot: %s (%s), %s." % (et_label(asof_dt), snap.kind, snap.stale_note or "fresh"))
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="session date YYYY-MM-DD (overnight: the map's date; default latest)")
    ap.add_argument("--edition", choices=["preclose", "morning", "overnight"])
    ap.add_argument("--asof", help="HHMM ET cut for the pre-close edition (default 1545)")
    ap.add_argument("--tickers", help="single names for heatmaps/vanna, e.g. NVDA,MU")
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    ap.add_argument("--score-only", action="store_true", help="score the morning band for --date at the close")
    a = ap.parse_args()
    if a.score_only:
        r = sc_score(a.date)
        print(r if r else "nothing to score for %s" % a.date)
        return
    if not a.edition:
        ap.error("--edition is required")
    if a.edition == "overnight" and not a.date:
        a.date = D.latest_overnight_date()
    cs.apply(a.theme)
    suffix = "" if a.theme == "dark" else "_light"
    out_dir = REPO / "reports" / "market_update" / ("%s_%s%s" % (a.date, a.edition, suffix))
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    doc, snap, asof_dt = {"preclose": preclose, "overnight": overnight, "morning": morning}[a.edition](a, out_dir)
    doc.h("Data and staleness")
    doc.bullets(data_notes(a.edition, a.date, snap, asof_dt))
    footer = ("GT-Analyst · data: Skylit maps %s · not investment advice. Levels describe dealer "
              "positioning, not targets; no trade, hedge or size is implied." % et_label(asof_dt))
    (out_dir / "update.md").write_text(doc.markdown(footer), encoding="utf-8")
    pdf = write_pdf(doc, out_dir, footer)
    dx = write_docx(doc, out_dir, footer)
    print("wrote", out_dir)
    for c in doc.charts:
        print("  chart", c)
    print("  update.md", "\n  ", pdf, "\n  ", dx or "docx skipped (python-docx not installed)")


if __name__ == "__main__":
    main()
