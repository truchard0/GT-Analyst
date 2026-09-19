#!/usr/bin/env python3
"""Record a TradingAgents debate verdict into data/fusion.json.

Usage:
  python tools/record_ta.py --ticker NVDA --sector semis_ai --verdict BUY \
      --confidence 0.7 --price 171.20 --summary "Bull case won on ..."

Verdict in {BUY, HOLD, SELL}; confidence 0-1. Score mapping:
BUY -> +confidence, SELL -> -confidence, HOLD -> 0.
Also recomputes the sector's fused score (0.5*topdown + 0.5*mean ticker score).
"""
import argparse
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUSION = ROOT / "data" / "fusion.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--sector", required=True, help="key in fusion.json sectors")
    ap.add_argument("--verdict", required=True, choices=["BUY", "HOLD", "SELL"])
    ap.add_argument("--confidence", type=float, required=True)
    ap.add_argument("--price", default="", help="price at verdict time")
    ap.add_argument("--summary", required=True, help="one-paragraph debate outcome")
    args = ap.parse_args()

    d = json.loads(FUSION.read_text(encoding="utf-8"))
    if args.sector not in d["sectors"]:
        raise SystemExit(f"unknown sector {args.sector}; have {list(d['sectors'])}")

    score = {"BUY": args.confidence, "SELL": -args.confidence, "HOLD": 0.0}[args.verdict]
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%MZ")
    entry = {"verdict": args.verdict, "confidence": args.confidence, "score": round(score, 3),
             "price_at_verdict": args.price, "summary": args.summary, "recorded": now}

    sec = d["sectors"][args.sector]
    sec.setdefault("bottomup", {}).setdefault("tickers", {})[args.ticker.upper()] = entry
    d["ticker_verdicts"][args.ticker.upper()] = {**entry, "sector": args.sector}

    scores = [t["score"] for t in sec["bottomup"]["tickers"].values()]
    bu_mean = sum(scores) / len(scores)
    td = sec["topdown"]["score"]
    fused = round(0.5 * td + 0.5 * bu_mean, 3)
    same_sign = (td > 0.15 and bu_mean > 0.15) or (td < -0.15 and bu_mean < -0.15)
    conflict = (td > 0.15 and bu_mean < -0.15) or (td < -0.15 and bu_mean > 0.15)
    sec["fused"] = {"score": fused, "bottomup_mean": round(bu_mean, 3),
                    "badge": "CONFIRM" if same_sign else "CONFLICT" if conflict else "MIXED"}
    d["updated"] = now
    FUSION.write_text(json.dumps(d, indent=2), encoding="utf-8")
    print(f"recorded {args.ticker.upper()} {args.verdict} ({args.confidence:.2f}) -> "
          f"{args.sector} fused={fused} badge={sec['fused']['badge']}")


if __name__ == "__main__":
    main()
