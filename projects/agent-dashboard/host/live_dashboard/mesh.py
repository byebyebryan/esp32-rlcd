"""One optional installed SDK subscription; no native reads or actions."""

import asyncio
import os
import secrets

from .projection import Source, exclusion, token
from .runtime import Events, Failure


class Fleet:
    def __init__(self, hosts, events=None):
        from agent_observer.mesh_profile import AgentProfile
        from agent_observer.mesh_read import PreparedAgentWatch

        self.hosts = list(hosts)
        self.profile = AgentProfile()
        self.request_id = secrets.token_hex(16)
        self.guard = PreparedAgentWatch(
            self.request_id, host_ids=self.hosts, profile=self.profile
        )
        self.ready = asyncio.Event()
        self.closed = False
        self.error = None
        self.events = events or Events()

    def sources(self):
        from mesh_plus.evidence import clock_domain
        from mesh_plus.transport import boottime_ms

        now = boottime_ms()
        read = self.guard.read(now, clock_domain())
        context = read.context
        if context is None or self.closed:
            return [
                Source(host, "offline" if self.closed else "warming")
                for host in self.hosts
            ]
        by_host = {host: [] for host in self.hosts}
        for row in read.sessions:
            by_host[row["identity"]["hostScope"]].append(row)
        result = []
        for host in context["hosts"]:
            identifier = host["hostId"]
            status = "current"
            receipts = host["receipts"]
            remaining = min(
                (
                    r["expiresAtMs"] - now
                    for r in receipts
                    if r["health"] in {"current", "partial"}
                ),
                default=0,
            )
            if (
                host["delivery"]["status"] != "ready"
                or host["viewState"] != "current"
                or remaining <= 0
            ):
                status = "offline"
            metadata = (
                host["owner"]["metadata"]
                if host["owner"] is not None
                else None
            )
            rows = by_host[identifier]
            if (
                metadata is not None
                and status == "current"
                and (
                    metadata["sourceHealth"] != "current"
                    or any(
                        s["coverage"]["runtime"]["status"] != "complete"
                        for s in metadata["sources"]
                    )
                )
            ):
                status = "partial"
            known, excluded = set(), set()
            for row in rows:
                identity = token(row["identity"])[0]
                known.add(identity)
                if exclusion(row):
                    excluded.add(identity)
            result.append(
                Source(
                    identifier,
                    status,
                    max(0, remaining),
                    None if metadata is None else metadata["collectedAt"],
                    rows,
                    known,
                    excluded,
                )
            )
        return result

    async def run(self):
        from mesh_plus.api import configured_reader
        from mesh_plus.catalog import SSHPlusAuthority

        delay = 1
        while True:
            stream = None
            try:
                self.closed = False
                socket = os.path.join(
                    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
                    "mesh-plus-agent/read.sock",
                )
                reader = await configured_reader(
                    "agent",
                    source="agent",
                    socket=socket,
                    scope="hosts",
                    hosts=self.hosts,
                    authority=SSHPlusAuthority(),
                    report_routes=False,
                    profile=self.profile,
                )
                request = {
                    "meshProtocol": 1,
                    "requestId": self.request_id,
                    "operation": "watch",
                    "profile": "agent-observer.mesh-candidate.v3",
                    "access": "cached",
                    "selection": {"mode": "hosts", "hostIds": self.hosts},
                    "extensions": {},
                }
                stream = reader.execute(request)
                connected = False
                async for frame in stream:
                    self.guard.accept(frame)
                    self.ready.set()
                    if "mesh" not in frame or frame["mesh"]["kind"] == "error":
                        raise ValueError("mesh_terminal")
                    if not connected:
                        self.error = None
                        self.events.emit("mesh_connected")
                        connected = True
                    delay = 1
                raise ValueError("mesh_disconnected")
            except asyncio.CancelledError:
                raise
            except Exception as error:  # noqa: BLE001 - redact SDK failures at the delivery boundary
                self.error = (
                    "mesh_timeout" if isinstance(error, TimeoutError) else "mesh_retry"
                )
                self.events.emit(
                    "mesh_retry", interval=30, reason=self.error, retry_ms=delay * 1000
                )
            finally:
                self.guard.disconnect()
                self.closed = True
                if stream is not None:
                    try:
                        await asyncio.wait_for(stream.aclose(), timeout=3)
                    except asyncio.CancelledError:
                        raise
                    except Exception:  # noqa: BLE001 - redact upstream cleanup payloads
                        raise Failure("mesh_cleanup_failed") from None
            await asyncio.sleep(delay)
            delay = min(30, delay * 2)
            from agent_observer.mesh_read import PreparedAgentWatch

            self.request_id = secrets.token_hex(16)
            self.guard = PreparedAgentWatch(
                self.request_id, host_ids=self.hosts, profile=self.profile
            )
