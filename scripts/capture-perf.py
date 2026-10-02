"""Capture the RLCD benchmark using the activated IDF Python environment."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import time

import serial
from esptool.reset import HardReset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="Explicit RLCD by-id path")
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--output", type=Path, required=True, help="New capture directory")
    parser.add_argument("--reset", action="store_true", help="USB RTS reset before capture")
    args = parser.parse_args()
    if args.seconds < 1:
        parser.error("--seconds must be positive")
    args.output.mkdir(parents=True, exist_ok=False)
    data = bytearray()
    pending = b""
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with serial.Serial(args.port, 115200, timeout=0.2, exclusive=True) as port:
        port.dtr = False
        port.rts = False
        port.reset_input_buffer()
        if args.reset:
            HardReset(port, uses_usb=True)()
        start = time.monotonic()
        while time.monotonic() - start < args.seconds:
            chunk = port.read(port.in_waiting or 1)
            data.extend(chunk)
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                if b"RESULT " in line or b"SUITE_COMPLETE" in line:
                    print(line.decode(errors="replace").strip(), flush=True)
        elapsed = time.monotonic() - start
    text = data.decode(errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    log = text.encode()
    (args.output / "serial.log").write_bytes(log)
    records = []
    for line in text.splitlines():
        match = re.search(r"rlcd_perf: (RESULT|TIMING) (.*)", line)
        if match:
            values = dict(re.findall(r"(\w+)=([^ ]+)", match[2]))
            records.append({"type": match[1], **{
                k: int(v) if v.isdecimal() else v for k, v in values.items()
            }})
    errors = re.findall(r"^.*(?:Guru Meditation|panic|assert failed|task_wdt|^E \().*$",
                        text, re.MULTILINE)
    summary = {
        "started_utc": started, "port": args.port, "usb_rts_reset": args.reset,
        "elapsed_seconds": elapsed,
        "log_sha256": hashlib.sha256(log).hexdigest(),
        "raw_sha256": hashlib.sha256(data).hexdigest(),
        "suite_complete_count": text.count("SUITE_COMPLETE"),
        "application_start_count": text.count("RLCD drawing benchmark;"),
        "errors": errors, "records": records,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Saved {len(records)} timing/result records to {args.output}")
    if errors or not records:
        raise SystemExit("Capture contains errors or no benchmark records; inspect serial.log")


if __name__ == "__main__":
    main()
