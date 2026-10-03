---
description: Give every article in the inbox a typed Jev verdict and show me what it found - no analysis, no Claude usage
allowed-tools: Read, Bash(python pipeline/analyst.py run --no-claude), Bash(python pipeline/analyst.py status), Bash(python pipeline/jev.py:*)
---
1. Run `python pipeline/analyst.py run --no-claude`.
2. Read the newest `proposals/<stamp>/batch.json` and report: the `triage_stage` block (stage, model, articles decided, errors, seconds, estimated cost), the triage counts, the STATE-CHANGE ALERTS in full, anything flagged `possible-prompt-injection`, and the ten highest-ranked selected items with why each was selected.
3. If the stage fell back to the keyword pre-cut, tell me why (no TYPESAFE_API_KEY in .env, a rejected key, or the service unreachable) and how to fix it.
4. Then ask whether I want to run /analyze-news on this batch now (pass it the stamp).
