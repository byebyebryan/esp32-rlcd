"""One optional installed SDK subscription; no native reads or actions."""

import asyncio
import os
import secrets

from .projection import (
    MAX_VALID_MS,
    MARGIN_MS,
    Source,
    exclusion,
    identity_key,
    token,
)
from .runtime import Events, Failure


class Fleet:
    def __init__(self, hosts, events=None, *, full_roster=False, source=None,
                 socket=None, expected_homes=None):
        self.hosts = list(hosts)
        self.full_roster = full_roster
        if full_roster:
            from agent_observer.mesh_profile import AgentProfile
            self.profile = AgentProfile()
            self.source = "agent"
        else:
            from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
            self.profile = WorkingSetAgentProfile()
            self.source = "agent_working_set"
        if source is not None:
            self.source = source
        self.socket = socket
        self.expected_homes = dict(expected_homes or {})
        if set(self.expected_homes) - set(self.hosts):
            raise ValueError("profile_host_scope")
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
        from agent_observer.mesh_working_set_read import PreparedWorkingSetAgentWatch
        return PreparedWorkingSetAgentWatch(
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
        if not self.full_roster:
            return self._bound_sources(self.working_set_sources(read, now, by_host), context)
        membership = {host: (set(), set()) for host in self.hosts}
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
        return self._bound_sources(result, context)

    def _bound_sources(self, sources, context):
        result = []
        for source in sources:
            try:
                if not self._check_configured_homes(context, expected_host=source.host):
                    raise ValueError("profile_home_binding")
            except (ValueError, KeyError, TypeError):
                self.events.emit("mesh_profile_unavailable", interval=30,
                                 host=source.host, reason="profile_home_binding")
                source = Source(source.host, "offline")
            result.append(source)
        return result

    def _check_configured_homes(self, context, *, expected_host=None):
        """A configured profile label never substitutes for native provenance."""
        expected = getattr(self, "expected_homes", {})
        if not expected or context is None:
            return not expected
        from agent_observer.public import store_namespace

        matched = False
        for host in context["hosts"]:
            if expected_host is not None and host["hostId"] != expected_host:
                continue
            owner = host.get("owner")
            if owner is None:
                continue
            identifier = host["hostId"]
            service = owner["service"]
            sources = service["sources"]
            if (identifier not in expected or len(sources) != 1
                    or sources[0]["provider"] != "codex"
                    or sources[0]["configHome"] != expected[identifier]
                    or sources[0]["configHomeKind"] != "explicit"
                    or sources[0]["namespace"] != store_namespace(
                        "codex", expected[identifier], "explicit", service["uid"]
                    )):
                raise ValueError("profile_home_binding")
            matched = True
        return matched

    def working_set_sources(self, read, now, by_host):
        """Pair current member bodies to the public facade's exact lease identity."""
        lease_fields = {
            "activity", "kind", "lastUpdated", "latestTurn", "outcome",
            "phase", "runtime", "savedIdentity", "workspace",
        }
        leases = {}
        for lease in read.member_leases:
            key = identity_key(lease["identity"])
            if key in leases or set(lease["fieldExpiresAtMs"]) != lease_fields:
                raise ValueError("mesh_member_lease_invalid")
            leases[key] = lease

        scopes_by_host = {host: [] for host in self.hosts}
        scope_remaining_by_host = {host: [] for host in self.hosts}
        for scope in read.scopes:
            host = scope["hostScope"]
            if host in scopes_by_host:
                coverage = scope.get("coverage")
                state = coverage.get("status") if isinstance(coverage, dict) else None
                if state == "complete":
                    expires_at = coverage.get("expiresAtMs")
                    if type(expires_at) is int and expires_at > now:
                        scope_remaining_by_host[host].append(expires_at - now)
                    else:
                        # A complete label without a live public scope lease
                        # cannot authorize fleet counts or negative census.
                        state = "partial"
                scopes_by_host[host].append((scope, state))

        for entry in read.uncertain:
            host = entry["identity"]["hostScope"]
            if host in by_host:
                by_host[host].append({
                    "identity": entry["identity"],
                    "_membership": entry,
                    "_membership_kind": "uncertain",
                })
        for entry in read.nonmembers:
            host = entry["identity"]["hostScope"]
            if host in by_host:
                by_host[host].append({
                    "identity": entry["identity"],
                    "_membership": entry,
                    "_membership_kind": "nonmember",
                })

        result = []
        for host in self.hosts:
            scopes = scopes_by_host[host]
            states = [state for _, state in scopes]
            if states and all(state == "complete" for state in states):
                status = "current"
            elif states and all(state in {"complete", "partial"} for state in states):
                status = "partial"
            elif any(state == "unavailable" for state in states):
                status = "offline"
            else:
                status = "partial"

            rows, admitted, excluded, complete = [], set(), set(), set()
            remaining_by_id, sampled_by_id, categories = {}, {}, {}
            for scope, state in scopes:
                if state == "complete":
                    complete.add((scope["provider"], scope["namespace"]))
            for row in by_host[host]:
                identity = row["identity"]
                identifier, _ = token(identity)
                admitted.add(identifier)
                if row.get("_membership") is not None:
                    if row["_membership_kind"] == "nonmember":
                        excluded.add(identifier)
                    continue
                if row["kind"] in {"child", "system"} or identity["provider"] != "codex":
                    excluded.add(identifier)
                    continue
                lease = leases.get(identity_key(identity))
                if lease is None or lease["identity"] != identity:
                    continue
                field_expiry = lease["fieldExpiresAtMs"]
                if not self._valid_lease(lease, field_expiry, row, now):
                    continue
                active = lease["activeExpiresAtMs"]
                recent = lease["recentExpiresAtMs"]
                if type(active) is int and active > now:
                    category = "active"
                elif type(recent) is int and recent > now:
                    category = "recent"
                else:
                    continue

                # The explicit row category is itself a positive-membership
                # claim.  If both branches are live, an active row must lose
                # its active authority at the active deadline even while its
                # recent branch remains positive; a fresh read can then
                # reclassify it as recent.
                branch_deadline = lease[
                    "activeExpiresAtMs" if category == "active" else "recentExpiresAtMs"
                ]
                deadline = min(lease["membershipExpiresAtMs"], branch_deadline)
                for name in ("runtime", "phase", "outcome", "latestTurn", "activity", "workspace"):
                    value = row.get(name)
                    if isinstance(value, dict) and value.get("health") == "current":
                        deadline = min(deadline, field_expiry[name])
                remaining_by_id[identifier] = max(0, deadline - now)
                sampled_by_id[identifier] = (
                    row["runtime"].get("observedAt")
                    if row["runtime"].get("clock") == "sample"
                    else None
                )
                categories[identifier] = category
                rows.append(row)

            # Host totals describe whole-roster membership, so their authority
            # ends with the first row proof that could change those totals.
            remaining = min(
                (*remaining_by_id.values(), *scope_remaining_by_host[host]),
                default=MAX_VALID_MS + MARGIN_MS,
            )
            result.append(Source(
                host, status, remaining, None, rows, admitted, excluded, complete,
                remaining_by_id, sampled_by_id, categories, True,
            ))
        return result

    @staticmethod
    def _valid_lease(lease, field_expiry, row, now):
        membership = lease.get("membershipExpiresAtMs")
        if type(membership) is not int or membership <= now:
            return False
        expected = {
            "activity", "kind", "lastUpdated", "latestTurn", "outcome",
            "phase", "runtime", "savedIdentity", "workspace",
        }
        if set(field_expiry) != expected:
            return False
        if any(value is not None and type(value) is not int for value in field_expiry.values()):
            return False
        for name in ("activeExpiresAtMs", "recentExpiresAtMs"):
            value = lease.get(name)
            if value is not None and (type(value) is not int or value <= now):
                return False
        if not any(
            type(lease.get(name)) is int and lease[name] > now
            for name in ("activeExpiresAtMs", "recentExpiresAtMs")
        ):
            return False
        for name in ("runtime", "phase", "outcome", "latestTurn", "activity", "workspace"):
            value = row.get(name)
            if isinstance(value, dict) and value.get("health") == "current":
                deadline = field_expiry[name]
                if type(deadline) is not int or deadline <= now:
                    return False
        return True

    async def run(self):
        from mesh_plus.api import configured_reader
        from mesh_plus.library_authority import LibraryMeshAuthority

        delay = 1
        while True:
            stream = None
            authority = LibraryMeshAuthority()
            try:
                self.closed = False
                socket = getattr(self, "socket", None) or os.path.join(
                    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
                    "mesh-plus-agent/read.sock" if self.full_roster
                    else "mesh-plus-agent-working-set/read.sock",
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
