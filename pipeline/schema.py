#!/usr/bin/env python3
"""Typed contract for the per-news analysis. Stdlib only, `mypy --strict` clean.

The analyst (headless Claude) does not hand back prose - it hands back ONE JSON document that
must parse into the dataclasses below. Parsing is STRICT: unknown keys, missing keys, wrong
types (a bool is not a number, "0.6" is not 0.6) and out-of-enum values are all rejected with
the exact JSON path. Then `check()` runs the RULESET - CLAUDE.md's output schema, the conviction
rubric and the pre-ledger gates from the 2026-09-19 scoring cycle - as machine-checked rules.
Each rule has an id (R01..R27) so a violation names the rule it broke.

One source of truth: `json_schema()` is generated from these same types, and that is the
contract printed into the analyst's prompt.

    python pipeline/schema.py            # print the JSON Schema
    python pipeline/schema.py rules      # print the rule list
"""
from __future__ import annotations

import dataclasses
import datetime
import json
import re
import sys
import types
import typing
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, TypeVar, Union, get_args, get_origin, get_type_hints

SCHEMA_VERSION = 3          # 3 = the self-coherence rules R28-R36, 2026-09-21. Breaking: every row now
#                             carries a resolution_source (R30). 2 = reference forecast (R25/R26) +
#                             duration/marker rows (R27), 2026-09-20.

# ── closed vocabularies (the ruleset's enums) ────────────────────────────────
Direction = Literal["up", "down", "vol", "neutral"]
Lean = Literal["escalation", "de-escalation", "neutral"]
Triage = Literal["analyze", "sentiment-only", "noise", "stale", "duplicate"]
ShockType = Literal["supply", "demand", "generic", "not-market-relevant"]
ConflictKind = Literal["constitutive", "distributive", "mixed"]
SourceTier = Literal["primary-doc", "top-wire", "trade-press", "aggregator"]
CapitalTier = Literal["capital-committed", "binding-scheduled", "costly-signal", "rhetoric"]
FormalVerdict = Literal["PASS", "PASS-WITH-FLAGS", "FAIL"]
PreconditionStatus = Literal["materializing", "mixed", "stalling"]
RowClass = Literal["invariant", "scheduled-print", "event-occurrence", "direction",
                   "level-range", "conditional",
                   "duration",   # "the current pause/round lasts beyond D" - priced by tools/cycle_odds.py (16.18)
                   "marker"]     # an observable STRUCTURAL marker appears by D: monitors, a DMZ, a third-party
#                                  guarantee, an inspection regime, a signed text (16.18)
TapeDirection = Literal["escalation", "de-escalation", "mixed"]
GateVerdict = Literal["PASS", "FAIL"]
NodeKind = Literal["event"]          # the tool may add conditional EVENT nodes only; re-weighting
#                                      mutually-exclusive BRANCH siblings stays a human decision.

# conviction rubric (CLAUDE.md): component -> (weight, allowed anchor values per tier)
SOURCE_ANCHORS: dict[str, tuple[float, ...]] = {
    "primary-doc": (0.20,), "top-wire": (0.15,), "trade-press": (0.10,), "aggregator": (0.0, 0.05)}
CAPITAL_ANCHORS: dict[str, tuple[float, ...]] = {
    "capital-committed": (0.30,), "binding-scheduled": (0.20,), "costly-signal": (0.10,),
    "rhetoric": (0.0,)}
FORMAL_ANCHORS: dict[str, tuple[float, ...]] = {
    "PASS": (0.20,), "PASS-WITH-FLAGS": (0.10,), "FAIL": (0.0,)}
LENS_ANCHORS: dict[int, float] = {1: 0.05, 2: 0.10, 3: 0.15}
PRECONDITION_ANCHORS: dict[str, tuple[float, ...]] = {
    "materializing": (0.15,), "mixed": (0.07,), "stalling": (0.0,)}

LEG_CLUSTERS = frozenset({"iran-war", "oil-tape", "opec-policy"})   # doctrine 16.15
CLUSTER_CAP = 0.35                                                   # hygiene rule 1


# ── the typed document ───────────────────────────────────────────────────────
@dataclass(frozen=True)
class ItemVerdict:
    """One per news item handed to the analyst - nothing is silently skipped."""
    item_id: str
    triage: Triage
    reason: str                       # one line: WHY this triage (12.1 rhetoric? stale? dup of what?)
    event_id: Optional[str] = None    # required when triage == "analyze"


@dataclass(frozen=True)
class Player:
    name: str
    role: str                         # chessboard decomposition - allies are SEPARATE players
    objective: str


@dataclass(frozen=True)
class GameStructure:
    game_type: str                    # e.g. "war of attrition", "signaling", "bargaining w/ outside option"
    conflict_kind: ConflictKind
    information: str                  # who knows what; complete/incomplete; public vs private signal
    timing: str                       # simultaneous / sequential / repeated; who moves next and when


@dataclass(frozen=True)
class Preference:
    actor: str
    assumption: str
    flip_test: str                    # what we would observe if this preference assumption were false


@dataclass(frozen=True)
class Conviction:
    source_tier: SourceTier
    source_quality: float
    capital_tier: CapitalTier
    capital_committed: float
    formal_verdict: FormalVerdict
    formal_validity: float
    formal_flags: list[str]           # checklist items raised (formal 10 / 12.9); [] only on a full PASS
    independent_lenses: int           # 1, 2 or 3 (3 = three or more)
    lens_names: list[str]
    multi_lens: float
    precondition_status: PreconditionStatus
    precondition: float
    total: float


@dataclass(frozen=True)
class LegNeutral:
    """Doctrine 16.15 - mandatory on iran-war / oil / energy-direction rows."""
    tape_direction_10d: TapeDirection  # which way the last 10 sessions of tape ran
    evidence: str                      # the datapoints behind that read (Brent path, transit counts, strike nights)
    same_direction_as_call: bool
    reversal_trigger: str              # DATED, numeric: "Brent back above 85 within 5 sessions kills this"


@dataclass(frozen=True)
class StatePremise:
    """Doctrine 16.16 - mandatory when the row rests on a state (ceasefire holds, strait open...)."""
    state: str
    datapoint: str                     # the primary datapoint that shows the state is LIVE
    datapoint_ts: str                  # ISO-8601 UTC, e.g. 2026-09-20T06:00Z
    source_url: str


@dataclass(frozen=True)
class Reference:
    """The outside view, decided BEFORE the probability (research review 2026-09-20). Mandatory on every row.
    The edge score in `ledger.py report` is measured against this: the market price when one is given,
    else the base rate."""
    base_rate: float                   # outside-view probability from a NAMED comparison class
    base_class: str                    # the class, its count and its source: "21/48 interstate ceasefires resumed (Fortna 2003)"
    market_prob: Optional[float] = None  # market-implied probability, only if a LIQUID market exists
    market_src: str = ""               # venue, contract, spread, volume, time - a thin market's midpoint is not a price
    divergence_reason: str = ""        # REQUIRED when |P - reference| > 0.10: the dated datapoint the reference lacks


@dataclass(frozen=True)
class CycleOdds:
    """Doctrine 16.18 - mandatory on duration rows: the no-view odds from the cycle's own phase lengths."""
    command: str                       # the exact `python tools/cycle_odds.py ...` that was run
    ends_lo: float                     # the printed band for "the phase ENDS by the horizon"
    ends_hi: float
    catalyst: str = ""                 # REQUIRED when P is more than 0.10 outside the band: dated + capital-committed


@dataclass(frozen=True)
class NoViewOdds:
    """market-transmission 13f - mandatory on level / range rows."""
    command: str                       # the exact `python tools/range_odds.py ...` that was run
    odds: float                        # the no-view probability it printed
    mechanism: str                     # why the stated P deviates from it (may be "none - modest view")
    catalyst_date: Optional[str] = None  # ISO date; REQUIRED when |P - odds| > 0.20


@dataclass(frozen=True)
class ResolutionSource:
    """R30 - WHO decides this row, from WHICH number, read HOW. Written before the horizon,
    not argued after it. #59 was scored against the engine purely because 'strike-free' was
    never scoped to a source; #30 reached its horizon still 'AMBIGUOUS, leaning HIT'."""
    publisher: str                     # the agency, exchange or outlet whose print is decisive
    series: str                        # the named series/field: "AAA national average regular gasoline"
    convention: str                    # which observation counts: "published month-end close", "first print, not revisions"
    url: str = ""


@dataclass(frozen=True)
class Conjunction:
    """R36 - a row that needs TWO things to happen. #63 (strike AND framework) was priced 0.75,
    above the probability of either leg alone. Rewording a conjunction does not fix its price."""
    legs: list[str]
    leg_probs: list[float]


@dataclass(frozen=True)
class RelativeValue:
    """R29 - a two-ticker row is only an RV trade if the legs carry comparable risk. #74 expressed
    a refining-margin view as XLE vs USO: 1.25pct/day against 3.8pct/day, i.e. a levered direction
    bet on crude wearing a spread's clothes. Second-worst score in the book."""
    high_vol_ticker: str
    low_vol_ticker: str
    high_vol_daily: float              # realized daily vol, pct
    low_vol_daily: float
    note: str = ""


@dataclass(frozen=True)
class Contradiction:
    """R28 - this row disagrees with one of the engine's OWN open rows. STATE.md lesson 7:
    'when two of your own rows contradict, that is a hedge, not two insights'. #26 (no oil-driven
    hike) contradicted #32 (August CPI hot) and the book carried both."""
    ledger_id: int
    nature: str                        # what exactly disagrees
    hedge_reason: str                  # why holding both is a view and not a hedge


@dataclass(frozen=True)
class Independence:
    """R34 - this row shares an asset and a direction with another live row. #70 (SMH<SPY) and
    #27 (SMH<XLE) were one semis bet logged twice, and they tracked MISS together."""
    ledger_id: int
    argument: str                      # what makes this a SECOND bet rather than the same bet restated


@dataclass(frozen=True)
class PlanningBasis:
    """R32 / doctrine 16.14 - the row rests on a reported PLAN. #72 read a fully-coordinated leaked
    strike plan as an action forecast and scored 0.30. A leaked plan is a negotiating instrument."""
    reported_plan: str
    execution_signal: str = ""         # aircraft launched, NOTAMs, notice FILED - not 'bill tabled'


@dataclass(frozen=True)
class MeetingScope:
    """R35 - a claim about ONE dated meeting is strictly harder than the same claim over a window
    that contains it. #26 priced a six-month window with one-meeting reasoning."""
    meeting_date: str                  # ISO date of the specific meeting
    window_prob: float                 # P of the SAME claim over the containing window


@dataclass(frozen=True)
class SelfDowngrade:
    """R31 / doctrine 13g - this row reverses one of the engine's own open rows. #76 talked itself
    out of the correct #32 on two sessions of contrary tape, against a 2-3 week pass-through lag."""
    ledger_id: int
    lag_length_days: int               # the mechanism's own lag length
    data_days: int                     # how many days of contrary data are actually in hand
    mechanism: str


@dataclass(frozen=True)
class RedTeamGate:
    """contrarian-red-team Part B - one line per step. Required at conviction >= 0.65, on a 5th+
    row in a cluster, and on any row in a cluster over the 35pct cap."""
    key_assumptions: str
    mini_ach: str
    premortem: str
    cascade_check: str
    reference_class: str
    independence: str
    leg_neutral_and_arithmetic: str
    verdict: GateVerdict


@dataclass(frozen=True)
class NewNode:
    id: str
    parent: str
    label: str
    p: float
    horizon: str
    rationale: str
    confluence: list[str]
    market: str
    kind: NodeKind
    lane: str
    date: str                          # ISO date - the x-position on the map


@dataclass(frozen=True)
class TimelineWiring:
    """CLAUDE.md ABSOLUTE rule: every prediction lives on the timeline. Exactly one of the two."""
    attach_to: Optional[str] = None    # id of an existing node in data/timelines.json
    new_node: Optional[NewNode] = None


@dataclass(frozen=True)
class Prediction:
    ref: str                           # "p1", "p2", ... unique in the document - used by `approve`
    prediction: str
    prob: float
    horizon: str                       # ISO date YYYY-MM-DD
    falsifier: str
    sensitivity: str                   # which assumption breaks it
    row_class: RowClass
    direction: Direction
    lean: Lean
    sectors: list[str]                 # keys of data/sector_map.json
    tickers: list[str]
    cluster: str                       # correlation-cluster slug, "" = an independent bet
    conviction_adjust: float           # -0.05 .. +0.05 vs the event's conviction
    timeline: TimelineWiring
    conviction_adjust_reason: str = ""
    leg_neutral: Optional[LegNeutral] = None
    state_premise: Optional[StatePremise] = None
    no_view_odds: Optional[NoViewOdds] = None
    red_team: Optional[RedTeamGate] = None
    reference: Optional[Reference] = None   # R25: required on EVERY row (Optional only so old documents parse)
    cycle_odds: Optional[CycleOdds] = None  # R27: required on duration rows
    phase_ends: Optional[bool] = None       # duration rows: True = the row says the phase ENDS by the horizon
    print_guide: str = ""              # scheduled-print at P>=0.80: the issuer's OWN guide for the period (13i)
    concentration_note: str = ""       # required when the row's cluster is over the 35pct cap
    # ── schema v3 (2026-09-21): nine rules, each bought with a specific loss ──
    resolution_source: Optional[ResolutionSource] = None      # R30
    conjunction: Optional[Conjunction] = None                 # R36
    relative_value: Optional[RelativeValue] = None            # R29
    planning: Optional[PlanningBasis] = None                  # R32
    meeting: Optional[MeetingScope] = None                    # R35
    self_downgrade: Optional[SelfDowngrade] = None            # R31
    contradicts: list[Contradiction] = field(default_factory=list)   # R28
    independence: list[Independence] = field(default_factory=list)   # R34


@dataclass(frozen=True)
class MarketTranslation:
    shock_type: ShockType              # market-transmission 1: THE master gate
    branch_confirmation: str           # 2y-yield sign / flows datapoint that confirms the branch
    channels: list[str]
    priced_in: str                     # what the market has already had time to price (report age!)
    horizon_match: str                 # horizon of the call vs the physical disruption


@dataclass(frozen=True)
class EventAnalysis:
    id: str                            # "e1", "e2", ...
    title: str
    item_ids: list[str]
    load_bearing_reported: list[str]   # reported timestamps of the load-bearing items ("unknown" allowed)
    players: list[Player]
    game: GameStructure
    preferences: list[Preference]
    ladder_credibility_read: str
    conviction: Conviction
    market: MarketTranslation
    predictions: list[Prediction]
    staleness_note: str = ""           # required when every item behind the event is stale/undated


@dataclass(frozen=True)
class SuggestedResolution:
    """A matured or already-decided OPEN ledger row. A suggestion only - the human resolves."""
    ledger_id: int
    outcome: Literal["hit", "miss", "void"]
    evidence: str
    source_url: str


@dataclass(frozen=True)
class BatchAnalysis:
    schema_version: int
    batch: str                         # e.g. "inbox/queue/20260920T0700Z.md"
    generated: str                     # ISO-8601 UTC
    items: list[ItemVerdict]
    events: list[EventAnalysis]
    suggested_resolutions: list[SuggestedResolution] = field(default_factory=list)
    summary: str = ""


# ── strict, type-driven parsing ──────────────────────────────────────────────
class SchemaError(ValueError):
    """Raised with every structural problem found, each prefixed by its JSON path."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


T = TypeVar("T")
_NONE = type(None)


def _is_union(origin: Any) -> bool:
    return origin is Union or origin is types.UnionType


def _coerce(tp: Any, value: Any, path: str, problems: list[str]) -> Any:
    origin = get_origin(tp)
    if _is_union(origin):
        args = get_args(tp)
        if value is None:
            if _NONE in args:
                return None
            problems.append(f"{path}: null is not allowed")
            return None
        inner = [a for a in args if a is not _NONE]
        return _coerce(inner[0], value, path, problems)
    if origin is Literal:
        allowed = get_args(tp)
        if isinstance(value, bool) or value not in allowed:
            problems.append(f"{path}: {value!r} is not one of {list(allowed)}")
        return value
    if origin is list:
        (elem,) = get_args(tp)
        if not isinstance(value, list):
            problems.append(f"{path}: expected a list, got {type(value).__name__}")
            return []
        return [_coerce(elem, v, f"{path}[{i}]", problems) for i, v in enumerate(value)]
    if dataclasses.is_dataclass(tp) and isinstance(tp, type):
        return _parse_dc(tp, value, path, problems)
    if tp is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            problems.append(f"{path}: expected a number, got {type(value).__name__} {value!r}")
            return 0.0
        return float(value)
    if tp is int:
        if isinstance(value, bool) or not isinstance(value, int):
            problems.append(f"{path}: expected an integer, got {type(value).__name__} {value!r}")
            return 0
        return value
    if tp is bool:
        if not isinstance(value, bool):
            problems.append(f"{path}: expected true/false, got {type(value).__name__} {value!r}")
            return False
        return value
    if tp is str:
        if not isinstance(value, str):
            problems.append(f"{path}: expected a string, got {type(value).__name__} {value!r}")
            return ""
        return value
    problems.append(f"{path}: unsupported type {tp!r}")
    return value


def _parse_dc(cls: type[Any], data: Any, path: str, problems: list[str]) -> Any:
    if not isinstance(data, dict):
        problems.append(f"{path}: expected an object ({cls.__name__}), got {type(data).__name__}")
        return None
    hints = get_type_hints(cls)
    flds = {f.name: f for f in dataclasses.fields(cls)}
    for key in data:
        if key not in flds:
            problems.append(f"{path}.{key}: unknown field for {cls.__name__} "
                            f"(allowed: {sorted(flds)})")
    kwargs: dict[str, Any] = {}
    for name, f in flds.items():
        if name in data:
            kwargs[name] = _coerce(hints[name], data[name], f"{path}.{name}", problems)
        elif f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
            problems.append(f"{path}.{name}: required field is missing")
    if any(p.startswith(path) and "required field" in p for p in problems):
        return None
    return cls(**kwargs)


def parse(data: Any) -> BatchAnalysis:
    """dict (from json.load) -> BatchAnalysis, or SchemaError listing every structural problem."""
    problems: list[str] = []
    doc = _parse_dc(BatchAnalysis, data, "$", problems)
    if problems or doc is None:
        raise SchemaError(problems or ["$: could not be parsed"])
    assert isinstance(doc, BatchAnalysis)
    return doc


# ── JSON Schema, generated from the same types ───────────────────────────────
def _js(tp: Any, defs: dict[str, Any]) -> dict[str, Any]:
    origin = get_origin(tp)
    if _is_union(origin):
        inner = [a for a in get_args(tp) if a is not _NONE]
        return {"anyOf": [_js(inner[0], defs), {"type": "null"}]}
    if origin is Literal:
        return {"enum": list(get_args(tp))}
    if origin is list:
        return {"type": "array", "items": _js(get_args(tp)[0], defs)}
    if dataclasses.is_dataclass(tp) and isinstance(tp, type):
        name = tp.__name__
        if name not in defs:
            defs[name] = {}
            hints = get_type_hints(tp)
            props = {f.name: _js(hints[f.name], defs) for f in dataclasses.fields(tp)}
            req = [f.name for f in dataclasses.fields(tp)
                   if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING]
            defs[name] = {"type": "object", "additionalProperties": False,
                          "properties": props, "required": req,
                          "description": (tp.__doc__ or "").strip().split("\n")[0]}
        return {"$ref": f"#/$defs/{name}"}
    return {"type": {float: "number", int: "integer", bool: "boolean", str: "string"}[tp]}


def json_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {}
    root = _js(BatchAnalysis, defs)
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", **root, "$defs": defs}


# ── the ruleset ──────────────────────────────────────────────────────────────
RULES: dict[str, str] = {
    "R01": "every item handed to the analyst gets exactly one verdict; no unknown item ids",
    "R02": "triage=analyze <-> the item belongs to exactly the event it names; events cite real items",
    "R03": "an event resting only on trump-truth items must carry a capital-committed ACTION, not rhetoric (12.1)",
    "R04": "an event whose items are all stale (>48h) or undated: source quality <= 0.05 and a staleness_note",
    "R05": "each conviction component equals an anchor of its tier; total = the sum of the five",
    "R06": "formal FAIL or conviction < 0.35 (noise band) -> the event proposes NO predictions",
    "R07": "per-row conviction adjust is within +/-0.05 and carries a reason when non-zero",
    "R08": "prob in (0,1); horizon is an ISO date after the analysis date; prediction, falsifier, sensitivity non-empty",
    "R09": "wording lint is clean: no compound AND, conditionals carry a void clause, thresholds are numeric, "
           "'strike' is scoped, the falsifier restates its date",
    "R10": "a state-premise row carries a primary datapoint < 24h old, else P <= 0.55 (16.16)",
    "R11": "a level/range row names ONE asset and carries range_odds.py no-view odds; |P - odds| > 0.20 "
           "needs a dated catalyst (13f)",
    "R12": "iran/oil/energy-direction rows carry the leg-neutral read; same direction as the tape -> P <= 0.55; "
           "at most ONE same-direction iran/oil row per batch (16.15)",
    "R13": "P >= 0.70 only for invariant or scheduled-print rows; P >= 0.80 on a print needs the issuer's "
           "own guide (13i)",
    "R14": "conviction >= 0.65, a 5th+ row in a cluster, or a cluster over the 35pct cap -> a complete, "
           "PASSing red-team gate",
    "R15": "a row in a cluster over the 35pct cap carries a concentration_note (hygiene rule 1)",
    "R16": "sectors exist in data/sector_map.json; tickers are upper-case symbols; refs are unique",
    "R17": "timeline wiring: exactly one of attach_to (an existing node) / new_node (valid parent + lane, "
           "unused id, 0<=p<=1)",
    "R18": "direction and mechanism only - no sizing language (doctrine 14)",
    "R19": "a conditional row says in its falsifier what happens when the trigger never fires (N/A / void)",
    "R20": "a disjunction (OR) is priced off its EASIEST leg - flagged for the human (warning)",
    "R21": "suggested resolutions point at OPEN ledger rows",
    "R22": "schema_version matches; generated is an ISO timestamp",
    "R23": "players >= 2 with allies separate; every preference has a flip-test; market gate is filled "
           "in for market-relevant events",
    "R24": "no two rows in the batch carry the same prediction text (never log a call twice)",
    "R25": "outside view first: every row carries a reference - a base rate in (0,1) with its named comparison "
           "class; a market price only with venue/contract/liquidity",
    "R26": "|P - reference| > 0.10 (market price if given, else base rate) needs a divergence_reason naming a "
           "dated datapoint the reference lacks",
    "R27": "iran-war rows are NOT direction-of-the-next-leg calls (16.18): row_class direction is refused there - "
           "re-express as duration / marker / invariant / level; a duration row carries cycle_odds.py's band and a "
           "P more than 0.10 outside it needs a dated capital-committed catalyst",
    # ── v3, 2026-09-21. Every rule below is a specific resolved loss, made unrepeatable. ──
    "R28": "the book may not contradict itself silently: a row opposing an OPEN row on the same asset, or another "
           "row in the same batch, must declare it in contradicts[] with a hedge_reason (#26 vs #32; lesson 7)",
    "R29": "a two-ticker row declares both legs' realized vol; ratio > 1.5x means it is a LEVERED DIRECTION bet on "
           "the high-vol leg, not a spread - P <= 0.55 and the direction must be the high-vol leg's (#74, 13h)",
    "R30": "every row names its resolution source: publisher, series and the reading convention, fixed BEFORE the "
           "horizon (#59 scored against the engine on scope; #30 reached its horizon ambiguous)",
    "R31": "a row that reverses one of the engine's own open rows carries self_downgrade with the mechanism's lag "
           "length and the days of contrary data actually in hand; data_days < lag_length_days is refused (#76, 13g)",
    "R32": "a row resting on a reported PLAN (leaked plan, 'preparing to', drafted options, a bill tabled) carries "
           "planning{} and caps at 0.35 until an EXECUTION signal exists (#72, 16.14)",
    "R33": "a row priced within 0.05 of the book's own base rate with no divergence_reason carries no information - "
           "it cannot earn resolution (warning; 9/20 research measured RES ~0.00)",
    "R34": "two rows sharing a ticker and a direction over overlapping horizons are ONE bet: the second needs an "
           "independence argument naming the first (#70 and #27 were one SMH bet, and missed together)",
    "R35": "a claim about ONE dated meeting must be priced strictly below the same claim over the window that "
           "contains it; meeting{} carries that window probability (#26 priced a window with meeting reasoning)",
    "R36": "a conjunctive row declares its legs and their probabilities, and P must not exceed the WEAKEST leg; a "
           "wording fix for a compound AND does not fix its price (#63 at 0.75, #39, #69)",
}


@dataclass(frozen=True)
class OpenRow:
    """One live row of the book, as the coherence rules (R28 / R31 / R34) need to see it."""
    id: int
    prediction: str
    prob: float
    direction: str
    tickers: tuple[str, ...]
    cluster: str
    horizon: str


@dataclass
class Context:
    """Everything the rules need from the repo - passed in, so rules stay pure and testable."""
    item_ids: set[str]
    item_sources: dict[str, str]            # item_id -> feed label (e.g. "trump-truth")
    item_age_hours: dict[str, Optional[float]]  # None = reported unknown
    sector_keys: set[str]
    node_ids: set[str]
    lanes: set[str]
    open_by_cluster: dict[str, int]
    open_total: int
    open_ledger_ids: set[int]
    existing_predictions: set[str]
    # v3: the rules that check the book against ITSELF need to see the book
    open_rows: dict[int, OpenRow] = field(default_factory=dict)
    book_base_rate: float = 0.745           # the book's own realised hit rate (9/20 research)


@dataclass
class Finding:
    rule: str
    where: str
    message: str
    severity: Literal["error", "warning"] = "error"

    def __str__(self) -> str:
        return f"[{self.rule}] {self.where}: {self.message}"


_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SIZING = re.compile(r"\b(position siz|% of (the )?(portfolio|book|account)|allocate \d|"
                     r"buy \d+ (shares|contracts)|leverage of|risk \d+(\.\d+)?%)", re.I)
# R32 - the vocabulary of an intention. #72 read every one of these as an action.
_PLANNING = re.compile(r"\b(plans?\s+to|planning|prepar\w+\s+to|draft(ed|s)?|leaked|reportedly\s+"
                       r"(considering|weighing)|tabled|proposed\s+(bill|budget|rule)|options\s+"
                       r"(for|presented)|blueprint|is\s+expected\s+to\s+order)\b", re.I)
# R35 - a body that meets on a calendar and decides by vote
_COMMITTEE = re.compile(r"\b(FOMC|ECB|BoJ|Bank of Japan|Governing Council|OPEC|MPC|Politburo|"
                        r"committee|board of governors)\b", re.I)
_MEETING_WORD = re.compile(r"\b(meeting|session|summit|ministerial)\b", re.I)
_OPPOSED = {("up", "down"), ("down", "up")}


def _overlaps(h1: str, h2: str, days: int = 45) -> bool:
    """Two horizons are 'live together' when they land within `days` of each other."""
    try:
        d1 = datetime.date.fromisoformat(h1[:10])
        d2 = datetime.date.fromisoformat(h2[:10])
    except ValueError:
        return True          # unparseable: assume they overlap, and make the author argue otherwise
    return abs((d1 - d2).days) <= days


def _parse_ts(s: str) -> Optional[datetime.datetime]:
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def _near(value: float, anchors: typing.Iterable[float]) -> bool:
    return any(abs(value - a) < 0.005 for a in anchors)


def check(doc: BatchAnalysis, ctx: Context, lint: typing.Callable[[str, str, float], list[str]]
          ) -> list[Finding]:
    """Run R01..R24. `lint` is ledger.lint (injected so this module imports nothing from the repo)."""
    out: list[Finding] = []

    def err(rule: str, where: str, msg: str) -> None:
        out.append(Finding(rule, where, msg))

    def warn(rule: str, where: str, msg: str) -> None:
        out.append(Finding(rule, where, msg, "warning"))

    # R22
    if doc.schema_version != SCHEMA_VERSION:
        err("R22", "$.schema_version", f"expected {SCHEMA_VERSION}, got {doc.schema_version}")
    generated = _parse_ts(doc.generated)
    if generated is None:
        err("R22", "$.generated", f"{doc.generated!r} is not an ISO-8601 timestamp")
        generated = datetime.datetime.now(datetime.timezone.utc)

    # R01 / R02
    seen: dict[str, ItemVerdict] = {}
    for v in doc.items:
        if v.item_id in seen:
            err("R01", f"items[{v.item_id}]", "more than one verdict for this item")
        seen[v.item_id] = v
        if v.item_id not in ctx.item_ids:
            err("R01", f"items[{v.item_id}]", "no such item in the batch")
        if not v.reason.strip():
            err("R01", f"items[{v.item_id}]", "triage reason is empty")
    for missing in sorted(ctx.item_ids - set(seen)):
        err("R01", f"items[{missing}]", "item has no verdict - every incoming item is triaged")
    events = {e.id: e for e in doc.events}
    if len(events) != len(doc.events):
        err("R02", "$.events", "duplicate event ids")
    for v in doc.items:
        if v.triage == "analyze":
            if not v.event_id or v.event_id not in events:
                err("R02", f"items[{v.item_id}]", f"triage=analyze but event_id {v.event_id!r} is not an event")
            elif v.item_id not in events[v.event_id].item_ids:
                err("R02", f"items[{v.item_id}]", f"event {v.event_id} does not list this item")
        elif v.event_id:
            err("R02", f"items[{v.item_id}]", f"triage={v.triage} must not carry an event_id")

    refs: set[str] = set()
    same_dir_leg_rows: list[str] = []
    texts: set[str] = set()
    batch_rows: list[tuple[str, Prediction]] = []

    for e in doc.events:
        w = f"events[{e.id}]"
        if not e.item_ids:
            err("R02", w, "an event must cite at least one item")
        for iid in e.item_ids:
            if iid not in ctx.item_ids:
                err("R02", w, f"cites unknown item {iid}")
            elif seen.get(iid) and seen[iid].triage != "analyze":
                err("R02", w, f"cites item {iid} whose triage is {seen[iid].triage!r}, not 'analyze'")
        known = [i for i in e.item_ids if i in ctx.item_ids]

        # R03
        if known and all(ctx.item_sources.get(i) == "trump-truth" for i in known) \
                and e.conviction.capital_tier == "rhetoric":
            err("R03", w, "rests only on Truth Social posts with no capital-committed action - "
                          "sentiment-only, not an analyzable event")
        # R04
        ages = [ctx.item_age_hours.get(i) for i in known]
        if known and all(a is None or a > 48 for a in ages):
            if e.conviction.source_quality > 0.05 + 1e-9:
                err("R04", w, "all items are stale/undated: source_quality must be <= 0.05")
            if not e.staleness_note.strip():
                err("R04", w, "all items are stale/undated: staleness_note is required")

        # R05
        c = e.conviction
        if not _near(c.source_quality, SOURCE_ANCHORS[c.source_tier]):
            err("R05", w, f"source_quality {c.source_quality} is not an anchor of {c.source_tier} "
                          f"{SOURCE_ANCHORS[c.source_tier]}")
        if not _near(c.capital_committed, CAPITAL_ANCHORS[c.capital_tier]):
            err("R05", w, f"capital_committed {c.capital_committed} is not the anchor of {c.capital_tier} "
                          f"{CAPITAL_ANCHORS[c.capital_tier]}")
        if not _near(c.formal_validity, FORMAL_ANCHORS[c.formal_verdict]):
            err("R05", w, f"formal_validity {c.formal_validity} is not the anchor of {c.formal_verdict}")
        if c.independent_lenses not in LENS_ANCHORS:
            err("R05", w, f"independent_lenses must be 1, 2 or 3, got {c.independent_lenses}")
        else:
            if not _near(c.multi_lens, (LENS_ANCHORS[c.independent_lenses],)):
                err("R05", w, f"multi_lens {c.multi_lens} does not match {c.independent_lenses} lens(es)")
            if len(c.lens_names) < c.independent_lenses:
                err("R05", w, f"claims {c.independent_lenses} independent lenses but names {len(c.lens_names)}")
        if not _near(c.precondition, PRECONDITION_ANCHORS[c.precondition_status]):
            err("R05", w, f"precondition {c.precondition} is not the anchor of {c.precondition_status}")
        total = c.source_quality + c.capital_committed + c.formal_validity + c.multi_lens + c.precondition
        if abs(total - c.total) > 0.005:
            err("R05", w, f"conviction total {c.total} != sum of components {total:.2f}")
        if c.formal_verdict == "PASS-WITH-FLAGS" and not c.formal_flags:
            err("R05", w, "PASS-WITH-FLAGS but formal_flags is empty - name the checklist items")

        # R06
        if e.predictions and c.formal_verdict == "FAIL":
            err("R06", w, "formal validity FAIL -> do not ledger; remove the predictions")
        if e.predictions and total < 0.35 - 1e-9:
            err("R06", w, f"conviction {total:.2f} is in the noise band (<0.35) -> note it, do NOT ledger")

        # R23
        if len(e.players) < 2:
            err("R23", w, "chessboard decomposition needs at least two players (allies separate)")
        for i, pr in enumerate(e.preferences):
            if not pr.flip_test.strip():
                err("R23", f"{w}.preferences[{i}]", "flip_test is empty")
        if not e.preferences:
            err("R23", w, "no preference assumptions stated")
        if e.market.shock_type != "not-market-relevant":
            if not e.market.branch_confirmation.strip() or not e.market.priced_in.strip():
                err("R23", w, "market-relevant event: branch_confirmation and priced_in are required")
        elif any(p.tickers for p in e.predictions):
            err("R23", w, "shock_type is not-market-relevant but predictions carry tickers")

        for p in e.predictions:
            pw = f"{w}.{p.ref}"
            if p.ref in refs:
                err("R16", pw, "duplicate prediction ref")
            refs.add(p.ref)
            conv = total + p.conviction_adjust

            # R07
            if abs(p.conviction_adjust) > 0.05 + 1e-9:
                err("R07", pw, f"conviction_adjust {p.conviction_adjust} is outside +/-0.05")
            if abs(p.conviction_adjust) > 1e-9 and not p.conviction_adjust_reason.strip():
                err("R07", pw, "non-zero conviction_adjust needs a reason")

            # R08
            if not (0.0 < p.prob < 1.0):
                err("R08", pw, f"prob {p.prob} must be strictly between 0 and 1")
            if not _ISO_DATE.match(p.horizon):
                err("R08", pw, f"horizon {p.horizon!r} is not YYYY-MM-DD")
            else:
                try:
                    if datetime.date.fromisoformat(p.horizon) <= generated.date():
                        err("R08", pw, f"horizon {p.horizon} is not after the analysis date")
                except ValueError:
                    err("R08", pw, f"horizon {p.horizon!r} is not a real date")
            for name, val in (("prediction", p.prediction), ("falsifier", p.falsifier),
                              ("sensitivity", p.sensitivity)):
                if len(val.strip()) < 12:
                    err("R08", pw, f"{name} is missing or too thin to score")

            # R09 / R19 / R20 + which optional blocks the wording demands
            msgs = lint(p.prediction, p.falsifier, p.prob)
            kinds = {m.split(":")[0].split(" ")[0] for m in msgs}
            for m in msgs:
                head = m.split(":")[0]
                if head.startswith(("COMPOUND", "VAGUE", "SCOPE", "falsifier")):
                    err("R09", pw, m)
                elif head.startswith("CONDITIONAL"):
                    err("R19", pw, m)
                elif head.startswith("DISJUNCTION"):
                    warn("R20", pw, m)
            if p.row_class == "conditional" and not re.search(r"N/?A|void", p.falsifier, re.I):
                err("R19", pw, "conditional row: the falsifier must say what happens if the trigger never fires")

            # R10
            if "STATE-PREMISE" in kinds and p.state_premise is None:
                err("R10", pw, "wording rests on a state (ceasefire/deal/strait/pause): state_premise is required")
            if p.state_premise is not None:
                ts = _parse_ts(p.state_premise.datapoint_ts)
                if ts is None:
                    err("R10", pw, f"state_premise.datapoint_ts {p.state_premise.datapoint_ts!r} is not ISO-8601")
                else:
                    age_h = (generated - ts).total_seconds() / 3600
                    if age_h < -1:
                        err("R10", pw, "state_premise datapoint is dated in the future")
                    elif age_h > 24 and p.prob > 0.55 + 1e-9:
                        err("R10", pw, f"state datapoint is {age_h:.0f}h old (>24h): premise UNVERIFIED, P must be <= 0.55")
                if not p.state_premise.source_url.startswith("http"):
                    err("R10", pw, "state_premise.source_url must be a URL")

            # R11
            needs_odds = p.row_class == "level-range" or "LEVEL/RANGE" in kinds
            if needs_odds and p.no_view_odds is None:
                err("R11", pw, "level/range row: run tools/range_odds.py and fill no_view_odds")
            if p.row_class == "level-range" and len(p.tickers) != 1:
                err("R11", pw, f"level/range row must name exactly ONE asset, got {p.tickers}")
            if p.no_view_odds is not None:
                nv = p.no_view_odds
                if not (0.0 <= nv.odds <= 1.0):
                    err("R11", pw, f"no_view_odds.odds {nv.odds} is not a probability")
                if "range_odds.py" not in nv.command:
                    err("R11", pw, "no_view_odds.command must be the range_odds.py invocation that was run")
                if abs(p.prob - nv.odds) > 0.20 + 1e-9:
                    if not nv.catalyst_date or not _ISO_DATE.match(nv.catalyst_date):
                        err("R11", pw, f"P {p.prob} is {p.prob - nv.odds:+.2f} off the no-view odds {nv.odds}: "
                                       "needs a dated catalyst (catalyst_date) or a re-price")

            # R12
            energy_dir = "energy" in p.sectors and p.direction in ("up", "down")
            if p.cluster in LEG_CLUSTERS or energy_dir:
                if p.leg_neutral is None:
                    err("R12", pw, "iran/oil/energy-direction row: leg_neutral is required (doctrine 16.15)")
                else:
                    ln = p.leg_neutral
                    if not re.search(r"\d", ln.reversal_trigger):
                        err("R12", pw, "leg_neutral.reversal_trigger must be dated/numeric, not a mood")
                    if len(ln.evidence.strip()) < 12:
                        err("R12", pw, "leg_neutral.evidence: cite the 10-session datapoints")
                    if ln.same_direction_as_call and p.row_class not in ("invariant", "duration", "marker"):
                        same_dir_leg_rows.append(pw)
                        if p.prob > 0.55 + 1e-9:
                            err("R12", pw, f"leg-extrapolation (call runs WITH the last 10 sessions): cap P at 0.55 "
                                           f"(got {p.prob}) or re-express as a physical invariant")

            # R25 / R26 - outside view first
            if p.reference is None:
                err("R25", pw, "reference is required: decide the base rate and its comparison class BEFORE the probability")
            else:
                rf = p.reference
                if not (0.0 < rf.base_rate < 1.0):
                    err("R25", pw, f"reference.base_rate {rf.base_rate} must be strictly between 0 and 1")
                if len(rf.base_class.strip()) < 12 or not re.search(r"\d", rf.base_class):
                    err("R25", pw, "reference.base_class: name the comparison class WITH its count and source")
                if rf.market_prob is not None:
                    if not (0.0 < rf.market_prob < 1.0):
                        err("R25", pw, f"reference.market_prob {rf.market_prob} must be strictly between 0 and 1")
                    if len(rf.market_src.strip()) < 12:
                        err("R25", pw, "reference.market_src: venue, contract, spread/volume - or leave the market out")
                ref = rf.market_prob if rf.market_prob is not None else rf.base_rate
                if abs(p.prob - ref) > 0.10 + 1e-9 and (len(rf.divergence_reason.strip()) < 20
                                                        or not re.search(r"\d", rf.divergence_reason)):
                    err("R26", pw, f"P {p.prob} is {p.prob - ref:+.2f} off the reference {ref}: divergence_reason must "
                                   "name a DATED datapoint the reference lacks - or re-price toward it")

            # R27 - forecast durations, levels and markers, not the direction of the next leg
            if p.cluster == "iran-war" and p.row_class == "direction":
                err("R27", pw, "iran-war direction row: 0-for-8 on the direction of the next leg. Re-express as a "
                               "duration ('the pause lasts beyond D'), a marker ('monitors/guarantee announced by D'), "
                               "a physical level or an invariant (doctrine 16.18)")
            if p.row_class == "duration":
                co = p.cycle_odds
                if co is None or p.phase_ends is None:
                    err("R27", pw, "duration row: run tools/cycle_odds.py, fill cycle_odds, and set phase_ends")
                else:
                    if "cycle_odds.py" not in co.command:
                        err("R27", pw, "cycle_odds.command must be the cycle_odds.py invocation that was run")
                    if not (0.0 <= co.ends_lo <= co.ends_hi <= 1.0):
                        err("R27", pw, f"cycle_odds band {co.ends_lo}..{co.ends_hi} is not a probability band")
                    else:
                        lo, hi = (co.ends_lo, co.ends_hi) if p.phase_ends else (1 - co.ends_hi, 1 - co.ends_lo)
                        outside = p.prob < lo - 0.10 - 1e-9 or p.prob > hi + 0.10 + 1e-9
                        if outside and (len(co.catalyst.strip()) < 20 or not re.search(r"\d", co.catalyst)):
                            err("R27", pw, f"P {p.prob} is more than 0.10 outside the cycle band {lo:.2f}..{hi:.2f}: "
                                           "cycle_odds.catalyst must name a dated capital-committed catalyst, or re-price")

            # R13
            if p.prob >= 0.70 - 1e-9 and p.row_class not in ("invariant", "scheduled-print"):
                err("R13", pw, f"P {p.prob} >= 0.70 is reserved for invariant / scheduled-print rows "
                               f"(this is {p.row_class}) until the ledger's resolution clears 0.02")
            if p.prob >= 0.80 - 1e-9 and p.row_class == "scheduled-print" and len(p.print_guide.strip()) < 12:
                err("R13", pw, "P >= 0.80 on a print: print_guide must cite the issuer's own guide for the period")

            # R14 / R15
            n_cluster = ctx.open_by_cluster.get(p.cluster, 0) if p.cluster else 0
            share = (n_cluster / ctx.open_total) if (p.cluster and ctx.open_total) else 0.0
            over_cap = share > CLUSTER_CAP
            reasons = []
            if conv >= 0.65 - 1e-9:
                reasons.append(f"conviction {conv:.2f} >= 0.65")
            if p.cluster and n_cluster >= 4:
                reasons.append(f"{n_cluster} open rows already in '{p.cluster}'")
            if over_cap:
                reasons.append(f"'{p.cluster}' is {share:.0%} of the open book (cap 35%)")
            if reasons:
                if p.red_team is None:
                    err("R14", pw, "red-team gate required: " + "; ".join(reasons))
                else:
                    for f_ in dataclasses.fields(p.red_team):
                        val = getattr(p.red_team, f_.name)
                        if isinstance(val, str) and f_.name != "verdict" and len(val.strip()) < 8:
                            err("R14", pw, f"red_team.{f_.name} is empty")
                    if p.red_team.verdict != "PASS":
                        err("R14", pw, "red-team gate verdict is FAIL -> do not ledger at this conviction")
            if over_cap and not p.concentration_note.strip():
                err("R15", pw, f"'{p.cluster}' is {share:.0%} of the open book: concentration_note must justify "
                               "adding to an over-weight cluster")

            # R16
            for s in p.sectors:
                if s not in ctx.sector_keys:
                    err("R16", pw, f"unknown sector {s!r} (see data/sector_map.json)")
            for t in p.tickers:
                if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,6}", t):
                    err("R16", pw, f"ticker {t!r} is not an upper-case symbol")

            # R17
            tw = p.timeline
            if (tw.attach_to is None) == (tw.new_node is None):
                err("R17", pw, "timeline: give exactly one of attach_to / new_node")
            if tw.attach_to is not None and tw.attach_to not in ctx.node_ids:
                err("R17", pw, f"timeline.attach_to {tw.attach_to!r} is not a node in data/timelines.json")
            if tw.new_node is not None:
                nn = tw.new_node
                if nn.id in ctx.node_ids:
                    err("R17", pw, f"new_node.id {nn.id!r} already exists")
                if nn.parent not in ctx.node_ids and nn.parent != "now":
                    err("R17", pw, f"new_node.parent {nn.parent!r} does not exist")
                if nn.lane not in ctx.lanes:
                    warn("R17", pw, f"new_node.lane {nn.lane!r} is a NEW lane (existing: {sorted(ctx.lanes)})")
                if not (0.0 <= nn.p <= 1.0):
                    err("R17", pw, f"new_node.p {nn.p} is not a probability")
                if not _ISO_DATE.match(nn.date):
                    err("R17", pw, f"new_node.date {nn.date!r} is not YYYY-MM-DD")
                if not re.fullmatch(r"[a-z0-9][a-z0-9\-]{2,40}", nn.id):
                    err("R17", pw, f"new_node.id {nn.id!r} must be a lower-case slug")

            # R18
            blob = " ".join((p.prediction, p.sensitivity, e.market.horizon_match, " ".join(e.market.channels)))
            if _SIZING.search(blob):
                err("R18", pw, "sizing language found - this layer does direction and mechanism only (doctrine 14)")

            # R24
            key = re.sub(r"\W+", " ", p.prediction.lower()).strip()
            if key in texts or key in ctx.existing_predictions:
                err("R24", pw, "this prediction text is already in the batch or the ledger")
            texts.add(key)

            # ══ v3 rules: every one below is a resolved loss made unrepeatable ══
            blob = f"{p.prediction} {p.falsifier} {p.sensitivity}"

            # R30 - who decides, from which number, read how
            rs = p.resolution_source
            if rs is None:
                err("R30", pw, "no resolution_source: name the publisher, the series and the reading "
                               "convention BEFORE the horizon (#59 was scored against the engine on scope)")
            else:
                for fname, val, minlen in (("publisher", rs.publisher, 3), ("series", rs.series, 4),
                                           ("convention", rs.convention, 8)):
                    if len(val.strip()) < minlen:
                        err("R30", pw, f"resolution_source.{fname} is empty or too thin to settle a dispute")

            # R36 - a conjunction is priced off its weakest leg, or it is not priced
            if p.conjunction is not None:
                cj = p.conjunction
                if len(cj.legs) < 2 or len(cj.legs) != len(cj.leg_probs):
                    err("R36", pw, "conjunction needs >= 2 legs and one probability per leg")
                elif any(not 0.0 < q < 1.0 for q in cj.leg_probs):
                    err("R36", pw, "every conjunction leg probability must be strictly between 0 and 1")
                elif p.prob > min(cj.leg_probs) + 1e-9:
                    err("R36", pw, f"conjunctive row priced {p.prob} above its weakest leg "
                                   f"{min(cj.leg_probs)} - a joint event cannot beat its hardest part (#63)")
            elif any(m.split(":")[0].startswith("COMPOUND") for m in msgs):
                err("R36", pw, "wording is conjunctive: declare conjunction{legs, leg_probs} so the PRICE is "
                               "checked too - rewording a compound AND does not fix what it cost (#63, #39)")

            # R29 - a spread between unequal legs is a levered direction bet
            if len(p.tickers) == 2 and p.row_class not in ("invariant", "scheduled-print"):
                if p.relative_value is None:
                    err("R29", pw, "two-ticker row: declare relative_value with both legs' realized vol - "
                                   "an RV row between unequal legs is a direction bet (#74)")
                else:
                    rv = p.relative_value
                    if rv.low_vol_daily <= 0:
                        err("R29", pw, "relative_value.low_vol_daily must be a positive realized vol")
                    else:
                        ratio = rv.high_vol_daily / rv.low_vol_daily
                        if ratio > 1.5 + 1e-9:
                            if p.prob > 0.55 + 1e-9:
                                err("R29", pw, f"vol ratio {ratio:.1f}x: this is a levered direction bet on "
                                               f"{rv.high_vol_ticker}, not a spread - cap P at 0.55 (got {p.prob})")
                            if p.row_class not in ("direction", "level-range"):
                                err("R29", pw, f"vol ratio {ratio:.1f}x: row_class must be 'direction' - the "
                                               f"{rv.high_vol_ticker} leg carries the risk (13h)")

            # R32 - a plan is a negotiating instrument, not a forecast
            if p.planning is not None:
                if not p.planning.execution_signal.strip() and p.prob > 0.35 + 1e-9:
                    err("R32", pw, f"rests on a reported plan with no execution signal: cap P at 0.35 "
                                   f"(got {p.prob}) - 16.14, validated by #72")
            elif _PLANNING.search(blob):
                err("R32", pw, "wording rests on a reported plan/intention: declare planning{} with the "
                               "execution signal, or the 0.35 cap applies (#72 - a leaked plan is not an action)")

            # R35 - one meeting is strictly harder than the window around it
            if p.meeting is not None:
                mt = p.meeting
                if not _ISO_DATE.match(mt.meeting_date):
                    err("R35", pw, f"meeting.meeting_date {mt.meeting_date!r} is not YYYY-MM-DD")
                if not 0.0 < mt.window_prob < 1.0:
                    err("R35", pw, "meeting.window_prob must be strictly between 0 and 1")
                elif p.prob > mt.window_prob + 1e-9:
                    err("R35", pw, f"single-meeting P {p.prob} exceeds the window P {mt.window_prob}: a dated "
                                   f"meeting is a SUBSET of the window containing it (#26)")
            elif _COMMITTEE.search(blob) and _MEETING_WORD.search(blob):
                err("R35", pw, "names a committee and a meeting: declare meeting{} with the probability of the "
                               "same claim over the containing window, so the subset relation is checked (#26)")

            # R31 - do not talk yourself out of your own call inside one lag length
            if p.self_downgrade is not None:
                sd = p.self_downgrade
                if sd.ledger_id not in ctx.open_ledger_ids:
                    err("R31", pw, f"self_downgrade names #{sd.ledger_id}, which is not an open row")
                if sd.lag_length_days <= 0:
                    err("R31", pw, "self_downgrade.lag_length_days must be the mechanism's own lag, in days")
                elif sd.data_days < sd.lag_length_days:
                    err("R31", pw, f"reversing #{sd.ledger_id} on {sd.data_days}d of contrary data against a "
                                   f"{sd.lag_length_days}d lag: less than one lag length is noise (13g, #76)")
                if len(sd.mechanism.strip()) < 12:
                    err("R31", pw, "self_downgrade.mechanism: name the lag you are claiming has run")

            # R33 - a row at the book's own base rate carries no information (warning)
            ref_block = p.reference
            no_diverge = ref_block is None or len(ref_block.divergence_reason.strip()) < 20
            if abs(p.prob - ctx.book_base_rate) <= 0.05 and no_diverge:
                warn("R33", pw, f"P {p.prob} sits within 0.05 of the book's own base rate "
                                f"{ctx.book_base_rate} with no divergence_reason: this row cannot earn "
                                f"resolution - a flat forecast would score the same")

            # R28 / R34 - the book against itself
            declared_contra = {c.ledger_id for c in p.contradicts}
            declared_indep = {i.ledger_id for i in p.independence}
            for c in p.contradicts:
                if c.ledger_id not in ctx.open_ledger_ids:
                    err("R28", pw, f"contradicts #{c.ledger_id}, which is not an open row")
                if len(c.hedge_reason.strip()) < 20:
                    err("R28", pw, f"contradicts #{c.ledger_id} with no hedge_reason: two of your own rows "
                                   f"disagreeing is a hedge, not two insights (lesson 7)")
            for i in p.independence:
                if i.ledger_id not in ctx.open_ledger_ids:
                    err("R34", pw, f"independence names #{i.ledger_id}, which is not an open row")
                if len(i.argument.strip()) < 20:
                    err("R34", pw, f"independence from #{i.ledger_id} is asserted, not argued")
            mine = {t.upper() for t in p.tickers}
            for oid, orow in sorted(ctx.open_rows.items()):
                if not mine & {t.upper() for t in orow.tickers}:
                    continue
                if not _overlaps(p.horizon, orow.horizon):
                    continue
                if (p.direction, orow.direction) in _OPPOSED and oid not in declared_contra:
                    err("R28", pw, f"opposes open row #{oid} on {sorted(mine & {t.upper() for t in orow.tickers})} "
                                   f"({p.direction} vs {orow.direction}) over an overlapping horizon and does not "
                                   f"declare it - #26 contradicted the engine's own #32 and both stayed live")
                elif p.direction == orow.direction and p.direction in ("up", "down") \
                        and oid not in declared_indep:
                    err("R34", pw, f"same asset and same direction as open row #{oid} over an overlapping "
                                   f"horizon: this is one bet logged twice unless independence is argued "
                                   f"(#70 and #27 were one SMH bet and missed together)")

            batch_rows.append((pw, p))

    if len(same_dir_leg_rows) > 1:
        err("R12", ", ".join(same_dir_leg_rows),
            "more than ONE same-direction iran/oil row in a single batch - they share one premise and "
            "live or die together; keep the best one")

    # R28 / R34 within the batch itself - two rows written in the same sitting can be one bet,
    # or can disagree, just as easily as a new row and an old one.
    for a in range(len(batch_rows)):
        wa, pa = batch_rows[a]
        ta = {t.upper() for t in pa.tickers}
        for b in range(a + 1, len(batch_rows)):
            wb, pb = batch_rows[b]
            shared = ta & {t.upper() for t in pb.tickers}
            if not shared or not _overlaps(pa.horizon, pb.horizon):
                continue
            if (pa.direction, pb.direction) in _OPPOSED:
                err("R28", f"{wa} vs {wb}", f"the same batch takes both sides of {sorted(shared)} over "
                                            f"overlapping horizons - that is a hedge, not two insights")
            elif pa.direction == pb.direction and pa.direction in ("up", "down"):
                err("R34", f"{wa} vs {wb}", f"both rows are the same direction on {sorted(shared)} over "
                                            f"overlapping horizons - one bet, logged twice (#70/#27)")

    # R21
    for i, r in enumerate(doc.suggested_resolutions):
        if r.ledger_id not in ctx.open_ledger_ids:
            err("R21", f"suggested_resolutions[{i}]", f"#{r.ledger_id} is not an open ledger row")
        if len(r.evidence.strip()) < 12:
            err("R21", f"suggested_resolutions[{i}]", "evidence is empty")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rules":
        for k, v in RULES.items():
            print(f"{k}  {v}")
    else:
        print(json.dumps(json_schema(), indent=1))
