#!/usr/bin/env python3
"""constraints.py - the DECIDERS' calendar: when are strikes held off, and what ends the restraint?

WHY (user, 2026-10-23). The engine forecast the war from the military leg - 'the fighting continues', 'the ceasefire
holds' - and never asked what the deciders wanted in the window. Strikes are held off for political and economic reasons
(the midterms, Netanyahu's campaign, pump prices, requests from the Gulf), so a strike-free window is predictable from the
calendar, and the shock arrives only after the restraint is broken or lapses. data/constraint_calendar.json holds the
dated windows with the public fact behind each (and the first day that fact was public: `known_from`). This module reads it
and applies RULE R37:

  every row about how hard the fighting gets must say   ACT it is about (us_strike_iran, il_strike_iran, ir_attack_us_forces,
  ir_ship_attack), whether it CLAIMS the act occurs or does not occur, the WINDOW it sits in (a calendar id, or 'none' with a
  reason), and the TRIGGER that would end the restraint. Then two checks on facts public on the row's date:

  R37a  a row that says the act OCCURS at P > 0.5 for a horizon that ends inside a known suppress window, with no trigger on
        file in the last 7 days, is refused: price it at 0.5 or below, or name the trigger that has fired and cite it.
  R37b  a row that says the act does NOT occur at P > 0.5 while a trigger was on file in the last 7 days is refused: the
        restraint it assumes was already breaking (#19 and #28 were logged the day after Iran hit vessels, 7/7).

It prices nothing. A window that lapses raises the hazard; it never fires by itself.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from dataclasses import dataclass
from typing import Optional

CAL = pathlib.Path(__file__).resolve().parent.parent / "data" / "constraint_calendar.json"
TRIGGER_DAYS = 7
COVER_SLACK = 3        # a horizon this far past a window's end is no longer 'inside' it
CLAIMS = ("occurs", "does_not_occur")


@dataclass(frozen=True)
class Finding:
    severity: str          # error | warn
    text: str


def load(path: Optional[pathlib.Path] = None) -> dict:
    return json.loads((path or CAL).read_text(encoding="utf-8"))


def d(s) -> dt.date:
    return dt.date.fromisoformat(str(s)[:10])


def windows_for(cal: dict, act: str, on: dt.date, effect: Optional[str] = None) -> list[dict]:
    """Windows that govern `act`, are in force on `on`, and were PUBLIC by `on`."""
    return [w for w in cal["windows"]
            if act in w["acts"] and d(w["start"]) <= on <= d(w["end"]) and d(w["known_from"]) <= on
            and (effect is None or w["effect"] == effect)]


def recent_triggers(cal: dict, on: dt.date, days: int = TRIGGER_DAYS) -> list[tuple[str, str]]:
    return [(a, b) for a, b in cal["triggers"] if 0 <= (on - d(a)).days < days]


def live_triggers(cal: dict, act: str, on: dt.date) -> list[tuple[str, str]]:
    """Triggers in the last 7 days that no later, public stand-down has superseded. If the decider re-chose restraint AFTER a
    trigger (a suppress window whose `known_from` is later than the trigger), the trigger is spent: #72 was logged on 8/2, the
    day Trump said he had called off the planned attack, three days after the 7/29 trigger."""
    trg = recent_triggers(cal, on)
    sup = windows_for(cal, act, on, "suppresses")
    if not sup:
        return trg
    latest = max(d(w["known_from"]) for w in sup)
    return [(a, b) for a, b in trg if d(a) >= latest]


def lens(cal: dict, act: str, on: dt.date) -> dict:
    """What the calendar says about `act` on `on`, using only facts public by then."""
    trg = live_triggers(cal, act, on)
    sup = windows_for(cal, act, on, "suppresses")
    per = windows_for(cal, act, on, "permits")
    net = "trigger" if trg else ("suppress" if sup else ("permit" if per else "neutral"))
    return {"net": net, "suppress": [w["id"] for w in sup], "permit": [w["id"] for w in per], "triggers": trg}


def check_incentive(cal: dict, *, act: str, claims: str, prob: float, window: str, trigger: str = "", horizon: str = "",
                    as_of: dt.date, note: str = "") -> list[Finding]:
    out: list[Finding] = []
    if act not in cal["acts"]:
        return [Finding("error", f"act {act!r} is not one of {sorted(cal['acts'])}")]
    if claims not in CLAIMS:
        return [Finding("error", f"claims must be one of {CLAIMS}, got {claims!r}")]
    by_id = {w["id"]: w for w in cal["windows"]}
    if window.startswith("none"):
        reason = window.split(":", 1)[1].strip() if ":" in window else note.strip()
        if len(reason) < 20:
            out.append(Finding("error", "window 'none' needs a reason of at least 20 characters (name why no decider's calendar "
                                        "bears on this row)"))
    elif window not in by_id:
        return [Finding("error", f"window {window!r} is not in the constraint calendar ({', '.join(sorted(by_id))})")]
    else:
        w = by_id[window]
        if act not in w["acts"]:
            out.append(Finding("error", f"window {window} governs {w['acts']}, not {act}"))
        if d(w["known_from"]) > as_of:
            out.append(Finding("error", f"window {window} was not public until {w['known_from']}; it cannot inform a row dated {as_of}"))
    hz = d(horizon)
    trg = live_triggers(cal, act, as_of)
    if claims == "occurs" and prob > 0.5:
        for w in windows_for(cal, act, as_of, "suppresses"):
            if hz <= d(w["end"]) + dt.timedelta(days=COVER_SLACK) and not trg:
                out.append(Finding("error", f"claims {act} OCCURS at P {prob:.2f} through {horizon}, inside window {w['id']} "
                                            f"({w['strength']}: {w['fact'][:110]}...) with no trigger on file in the last "
                                            f"{TRIGGER_DAYS} days - price it at 0.5 or below, or name the trigger that has fired "
                                            f"({w['trigger']})"))
                break
    if claims == "does_not_occur" and prob > 0.5 and trg:
        a, b = trg[-1]
        if len(trigger.strip()) < 20:
            out.append(Finding("error", f"claims {act} does NOT occur at P {prob:.2f} but a trigger is on file ({a}: {b}): the restraint "
                                        f"was already breaking - say in --trigger why it holds (20+ chars) or price it at 0.5 or below"))
    if claims == "occurs" and trigger and not trg and windows_for(cal, act, as_of, "suppresses"):
        out.append(Finding("warn", "a trigger is named but none is on file in the last 7 days: cite the fact and add it to "
                                   "data/constraint_calendar.json"))
    return out
