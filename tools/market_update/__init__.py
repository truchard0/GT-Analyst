"""GT-Analyst market-update engine: our own daily US market update from our Skylit maps.

Modules: chartstyle (house matplotlib style), data (read-only loaders with snapshot times and stale flags),
stats (measured base rates with n), charts (the chart catalogue), build (CLI that writes an edition).
Run: python -I tools/market_update/build.py --date 2026-11-17 --edition preclose
"""
import site
import sys

# Runs are made with `python -I` (no script-dir or user-site paths, so nothing in a scratch folder can shadow the
# stdlib). numpy lives in the user's own site-packages on this machine, so add that one directory back explicitly.
try:
    import numpy  # noqa: F401
except ImportError:
    _us = site.getusersitepackages()
    if _us not in sys.path:
        sys.path.append(_us)
