"""Public two-home Observer/Mesh admission through the dashboard profile fleet.

The services below use a committed synthetic API-v4 fixture and collect=False.
No native provider, ordinary user service, Mesh installation or firmware is run.
"""

import asyncio
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import threading
import time
import unittest
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
if str(APP / "host") not in os.sys.path:
    os.sys.path.insert(0, str(APP / "host"))

from live_dashboard.profiles import (  # noqa: E402
    ProfileFleet,
    ProfileProjector,
    parse_routes,
)
from live_dashboard.projection import identity_key, token  # noqa: E402

SDK_AVAILABLE = os.environ.get("RLCD_RUN_PUBLIC_INTEGRATION") == "1" and all(
    importlib.util.find_spec(name) is not None
    for name in ("agent_observer", "mesh_plus")
)
if SDK_AVAILABLE:
    from mesh_plus.api import Bridge, Client, Endpoint, Reader  # noqa: E402
    from mesh_plus.transport import IPCServer, connect_ipc  # noqa: E402

    from agent_observer.contract import store_namespace  # noqa: E402
    from agent_observer.mesh_working_set_publisher import (  # noqa: E402
        make_working_set_publisher,
    )
    from agent_observer.service_runtime import Runtime  # noqa: E402
    from agent_observer.service_state import ServiceState  # noqa: E402


HOST = "snap"
THREAD_ID = "00000000-0000-4000-8000-000000000123"
WINDOW_MS = 72 * 60 * 60 * 1000
FIXTURE = APP / "tests/fixtures/service-v4/view.json"


@dataclass(frozen=True)
class _ObserverRoute:
    host: str
    profile_id: str
    label: str
    codex_home: str
    namespace: str
    mesh_source: str
    collector_socket: Path
    publisher_runtime_dir: Path
    publisher_socket: Path
    window_ms: int = WINDOW_MS


def _observer_route(runtime_dir, profile_id, label, codex_home):
    if profile_id == "default":
        collector_name = "agent-observer"
        publisher_name = "mesh-plus-agent-working-set"
        mesh_source = "agent_working_set"
    else:
        collector_name = f"agent-observer-profile-{profile_id}"
        publisher_name = f"mesh-plus-agent-working-set-{profile_id}"
        mesh_source = f"agent_working_set_{profile_id}"
    home = str(codex_home)
    namespace = store_namespace("codex", home, "explicit", os.geteuid())
    return _ObserverRoute(
        host=HOST,
        profile_id=profile_id,
        label=label,
        codex_home=home,
        namespace=namespace,
        mesh_source=mesh_source,
        collector_socket=runtime_dir / collector_name / "read.sock",
        publisher_runtime_dir=runtime_dir / publisher_name,
        publisher_socket=runtime_dir / publisher_name / "read.sock",
    )


def _service_state(route, *, native_home=None, include_row=True):
    home = route.codex_home if native_home is None else str(native_home)
    uid = os.geteuid()
    namespace = store_namespace("codex", home, "explicit", uid)
    envelope = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sample = copy.deepcopy(envelope["snapshot"])
    sample["sources"] = [source for source in sample["sources"] if source["provider"] == "codex"]
    sample["sessions"] = [row for row in sample["sessions"] if row["identity"]["provider"] == "codex"]
    sample["host"].update(authority=route.host, uid=uid)
    wall = time.time_ns() // 1_000_000
    sample["collectedAt"] = wall
    sample["sourceHealth"] = "current"
    source = sample["sources"][0]
    source.update(configHome=home, configHomeKind="explicit", namespace=namespace)
    source["capabilities"]["activity"] = True
    sample["sessions"] = sample["sessions"][:1] if include_row else []
    for row in sample["sessions"]:
        row["identity"].update(
            hostScope=route.host,
            namespace=namespace,
            nativeId=THREAD_ID,
        )
        row["nativeIds"].update(threadId=THREAD_ID, sessionTreeRootId=THREAD_ID)
        row["runtime"].update(
            value="running",
            observedAt=wall,
            source="codex_rpc",
            health="current",
            reason="native_timestamp",
            clock="sample",
        )
        row["activity"].update(
            at=wall - 5_000,
            source="codex_rpc",
            health="current",
            reason="native_timestamp",
        )
        if row["phase"] is not None:
            row["phase"].update(observedAt=wall, clock="sample")

    state = ServiceState(
        host_scope=route.host,
        configs={"codex": (home, "explicit")},
        uid=uid,
        working_set_window_ms=route.window_ms,
    )
    sampled = state.clock()
    state.attempt("codex", "runtime")
    accepted = state.accept(
        "codex",
        "runtime",
        sample,
        sampled_ms=sampled,
        ttl_ms=120_000,
        accepted_boottime_ms=sampled,
    )
    if accepted is not True:
        raise AssertionError("fixture_acceptance_required")
    return state, namespace


class _ObserverFixtureRuntime:
    """One disposable Observer socket serving an already seeded ServiceState."""

    def __init__(self, state, path):
        self.path = Path(path)
        self.runtime = Runtime(state, self.path, collect=False)
        self.stop = threading.Event()
        self.errors = []
        self.thread = threading.Thread(target=self._run, name="profile-observer-fixture")

    def _run(self):
        try:
            self.runtime.run(self.stop)
        except BaseException as error:  # surfaced in the owning test thread
            self.errors.append(error)

    def __enter__(self):
        self.thread.start()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if self.errors:
                self.__exit__()
                raise AssertionError(self.errors)
            try:
                if self.path.stat().st_mode & 0o777 == 0o600:
                    return self
            except OSError:
                pass
            time.sleep(0.01)
        self.__exit__()
        raise AssertionError("observer_fixture_socket_not_ready")

    def __exit__(self, *_args):
        self.stop.set()
        self.thread.join(4)
        if self.thread.is_alive():
            raise AssertionError("observer_fixture_thread_not_stopped")
        if self.path.exists():
            raise AssertionError("observer_fixture_socket_leaked")
        if self.errors:
            raise AssertionError(self.errors)


def _reader_clock():
    return {
        "bootId": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        "timeNamespace": os.readlink("/proc/self/ns/time").replace("[", "").replace("]", ""),
    }


def _reader_now():
    return int(time.clock_gettime(time.CLOCK_BOOTTIME) * 1000)


class _PublicProfileHarness:
    def __init__(self, *, empty_profiles=(), wrong_homes=None):
        self.temporary = tempfile.TemporaryDirectory(prefix="hp-public-")
        self.root = Path(self.temporary.name)
        self.runtime_dir = self.root / "xdg"
        self.runtime_dir.mkdir(mode=0o700)
        self.default_home = self.root / "codex-default"
        self.work_home = self.root / "codex-work"
        self.observer_routes = (
            _observer_route(self.runtime_dir, "default", "Default", self.default_home),
            _observer_route(self.runtime_dir, "work", "Work", self.work_home),
        )
        consumer_document = {
            "version": 1,
            "routes": [
                {
                    "host": route.host,
                    "profile": route.profile_id,
                    "label": route.label,
                    "codex_home": route.codex_home,
                    "source": route.mesh_source,
                    "socket": str(route.publisher_socket),
                }
                for route in self.observer_routes
            ],
        }
        self.routes = parse_routes(consumer_document, hosts=[HOST])
        self.profile_fleet = ProfileFleet([HOST], self.routes)
        self.fleets = {
            routes[0].profile: fleet for routes, fleet in self.profile_fleet.feeds
        }
        self.empty_profiles = set(empty_profiles)
        self.wrong_homes = dict(wrong_homes or {})
        self.runtime_stack = ExitStack()
        self.servers = []
        self.feeds = {}

    async def start(self):
        observer_by_id = {route.profile_id: route for route in self.observer_routes}
        for profile_id, route in observer_by_id.items():
            native_home = self.wrong_homes.get(profile_id)
            state, namespace = _service_state(
                route,
                native_home=native_home,
                include_row=profile_id not in self.empty_profiles,
            )
            self.runtime_stack.enter_context(
                _ObserverFixtureRuntime(state, route.collector_socket)
            )
            publisher = make_working_set_publisher(
                route.host,
                route.mesh_source,
                route.collector_socket,
                window_ms=route.window_ms,
            )
            route.publisher_runtime_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            server = await IPCServer(route.publisher_socket, Bridge(publisher).serve).start()
            self.servers.append(server)
            consumer_route = next(r for r in self.routes if r.profile == profile_id)
            fleet = self.fleets[profile_id]
            profile = fleet.profile
            codec = profile.bind(route.host, route.mesh_source)
            revision = "sha256:" + hashlib.sha256(route.mesh_source.encode()).hexdigest()

            async def connect(route=route, profile=profile, codec=codec):
                channel = await connect_ipc(route.publisher_socket)
                return await Client.connect(
                    channel,
                    host=route.host,
                    source=route.mesh_source,
                    profile=profile.descriptor.profile_id,
                    codec=codec.validate_bridge,
                )

            async def catalog_check(revision=revision):
                return revision

            reader = Reader(
                "agent",
                [Endpoint(route.host, False, revision, connect, codec)],
                local_host="home-profile-test",
                profile=profile,
                catalog_revision=revision,
                catalog_check=catalog_check,
            )
            stream = reader.watch_admitted(
                request_id=fleet.request_id,
                proof_interval=0.1,
            )
            self.feeds[profile_id] = {
                "observer_route": route,
                "consumer_route": consumer_route,
                "namespace": namespace,
                "publisher": publisher,
                "server": server,
                "reader": reader,
                "stream": stream,
                "fleet": fleet,
            }

    def _raw_host(self, profile_id):
        snapshot = self.feeds[profile_id]["fleet"].guard.snapshot()
        if snapshot is None:
            return None
        return snapshot["mesh"]["hosts"][0]

    def _public_ready(self, profile_id):
        host = self._raw_host(profile_id)
        return (
            host is not None
            and host["delivery"]["status"] == "ready"
            and host["delivery"]["proof"] is not None
        )

    async def pump_profile(self, profile_id, *, public_ready_only=False, row_count=1):
        feed = self.feeds[profile_id]
        fleet = feed["fleet"]
        for _ in range(60):
            frame = await asyncio.wait_for(anext(feed["stream"]), timeout=3)
            fleet.guard.accept(frame)
            if not self._public_ready(profile_id):
                continue
            host = self._raw_host(profile_id)
            context_source = host["owner"]["service"]["sources"][0]
            if public_ready_only:
                return context_source
            source, = fleet.sources()
            if source.status == "current" and len(source.rows) == row_count:
                return source
        raise AssertionError(f"profile_{profile_id}_did_not_reach_expected_public_read")

    def sources(self):
        return self.profile_fleet.sources()

    async def close(self):
        for feed in self.feeds.values():
            feed["fleet"].guard.disconnect()
            await feed["stream"].aclose()
        for server in reversed(self.servers):
            if not server.closed:
                await server.close()
        self.runtime_stack.close()
        self.temporary.cleanup()


@unittest.skipUnless(
    SDK_AVAILABLE,
    "strict Observer/Mesh integration runs only through "
    "scripts/test-dashboard-integration.sh",
)
class PublicHomeProfileIntegrationTest(unittest.IsolatedAsyncioTestCase):
    async def test_same_host_same_native_id_survives_with_plain_titles_and_independent_expiry_close(self):
        harness = _PublicProfileHarness()
        try:
            await harness.start()
            await harness.pump_profile("default")
            await harness.pump_profile("work")

            default_route = next(r for r in harness.routes if r.profile == "default")
            work_route = next(r for r in harness.routes if r.profile == "work")
            self.assertEqual(harness.fleets["default"].source, default_route.source)
            self.assertEqual(harness.fleets["work"].source, work_route.source)
            self.assertEqual(harness.fleets["default"].expected_homes, {HOST: default_route.codex_home})
            self.assertEqual(harness.fleets["work"].expected_homes, {HOST: work_route.codex_home})
            self.assertEqual(harness.feeds["default"]["reader"].endpoints[0].codec.source, default_route.source)
            self.assertEqual(harness.feeds["work"]["reader"].endpoints[0].codec.source, work_route.source)
            for profile_id, route in (("default", default_route), ("work", work_route)):
                native_source = harness._raw_host(profile_id)["owner"]["service"]["sources"][0]
                self.assertEqual(native_source["configHome"], route.codex_home)
                self.assertEqual(native_source["namespace"], route_namespace(route))

            combined, = harness.sources()
            self.assertEqual(combined.status, "current")
            self.assertEqual(combined.profile_statuses, {"default": "current", "work": "current"})
            rows = combined.rows
            self.assertEqual(len(rows), 2)
            self.assertEqual([row["identity"]["hostScope"] for row in rows], [HOST, HOST])
            self.assertEqual([row["identity"]["nativeId"] for row in rows], [THREAD_ID, THREAD_ID])
            self.assertEqual(
                {row["identity"]["namespace"] for row in rows},
                {route_namespace(default_route), route_namespace(work_route)},
            )
            self.assertEqual(len({identity_key(row["identity"]) for row in rows}), 2)
            self.assertTrue(all(row["title"] == "Fixture Codex 2" for row in rows))
            projected = ProfileProjector([HOST]).project([combined])
            self.assertEqual(len(projected["rows"]), 2)
            self.assertTrue(all(row["label"].startswith("Fixture Codex 2") for row in projected["rows"]))
            self.assertEqual(len({row["label"] for row in projected["rows"]}), 2)
            self.assertEqual({row["badge"] for row in projected["rows"]}, {"SN", "SW"})
            self.assertEqual(len(projected["hosts"]), 1)

            work_snapshot = harness._raw_host("work")
            expiry = [receipt["expiresAtMs"] for receipt in work_snapshot["receipts"]
                      if type(receipt["expiresAtMs"]) is int]
            self.assertTrue(expiry)
            expired_work = harness.fleets["work"].guard.read(max(expiry) + 1, _reader_clock())
            self.assertEqual(expired_work.members, [])
            current_default = harness.fleets["default"].guard.read(_reader_now(), _reader_clock())
            self.assertEqual(len(current_default.members), 1)
            harness.fleets["work"].guard.disconnect()
            after_close, = harness.sources()
            after_close_view = ProfileProjector([HOST]).project([after_close])
            self.assertEqual([row["label"] for row in after_close_view["rows"]], ["Fixture Codex 2"])
            self.assertEqual(after_close_view["rows"][0]["badge"], "SN")
        finally:
            await harness.close()

    async def test_valid_wrong_home_public_frame_is_refused_without_hiding_sibling(self):
        harness = _PublicProfileHarness(wrong_homes={"work": "/fixture/codex-work-wrong"})
        try:
            await harness.start()
            await harness.pump_profile("default")
            actual = await harness.pump_profile("work", public_ready_only=True)
            work_route = next(r for r in harness.routes if r.profile == "work")
            self.assertEqual(actual["configHome"], "/fixture/codex-work-wrong")
            self.assertNotEqual(actual["configHome"], work_route.codex_home)
            self.assertEqual(
                actual["namespace"],
                store_namespace("codex", actual["configHome"], "explicit", os.geteuid()),
            )
            work_read = harness.fleets["work"].guard.read(_reader_now(), _reader_clock())
            self.assertEqual(work_read.context["hosts"][0]["owner"]["service"]["sources"][0]["configHome"], actual["configHome"])

            combined, = harness.sources()
            self.assertEqual(combined.status, "partial")
            self.assertEqual(combined.profile_statuses, {"default": "current", "work": "offline"})
            self.assertEqual(len(combined.rows), 1)
            self.assertEqual(combined.rows[0]["identity"]["nativeId"], THREAD_ID)
            self.assertEqual(combined.rows[0]["identity"]["namespace"], route_namespace(default_route(harness)))
            projected = ProfileProjector([HOST]).project([combined])
            self.assertEqual(len(projected["rows"]), 1)
            self.assertEqual(projected["rows"][0]["label"], "Fixture Codex 2")
        finally:
            await harness.close()

    async def test_complete_empty_work_scope_keeps_default_row(self):
        harness = _PublicProfileHarness(empty_profiles={"work"})
        try:
            await harness.start()
            await harness.pump_profile("default")
            await harness.pump_profile("work", row_count=0)
            combined, = harness.sources()
            self.assertEqual(combined.status, "current")
            self.assertEqual(combined.profile_statuses, {"default": "current", "work": "current"})
            self.assertIn(("codex", route_namespace(default_route(harness))), combined.complete_scopes)
            self.assertIn(("codex", route_namespace(work_route(harness))), combined.complete_scopes)
            projected = ProfileProjector([HOST]).project([combined])
            self.assertEqual(len(projected["rows"]), 1)
            self.assertEqual(projected["rows"][0]["id"], token(combined.rows[0]["identity"])[0])
            self.assertEqual(projected["rows"][0]["label"], "Fixture Codex 2")
        finally:
            await harness.close()


def default_route(harness):
    return next(route for route in harness.routes if route.profile == "default")


def work_route(harness):
    return next(route for route in harness.routes if route.profile == "work")


def route_namespace(route):
    return store_namespace("codex", route.codex_home, "explicit", os.geteuid())


if __name__ == "__main__":
    unittest.main()
