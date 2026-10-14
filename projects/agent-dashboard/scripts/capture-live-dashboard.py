#!/usr/bin/env python3
"""Bounded live USB admission, bridge-stop expiry and restart capture."""

import argparse
import fcntl
import json
import os
import re
import subprocess
import termios
import time
from pathlib import Path


def fields(line):
    return {name: int(value) for name, value in re.findall(r"([a-z_]+)=([0-9]+)", line)}


def live(args, phase):
    command = [
        str(args.python),
        str(Path(__file__).with_name("live-dashboard.py")),
        "--port",
        str(args.port),
        "--seconds",
        str(args.seconds),
        "--verbose",
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=args.seconds + 30, check=False
    )
    (args.output / f"{phase}.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError("bridge_failed")
    sent, acknowledgements, health = {}, [], []
    for line in result.stdout.splitlines():
        if line.startswith("{"):
            value = json.loads(line)
            sent[value["sequence"]] = value
        elif line.startswith("RLCD_ACK "):
            value = fields(line)
            crc = re.search(r"crc=([0-9a-f]{8})", line)
            if crc is not None:
                value["crc"] = crc[1]
            acknowledgements.append(value)
        elif line.startswith("RLCD_HEALTH "):
            health.append(fields(line))
    confirmed = []
    for ack in acknowledgements:
        original = sent.get(ack.get("seq"))
        if original is None:
            continue  # Buffered diagnostics from an earlier bridge incarnation.
        if (
            ack.get("crc") != original["crc"]
            or ack.get("request") != original["request"]
        ):
            raise ValueError("accepted_frame_mismatch")
        if all(h["status"] < 2 for h in original["hosts"]):
            if ack["rows"] != original["rows"]:
                raise ValueError("admitted_row_count_mismatch")
            confirmed.append(original)
    if len(confirmed) < 3 or not any(v["rows"] for v in confirmed):
        raise ValueError("insufficient_live_admission")
    return {
        "sent": len(sent),
        "acknowledged": len(acknowledgements),
        "healthyConfirmed": len(confirmed),
        "lastView": confirmed[-1],
        "maxFrameUs": max((h["frame_us"] for h in health), default=None),
        "deadlineMisses": sum(h.get("miss", 0) for h in health),
        "minInternalHeap": min((h["heap"] for h in health), default=None),
        "minStackWatermark": min((h["stack"] for h in health), default=None),
    }


def silence(args):
    fd = os.open(args.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    old = None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.ioctl(fd, termios.TIOCEXCL)
        old = termios.tcgetattr(fd)
        raw = termios.tcgetattr(fd)
        raw[0] = 0
        raw[1] = 0
        raw[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        raw[3] = 0
        raw[6][termios.VMIN] = 0
        raw[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, raw)
        started = time.monotonic()
        data = bytearray()
        while time.monotonic() - started < 6:
            try:
                data.extend(os.read(fd, 4096))
            except BlockingIOError:
                pass
            time.sleep(0.01)
        text = data.decode("ascii", "replace")
        (args.output / "silence.log").write_text(text)
        reports = [
            fields(line)
            for line in text.splitlines()
            if line.startswith("RLCD_HEALTH ")
        ]
        expired = [
            r
            for r in reports
            if r.get("health") == 2
            and not r.get("attention")
            and not r.get("waiting")
            and not r.get("working")
        ]
        if not expired:
            raise ValueError("device_did_not_revoke_during_silence")
        return {"windowSeconds": 6, "expired": expired[-1]}
    finally:
        if old is not None:
            termios.tcsetattr(fd, termios.TCSANOW, old)
        fcntl.ioctl(fd, termios.TIOCNXCL)
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--port", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=25)
    args = parser.parse_args()
    if args.seconds < 10 or args.seconds > 300:
        parser.error("seconds must be 10..300")
    if (
        args.port.parent != Path("/dev/serial/by-id")
        or "94:A9:90:F3:43:74" not in args.port.name
    ):
        parser.error("explicit known RLCD identity required")
    args.output.mkdir(parents=True, exist_ok=False)
    result = {
        "scope": "live cached feed and USB/device admission; physical readability remains separate"
    }
    try:
        result["initial"] = live(args, "initial")
        result["silence"] = silence(args)
        result["recovery"] = live(args, "recovery")
        result["passed"] = True
    except Exception as error:  # noqa: BLE001 - record finite diagnostic codes instead of payload-bearing tracebacks
        result.update(
            passed=False,
            error=str(error) if isinstance(error, ValueError) else type(error).__name__,
        )
    (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
