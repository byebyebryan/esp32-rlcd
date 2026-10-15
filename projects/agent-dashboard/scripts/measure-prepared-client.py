#!/usr/bin/env python3
"""Owned IPC/proof/serial-fixture pipeline at real one-second request cadence.

No provider reads, ordinary endpoints, services or physical serial device. Both
fixture publishers and the application run in this process; reported CPU is the
combined owned pipeline, not an installed dashboard application measurement.
"""

import time

PROCESS_STARTED = (time.monotonic(), time.process_time())

import argparse
import asyncio
import collections
import copy
import hashlib
import importlib.metadata
import io
import json
import os
import secrets
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--application", type=Path, required=True)
parser.add_argument("--seconds", type=int, choices=range(10, 121), default=30)
parser.add_argument("--warmup", type=int, choices=range(5, 21), default=10)
parser.add_argument("--rows", type=int, choices=(50, 250), default=250)
parser.add_argument("--readers", type=int, choices=(1, 2), default=1)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.application / "host"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from mesh_fixture import native
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector
from live_dashboard.runtime import Events, supervise
from live_dashboard.serial import serve_serial
from agent_observer.mesh_profile import AgentProfile
from mesh_plus.api import Bridge, CachedPublication, CachedPublisher, Client, Endpoint, Reader
from mesh_plus.transport import IPCServer, connect_ipc


async def run():
    counters = collections.Counter()
    signatures = collections.Counter()
    measuring = False
    class Native:
        def __init__(self, host):
            self.frame = native(host, args.rows, lease_ms=600000)
            self.watches = 0
        async def snapshot(self):
            if measuring:
                counters["cachedNativeReads"] += 1
            return copy.deepcopy(self.frame)
        async def watch(self):
            self.watches += 1
            try:
                yield CachedPublication(copy.deepcopy(self.frame), self.frame["serviceId"], {"viewRevision": 1})
                await asyncio.Event().wait()
            finally:
                self.watches -= 1
    class Port:
        def __init__(self):
            self.next = time.monotonic()
            self.request, self.queue, self.sent = 0, [], {}
            self.closed = False
            self.boot = secrets.token_hex(8)
        def read(self):
            if self.queue:
                return self.queue.pop(0)
            now = time.monotonic()
            if now < self.next:
                return b""
            due = int(now - self.next) + 1
            lines = []
            for _ in range(due):
                self.request += 1
                self.sent[self.request] = self.next
                self.next += 1
                lines.append(f"RLCD?2 {self.boot} {self.request}\n".encode())
                if measuring:
                    counters["deviceRequests"] += 1
            return b"".join(lines)
        def write(self, payload):
            fields = payload.rstrip(b"\n").split(b"\t")
            request = int(fields[2])
            late = time.monotonic() - self.sent[request] >= 1
            if measuring:
                counters["responses"] += 1
                counters["lateResponses"] += late
                signatures[hashlib.sha256(b"\t".join(fields[5:-1])).hexdigest()] += 1
            if not late:
                self.queue.append(b"RLCD_ACK seq=" + fields[4] + b" rows=" + fields[6]
                    + b" request=" + fields[2] + b" crc=" + fields[-1] + b"\n")
            return len(payload)
        def close(self):
            self.closed = True
    with tempfile.TemporaryDirectory(prefix="rlcd-prepared-cost-") as directory:
        endpoints, servers, publishers, natives = [], [], [], []
        profile = AgentProfile()
        try:
            for host in ("starship", "snap"):
                source = Native(host)
                publisher = CachedPublisher("agent", host, "agent", source, profile=profile)
                path = Path(directory) / (host + ".sock")
                servers.append(await IPCServer(path, Bridge(publisher).serve).start())
                publishers.append(publisher)
                natives.append(source)
                async def connect(path=path, host=host, publisher=publisher):
                    return await Client.connect(await connect_ipc(path), host=host, source="agent",
                        profile=profile.descriptor.profile_id, codec=publisher.validate)
                endpoints.append(Endpoint(host, host == "starship",
                    None if host == "starship" else "sha256:" + "b" * 64,
                    connect, profile.bind(host, "agent")))
            async def revision():
                return "sha256:" + "c" * 64
            readers = []
            async def configured(*a, **kw):
                reader = Reader("agent", endpoints, local_host="starship", catalog_revision="sha256:" + "c" * 64,
                                catalog_check=revision, profile=profile)
                readers.append(reader)
                return reader
            stop = asyncio.Event()
            fleets = [Fleet(["starship", "snap"], Events(io.StringIO())) for _ in range(args.readers)]
            ports = [Port() for _ in fleets]
            with patch("mesh_plus.api.configured_reader", configured):
                owners = [asyncio.create_task(supervise(fleet.run(), serve_serial(
                    Path("owned-fixture"), fleet, Projector(fleet.hosts), Events(io.StringIO()),
                    opener=lambda _, port=port: port, output=io.StringIO()), stop))
                    for fleet, port in zip(fleets, ports)]
                try:
                    await asyncio.sleep(args.warmup)
                    if any(s.status != "current" for fleet in fleets for s in fleet.sources()):
                        raise ValueError("fixture_not_current")
                    measuring = True
                    cpu, wall = time.process_time(), time.monotonic()
                    startup = {"seconds": wall - PROCESS_STARTED[0],
                               "cpuSeconds": cpu - PROCESS_STARTED[1]}
                    await asyncio.sleep(args.seconds)
                    elapsed, used = time.monotonic() - wall, time.process_time() - cpu
                    measuring = False
                finally:
                    stop.set()
                    await asyncio.wait_for(asyncio.gather(*owners), 10)
            if (any(not p.closed for p in ports) or any(n.watches for n in natives)
                    or any(r.inspect()["activeConnections"] or r.inspect()["cleanupFailures"] for r in readers)):
                raise ValueError("owned_cleanup")
            return {"cpuSeconds": used, "seconds": elapsed, "percentOneCore": used / elapsed * 100,
                    "startupAndWarmup": startup,
                    "counts": dict(counters), "semanticSignatures": dict(signatures), "rowsPerHost": args.rows,
                    "warmupSeconds": args.warmup, "application": str(args.application),
                    "readers": args.readers,
                    "packages": {p: importlib.metadata.version(p) for p in ("agent-observer", "mesh-plus")},
                    "cleanup": True,
                    "limits": ["synthetic native bodies; no providers or ordinary endpoints",
                        "combined fixture publisher/Reader/application/serial-supervisor process CPU",
                        "remote nonce proof over owned IPC; SSH crypto/server and physical device excluded",
                        "unchanged native views with original ten-minute fixture leases; not native freshness proof"]}
        finally:
            for server in servers:
                await server.close()

result = asyncio.run(run())
args.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
