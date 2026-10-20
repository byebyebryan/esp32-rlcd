"""Profile composition keeps native identity, coverage and worker lifetime separate."""

import asyncio
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.profiles import (
    ProfileFleet, ProfileProjector as Projector, ProfileRoute,
    combine_sources, load_routes, parse_routes,
)
from live_dashboard.projection import Source, token
from live_dashboard.runtime import Events, Failure
from test_working_set_consumer import session


def route(profile="default", *, host="snap"):
    return ProfileRoute(
        host, profile, profile.title(), "/fixture/" + profile,
        "agent_working_set" + ("_" + profile if profile != "default" else ""),
        "/run/user/1000/mesh-" + profile + "/read.sock",
    )


def document():
    return {"version": 1, "routes": [vars(route()), vars(route("work")),
                                     vars(route(host="starship"))]}


def row(namespace="default", *, host="snap", identifier="same-native-id"):
    value = session(identifier, host=host)
    value["identity"]["namespace"] = namespace
    return value


def source(value=None, *, namespace="default", status="current", remaining=5000):
    rows = [] if value is None else [value]
    ids = {token(r["identity"])[0] for r in rows}
    return Source(
        "snap", status, remaining, 10000, rows, ids, set(),
        {("codex", namespace)} if status == "current" else set(),
        {identifier: remaining for identifier in ids},
        {identifier: 10000 for identifier in ids},
        {identifier: "active" for identifier in ids}, True,
    )


class Configuration(unittest.TestCase):
    def test_configured_home_spelling_is_preserved_for_native_namespace(self):
        value = document()
        value["routes"][0]["codex_home"] = "/fixture/codex/"
        parsed = parse_routes(value)
        self.assertEqual(next(r.codex_home for r in parsed
                              if r.host == "snap" and r.profile == "default"),
                         "/fixture/codex/")

    def test_all_and_work_only_have_exact_configured_hosts(self):
        routes = parse_routes(document(), hosts=["starship", "snap"])
        self.assertEqual(len(routes), 3)
        selected = parse_routes(document(), hosts=["starship", "snap"], selected=["work"])
        self.assertEqual([(r.host, r.profile) for r in selected], [("snap", "work")])
        for selected in (["missing"], ["work", "work"]):
            with self.assertRaisesRegex(ValueError, "profile_selection_unknown"):
                parse_routes(document(), selected=selected)

    def test_route_aliases_and_malformed_config_reject(self):
        for modify in (
            lambda d: d.update(version=True),
            lambda d: d["routes"].append(dict(d["routes"][0])),
            lambda d: d["routes"][1].update(codex_home="/fixture/default"),
            lambda d: d["routes"][1].update(source="agent_working_set"),
            lambda d: d["routes"][1].update(socket=d["routes"][0]["socket"]),
            lambda d: d["routes"][1].update(codex_home="/fixture/../work"),
            lambda d: d["routes"][1].update(label="hidden\nlabel"),
            lambda d: d["routes"][1].update(host=[]),
        ):
            value = document()
            modify(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_routes(value)

    def test_private_file_is_bounded_and_duplicate_keys_reject(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profiles.json"
            path.write_text(json.dumps(document()))
            path.chmod(0o600)
            self.assertEqual(len(load_routes(path)), 3)
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "profile_config_policy"):
                load_routes(path)
            path.chmod(0o600)
            path.write_text('{"version":1,"version":1,"routes":[]}')
            with self.assertRaisesRegex(ValueError, "profile_config_duplicate_key"):
                load_routes(path)
            path.write_bytes(b" " * 65537)
            with self.assertRaisesRegex(ValueError, "profile_config_policy"):
                load_routes(path)


class Composition(unittest.TestCase):
    def test_same_native_uuid_in_two_namespaces_survives_union_and_wire_limit(self):
        first, second = row(), row("work")
        first["title"] = "First session"
        second["title"] = "yearly-recap-review"
        combined, = combine_sources(["snap"], [
            (route(), source(first)),
            (route("work"), source(second, namespace="work")),
        ])
        self.assertEqual(combined.status, "current")
        view = Projector(["snap"]).project([combined])
        self.assertEqual(len(view["rows"]), 2)
        self.assertEqual(len({r["id"] for r in view["rows"]}), 2)
        self.assertTrue(all(r["host"] == 0 for r in view["rows"]))
        self.assertEqual({r["label"] for r in view["rows"]},
                         {"First session", "yearly-recap-review"})
        self.assertEqual({r["label"]: r["badge"] for r in view["rows"]},
                         {"First session": "SN", "yearly-recap-review": "SW"})
        self.assertEqual(first["title"], "First session")
        self.assertEqual(second["title"], "yearly-recap-review")

    def test_one_profile_outage_keeps_other_current_and_context_scoped(self):
        default, work = row(), row("work")
        projector = Projector(["snap"])
        both = [(route(), source(default)), (route("work"), source(work, namespace="work"))]
        projector.project(combine_sources(["snap"], both))
        lost = [(route(), source(status="offline")), both[1]]
        combined, = combine_sources(["snap"], lost)
        self.assertEqual(combined.status, "partial")
        view = projector.project([combined])
        by_id = {r["id"]: r for r in view["rows"]}
        self.assertEqual(by_id[token(work["identity"])[0]]["state"], "working")
        self.assertGreater(by_id[token(work["identity"])[0]]["valid_ms"], 0)
        self.assertEqual(by_id[token(default["identity"])[0]]["state"], "unknown")
        self.assertEqual(by_id[token(default["identity"])[0]]["badge"], "SN")
        self.assertEqual(by_id[token(work["identity"])[0]]["badge"], "SW")

        work_lost = [both[0], (route("work"), source(status="offline"))]
        uncertain = projector.project(combine_sources(["snap"], work_lost))
        work_context = next(r for r in uncertain["rows"] if r["id"] == token(work["identity"])[0])
        self.assertEqual((work_context["state"], work_context["badge"]), ("unknown", "SW"))

        empty = [(route(), source()), both[1]]
        view = projector.project(combine_sources(["snap"], empty))
        self.assertEqual([r["id"] for r in view["rows"]], [token(work["identity"])[0]])

    def test_short_profile_lease_does_not_shorten_healthy_sibling_row(self):
        default, work = row(), row("work")
        combined, = combine_sources(["snap"], [
            (route(), source(default, remaining=50)),
            (route("work"), source(work, namespace="work", remaining=5000)),
        ])
        view = Projector(["snap"]).project([combined])
        by_id = {r["id"]: r for r in view["rows"]}
        self.assertEqual(by_id[token(default["identity"])[0]]["valid_ms"], 0)
        self.assertEqual(by_id[token(work["identity"])[0]]["valid_ms"], 3000)

    def test_duplicate_exact_identity_is_a_conflict(self):
        value = row()
        with self.assertRaisesRegex(ValueError, "profile_identity_duplicate"):
            combine_sources(["snap"], [(route(), source(value)), (route("work"), source(value))])

    def test_profile_health_is_available_without_firmware_extension(self):
        combined, = combine_sources(["snap"], [
            (route(), source()), (route("work"), source(status="offline")),
        ])
        projector = Projector(["snap"])
        report = projector.explain([combined], projector.project([combined]))
        self.assertEqual(report["profiles"], {"snap": {"default": "current", "work": "offline"}})

    def test_device_limit_is_applied_after_profiles_are_combined(self):
        first = source()
        for index in range(32):
            value = row(identifier="default-" + str(index))
            identifier = token(value["identity"])[0]
            first.rows.append(value)
            first.admitted_ids.add(identifier)
            first.row_remaining_ms[identifier] = 5000
            first.sampled_by_id[identifier] = 10000
        urgent = row("work")
        urgent["phase"]["value"] = "blocked"
        view = Projector(["snap"]).project(combine_sources(["snap"], [
            (route(), first), (route("work"), source(urgent, namespace="work")),
        ]))
        self.assertEqual(view["hosts"][0]["total"], 33)
        self.assertEqual(len(view["rows"]), 32)
        self.assertEqual(view["rows"][0]["id"], token(urgent["identity"])[0])


class HomeBinding(unittest.TestCase):
    def test_warming_owner_does_not_report_a_false_home_mismatch(self):
        fleet = Fleet.__new__(Fleet)
        fleet.expected_homes = {"snap": "/fixture/work"}
        output = io.StringIO()
        fleet.events = Events(output)
        source = Source("snap", "warming")
        self.assertEqual(fleet._bound_sources([source], {"hosts": [
            {"hostId": "snap", "owner": None},
        ]}), [source])
        self.assertEqual(output.getvalue(), "")
        # One host may already be ready while the other's owner is absent.
        # Host-level scope summaries do not make that missing owner a mismatch.
        for status in ("current", "partial"):
            result, = fleet._bound_sources([Source("snap", status)], {"hosts": [
                {"hostId": "snap", "owner": None},
            ]})
            self.assertEqual(result.status, "warming")
        self.assertEqual(output.getvalue(), "")

    @unittest.skipUnless(__import__("importlib").util.find_spec("agent_observer"), "optional Observer")
    def test_one_wrong_home_does_not_hide_another_host(self):
        from agent_observer.public import store_namespace

        fleet = Fleet.__new__(Fleet)
        fleet.expected_homes = {"starship": "/fixture/default", "snap": "/fixture/work"}
        fleet.events = Events(io.StringIO())
        hosts = []
        for host in ("starship", "snap"):
            home = "/fixture/default"
            hosts.append({"hostId": host, "owner": {"service": {
                "uid": os.getuid(), "sources": [{"provider": "codex", "configHome": home,
                    "configHomeKind": "explicit", "namespace": store_namespace(
                        "codex", home, "explicit", os.getuid())}],
            }}})
        result = fleet._bound_sources([Source("starship", "current"), Source("snap", "current")],
                                      {"hosts": hosts})
        self.assertEqual([(s.host, s.status) for s in result],
                         [("starship", "current"), ("snap", "offline")])


class Lifetime(unittest.IsolatedAsyncioTestCase):
    async def test_worker_failure_survives_successful_cleanup(self):
        class FakeFleet:
            def __init__(self, *args, **kwargs):
                self.ready = asyncio.Event()

            async def run(self):
                raise Failure("mesh_cleanup_failed")

        fleet = ProfileFleet(["snap"], [route()], fleet_factory=FakeFleet)
        with self.assertRaisesRegex(Failure, "^mesh_cleanup_failed$"):
            await fleet.run()

    async def test_independent_readiness_and_owner_cancel_retire_all_workers(self):
        instances = []

        class FakeFleet:
            def __init__(self, hosts, events, **options):
                self.hosts, self.options = hosts, options
                self.ready = asyncio.Event()
                self.entered, self.retired = asyncio.Event(), asyncio.Event()
                instances.append(self)

            async def run(self):
                self.entered.set()
                if self.options["source"].endswith("_work"):
                    self.ready.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    self.retired.set()

            def sources(self):
                return [Source(host, "warming") for host in self.hosts]

        fleet = ProfileFleet(["starship", "snap"], parse_routes(document()), fleet_factory=FakeFleet)
        task = asyncio.create_task(fleet.run())
        await asyncio.wait_for(fleet.ready.wait(), 1)
        self.assertTrue(any(not instance.ready.is_set() for instance in instances))
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(all(instance.retired.is_set() for instance in instances))


if __name__ == "__main__":
    unittest.main()
