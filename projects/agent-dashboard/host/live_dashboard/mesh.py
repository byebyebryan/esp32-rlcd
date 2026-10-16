"""One optional installed SDK subscription; no native reads or actions."""

import asyncio
import os
import secrets

from .projection import Source, exclusion, token
from .runtime import Events, Failure


class Fleet:
    def __init__(self, hosts, events=None, *, full_roster=False):
        self.hosts = list(hosts)
        self.full_roster = full_roster
        if full_roster:
            from agent_observer.mesh_profile import AgentProfile
            self.profile = AgentProfile()
        else:
            from agent_observer.mesh_active_profile import ActiveAgentProfile
            self.profile = ActiveAgentProfile()
        self.source = "agent" if full_roster else "agent_active"
        self.request_id = secrets.token_hex(16)
        self.guard = self.new_guard()
        self.ready = asyncio.Event()
        self.closed = False
        self.error = None
        self.events = events or Events()

    def new_guard(self):
        if self.full_roster:
            from agent_observer.mesh_read import PreparedAgentWatch
            return PreparedAgentWatch(
                self.request_id, host_ids=self.hosts, profile=self.profile,
            )
        from agent_observer.mesh_active_read import PreparedActiveAgentWatch
        return PreparedActiveAgentWatch(
            self.request_id, host_ids=self.hosts, profile=self.profile,
        )

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
        membership = {host: (set(), set()) for host in self.hosts}
        if not self.full_roster:
            return self.active_sources(read, now, by_host)
        # Full diagnostics keep every currently admitted body.
        for row in read.sessions:
            known, excluded = membership[row["identity"]["hostScope"]]
            identifier = token(row["identity"])[0]
            known.add(identifier)
            if exclusion(row):
                excluded.add(identifier)
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
            known, excluded = membership[identifier]
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

    def active_sources(self, read, now, by_host):
        result = []
        for host in read.context["hosts"]:
            identifier = host["hostId"]
            scopes = [s for s in read.scopes if s["hostScope"] == identifier]
            complete = {(s["provider"], s["namespace"]) for s in scopes
                        if s["coverage"]["status"] == "complete"}
            # Fields and scope coverage expire independently. A shorter history
            # lease must not turn supported runtime membership into an outage.
            receipts = {(r["sourceId"], r["component"]): r for r in host["receipts"]}
            remaining = max((r["expiresAtMs"] - now for r in receipts.values()
                             if r["health"] in {"current", "partial"}), default=0)
            ready = (host["delivery"]["status"] == "ready"
                     and host["viewState"] == "current" and remaining > 0)
            status = ("current" if scopes and len(complete) == len(scopes) else "partial") if ready else "offline"
            rows = by_host[identifier]
            known = {token(row["identity"])[0] for row in rows}
            # Both exports are already checked at this read's clock by the owner
            # facade. Raw context/omissions are never retirement authority.
            known.update(token(e["identity"])[0] for e in read.uncertain
                         if e["identity"]["hostScope"] == identifier)
            excluded = {token(e["identity"])[0] for e in read.nonmembers
                        if e["identity"]["hostScope"] == identifier}
            deadlines = {}
            owner = host["owner"]
            if owner is not None and owner["metadata"] is not None:
                for scope in owner["metadata"]["scopes"]:
                    for entry in scope["members"]:
                        supports = entry["fieldSupports"]
                        leases = []
                        for ref in supports.values():
                            if ref is None:
                                continue
                            receipt = receipts.get((ref["provider"] + ":" + ref["namespace"], ref["component"]))
                            if (receipt is not None and receipt["accepted"] == ref["accepted"]
                                    and receipt["health"] in {"current", "partial"}
                                    and receipt["expiresAtMs"] > now):
                                leases.append(receipt["expiresAtMs"] - now)
                        deadlines[token(entry["identity"])[0]] = min(leases, default=0)
            # The active DTO carries each row's original runtime observation,
            # not the full snapshot's publication wall time. Cached proof and
            # service emission must never advance this source sample anchor.
            samples = {token(row["identity"])[0]: row["runtime"].get("observedAt")
                       if row["runtime"].get("clock") == "sample" else None for row in rows}
            result.append(Source(identifier, status, max(0, remaining), None, rows,
                                 known, excluded, complete, deadlines, samples))
        return result

    async def run(self):
        from mesh_plus.api import configured_reader
        from mesh_plus.library_authority import LibraryMeshAuthority

        delay = 1
        while True:
            stream = None
            authority = LibraryMeshAuthority()
            try:
                self.closed = False
                socket = os.path.join(
                    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
                    "mesh-plus-agent/read.sock" if self.full_roster
                    else "mesh-plus-agent-active/read.sock",
                )
                reader = await configured_reader(
                    "agent",
                    source=self.source,
                    socket=socket,
                    scope="hosts",
                    hosts=self.hosts,
                    authority=authority,
                    report_routes=False,
                    profile=self.profile,
                )
                request = {
                    "meshProtocol": 1,
                    "requestId": self.request_id,
                    "operation": "watch",
                    "profile": self.profile.descriptor.profile_id,
                    "access": "cached",
                    "selection": {"mode": "hosts", "hostIds": self.hosts},
                    "extensions": {},
                }
                stream = reader.execute_admitted(request)
                connected = False
                async for frame in stream:
                    self.guard.accept(frame)
                    self.ready.set()
                    if isinstance(frame, dict) and (
                        "mesh" not in frame or frame["mesh"]["kind"] == "error"
                    ):
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
                try:
                    if stream is not None:
                        await asyncio.wait_for(stream.aclose(), timeout=3)
                except asyncio.CancelledError:
                    raise
                except Exception:  # noqa: BLE001 - redact upstream cleanup payloads
                    raise Failure("mesh_cleanup_failed") from None
                finally:
                    try:
                        await asyncio.to_thread(authority.close)
                    except Exception:  # noqa: BLE001 - bounded owned catalog cleanup
                        raise Failure("mesh_cleanup_failed") from None
            await asyncio.sleep(delay)
            delay = min(30, delay * 2)
            self.request_id = secrets.token_hex(16)
            self.guard = self.new_guard()
