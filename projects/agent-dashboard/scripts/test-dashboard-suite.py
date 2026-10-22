#!/usr/bin/env python3
"""Run dashboard client tests, optionally requiring every case to execute."""

import os
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
suite = unittest.defaultTestLoader.discover(
    str(APP_ROOT / "tests"), pattern="test_*.py"
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if os.environ.get("RLCD_REQUIRE_ZERO_SKIPS") == "1" and result.skipped:
    print(
        f"ERROR: full dashboard suite skipped {len(result.skipped)} case(s)",
        file=sys.stderr,
    )
    raise SystemExit(1)
if not result.wasSuccessful():
    raise SystemExit(1)
