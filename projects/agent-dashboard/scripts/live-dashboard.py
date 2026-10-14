#!/usr/bin/env python3
"""Run with the accepted Observer/Mesh Python environment; stdlib USB IO."""

import argparse
import asyncio
import contextlib
import fcntl
import json
import math
import os
import secrets
import sys
import termios
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector
from live_dashboard.wire import encode, parse_request


async def main(args):
    fleet = Fleet(args.hosts)
    projector = Projector(args.hosts)
    task = asyncio.create_task(fleet.run())
    fd = None
    old = None
    epoch = secrets.token_hex(8)
    sequence = 0
    stop = time.monotonic() + args.seconds if args.seconds else float("inf")
    try:
        if args.preview or args.roster:
            await asyncio.wait_for(fleet.ready.wait(), 15)
            # Initial watch views can be partial while a sibling is connecting.
            deadline = time.monotonic() + 10
            while (
                any(s.status not in {"current", "partial"} for s in fleet.sources())
                and time.monotonic() < deadline
            ):
                await asyncio.sleep(0.1)
            sources = fleet.sources()
            view = projector.project(sources)
            if args.roster:
                print(
                    json.dumps(
                        projector.explain(sources, view, include_all=args.all),
                        ensure_ascii=False,
                    )
                )
                return
            args.preview.parent.mkdir(parents=True, exist_ok=True)
            args.preview.write_bytes(encode(view, "0" * 16, 1, epoch, 1))
            print(
                json.dumps(
                    {
                        "preview": str(args.preview),
                        "rows": len(view["rows"]),
                        "hosts": view["hosts"],
                    }
                )
            )
            return
        if not args.port:
            raise ValueError("serial_port_required")
        if (
            not args.port.is_absolute()
            or args.port.parent != Path("/dev/serial/by-id")
            or "94:A9:90:F3:43:74" not in args.port.name
        ):
            raise ValueError("explicit_rlcd_identity_required")
        fd = os.open(args.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.ioctl(fd, termios.TIOCEXCL)
        old = termios.tcgetattr(fd)
        config = termios.tcgetattr(fd)
        config[0] = 0
        config[1] = 0
        config[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        config[3] = 0
        config[4] = termios.B115200
        config[5] = termios.B115200
        config[6][termios.VMIN] = 0
        config[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, config)
        pending = bytearray()
        last_request = None
        while time.monotonic() < stop:
            try:
                part = os.read(fd, 4096)
            except BlockingIOError:
                part = b""
            if part:
                pending.extend(part)
                if len(pending) > 16384:
                    pending.clear()
                while b"\n" in pending:
                    line, _, rest = pending.partition(b"\n")
                    pending = bytearray(rest)
                    request = parse_request(line)
                    if request is None:
                        if line.startswith((b"RLCD_ACK ", b"RLCD_HEALTH ")):
                            print(line.decode("ascii", "replace"), flush=True)
                        continue
                    if request == last_request:
                        continue
                    last_request = request
                    sequence += 1
                    view = projector.project(fleet.sources())
                    response = encode(view, *request, epoch, sequence)
                    checksum = response[-9:-1].decode()
                    deadline = time.monotonic() + 0.5
                    while response:
                        if time.monotonic() > deadline:
                            raise ValueError("serial_write_timeout")
                        try:
                            sent = os.write(fd, response)
                            response = response[sent:]
                        except BlockingIOError:
                            await asyncio.sleep(0.01)
                    if args.verbose:
                        print(
                            json.dumps(
                                {
                                    "sequence": sequence,
                                    "request": request[1],
                                    "crc": checksum,
                                    "rows": len(view["rows"]),
                                    "hosts": view["hosts"],
                                }
                            ),
                            flush=True,
                        )
            await asyncio.sleep(0.01)
    finally:
        task.cancel()
        try:
            with contextlib.suppress(asyncio.CancelledError):
                await task
        finally:
            if fd is not None:
                try:
                    if old is not None:
                        termios.tcsetattr(fd, termios.TCSANOW, old)
                    fcntl.ioctl(fd, termios.TIOCNXCL)
                finally:
                    os.close(fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hosts", nargs="+", default=["starship", "snap"], choices=["starship", "snap"]
    )
    parser.add_argument("--port", type=Path)
    parser.add_argument(
        "--preview", type=Path, help="write one device frame for native rendering"
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=0,
        help="bounded run; zero runs until interrupted",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--roster",
        action="store_true",
        help="explain labels, identity, selection and hidden running rows without opening USB",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="include excluded/saved rows in --roster diagnostics",
    )
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error("seconds must be finite and nonnegative")
    if args.all and not args.roster:
        parser.error("--all requires --roster")
    if args.roster and (args.port or args.preview):
        parser.error("--roster is a standalone cached read")
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
    except Exception:  # noqa: BLE001 - do not expose native metadata in exception diagnostics
        print(
            "live dashboard unavailable; check accepted environment, feed and device ownership",
            file=sys.stderr,
        )
        raise SystemExit(1)
