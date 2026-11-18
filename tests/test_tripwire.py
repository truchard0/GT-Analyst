import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))
import marketdata  # noqa: E402
import tripwire  # noqa: E402

# 10/23/2026: BZ=F had rolled to January Brent (111.70) while December, still the ICE front month, settled 116.72
TAPE = {
    "BZ=F": [("2026-10-22", 113.17), ("2026-10-23", 111.70), ("2026-11-02", 110.0)],
    "BZZ26.NYM": [("2026-10-22", 113.17), ("2026-10-23", 126.00), ("2026-10-30", 118.0)],
}


def fake_closes(ticker, start, end):
    return [(d, v) for d, v in TAPE[ticker] if start <= d < end]


class FrontMonth(unittest.TestCase):
    SPEC = {"type": "stay_inside", "ticker": "BZ=F", "lo": 85.0, "hi": 125.0, "start": "2026-10-05", "end": "2026-12-31"}

    def test_the_continuous_ticker_alone_misses_a_front_month_breach(self):
        with mock.patch.object(marketdata, "closes", fake_closes):
            self.assertEqual(tripwire.check_spec(self.SPEC)[0], "OPEN")

    def test_front_month_closes_replace_the_continuous_series_until_expiry(self):
        spec = dict(self.SPEC, front_months=[{"ticker": "BZZ26.NYM", "until": "2026-10-30"}])
        with mock.patch.object(marketdata, "closes", fake_closes):
            state, outcome, ev = tripwire.check_spec(spec)
        self.assertEqual((state, outcome), ("DECIDED", 0))
        self.assertIn("126", ev)


if __name__ == "__main__":
    unittest.main()
