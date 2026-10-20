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
from live_dashboard.profiles import ProfileFleet, ProfileProjector, load_routes
from live_dashboard.projection import Projector
from live_dashboard.context import ContextStore, default_context_path, route_binding
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
    fleet = (
        ProfileFleet(args.hosts, load_routes(args.profiles_config, hosts=args.hosts,
                                           selected=args.profile), events)
        if args.profiles_config else Fleet(args.hosts, events, full_roster=args.roster)
    )
    projector = (ProfileProjector if args.profiles_config else Projector)(fleet.hosts)
    context_store = None

    async def preview():
        await asyncio.wait_for(fleet.ready.wait(), 15)
        deadline = loop.time() + 10
        while (
            any(s.status != "current" for s in fleet.sources())
            and loop.time() < deadline
        ):
            await asyncio.sleep(0.1)
        sources = fleet.sources()
        view = projector.project(sources)
        if args.roster or args.inspect:
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
        if args.preview or args.roster or args.inspect:
            consumer = preview()
        else:
            if args.profiles_config:
                routes = [
                    {
                        "host": route.host,
                        "profile": route.profile,
                        "label": route.label,
                        "codex_home": route.codex_home,
                        "source": route.source,
                        "socket": route.socket,
                    }
                    for route in fleet.routes
                ]
            else:
                socket = getattr(fleet, "socket", None) or os.path.join(
                    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
                    "mesh-plus-agent/read.sock"
                    if getattr(fleet, "full_roster", False)
                    else "mesh-plus-agent-working-set/read.sock",
                )
                routes = [
                    {
                        "host": host,
                        "profile": "full" if fleet.full_roster else "working_set",
                        "label": "Default",
                        "codex_home": None,
                        "source": fleet.source,
                        "socket": socket,
                    }
                    for host in fleet.hosts
                ]
            path = args.state_path or default_context_path(args.port)
            context_store = ContextStore(
                path, route_binding(args.port, fleet.hosts, routes), fleet.hosts
            )
            restored = context_store.open()
            projector.restore_context(restored.rows, restored.initialized_hosts)
            consumer = serve_serial(
                args.port,
                fleet,
                projector,
                events,
                verbose=args.verbose,
                context_store=context_store,
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
        if context_store is not None:
            context_store.close()
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
    parser.add_argument("--profiles-config", type=Path,
                        help="private explicit home-profile route manifest")
    parser.add_argument("--state-path", type=Path,
                        help="private bridge restart-context file (live serial only)")
    parser.add_argument("--profile", action="append", default=[],
                        help="select one configured home profile; repeat to combine")
    parser.add_argument(
        "--roster",
        action="store_true",
        help="explain cached roster without opening USB",
    )
    parser.add_argument("--inspect", action="store_true",
                        help="explain the current dashboard selection without opening USB")
    parser.add_argument(
        "--all", action="store_true", help="include excluded/saved rows in --roster"
    )
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error("seconds must be finite and nonnegative")
    if args.all and not args.roster:
        parser.error("--all requires --roster")
    if args.profile and not args.profiles_config:
        parser.error("--profile requires --profiles-config")
    if args.profiles_config and args.roster:
        parser.error("full diagnostics use each profile's Observer service socket")
    if args.inspect and (args.roster or args.port or args.preview):
        parser.error("--inspect is a standalone selected-feed read")
    if args.roster and (args.port or args.preview):
        parser.error("--roster is a standalone cached read")
    if args.preview and args.port:
        parser.error("--preview is a standalone cached read")
    if args.state_path and (args.roster or args.preview or args.inspect):
        parser.error("--state-path is only available to the live serial bridge")
    if not (args.roster or args.preview or args.inspect) and (
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
