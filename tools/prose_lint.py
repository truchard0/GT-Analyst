#!/usr/bin/env python3
"""Prose checker for GT-Analyst reports (report-writing skill, Part B self-edit pass). Stdlib only.

    python tools/prose_lint.py reports/<report>.md [--stop-at "# APPENDIX"]

Flags, per paragraph of body prose (tables, headings, images, code and the Sources section are skipped):
  - LONG     a sentence over 35 words
  - NUMBERS  a sentence with more than two numbers
  - PARENS   more than one parenthesis in a paragraph
  - PARA     a paragraph over 90 words
  - CLUTTER  throat-clearing phrases
Prints the flags with line numbers and a summary (average sentence length, share of sentences flagged).
Exit code 1 if anything is flagged, so it can gate a publish.
"""
import argparse
import re
import sys

CLUTTER = ["note that", "it is worth noting", "importantly,", "in terms of", "it should be noted", "needless to say",
           "at the end of the day", "going forward", "about roughly", "potentially could"]
NUM = re.compile(r"(?<![\w/])[$€£]?\d[\d,]*(?:\.\d+)?\s?(?:%|bn|m|GW|bp|x)?")
MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
# dates and years are not counted as figures: "9 December", "15-23 Dec", "2027", "Q4"
DATE = re.compile(r"\b\d{1,2}(?:\s?(?:-|to|and)\s?\d{1,2})?\s" + MONTHS + r"|\b(?:19|20)\d\d\b|\bF?Q[1-4]\b")


def sentences(text):
    text = re.sub(r"\*\*|`|\[([^\]]+)\]\([^)]+\)", lambda m: m.group(1) or "", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", text.strip())
    return [p for p in parts if p]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--stop-at", default="# APPENDIX")
    a = ap.parse_args()
    lines = open(a.path, encoding="utf-8").read().split("\n")
    flags, n_sent, n_words, n_flagged = [], 0, 0, 0
    in_sources = False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if a.stop_at and s.startswith(a.stop_at):
            break
        if s.startswith("#"):
            in_sources = s.lower().lstrip("# ").startswith("sources")
            continue
        if in_sources or not s or s.startswith(("|", "![", "```", "---")):
            continue
        body = re.sub(r"^[-*]\s+", "", s)
        words = len(body.split())
        if words > 90:
            flags.append((i, "PARA", "%d words" % words))
        parens = body.count("(")
        if parens > 1:
            flags.append((i, "PARENS", "%d parentheses" % parens))
        low = body.lower()
        for c in CLUTTER:
            if c in low:
                flags.append((i, "CLUTTER", c))
        for sen in sentences(body):
            w = len(sen.split())
            if w < 3:
                continue
            n_sent += 1
            n_words += w
            bad = False
            if w > 35:
                flags.append((i, "LONG", "%d words: %s..." % (w, sen[:70])))
                bad = True
            nums = list(NUM.finditer(DATE.sub(" ", sen)))
            if len(nums) > 2:
                flags.append((i, "NUMBERS", "%d numbers: %s..." % (len(nums), sen[:70])))
                bad = True
            n_flagged += bad
    for i, kind, msg in flags:
        print("%5d  %-8s %s" % (i, kind, msg))
    avg = n_words / n_sent if n_sent else 0
    print("\n%d sentences, average %.1f words; %d flagged sentences (%.0f%%); %d flags in all"
          % (n_sent, avg, n_flagged, 100 * n_flagged / max(n_sent, 1), len(flags)))
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
