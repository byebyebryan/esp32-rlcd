"""Explicit home routes and composition of independently admitted profile feeds."""

import asyncio
import json
import os
import re
import stat
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .projection import ALIASES, Projector, Source, identity_key, token
from .runtime import Events, Failure

MAX_CONFIG_BYTES = 65536
PROFILE_ID = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")
SOURCE_ID = re.compile(r"[a-z][a-z0-9_]{0,127}\Z")


@dataclass(frozen=True)
class ProfileRoute:
    host: str
    profile: str
    label: str
    codex_home: str
    source: str
    socket: str


@dataclass
class ProfileSource(Source):
    row_aliases: dict[str, str] = field(default_factory=dict)
    profile_statuses: dict[str, str] = field(default_factory=dict)


class ProfileProjector(Projector):
    """Keep native hosts/titles and attach presentation-only profile badges."""

    def __init__(self, hosts=("starship", "snap")):
        super().__init__(hosts)
        self.row_aliases = {}

    def project(self, sources):
        for source in sources:
            self.row_aliases.update(getattr(source, "row_aliases", {}))
        view = super().project(sources)
        # Keep a badge while a row is retained as uncertain context. Prune it
        # with the bounded roster, without changing native keys or host totals.
        self.row_aliases = {
            row["id"]: self.row_aliases.get(row["id"], ALIASES[self.hosts[row["host"]]])
            for row in self.roster
        }
        for row in view["rows"]:
            row["badge"] = self.row_aliases[row["id"]]
        return view

    def explain(self, sources, view, *, include_all=False):
        result = super().explain(sources, view, include_all=include_all)
        result["profiles"] = {
            source.host: dict(getattr(source, "profile_statuses", {})) for source in sources
        }
        for row in result["rows"]:
            row["display_host"] = self.row_aliases.get(row["display_id"])
        return result


def _path(value, *, canonical=True):
    return (isinstance(value, str) and value.startswith("/")
            and ".." not in PurePosixPath(value).parts
            and not any(unicodedata.category(c).startswith("C") for c in value)
            and (not canonical or str(PurePosixPath(value)) == value))


def parse_routes(document, *, hosts=None, selected=()):
    """Validate remote declarations without inspecting remote homes locally."""
    if (type(document) is not dict or set(document) != {"version", "routes"}
            or type(document["version"]) is not int or document["version"] != 1
            or type(document["routes"]) is not list
            or not 1 <= len(document["routes"]) <= 4):
        raise ValueError("profile_config_shape")
    routes, bindings, homes = [], set(), set()
    for entry in document["routes"]:
        fields = {"host", "profile", "label", "codex_home", "source", "socket"}
        if type(entry) is not dict or set(entry) != fields:
            raise ValueError("profile_route_shape")
        if (not isinstance(entry["host"], str) or entry["host"] not in ALIASES
                or not isinstance(entry["profile"], str)
                or PROFILE_ID.fullmatch(entry["profile"]) is None
                or not isinstance(entry["source"], str)
                or SOURCE_ID.fullmatch(entry["source"]) is None
                or not isinstance(entry["label"], str)
                or not 1 <= len(entry["label"]) <= 32
                or not entry["label"].isprintable()
                or not entry["label"].strip()
                or not _path(entry["codex_home"], canonical=False)
                or not _path(entry["socket"])):
            raise ValueError("profile_route_invalid")
        binding = entry["host"], entry["profile"]
        home = entry["host"], entry["codex_home"]
        if binding in bindings or home in homes:
            raise ValueError("profile_route_duplicate")
        if any(r.host == entry["host"] and r.source == entry["source"] for r in routes):
            raise ValueError("profile_source_duplicate")
        if any(r.host == entry["host"] and r.socket == entry["socket"] for r in routes):
            raise ValueError("profile_socket_duplicate")
        bindings.add(binding)
        homes.add(home)
        routes.append(ProfileRoute(**entry))
    if any(sum(r.host == host for r in routes) > 2 for host in ALIASES):
        raise ValueError("profile_config_capacity")
    selected = tuple(selected)
    if (len(selected) != len(set(selected))
            or set(selected) - {r.profile for r in routes}):
        raise ValueError("profile_selection_unknown")
    routes = [r for r in routes if (hosts is None or r.host in hosts)
              and (not selected or r.profile in selected)]
    if not routes:
        raise ValueError("profile_selection_empty")
    return tuple(sorted(routes, key=lambda r: (r.host, r.profile)))


def load_routes(path, *, hosts=None, selected=()):
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        node = os.fstat(stream.fileno())
        if (not stat.S_ISREG(node.st_mode) or node.st_uid != os.getuid()
                or node.st_mode & 0o077 or node.st_size > MAX_CONFIG_BYTES):
            raise ValueError("profile_config_policy")
        raw = stream.read(MAX_CONFIG_BYTES + 1)
        if len(raw) > MAX_CONFIG_BYTES:
            raise ValueError("profile_config_capacity")

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("profile_config_duplicate_key")
            value[key] = item
        return value

    return parse_routes(json.loads(raw, object_pairs_hook=unique), hosts=hosts, selected=selected)


def combine_sources(hosts, inputs):
    """Compose host presentation after each route has checked its own authority."""
    combined = []
    for host in hosts:
        profiles = [(route, source) for route, source in inputs if route.host == host]
        if not profiles:
            continue
        rows, admitted, excluded, complete, keys = [], set(), set(), set(), set()
        remaining, sampled, categories, labels, statuses = {}, {}, {}, {}, {}
        healthy = []
        for route, source in profiles:
            if source.host != route.host or route.profile in statuses:
                raise ValueError("profile_source_scope")
            statuses[route.profile] = source.status
            if source.status not in {"current", "partial"}:
                continue
            if not source.working_set:
                raise ValueError("profile_source_contract")
            if admitted & source.admitted_ids:
                raise ValueError("profile_identity_duplicate")
            healthy.append(source)
            admitted.update(source.admitted_ids)
            excluded.update(source.excluded_ids)
            complete.update(source.complete_scopes or ())
            for row in source.rows:
                key = identity_key(row["identity"])
                if key in keys or key[0] != host:
                    raise ValueError("profile_identity_duplicate")
                keys.add(key)
                identifier = token(row["identity"])[0]
                rows.append(row)
                remaining[identifier] = source.row_remaining_ms.get(identifier, source.remaining_ms)
                sampled[identifier] = source.sampled_by_id.get(identifier, source.sampled_at)
                if identifier in source.row_categories:
                    categories[identifier] = source.row_categories[identifier]
                labels[identifier] = (
                    "SW" if route.host == "snap" and route.profile == "work"
                    else ALIASES[route.host]
                )
        if healthy:
            status = "current" if all(s == "current" for s in statuses.values()) else "partial"
        elif all(s == "warming" for s in statuses.values()):
            status = "warming"
        else:
            status = "offline"
        combined.append(ProfileSource(
            host, status, min((s.remaining_ms for s in healthy), default=0),
            None, rows, admitted, excluded, complete, remaining, sampled,
            categories, True, labels, statuses,
        ))
    return combined


class ProfileFleet:
    """Multiple owned watches; ordinary route retries do not reset siblings."""

    def __init__(self, hosts, routes, events=None, *, fleet_factory=None):
        if fleet_factory is None:
            from .mesh import Fleet
            fleet_factory = Fleet
        self.routes = tuple(routes)
        self.hosts = [host for host in hosts if any(r.host == host for r in routes)]
        if not self.hosts or not self.routes:
            raise ValueError("profile_selection_empty")
        self.events = events or Events()
        self.ready = asyncio.Event()
        self.feeds = []
        groups = {}
        for route in self.routes:
            groups.setdefault((route.profile, route.source, route.socket), []).append(route)
        for (_, source, socket), group in sorted(groups.items()):
            fleet = fleet_factory(
                [r.host for r in group], self.events, source=source, socket=socket,
                expected_homes={r.host: r.codex_home for r in group},
            )
            self.feeds.append((tuple(group), fleet))

    def sources(self):
        inputs = []
        for routes, fleet in self.feeds:
            try:
                sources = {s.host: s for s in fleet.sources()}
            except (ValueError, KeyError, TypeError):
                sources = {}
                self.events.emit("mesh_profile_unavailable", interval=30,
                                 reason="profile_home_binding", profile=routes[0].profile)
            for route in routes:
                inputs.append((route, sources.get(route.host, Source(route.host, "offline"))))
        return combine_sources(self.hosts, inputs)

    async def run(self):
        async def ready(fleet):
            await fleet.ready.wait()
            self.ready.set()

        workers = [asyncio.create_task(fleet.run()) for _, fleet in self.feeds]
        notices = [asyncio.create_task(ready(fleet)) for _, fleet in self.feeds]
        original_error = None
        try:
            done, _ = await asyncio.wait(workers, return_when=asyncio.FIRST_COMPLETED)
            for worker in done:
                await worker
            raise Failure("profile_worker_returned")
        except BaseException as error:
            original_error = error
            raise
        finally:
            for task in [*workers, *notices]:
                task.cancel()
            results = await asyncio.gather(*workers, *notices, return_exceptions=True)
            if any(isinstance(r, Exception) and r is not original_error for r in results):
                raise Failure("profile_cleanup_failed") from None
