"""Capture the synthetic motion demo with the activated ESP-IDF Python."""

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import signal
import time

import serial
from esptool.reset import HardReset


def summarize(raw: bytes, started: str, args, elapsed: float, interrupted: int):
    text = raw.decode(errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    records = []
    for line in text.splitlines():
        match = re.search(r"rlcd_dashboard: MOTION (.*)", line)
        if match:
            values = dict(re.findall(r"(\w+)=([^ ]+)", match[1]))
            records.append({key: int(value) if value.isdecimal() else value
                            for key, value in values.items()})
    configs = [row for row in records if row.get("event") == "config"]
    phases = {row["phase"] for row in records if row.get("event") == "phase"}
    cycles = [row for row in records if row.get("event") == "cycle"]
    frames = [row for row in records if row.get("event") == "frame"]
    moving = [row for row in frames if row.get("moving") == 1]
    errors = re.findall(r"^.*(?:Guru Meditation|panic|assert failed|task_wdt|^E \().*$",
                        text, re.MULTILINE)
    starts = text.count("Calling app_main()")
    expected = int(configs[0]["phases"]) if configs else None
    missing = sorted(set(range(expected)) - phases) if expected is not None else None
    timing = {}
    for key in ("draw_us", "transfer_us", "frame_us", "internal_free", "stack_watermark"):
        values = [row[key] for row in frames if isinstance(row.get(key), int)]
        timing[key] = {"min": min(values), "max": max(values)} if values else None
    intervals = [row["interval_us"] for row in moving
                 if isinstance(row.get("interval_us"), int) and row["interval_us"] > 0]
    timing["consecutive_motion_interval_us"] = {
        "min": min(intervals), "max": max(intervals)
    } if intervals else None
    budget = configs[0].get("frame_budget_us", 40000) if configs else 40000
    misses = sum(bool(row.get("deadline_miss", 0)) or row.get("frame_us", 0) > budget
                 for row in frames)
    complete = (bool(configs) and bool(cycles) and missing == [] and starts == 1
                and bool(moving) and not errors and not interrupted and misses == 0)
    summary = {
        "started_utc": started, "port": args.port, "usb_rts_reset": args.reset,
        "elapsed_seconds": elapsed, "interrupted_signal": interrupted or None,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "log_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "synthetic_data": True, "physical_animation_acceptance": "pending",
        "application_start_count": starts, "expected_phase_count": expected,
        "missing_phases": missing, "cycles_observed": len(cycles),
        "frame_count": len(frames), "moving_frame_count": len(moving),
        "frame_budget_us": budget, "frame_budget_misses": misses,
        "errors": errors, "timing": timing,
        "complete_cycle_pass": complete, "records": records,
    }
    return text, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="Explicit RLCD by-id path")
    parser.add_argument("--seconds", type=int, default=95)
    parser.add_argument("--output", type=Path, required=True, help="New capture directory")
    parser.add_argument("--reset", action="store_true", help="USB RTS reset before capture")
    args = parser.parse_args()
    if args.seconds < 1:
        parser.error("--seconds must be positive")
    args.output.mkdir(parents=True, exist_ok=False)
    interrupted = 0

    def stop(signum, _frame):
        nonlocal interrupted
        interrupted = signum

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    pending = b""
    start = time.monotonic()
    # Preserve every received chunk even if the host capture is interrupted.
    raw_path = args.output / "serial.raw"
    with raw_path.open("wb") as stream:
        with serial.Serial(args.port, 115200, timeout=0.2, exclusive=True) as port:
            port.dtr = False
            port.rts = False
            port.reset_input_buffer()
            if args.reset:
                HardReset(port, uses_usb=True)()
            start = time.monotonic()
            while not interrupted and time.monotonic() - start < args.seconds:
                chunk = port.read(port.in_waiting or 1)
                stream.write(chunk)
                stream.flush()
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    if b"rlcd_dashboard: MOTION" in line and b"event=frame" not in line:
                        print(line.decode(errors="replace").strip(), flush=True)
    elapsed = time.monotonic() - start
    text, summary = summarize(raw_path.read_bytes(), started, args, elapsed, interrupted)
    (args.output / "serial.log").write_text(text)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Saved {summary['frame_count']} frames to {args.output}; "
          f"complete_cycle_pass={summary['complete_cycle_pass']}")
    if not summary["complete_cycle_pass"]:
        raise SystemExit("Incomplete cycle, errors, restart, interruption or frame budget miss; "
                         "inspect serial.log and summary.json")


if __name__ == "__main__":
    main()
