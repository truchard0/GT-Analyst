---
description: Walk me through the analyst's proposed ledger rows and approve / reject the ones I choose
argument-hint: "[stamp - defaults to the latest batch]"
allowed-tools: Read, Bash(python pipeline/analyst.py status), Bash(python pipeline/analyst.py review:*), Bash(python pipeline/analyst.py approve:*), Bash(python pipeline/analyst.py reject:*), Bash(python pipeline/analyst.py validate:*), Bash(python tools/web_coverage.py), Bash(python pipeline/ledger.py sweep), Bash(python pipeline/ledger.py report)
---
1. Run `python pipeline/analyst.py status`, then `python pipeline/analyst.py review $ARGUMENTS`.
2. Summarize for me, per proposed row: the call in one line, P and horizon, row class, cluster, what breaks it, and - plainly - the weakest point in it. Flag rows marked BLOCKED with the rule that blocked them. Show the per-article stage line (Jev agreement, articles Jev alone would have lost).
3. Give me your own recommendation per row (approve / reject / fix), then STOP and ask me which refs to approve. Never approve on your own.
4. When I answer, run `python pipeline/analyst.py approve <stamp> --ids <refs>` and `python pipeline/analyst.py reject <stamp> --ids <refs> --why "<my reason>"` exactly as I said. Approval is what writes the ledger and wires the timeline - report the ledger ids it prints.
5. After approving anything: run `python tools/web_coverage.py` and `python pipeline/ledger.py sweep`, report both, and remind me that STATE.md needs its scoreboard/live-calls section updated (offer to draft the edit; do not make it unasked).
6. For `suggested_resolutions`: show the evidence and ask me before resolving anything; every resolution also needs its `ledger.py lesson`.
