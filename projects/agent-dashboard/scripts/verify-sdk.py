#!/usr/bin/env python3
"""Verify installed Observer/Mesh versions, public APIs, and exact wheel hashes."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SCRIPT = APP_ROOT / "scripts" / "dashboard-bundle.py"
spec = importlib.util.spec_from_file_location("dashboard_bundle", BUNDLE_SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load dashboard bundle verifier")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    observed = bundle.probe(args.python, APP_ROOT / bundle.LOCK_INPUT)
    print(json.dumps(observed, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - stable message keeps paths out of CI logs
        raise SystemExit("SDK verification failed: check the locked pair, prefix, and public APIs") from None
