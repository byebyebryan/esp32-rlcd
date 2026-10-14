#!/usr/bin/env python3
"""Bounded wire-2 device proof with fictional inputs and no provider reads."""

import copy
import json
import secrets
import sys
import termios
import time
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "host"))
from live_dashboard.projection import Projector, Source, token
from live_dashboard.serial import Port, parse_health
from live_dashboard.wire import encode, parse_request

PORT = "/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:F3:43:74-if00"


def main():
    case = json.loads((APP / "tests/fixtures/capacity-case.json").read_text())
    projector = Projector()
    bridge, sequence, pending = secrets.token_hex(8), 0, bytearray()
    sent, acknowledged, health = {}, [], []
    start = time.monotonic()
    port = Port(PORT)
    try:
        # Ignore accumulated requests from earlier owners and silence windows.
        termios.tcflush(port.fd, termios.TCIFLUSH)
        while time.monotonic() - start < 16:
            pending.extend(port.read())
            if len(pending) > 16384:
                raise ValueError("capture_framing_limit")
            while b"\n" in pending:
                line, _, remainder = pending.partition(b"\n")
                pending = bytearray(remainder)
                elapsed = time.monotonic() - start
                request = parse_request(line)
                if request is not None and elapsed < 8:
                    rows = copy.deepcopy(case["normalizedFailedRows"])
                    stage = "failure" if elapsed < 4 else "retry"
                    if stage == "retry":
                        rows[0] = copy.deepcopy(case["normalizedRetry"])
                    rows += copy.deepcopy(case["normalizedHelpers"])
                    for row in rows:
                        row["title"] = "TEST " + row["title"]
                    sources = []
                    for host in ("starship", "snap"):
                        selected = [r for r in rows if r["identity"]["hostScope"] == host]
                        sources.append(Source(host, "current", 10000,
                                              case["normalizedProvenance"]["sampledAt"],
                                              selected, {token(r["identity"])[0] for r in selected}))
                    view = projector.project(sources)
                    sequence += 1
                    payload = encode(view, request[0], request[1], bridge, sequence)
                    remaining = payload
                    deadline = time.monotonic() + .5
                    while remaining:
                        try:
                            remaining = remaining[port.write(remaining):]
                        except BlockingIOError:
                            pass
                        if remaining:
                            if time.monotonic() >= deadline:
                                raise ValueError("capture_write_timeout")
                            time.sleep(.005)
                    sent[sequence] = {"stage": stage, "request": request[1],
                                      "crc": payload.rstrip().split(b"\t")[-1].decode(),
                                      "rows": len(view["rows"])}
                elif line.startswith(b"RLCD_ACK "):
                    values = dict(field.split("=", 1) for field in line.decode("ascii").split()[1:])
                    original = sent.get(int(values["seq"]))
                    if original is not None:
                        if (values["crc"] != original["crc"] or int(values["request"]) != original["request"]
                                or int(values["rows"]) != original["rows"]):
                            raise ValueError("capture_ack_mismatch")
                        acknowledged.append(original)
                sample = parse_health(line)
                if sample is not None:
                    health.append({"elapsed": round(elapsed, 3), **sample})
            time.sleep(.01)
    finally:
        port.close()
    checks = {
        "failureAcknowledged": any(a["stage"] == "failure" and a["rows"] == 3 for a in acknowledged),
        "retryAcknowledged": any(a["stage"] == "retry" and a["rows"] == 3 for a in acknowledged),
        "failureAttention": any(h["health"] == 0 and h["attention"] == 3 and h["working"] == 0 for h in health),
        "retryAttention": any(h["health"] == 0 and h["attention"] == 2 and h["working"] == 1 for h in health),
        # Diagnostics are emitted on transition; no later periodic report is promised.
        "silenceExpiry": any(h["elapsed"] >= 8 and h["health"] == 2 and h["attention"] == 0
                             and h["working"] == 0 and h["unknown"] == 3 for h in health),
    }
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "scope": "fictional device input, no provider reads/actions",
                      "wire": 2, "checks": checks, "acknowledged": acknowledged, "health": health}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
