"""GT-Analyst house chart style for matplotlib (dark default, light variant for print).

This is the house style for every matplotlib chart in the repo. Usage:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(<repo>) / "tools"))
    from market_update import chartstyle as cs

    cs.apply("dark")                       # or "light" for printed reports
    fig, panels = cs.frame(
        title="Wednesday's expiry lost its 7,510/7,520 pair",      # the finding, with its number
        subtitle="Dealer gamma by strike, 09:30 vs 15:45 ET. Net within +-3%: +4.1M -> -2.3M.",
        panels=1, tags=[("GAMMA BY STRIKE", "cyan")],
        callout="Our record: ... (measured, with n)",               # yellow box = our measured record
        footer_right="Skylit SPXW map, 17 Nov 15:45 ET, 18 Nov expiry",
        snapshot="17 Nov 2026 15:45 ET")
    ax = cs.panel_axes(fig, panels[0])
    ...
    cs.save(fig, "out.png")                # 2x export (3000 px wide at the default size)

Grammar (one finding per chart): pure-black canvas, near-black rounded panel, two-line header outside the panel
(bold title stating the finding with its number, grey subtitle with the numbers), an uppercase letter-spaced
panel tag whose outline colour codes the panel type (cyan = gamma, purple = vanna/derived, orange = VIX/vol,
white = price/levels, yellow = scenarios), one green/red semantic used identically everywhere, no gridlines (a single
zero axis), labels on the extremes only, a yellow-outlined call-out box that states OUR MEASURED RECORD (never a
trade read), and a footer: our attribution and snapshot time on the left, the exact source string on the right.
No watermark. Never a trade, hedge, size, target or payoff chart.
"""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

# ---------------------------------------------------------------- palettes
DARK = {
    "canvas": "#000000",
    "panel": "#0a0a0a",
    "border": "#1f1f1f",
    "callout_fill": "#0e0e0e",
    "callout_border": "#ffd23f",
    "callout_text": "#f3dfa2",
    "title": "#ececec",
    "text": "#d6d6d6",
    "subtitle": "#a8a8a8",
    "muted": "#6f6f6f",
    "zero": "#3a3a3a",
    "free": "#141414",
    "green": "#2ec48a",
    "red": "#ff4d4f",
    "fast_heavy": "#581f20",
    "fast_light": "#3a1717",
    "slow_heavy": "#154533",
    "slow_light": "#0f271e",
    "cyan": "#19c3f0",
    "purple": "#b388ff",
    "orange": "#ff8c1a",
    "yellow": "#ffd23f",
    "white": "#f2f2f2",
    "price": "#f2f2f2",
    "node_green": "#06140f",
    "node_red": "#220707",
    "node_yellow": "#141204",
    "node_cyan": "#04181d",
    "node_grey": "#111111",
    "label_box": "#0a0a0a",
}
LIGHT = {
    "canvas": "#ffffff",
    "panel": "#f7f7f7",
    "border": "#dcdcdc",
    "callout_fill": "#fff8e1",
    "callout_border": "#d9a400",
    "callout_text": "#5c4300",
    "title": "#111111",
    "text": "#262626",
    "subtitle": "#555555",
    "muted": "#8a8a8a",
    "zero": "#bdbdbd",
    "free": "#ececec",
    "green": "#11905a",
    "red": "#d6343a",
    "fast_heavy": "#f4c6c7",
    "fast_light": "#fae3e3",
    "slow_heavy": "#c4e9d6",
    "slow_light": "#e4f5ec",
    "cyan": "#0a86ad",
    "purple": "#6f42c1",
    "orange": "#d96a00",
    "yellow": "#b58900",
    "white": "#111111",
    "price": "#111111",
    "node_green": "#e8f6ef",
    "node_red": "#fbeaea",
    "node_yellow": "#fbf5dc",
    "node_cyan": "#e3f4fa",
    "node_grey": "#f0f0f0",
    "label_box": "#f7f7f7",
}
P = dict(DARK)  # the active palette (mutated by apply())
THEME = {"name": "dark"}

FONT = "DejaVu Sans"
MONO = "DejaVu Sans Mono"   # house flair: every number we draw on a chart is set in the mono face
SIZES = {"title": 24, "subtitle": 13.5, "tag": 12, "label": 13, "small": 11, "tiny": 9.5, "callout": 14,
         "footer": 10.5, "level": 15}
DPI = 200            # 15 in x 200 dpi = 3000 px: the 2x export
DEFAULT_SIZE = (15, 9.375)   # 1.60 aspect
WIDE_SIZE = DEFAULT_SIZE      # two-panel charts use the same 3000 x 1875 frame so type sizes match


def apply(theme="dark"):
    """Set the house rcParams. theme = 'dark' (screens, email) or 'light' (printed reports)."""
    P.clear()
    P.update(DARK if theme == "dark" else LIGHT)
    THEME["name"] = theme
    matplotlib.rcParams.update({
        "font.family": FONT,
        "font.size": SIZES["label"],
        "text.color": P["text"],
        "axes.facecolor": "none",
        "axes.edgecolor": P["zero"],
        "axes.labelcolor": P["subtitle"],
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "xtick.color": P["subtitle"],
        "ytick.color": P["subtitle"],
        "xtick.labelsize": SIZES["small"],
        "ytick.labelsize": SIZES["small"],
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "figure.facecolor": P["canvas"],
        "savefig.facecolor": P["canvas"],
        "legend.frameon": False,
        "axes.unicode_minus": True,
    })
    return P


# ---------------------------------------------------------------- number formats
MINUS = "−"


def fmt_big(v, signed=True, digits=1):
    """+19.9M / -412K / +1.2B, with a true minus sign."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    a = abs(v)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= div:
            s = ("%." + str(digits) + "f%s") % (a / div, suf)
            break
    else:
        s = "%.0f" % a
    sign = (MINUS if v < 0 else "+") if signed else (MINUS if v < 0 else "")
    return sign + s


def fmt_level(x, decimals=None):
    """7,310 / 7,340.53 / 25.5 depending on magnitude."""
    if decimals is None:
        decimals = 0 if abs(x - round(x)) < 1e-9 and abs(x) >= 100 else (2 if abs(x) >= 100 else (1 if abs(x) >= 10 and abs(x * 2 - round(x * 2)) < 1e-9 else 2))
    return f"{x:,.{decimals}f}"


def fmt_pct(x, decimals=1, signed=True):
    s = f"{abs(x):.{decimals}f}%"
    return ((MINUS if x < 0 else "+") if signed else (MINUS if x < 0 else "")) + s


def spaced(text):
    """Letter-spaced capitals for panel tags: 'GAMMA BY STRIKE' -> 'G A M M A   B Y   S T R I K E'."""
    return "   ".join(" ".join(w) for w in text.upper().split())


# ---------------------------------------------------------------- frame
class Layout:
    """Figure-fraction geometry for one frame (computed from the figure size so margins stay constant in inches)."""

    def __init__(self, size, callout, n_header_lines=1):
        w, h = size
        self.w, self.h = w, h
        self.mx = 0.32 / w                     # side margin (inches -> fraction)
        self.title_y = 1 - 0.36 / h
        self.sub_y = 1 - (0.36 + 0.42) / h
        self.panel_top = 1 - (0.36 + 0.42 + 0.30 + 0.25 * (n_header_lines - 1)) / h
        self.footer_y = 0.20 / h
        self.callout_h = 0.50 / h if callout else 0
        self.callout_y = (0.20 + 0.30) / h if callout else 0
        self.panel_bottom = (self.callout_y + self.callout_h + 0.20 / h) if callout else (0.20 + 0.36) / h


def _round_box(fig, x, y, w, h, fc, ec, lw=1.0, r_in=0.06, z=0, ls="-"):
    fw, fh = fig.get_size_inches()
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%f" % (r_in / fw),
                         transform=fig.transFigure, facecolor=fc, edgecolor=ec, linewidth=lw,
                         mutation_aspect=fw / fh, zorder=z, linestyle=ls)
    fig.add_artist(box)
    return box


def frame(title, subtitle, panels=1, tags=None, callout=None, footer_right="", snapshot="",
          size=DEFAULT_SIZE, panel_gap_in=0.28, panel_widths=None, badge=None):
    """Draw the common frame and return (fig, [panel rects in figure fractions (x, y, w, h)]).

    badge = (number, caption): the house flair, a headline-number pill top right (e.g. ("41%", "base case")).
    Every frame also carries the signal stripe, a thin cyan / purple / yellow rule across the top edge."""
    fig = plt.figure(figsize=size, dpi=DPI)
    avail = size[0] - 2 * 0.32 - (badge_width_in(fig, badge) + 0.45 if badge else 0)
    title_size = SIZES["title"]
    while title_size > 17 and text_width_in(fig, title, title_size, "bold") > avail:
        title_size -= 1
    if subtitle:
        subtitle = "\n".join(wrap_to(fig, line, SIZES["subtitle"], avail) for line in subtitle.split("\n"))
    sub_lines = subtitle.count("\n") + 1 if subtitle else 1
    L = Layout(size, callout, sub_lines)
    fig._gt_layout = L
    fig.text(L.mx, L.title_y, title, fontsize=title_size, fontweight="bold", color=P["title"],
             va="top", ha="left")
    if subtitle:
        fig.text(L.mx, L.sub_y, subtitle, fontsize=SIZES["subtitle"], color=P["subtitle"], va="top", ha="left",
                 linespacing=1.35)
    # panels
    total_w = 1 - 2 * L.mx
    gap = panel_gap_in / size[0]
    widths = panel_widths or [1] * panels
    unit = (total_w - gap * (panels - 1)) / sum(widths)
    rects, x = [], L.mx
    for i in range(panels):
        w = unit * widths[i]
        rect = (x, L.panel_bottom, w, L.panel_top - L.panel_bottom)
        _round_box(fig, *rect, fc=P["panel"], ec=P["border"], lw=1.0, r_in=0.09, z=0)
        rects.append(rect)
        x += w + gap
    for i, tg in enumerate(tags or []):
        if tg is None or i >= len(rects):
            continue
        text, colour = tg
        add_tag(fig, rects[i], text, colour)
    if callout:
        callout_box(fig, callout, L)
    footer(fig, snapshot, footer_right, L)
    signal_stripe(fig)
    if badge:
        draw_badge(fig, badge, L)
    return fig, rects


# ---------------------------------------------------------------- house flair
def signal_stripe(fig, h_in=0.055):
    """A thin three-colour rule across the top edge: cyan (positioning), purple (derived), yellow (our record)."""
    fw, fh = fig.get_size_inches()
    h = h_in / fh
    for x0, w, col in ((0, 0.5, "cyan"), (0.5, 0.3, "purple"), (0.8, 0.2, "yellow")):
        fig.add_artist(plt.Rectangle((x0, 1 - h), w, h, transform=fig.transFigure, facecolor=P[col],
                                     edgecolor="none", zorder=10))


def badge_width_in(fig, badge):
    big, cap = badge
    return max(text_width_in(fig, big, 30, "bold"), text_width_in(fig, " ".join(cap.upper()), 8.5)) + 0.5


def draw_badge(fig, badge, L):
    """Headline-number pill, top right: the one number the chart exists to show, in the mono face."""
    big, cap = badge
    fw, fh = fig.get_size_inches()
    w_in = badge_width_in(fig, badge)
    h_in = 0.92
    x = 1 - L.mx - w_in / fw
    y = 1 - (0.22 + h_in) / fh
    _round_box(fig, x, y, w_in / fw, h_in / fh, fc=P["callout_fill"], ec=P["yellow"], lw=1.4, r_in=0.12, z=3)
    fig.text(x + w_in / fw / 2, y + 0.58 / fh, big, fontsize=30, fontweight="bold", color=P["yellow"],
             family=MONO, ha="center", va="center", zorder=4)
    fig.text(x + w_in / fw / 2, y + 0.17 / fh, " ".join(cap.upper()), fontsize=8.5, color=P["subtitle"],
             ha="center", va="center", zorder=4)


def add_tag(fig, rect, text, colour="cyan"):
    col = P.get(colour, colour)
    x, y, w, h = rect
    fw, fh = fig.get_size_inches()
    fig.text(x + 0.16 / fw, y + h - 0.17 / fh, spaced(text), fontsize=SIZES["tag"], fontweight="bold", color=col,
             va="top", ha="left",
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.35", facecolor="none", edgecolor=col, linewidth=1.3))


def text_width_in(fig, text, size, weight="normal"):
    """Rendered width of one line of text, in inches."""
    t = fig.text(0, 0, text, fontsize=size, fontweight=weight)
    w = t.get_window_extent(renderer=fig.canvas.get_renderer()).width / fig.dpi
    t.remove()
    return w


def wrap_to(fig, text, size, avail_in, weight="normal"):
    """Break one line into as few lines as needed to fit avail_in inches (word boundaries)."""
    if text_width_in(fig, text, size, weight) <= avail_in:
        return text
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and text_width_in(fig, trial, size, weight) > avail_in:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    return "\n".join(lines)


def callout_box(fig, text, L=None):
    """The yellow record box: one line, shrunk to fit; two balanced lines if it still does not fit."""
    L = L or fig._gt_layout
    _round_box(fig, L.mx, L.callout_y, 1 - 2 * L.mx, L.callout_h, fc=P["callout_fill"], ec=P["callout_border"],
               lw=1.6, r_in=0.10, z=1)
    avail = (1 - 2 * L.mx) * L.w - 0.5
    size = SIZES["callout"]
    while size > 12 and text_width_in(fig, text, size, "bold") > avail:
        size -= 0.5
    if text_width_in(fig, text, size, "bold") > avail:
        words = text.split(" ")
        best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
        text = " ".join(words[:best]) + "\n" + " ".join(words[best:])
        size = 11.5
    fig.text(0.5, L.callout_y + L.callout_h / 2, text, fontsize=size, fontweight="bold",
             color=P["callout_text"], ha="center", va="center", zorder=2, linespacing=1.25)


def footer(fig, snapshot, right, L=None):
    L = L or fig._gt_layout
    left = "G T · A N A L Y S T   ·   data: Skylit maps %s · not investment advice" % snapshot if snapshot else \
        "G T · A N A L Y S T   ·   not investment advice"
    fig.text(L.mx, L.footer_y, left, fontsize=SIZES["footer"], color=P["muted"], ha="left", va="bottom")
    if right:
        fig.text(1 - L.mx, L.footer_y, right, fontsize=SIZES["footer"], color=P["muted"], ha="right", va="bottom")


def panel_axes(fig, rect, pad=(0.9, 0.55, 0.5, 0.75), **kw):
    """An axes inside a panel rect; pad = (left, bottom, right, top) in inches."""
    x, y, w, h = rect
    fw, fh = fig.get_size_inches()
    l, b, r, t = pad
    ax = fig.add_axes([x + l / fw, y + b / fh, w - (l + r) / fw, h - (b + t) / fh], **kw)
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    return ax


def save(fig, path):
    fig.savefig(path, dpi=DPI, facecolor=P["canvas"])
    plt.close(fig)
    return path


# ---------------------------------------------------------------- small helpers
def spread_labels(ys, min_gap):
    """Nudge sorted label positions apart so neighbours are at least min_gap apart (keeps the mean in place)."""
    if not ys:
        return []
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = [ys[i] for i in order]
    for _ in range(200):
        moved = False
        for i in range(1, len(pos)):
            d = pos[i] - pos[i - 1]
            if d < min_gap:
                push = (min_gap - d) / 2
                pos[i - 1] -= push
                pos[i] += push
                moved = True
        if not moved:
            break
    out = [0] * len(ys)
    for k, i in enumerate(order):
        out[i] = pos[k]
    return out


def dot_label(ax, x, y, text, colour=None, dy=10, va="bottom", ha="center", size=None, weight="bold"):
    colour = colour or P["white"]
    ax.plot([x], [y], "o", ms=9, color=P["yellow"], zorder=6, markeredgewidth=0)
    ax.annotate(text, (x, y), xytext=(0, dy), textcoords="offset points", ha=ha, va=va,
                fontsize=size or SIZES["label"], fontweight=weight, color=colour, zorder=7)


def legend_row(ax, items, y=1.0, x0=0.0, size=None, gap=0.02, transform=None):
    """A row of legend entries [(kind, colour, text)]; kind in line|dash|dot|patch. Axes-fraction coordinates."""
    transform = transform or ax.transAxes
    size = size or SIZES["small"]
    fig = ax.figure
    renderer = fig.canvas.get_renderer()
    x = x0
    w_in = ax.get_position().width * fig.get_size_inches()[0]
    iw = 0.3 / w_in          # icon width: 0.3 in whatever the axes width
    for kind, colour, text in items:
        if kind == "patch":
            ax.add_patch(plt.Rectangle((x, y - 0.32), iw, 0.64, transform=transform, facecolor=colour,
                                       edgecolor="none", clip_on=False))
        else:
            ls = {"line": "-", "dash": (0, (4, 2)), "dot": (0, (1, 2))}[kind]
            ax.plot([x, x + iw], [y, y], transform=transform, color=colour, lw=3 if kind == "line" else 2,
                    linestyle=ls, clip_on=False, solid_capstyle="butt")
        t = ax.text(x + iw * 1.3, y, text, transform=transform, fontsize=size, color=P["text"], va="center",
                    ha="left", clip_on=False)
        bb = t.get_window_extent(renderer=renderer).transformed(ax.transAxes.inverted())
        x = bb.x1 + gap
    return x
