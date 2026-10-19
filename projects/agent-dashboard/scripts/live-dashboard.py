#!/usr/bin/env python3
"""Run with the accepted Observer/Mesh environment; owned, recovering USB feed."""

import argparse
import asyncio
import json
import math
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector
from live_dashboard.runtime import Events, Failure, supervise
from live_dashboard.serial import KNOWN_RLCD_DEVICE_NAMES, serve_serial
from live_dashboard.wire import encode


async def main(args):
    events = Events()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for name in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(name, stop.set)
    timer = loop.call_later(args.seconds, stop.set) if args.seconds else None
    fleet = Fleet(args.hosts, events, full_roster=args.roster)
    projector = Projector(args.hosts)

    async def preview():
        await asyncio.wait_for(fleet.ready.wait(), 15)
        deadline = loop.time() + 10
        while (
            any(s.status not in {"current", "partial"} for s in fleet.sources())
            and loop.time() < deadline
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
        else:
            args.preview.parent.mkdir(parents=True, exist_ok=True)
            args.preview.write_bytes(encode(view, "0" * 16, 1, "0" * 16, 1))
            print(
                json.dumps(
                    {
                        "preview": str(args.preview),
                        "rows": len(view["rows"]),
                        "hosts": view["hosts"],
                    }
                )
            )
        stop.set()

    events.emit("bridge_started")
    try:
        consumer = (
            preview()
            if args.preview or args.roster
            else serve_serial(args.port, fleet, projector, events, verbose=args.verbose)
        )
        await supervise(fleet.run(), consumer, stop)
        events.emit("bridge_stopped")
    except Failure as error:
        events.emit("bridge_failed", reason=str(error))
        if str(error) == "worker_cleanup_timeout":
            # An uncooperative owned task must not strand the service at shutdown.
            # Process exit releases the remaining OS handles after the grace bound.
            os._exit(1)
        raise
    finally:
        if timer is not None:
            timer.cancel()
        for name in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(name)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hosts", nargs="+", default=["starship", "snap"], choices=["starship", "snap"]
    )
    parser.add_argument("--port", type=Path)
    parser.add_argument(
        "--preview", type=Path, help="write one device frame for native rendering"
    )
    parser.add_argument(
        "--seconds", type=float, default=0, help="bounded run; zero runs until stopped"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--roster",
        action="store_true",
        help="explain cached roster without opening USB",
    )
    parser.add_argument(
        "--all", action="store_true", help="include excluded/saved rows in --roster"
    )
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error("seconds must be finite and nonnegative")
    if args.all and not args.roster:
        parser.error("--all requires --roster")
    if args.roster and (args.port or args.preview):
        parser.error("--roster is a standalone cached read")
    if args.preview and args.port:
        parser.error("--preview is a standalone cached read")
    if not (args.roster or args.preview) and (
        args.port is None
        or args.port.parent != Path("/dev/serial/by-id")
        or args.port.name not in KNOWN_RLCD_DEVICE_NAMES
    ):
        parser.error("explicit known RLCD serial identity required")
    return args


if __name__ == "__main__":
    try:
        asyncio.run(main(arguments()))
    except KeyboardInterrupt:
        pass
    except Exception:  # noqa: BLE001 - redact upstream exception payloads
        # Exception payloads may contain upstream native data; finite events above
        # explain worker failures without serializing those payloads.
        print('RLCD_EVENT {"event":"bridge_unavailable"}', file=sys.stderr, flush=True)
        raise SystemExit(1) from None
