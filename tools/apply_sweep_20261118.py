#!/usr/bin/env python3
"""Apply the 18 Nov 2026 mechanism sweep (reports/desk/20261118_mechanism-sweep-ai.md, P1-P11) to data/timelines.json.
User instruction, 18 Nov PT: "apply engine odds to map". Idempotent: re-running skips nodes/edges already present.
    python tools/apply_sweep_20261118.py
"""
import json, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / "data" / "timelines.json"
SRC = "reports/desk/20261118_mechanism-sweep-ai.md"
tl = json.loads(P.read_text(encoding="utf-8"))
nodes = {n["id"]: n for n in tl["nodes"]}


def ev(n, fact):
    if not isinstance(n.get("evidence"), list):
        n["evidence"] = []
    n["evidence"].append({"fact": fact, "reported": "2026-11-18"})


def set_p(nid, p, why):
    n = nodes[nid]
    old = n.get("p")
    if old != p:
        n["p"] = p
        ev(n, f"Re-marked {old} -> {p} on 18 Nov (mechanism sweep, {SRC}): {why}")


def edge(nid, target, p_to, note):
    n = nodes[nid]
    n.setdefault("shifts", [])
    if not any(s["target"] == target for s in n["shifts"]):
        n["shifts"].append({"target": target, "p_to": p_to, "date_delta": 0, "note": note})


def add(nid, **kw):
    if nid in nodes:
        return
    n = {"id": nid, "ledger": [], "evidence": [{"fact": f"Added 18 Nov from the mechanism sweep ({SRC})", "reported": "2026-11-18"}]}
    n.update(kw)
    tl["nodes"].append(n)
    nodes[nid] = n


# P1 read neocloud stress at the contract
set_p("ai-financing-chain", 0.82, "contract gauges healthy: new secured loans 7-7.5%, prepayments >100% of capex, H100 rent +58% y/y; "
      "a new CDS high counts only if a contract gauge confirms (new loans >10%, prepayments <50% of capex)")
# P3 permitting is a supply shock (timing, not demand)
set_p("capex-sprint", 0.37, "permitting delays move 3 points from sprint to digestion (timing, not demand)")
set_p("capex-digestion", 0.43, "permitting delays move 3 points from sprint to digestion (timing, not demand)")
# P7 Gulf re-escalation window to 3 Jan
set_p("frozen-tanker-war", 0.80, "re-escalation window to ~3 Jan: US strike 2 Nov, Iranian drones on a US base in Bahrain 15 Nov, third carrier group")
set_p("postmidterm-campaign", 0.15, "takes the 5 points from frozen-tanker-war (siblings sum to 1.0)")
# P9 capex is GDP demand
edge("ai-winter", "fed-h1-no-cuts", 0.70, "a 2027 capex decline is a demand shock (~3% of GDP, -0.75pp growth): no net easing in H1 falls to 0.70; long-end relief not implied (fiscal premium)")

# P2 Nvidia after its CEO's exit
add("nvda-support-lines", lane="markets-ai", parent="now", kind="event", date="2027-03-03", p=0.35,
    label="Nvidia's guarantee and credit-support lines flat or lower in the FY27 10-K",
    rationale="Interim CEO counts customers' access to capital in guidance; a vendor that stops extending support marks the financing chain's next link.",
    shifts=[{"target": "ai-financing-chain", "p_to": 0.77, "date_delta": 0, "note": "vendor stops financing customers: financing accident +0.05"},
            {"target": "capex-sprint", "p_to": 0.34, "date_delta": 0, "note": "less vendor finance, -0.03 to another 30%+ year"}])
# P3 state permitting node
add("dc-permitting-states", lane="us-politics", parent="now", kind="event", date="2027-07-31", p=0.75,
    label="At least 2 of Virginia, Texas, Georgia and Ohio restrict or reprice large data-centre approvals by 31 Jul 2027",
    rationale="46 of 47 local measures on 3 Nov favoured restriction; Texas freeze kept by the governor-elect; moratoria pending in ~14 states. Check first whether the Texas freeze counts as formal.",
    shifts=[{"target": "capex-digestion", "p_to": 0.46, "date_delta": 0, "note": "sites later, not demand lower"},
            {"target": "capex-sprint", "p_to": 0.34, "date_delta": 0, "note": "sites later, not demand lower"}])
# P5 Iran secondary sanctions tied to the truce
add("us-designates-cn-iran-buyer", lane="china-macro", parent="now", kind="event", date="2027-01-09", p=0.12,
    label="US designates a major Chinese refiner, terminal or bank over Iranian oil before 10 Jan 2027",
    rationale="China takes >80% of Iran's shipped barrels; no secondary sanctions on Chinese firms since Sept. Truce lapse ~60% with a designation, ~31% without (total 34% unchanged).",
    shifts=[{"target": "ev-busan-truce-rolled", "p_to": 0.40, "date_delta": 0, "note": "a designation lands on the truce: rollover 0.40 (lapse 0.60)"}])
# P6 Taiwan split (conditional on action by mid-2027) + second horizon
for nid, p, label, p_to in (("tw-quarantine", 0.45, "Form of PLA action: quarantine or blockade", 0.65),
                            ("tw-grayzone-kinetic", 0.40, "Form of PLA action: limited kinetic gray-zone action", 0.30),
                            ("tw-invasion", 0.15, "Form of PLA action: invasion", 0.85)):
    add(nid, lane="taiwan-china", parent="taiwan-h1-2027", kind="branch", date="2027-06-30", p=p, label=label,
        rationale="Split of the 10% PLA-action node: invasion 1.5%, quarantine/blockade 4.5%, gray-zone kinetic 4% (weighted capex-decline impact 54%, vs the parent edge 55%).",
        shifts=[{"target": "ai-winter", "p_to": p_to, "date_delta": 0, "note": "TSMC advanced packaging is the point every print runs through"}])
add("taiwan-2028", lane="taiwan-china", parent="now", kind="event", date="2028-12-31", p=0.15,
    label="PLA action on Taiwan by 31 Dec 2028 (quarantine the modal form)",
    rationale="Keyed to PLA readiness in 2027 and Taiwan's January 2028 election; the constraint window opens after the Arizona ramp.",
    shifts=[{"target": "fragmented-blocs", "p_to": 0.60, "date_delta": 0, "note": "a Taiwan crisis hardens the blocs"}])
# P7 Gulf window nodes
add("us-iran-campaign-jan3", lane="iran-energy", parent="now", kind="event", date="2027-01-03", p=0.18,
    label="Multi-day US strike campaign or ground operation inside Iran, 18 Nov 2026 - 3 Jan 2027",
    rationale="Lame-duck and Israeli caretaker windows run to ~3 Jan; escalation called imminent ~10 times before (discounted). Troops in theatre earn no credit; supply lines do.",
    shifts=[{"target": "fed-h1-no-cuts", "p_to": 0.93, "date_delta": 0, "note": "AI route only through oil -> core inflation -> Fed; no oil call"}])
add("iran-ground-op", lane="iran-energy", parent="us-iran-campaign-jan3", kind="event", date="2027-01-03", p=0.22,
    label="...of which a US ground operation inside Iran (0.04 unconditional)",
    rationale="Counted only when supply lines are built, not when troops arrive.")
add("iran-ends-by-purchase", lane="iran-energy", parent="now", kind="event", date="2027-03-31", p=0.20,
    label="Iran war ends by purchase (money for access) by 31 Mar 2027",
    rationale="Midterm result favours an end by purchase; correlated with the 22% strait-reopening read (1 - hormuz-impaired-q1).",
    shifts=[{"target": "fed-h1-no-cuts", "p_to": 0.87, "date_delta": 0, "note": "slight rate relief only; the Fed's driver is core inflation"}])
# P8 lab revenue as a print
add("lab-dec-runrate", lane="markets-ai", parent="now", kind="event", checkpoint=True, date="2027-01-15", p=1.0,
    label="A large AI lab's December revenue run-rate disclosed (estimate $86-90bn)",
    rationale="Lab run-rates now move the chip group like a print (Sept ~$70bn vs high-$70s expected). Input only; no view on any lab's shares.",
    shifts=[{"target": "ai-h1-repair", "p_to": 0.30, "date_delta": 0, "note": "if below $80bn (above $90bn: 0.40)"},
            {"target": "capex-sprint", "p_to": 0.34, "date_delta": 0, "note": "if below $80bn (above $90bn: 0.40)"}])
# P11 retaliation tied to the 16 Nov rule
add("cn-retaliation-remote-rule", lane="china-macro", parent="now", kind="event", date="2027-01-15", p=0.15,
    label="China retaliates explicitly against the 16 Nov remote-access rule by ~15 Jan 2027",
    rationale="Licence-based rule with a 90-day wind-down draws lobbying first; the 27 Nov gallium lapse is a scheduled clock, not retaliation.",
    shifts=[{"target": "ev-busan-truce-rolled", "p_to": 0.50, "date_delta": 0, "note": "retaliation lowers the rollover odds"}])

tl["updated"] = "2026-11-18"
P.write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
print("applied; nodes:", len(tl["nodes"]))
