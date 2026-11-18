#!/usr/bin/env python3
"""Learning loop: train a calibration model on the scored ledger, test it out of sample, run it in shadow.

WHY. On the 56 calls scored by 2026-11-14 the stated probabilities could not tell hits from misses (AUC 0.47)
and scored worse (Brier 0.236) than saying the base rate every time (0.224). What did carry information was
the TYPE of call (ledger column `kind`). This module turns that into a trained model and tests it the hard way.
It does not retrain the language model that writes the analysis. It trains the correction applied on top.

  train       fit P(call comes true | call type) with shrinkage; save data/learn/model.json
  validate    leave-one-out and leave-one-cluster-out Brier for every level below
  shadow      log the model's probability for every open call (append-only, data/learn/shadow.csv)
  scoreboard  forward test: stated vs model on calls that resolved AFTER the model first saw them
  nightly     all of the above, plus data/learn/report.md   (tools/server_loop.py runs this once a day)
  prior KIND  print the trained prior for one call type (ledger.py add shows it at logging time)

LEVELS, simplest first. A more complex level is only worth using if it beats the simpler one out of sample:
  coin 0.50  ->  base rate  ->  type model  ->  50/50 blend of type model and stated  ->  stated (the analyst)

INDEPENDENCE. Calls in one cluster rise and fall together, so the unit is the CLUSTER: the strict test leaves a
whole cluster out, and the bootstrap resamples whole clusters.

PROMOTION RULE (pre-registered 2026-11-18; do not edit once forward calls start resolving).
The model stays in SHADOW until FORWARD_MIN calls that it saw while they were open have resolved. Then:
  promote  Brier(model) <= Brier(stated) - MARGIN  -> published probabilities become the 50/50 blend
  retire   Brier(model) >= Brier(stated) + MARGIN  -> the model is dropped and the type caps in ledger.py reviewed
  else     keep shadowing
Stdlib only. Parses on Python 3.11.
"""
import csv
import hashlib
import json
import pathlib
import random
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, utc_iso

DB = ROOT / "ledger" / "ledger.db"
OUT = ROOT / "data" / "learn"
MODEL = OUT / "model.json"
SHADOW = OUT / "shadow.csv"
VALIDATION = OUT / "validation.json"
REPORT = OUT / "report.md"

SHRINK = 3.0          # pseudo-count pulling a type's hit rate toward the overall rate
FORWARD_MIN = 20      # forward-resolved calls needed before any promotion decision
MARGIN = 0.01         # Brier margin for promote / retire
BOOT = 2000
SHADOW_COLS = ["logged_utc", "pred_id", "kind", "cluster", "stated", "model", "blend", "model_version"]


def rows(resolved=True):
    """Ledger rows as dicts. A blank cluster is its own cluster; a blank kind is 'untagged'."""
    c = sqlite3.connect(DB)
    cols = {r[1] for r in c.execute("PRAGMA table_info(predictions)")}
    kind = "COALESCE(NULLIF(kind,''),'untagged')" if "kind" in cols else "'untagged'"
    where = "outcome IS NOT NULL" if resolved else "outcome IS NULL"
    out = []
    for i, ts, hz, p, o, k, cl, rts in c.execute(
            f"SELECT id, ts, horizon, prob, outcome, {kind}, COALESCE(cluster,''), resolved_ts "
            f"FROM predictions WHERE {where} ORDER BY id"):
        out.append({"id": i, "ts": ts, "horizon": hz, "p": p, "o": o, "kind": k,
                    "cluster": cl or f"solo-{i}", "resolved_ts": rts})
    return out


def fit(train):
    """The type model: per-type hit rate shrunk toward the overall rate."""
    n = len(train)
    base = sum(r["o"] for r in train) / n if n else 0.5
    kinds = {}
    for r in train:
        k = kinds.setdefault(r["kind"], {"n": 0, "hits": 0})
        k["n"] += 1
        k["hits"] += r["o"]
    for k in kinds.values():
        k["p"] = (k["hits"] + SHRINK * base) / (k["n"] + SHRINK)
    return {"base": base, "n": n, "kinds": kinds}


def predict(model, kind):
    k = model["kinds"].get(kind)
    return k["p"] if k else model["base"]


def brier(ps, os_):
    return sum((p - o) ** 2 for p, o in zip(ps, os_)) / len(os_) if os_ else float("nan")


def auc(ps, os_):
    pos = [p for p, o in zip(ps, os_) if o == 1]
    neg = [p for p, o in zip(ps, os_) if o == 0]
    if not pos or not neg:
        return float("nan")
    return sum((1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg) / (len(pos) * len(neg))


def version(train):
    h = hashlib.sha1(json.dumps(sorted((r["id"], r["o"], r["kind"]) for r in train)).encode()).hexdigest()[:8]
    return f"n{len(train)}-{h}"


def train(quiet=False):
    data = rows()
    if len(data) < 10:
        sys.exit(f"need at least 10 resolved calls to train (have {len(data)})")
    model = fit(data)
    model.update(version=version(data), trained_utc=utc_iso(), shrink=SHRINK, status=status_of(model=None))
    OUT.mkdir(parents=True, exist_ok=True)
    MODEL.write_text(json.dumps(model, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if not quiet:
        print(f"trained model {model['version']}: base rate {model['base']:.3f} on {model['n']} resolved calls")
        for k, v in sorted(model["kinds"].items(), key=lambda kv: -kv[1]["p"]):
            print(f"  {k:10s} n={v['n']:2d} right={v['hits']:2d} trained prior={v['p']:.2f}")
    return model


def held_out(data, key):
    """Out-of-sample type-model and base-rate predictions: leave out each call (key='id') or its whole cluster."""
    model_p, base_p = [], []
    for r in data:
        rest = [t for t in data if t[key] != r[key]]
        m = fit(rest)
        model_p.append(predict(m, r["kind"]))
        base_p.append(m["base"])
    return model_p, base_p


def cluster_boot(data, a, b):
    """Cluster bootstrap of mean((a-o)^2 - (b-o)^2): share of resamples where b beats a, and a 90% interval."""
    by = {}
    for r, pa, pb in zip(data, a, b):
        by.setdefault(r["cluster"], []).append((pa - r["o"]) ** 2 - (pb - r["o"]) ** 2)
    names = sorted(by)
    rng = random.Random(7)
    diffs = []
    for _ in range(BOOT):
        pick = [d for n in (rng.choice(names) for _ in names) for d in by[n]]
        diffs.append(sum(pick) / len(pick))
    diffs.sort()
    return {"p_better": sum(d > 0 for d in diffs) / BOOT, "lo": diffs[int(0.05 * BOOT)],
            "hi": diffs[int(0.95 * BOOT) - 1], "clusters": len(names)}


def validate(quiet=False):
    data = rows()
    os_ = [r["o"] for r in data]
    stated = [r["p"] for r in data]
    res = {"n": len(data), "hits": sum(os_), "clusters": len({r["cluster"] for r in data}),
           "auc_stated": auc(stated, os_), "tests": {}}
    for name, key in (("leave-one-out", "id"), ("leave-one-cluster-out", "cluster")):
        mp, bp = held_out(data, key)
        blend = [(a + b) / 2 for a, b in zip(mp, stated)]
        res["tests"][name] = {
            "coin": 0.25, "base_rate": brier(bp, os_), "type_model": brier(mp, os_),
            "blend": brier(blend, os_), "stated": brier(stated, os_), "auc_type_model": auc(mp, os_),
            "model_vs_stated": cluster_boot(data, stated, mp)}
    OUT.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if not quiet:
        print(f"{res['n']} resolved calls, {res['hits']} right, {res['clusters']} clusters. "
              f"AUC of the stated probabilities: {res['auc_stated']:.2f} (0.50 = cannot tell hits from misses)")
        for name, t in res["tests"].items():
            b = t["model_vs_stated"]
            print(f"  {name}: coin 0.250 | base rate {t['base_rate']:.3f} | type model {t['type_model']:.3f} | "
                  f"blend {t['blend']:.3f} | stated {t['stated']:.3f}")
            print(f"    type model beats stated in {b['p_better']:.0%} of cluster resamples "
                  f"(Brier gain {b['lo']:+.3f} to {b['hi']:+.3f}, 90% interval)")
    return res


def load_model():
    return json.loads(MODEL.read_text(encoding="utf-8")) if MODEL.exists() else None


def read_shadow():
    if not SHADOW.exists():
        return []
    with open(SHADOW, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def shadow(quiet=False):
    """Append the model's probability for every open call it has not yet logged under this model version."""
    model = load_model() or train(quiet=True)
    have = {(r["pred_id"], r["model_version"]) for r in read_shadow()}
    new = []
    for r in rows(resolved=False):
        if (str(r["id"]), model["version"]) in have:
            continue
        m = predict(model, r["kind"])
        new.append({"logged_utc": utc_iso(), "pred_id": r["id"], "kind": r["kind"], "cluster": r["cluster"],
                    "stated": f"{r['p']:.4f}", "model": f"{m:.4f}", "blend": f"{(m + r['p']) / 2:.4f}",
                    "model_version": model["version"]})
    OUT.mkdir(parents=True, exist_ok=True)
    fresh = not SHADOW.exists()
    with open(SHADOW, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHADOW_COLS)
        if fresh:
            w.writeheader()
        w.writerows(new)
    if not quiet:
        print(f"shadow: +{len(new)} rows under model {model['version']}")
    return len(new)


def forward():
    """Calls that resolved after the model FIRST saw them open: (stated, model, blend, outcome) per call."""
    first = {}
    for r in read_shadow():
        if r["pred_id"] not in first or r["logged_utc"] < first[r["pred_id"]]["logged_utc"]:
            first[r["pred_id"]] = r
    out = []
    for r in rows():
        s = first.get(str(r["id"]))
        if s:                                   # only open calls are ever shadow-logged, so a row means "seen open"
            out.append((float(s["stated"]), float(s["model"]), float(s["blend"]), r["o"], r["id"],
                        r["ts"] >= s["logged_utc"]))          # True = the call was also MADE after the model existed
    return out


def status_of(model=None):
    """shadow | promoted | retired, from the forward scoreboard and the pre-registered rule."""
    fw = forward()
    if len(fw) < FORWARD_MIN:
        return "shadow"
    os_ = [x[3] for x in fw]
    gap = brier([x[0] for x in fw], os_) - brier([x[1] for x in fw], os_)
    return "promoted" if gap >= MARGIN else "retired" if gap <= -MARGIN else "shadow"


def scoreboard(quiet=False):
    fw = forward()
    os_ = [x[3] for x in fw]
    res = {"n": len(fw), "needed": FORWARD_MIN, "status": status_of(),
           "stated": brier([x[0] for x in fw], os_), "model": brier([x[1] for x in fw], os_),
           "blend": brier([x[2] for x in fw], os_), "ids": [x[4] for x in fw],
           "made_after_model": sum(1 for x in fw if x[5])}
    if not quiet:
        if not fw:
            print(f"forward scoreboard: 0 of {FORWARD_MIN} calls resolved since the model began shadowing. "
                  "Status: shadow.")
        else:
            print(f"forward scoreboard: {res['n']} of {FORWARD_MIN} needed. Brier stated {res['stated']:.3f} | "
                  f"model {res['model']:.3f} | blend {res['blend']:.3f} | coin 0.250. Status: {res['status']}. "
                  f"{res['made_after_model']} of them were also made after the model existed.")
    return res


def prior_line(kind, prob):
    """One line for ledger.py add: the trained prior for this call type next to the stated probability."""
    model = load_model()
    if not model:
        return ""
    k = model["kinds"].get(kind)
    if not k:
        return f"TRAINED PRIOR: no scored {kind} calls yet; overall base rate {model['base']:.2f} (model {model['version']})."
    gap = prob - k["p"]
    note = " The stated probability is well above the record for this type." if gap > 0.15 else \
           " The stated probability is well below the record for this type." if gap < -0.15 else ""
    return (f"TRAINED PRIOR: {kind} calls came true {k['hits']} of {k['n']} times; trained prior {k['p']:.2f}, "
            f"stated {prob:.2f} (model {model['version']}, {model.get('status', 'shadow')}).{note}")


def nightly():
    model = train(quiet=True)
    val = validate(quiet=True)
    added = shadow(quiet=True)
    sb = scoreboard(quiet=True)
    model["status"] = sb["status"]
    MODEL.write_text(json.dumps(model, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    L = ["# Learning loop report", "",
         f"Updated {utc_iso()}. Model `{model['version']}`, status **{sb['status']}**.", "",
         f"- Trained on {val['n']} resolved calls ({val['hits']} right) in {val['clusters']} clusters.",
         f"- The stated probabilities separate hits from misses with AUC {val['auc_stated']:.2f} "
         "(0.50 means no separation).", "",
         "## Trained priors by call type", "", "| Type | Scored | Right | Trained prior |", "|---|---|---|---|"]
    for k, v in sorted(model["kinds"].items(), key=lambda kv: -kv[1]["p"]):
        L.append(f"| {k} | {v['n']} | {v['hits']} | {v['p']:.2f} |")
    L += ["", "## Out-of-sample test (Brier, lower is better)", "",
          "| Test | Coin | Base rate | Type model | Blend | Stated | Type model beats stated |", "|---|---|---|---|---|---|---|"]
    for name, t in val["tests"].items():
        L.append(f"| {name} | 0.250 | {t['base_rate']:.3f} | {t['type_model']:.3f} | {t['blend']:.3f} | "
                 f"{t['stated']:.3f} | {t['model_vs_stated']['p_better']:.0%} of cluster resamples |")
    loo, loco = val["tests"]["leave-one-out"], val["tests"]["leave-one-cluster-out"]
    if loo["type_model"] < loo["stated"] and loco["type_model"] >= loco["stated"]:
        L += ["", "Reading: the type model wins when it has already seen calls on the same topic and loses on a topic "
              "it has not seen. The type priors are lessons about these topics, not general laws, so the model "
              "stays in shadow until the forward scoreboard decides."]
    elif loo["type_model"] < loo["stated"] and loco["type_model"] < loco["stated"]:
        L += ["", "Reading: the type model beats the stated probabilities in both tests, including on topics it "
              "has not seen."]
    else:
        L += ["", "Reading: the type model does not beat the stated probabilities out of sample."]
    L += ["", "## Forward scoreboard", ""]
    if sb["n"]:
        L.append(f"{sb['n']} of {FORWARD_MIN} forward calls resolved. Brier: stated {sb['stated']:.3f}, "
                 f"model {sb['model']:.3f}, blend {sb['blend']:.3f}, coin 0.250. "
                 f"{sb['made_after_model']} of them were also made after the model existed; the rest carry "
                 "probabilities stated before it, which favours the model.")
    else:
        L.append(f"0 of {FORWARD_MIN} forward calls resolved so far. {added} new shadow rows logged this run.")
    L += ["", f"Promotion rule: after {FORWARD_MIN} forward calls, promote if the model beats the stated "
          f"probabilities by {MARGIN} Brier, retire if it loses by {MARGIN}, otherwise keep shadowing."]
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"learning loop: model {model['version']} ({sb['status']}), +{added} shadow rows, "
          f"forward {sb['n']}/{FORWARD_MIN} -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "train":
        train()
    elif cmd == "validate":
        validate()
    elif cmd == "shadow":
        shadow()
    elif cmd == "scoreboard":
        scoreboard()
    elif cmd == "nightly":
        nightly()
    elif cmd == "prior" and len(sys.argv) > 2:
        print(prior_line(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.5) or "no model yet - run train")
    else:
        print(__doc__)
