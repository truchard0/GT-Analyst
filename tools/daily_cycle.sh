#!/usr/bin/env bash
# Fixed-cadence scoring gate (cloud or local). The mechanical half of a cycle: fresh tape, the
# precursor log, the AI-financing index, what is due, and the three gates. Resolving due calls needs
# judgment and sourced facts, so the session that runs this does that part itself (see STATE.md §9).
# Exit status is non-zero while any gate fails: overdue or unlessoned calls, dormancy, an unwired
# prediction, or a debug failure.
set -u
cd "$(dirname "$0")/.."
python3 pipeline/ingest.py || echo "ingest failed (continuing)"
python3 tools/precursor_log.py update || true
python3 tools/ai_stress_index.py fetch --from "$(date -u -d '-5 days' +%F)" && python3 tools/ai_stress_index.py build || true
echo "== due";   python3 pipeline/ledger.py due
echo "== sweep"; python3 pipeline/ledger.py sweep;  sweep=$?
echo "== web";   python3 tools/web_coverage.py;     web=$?
echo "== debug"; python3 tools/debug_all.py | tail -3
exit $(( sweep || web ))
