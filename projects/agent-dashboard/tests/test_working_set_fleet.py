"""Installed working-set lifecycle and whole-roster presentation acceptance."""

import asyncio
import copy
import importlib.util
import io
import sys
import types
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


TESTS = Path(__file__).resolve().parent
APP = TESTS.parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(APP / "host"))

from live_dashboard.mesh import Fleet, _runtime_sample_at
from live_dashboard.projection import Projector, token
from live_dashboard.runtime import Events

AVAILABLE = all(
    importlib.util.find_spec(name) is not None
    for name in ("agent_observer", "mesh_plus")
)


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh working-set acceptance")
class WorkingSetFleet(unittest.TestCase):
    def fleet(self, frames, *, full_roster=False):
        from working_set_fixture import REQUEST, response

        fleet = Fleet(list(frames), full_roster=full_roster)
        fleet.request_id = REQUEST
        fleet.guard = fleet.new_guard()
        frame = response(frames, profile=fleet.profile, source=fleet.source)
        fleet.guard.accept(frame)
        self.addCleanup(fleet.guard.disconnect)
        return fleet, frame.snapshot()

    def at(self, fleet, frame, now=None):
        now = frame["mesh"]["reader"]["encodedAtMs"] if now is None else now
        with patch("mesh_plus.transport.boottime_ms", return_value=now), patch(
            "mesh_plus.evidence.clock_domain",
            return_value=frame["mesh"]["reader"]["clock"],
        ):
            return fleet.sources()

    def test_nominal_selected_view_matches_full_diagnostics(self):
        from working_set_fixture import REQUEST, native, new_state, response

        # Keep only three recent active members eligible. The other 97 saved
        # rows have current parked state and a supported old-window activity
        # anchor, providing complete negative membership evidence.
        row_specs = [{} for _ in range(3)] + [
            {"runtime": "parked", "activity_offset_ms": -(72 * 60 * 60 * 1000 + 5000)}
            for _ in range(97)
        ]
        states = {
            host: new_state(host, 100, row_specs=row_specs)
            for host in ("starship", "snap")
        }
        working_frames = {host: native(state) for host, state in states.items()}
        fleet, raw = self.fleet(working_frames)
        sources = self.at(fleet, raw)
        self.assertEqual(len(raw["sessions"]), 6)
        self.assertEqual(
            {
                host: sum(
                    row["identity"]["hostScope"] == host for row in raw["sessions"]
                )
                for host in states
            },
            {host: 3 for host in states},
        )
        self.assertEqual(len(fleet.guard.snapshot()["sessions"]), 6)
        self.assertTrue(all(source.complete_scopes for source in sources))

        full = Fleet(list(states), full_roster=True)
        full.request_id = REQUEST
        full.guard = full.new_guard()
        full_frame = response(
            {host: native(state, full=True) for host, state in states.items()},
            profile=full.profile,
            source=full.source,
        )
        full.guard.accept(full_frame)
        self.addCleanup(full.guard.disconnect)
        full_raw = full_frame.snapshot()
        full_sources = self.at(full, full_raw)
        self.assertEqual(len(full_raw["sessions"]), 200)
        self.assertEqual(
            {
                host: sum(
                    row["identity"]["hostScope"] == host
                    for row in full_raw["sessions"]
                )
                for host in states
            },
            {host: 100 for host in states},
        )
        self.assertEqual(len(full.guard.snapshot()["sessions"]), 200)
        for source in [*sources, *full_sources]:
            for row in source.rows:
                row_id = token(row["identity"])[0]
                self.assertIn(row_id, source.sampled_by_id)
                self.assertEqual(
                    source.sampled_by_id[row_id], _runtime_sample_at(row)
                )
        # The envelope collection time can differ from the row's own runtime
        # sample; both adapters must retain identical activity-age ordering.
        for source in full_sources:
            source.sampled_at += 60000
        self.assertEqual(Projector().project(sources), Projector().project(full_sources))

        sources[0].rows.clear()
        self.assertEqual(len(self.at(fleet, raw)[0].rows), 3)
        self.assertEqual(len(fleet.guard.snapshot()["sessions"]), 6)

    def test_complete_empty_scope_and_independent_expiry(self):
        from working_set_fixture import native, new_state

        home = "/fixture/starship-codex-working-set"
        positive = new_state(
            "starship", 3, home=home, history_ttl_ms=60000,
            runtime_ttl_ms=5000, split_activity=True,
        )
        prior_fleet, prior_raw = self.fleet({"starship": native(positive)})
        projector = Projector(["starship"])
        self.assertEqual(projector.project(self.at(prior_fleet, prior_raw))["hosts"][0]["total"], 3)

        empty = new_state(
            "starship", 0, home=home, history_ttl_ms=60000, runtime_ttl_ms=5000,
        )
        empty_fleet, empty_raw = self.fleet({"starship": native(empty)})
        projector.project(self.at(empty_fleet, empty_raw))
        deadline = min(
            receipt["expiresAtMs"]
            for receipt in empty_raw["mesh"]["hosts"][0]["receipts"]
            if receipt["health"] in {"current", "partial"}
        )
        before = self.at(empty_fleet, empty_raw, deadline - 1000)
        self.assertEqual(projector.project(before)["hosts"][0]["total"], 0)

        # A complete-empty generation observed before expiry stays retired.
        expired = self.at(empty_fleet, empty_raw, deadline)
        self.assertEqual(expired[0].status, "partial")
        self.assertFalse(expired[0].complete_scopes)
        self.assertEqual(projector.project(expired)["hosts"][0]["total"], 0)

        # If that short empty proof is missed, the prior long-lived member
        # fields remain as unknown context until their own support expires.
        missed = Projector(["starship"])
        missed.project(self.at(prior_fleet, prior_raw))
        retained = missed.project(expired)
        self.assertEqual(retained["hosts"][0]["total"], 3)
        self.assertTrue(all(row["valid_ms"] == 0 for row in missed.roster))

    def test_partial_missed_negative_never_retires_context(self):
        from working_set_fixture import accept, native, new_state, sample

        home = "/fixture/starship-codex-working-set"
        state = new_state("starship", 3, home=home, history_ttl_ms=60000,
                          runtime_ttl_ms=60000)
        first, raw = self.fleet({"starship": native(state)})
        projector = Projector(["starship"])
        projector.project(self.at(first, raw))

        partial = sample("starship", 2, home=home)
        partial["sourceHealth"] = "partial"
        partial["sources"][0]["sourceHealth"] = "partial"
        partial["sources"][0]["coverage"]["runtime"].update(
            status="partial", reason="catalog_limit",
        )
        accept(state, partial, history_ttl_ms=60000, runtime_ttl_ms=60000)
        second, current = self.fleet({"starship": native(state, sequence=2)})
        current_sources = self.at(second, current)
        self.assertEqual(current_sources[0].status, "partial")
        projector.project(current_sources)
        self.assertEqual(len(projector.roster), 3)

        deadline = min(
            receipt["expiresAtMs"]
            for receipt in current["mesh"]["hosts"][0]["receipts"]
            if receipt["health"] in {"current", "partial"}
        )
        projector.project(self.at(second, current, deadline + 1000))
        self.assertEqual(len(projector.roster), 3)
        self.assertTrue(all(row["state"] == "unknown" for row in projector.roster))
        self.assertTrue(all(row["valid_ms"] == 0 for row in projector.roster))

    def test_original_activity_anchor_and_independent_field_expiry(self):
        from working_set_fixture import native, new_state

        state = new_state(
            "starship", 3, activity_offset_ms=-30000,
            history_ttl_ms=5000, runtime_ttl_ms=60000, split_activity=True,
        )
        fleet, raw = self.fleet({"starship": native(state)})
        scope = raw["mesh"]["hosts"][0]["owner"]["metadata"]["scopes"][0]
        member = scope["members"][0]
        supports = scope["supportTable"]
        activity_support = supports[member["fieldSupports"]["activity"]]
        runtime_support = supports[member["fieldSupports"]["runtime"]]
        self.assertEqual(activity_support["component"], "history")
        self.assertEqual(runtime_support["component"], "runtime")

        projector = Projector(["starship"])
        initial = projector.project(self.at(fleet, raw))
        self.assertTrue(all(row["age"] == "30s" for row in initial["rows"]))
        later = raw["mesh"]["reader"]["encodedAtMs"] + 1000
        self.assertTrue(all(
            row["age"] == "30s"
            for row in projector.project(self.at(fleet, raw, later))["rows"]
        ))

        history_deadline = next(
            receipt["expiresAtMs"]
            for receipt in raw["mesh"]["hosts"][0]["receipts"]
            if receipt["component"] == "history"
        )
        expired = self.at(fleet, raw, history_deadline)
        self.assertEqual(len(expired[0].rows), 3)
        view = projector.project(expired)
        self.assertTrue(all(row["age"] == "?" and row["valid_ms"] > 0 for row in view["rows"]))

    def test_receipt_replacement_cannot_renew_old_membership_support(self):
        from working_set_fixture import native, new_state

        state = new_state("starship", 3)
        fleet, raw = self.fleet({"starship": native(state)})
        broken = copy.deepcopy(raw)
        host = broken["mesh"]["hosts"][0]
        component = next(
            item for item in host["owner"]["service"]["sources"][0]["components"]
            if item["name"] == "runtime"
        )
        component["accepted"] += 1
        component["attempts"] += 1
        receipt = next(item for item in host["receipts"] if item["component"] == "runtime")
        receipt["accepted"] += 1
        broken["mesh"]["reader"].update(sequence=2, revision=2)

        with self.assertRaises(ValueError):
            fleet.guard.accept(broken)
        source = self.at(fleet, raw)[0]
        self.assertFalse(source.rows)
        self.assertFalse(source.complete_scopes)
        self.assertFalse(source.excluded_ids)

    def test_exact_nonmember_reconciles_beyond_display_limit(self):
        from working_set_fixture import accept, native, new_state, sample

        home = "/fixture/starship-codex-working-set"
        state = new_state("starship", 40, home=home)
        fleet, raw = self.fleet({"starship": native(state)})
        projector = Projector(["starship"])
        view = projector.project(self.at(fleet, raw))
        self.assertEqual(len(view["rows"]), 32)
        self.assertEqual(len(projector.roster), 40)

        visible = {row["id"] for row in view["rows"]}
        target = next(row["id"] for row in projector.roster if row["id"] not in visible)
        identity = next(
            row["identity"] for row in raw["sessions"]
            if token(row["identity"])[0] == target
        )
        target_index = uuid.UUID(identity["nativeId"]).int - 1
        specs = [{} for _ in range(40)]
        specs[target_index] = {"kind": "system"}
        partial = sample("starship", 40, home=home, row_specs=specs)
        partial["sourceHealth"] = "partial"
        partial["sources"][0]["sourceHealth"] = "partial"
        partial["sources"][0]["coverage"]["runtime"].update(
            status="partial", reason="catalog_limit",
        )
        accept(state, partial)
        other, current = self.fleet({"starship": native(state, sequence=2)})
        negative = self.at(other, current)[0]
        self.assertIn(target, negative.excluded_ids)
        projector.project([negative])
        self.assertEqual(len(projector.roster), 39)
        self.assertNotIn(target, projector.previous)

    def test_namespace_scope_change_preserves_only_sibling_context(self):
        from working_set_fixture import native, new_state

        old_home = "/fixture/snap-codex-working-set"
        original = {
            "starship": new_state("starship", 3),
            "snap": new_state("snap", 3, home=old_home),
        }
        first, raw = self.fleet({host: native(state) for host, state in original.items()})
        projector = Projector()
        projector.project(self.at(first, raw))

        changed = {
            "starship": new_state("starship", 0),
            "snap": new_state("snap", 0, home="/fixture/snap-codex-new"),
        }
        second, current = self.fleet({host: native(state) for host, state in changed.items()})
        view = projector.project(self.at(second, current))
        self.assertEqual(len(projector.roster), 3)
        self.assertTrue(all(row["host"] == 1 and row["valid_ms"] == 0 for row in projector.roster))
        self.assertEqual(view["hosts"][0]["total"], 0)

    def test_gap_heartbeat_bad_clock_and_disconnect_revoke_authority(self):
        from working_set_fixture import control, native, new_state

        for fault in ("gap", "clock", "disconnect", "malformed"):
            with self.subTest(fault=fault):
                fleet, raw = self.fleet({"starship": native(new_state("starship", 3))})
                initial = self.at(fleet, raw)
                fleet.guard.accept(control(raw, "heartbeat", 2))
                self.assertEqual(initial, self.at(fleet, raw))
                if fault == "gap":
                    fleet.guard.accept(control(raw, "gap", 3))
                elif fault == "clock":
                    with self.assertRaises(ValueError), patch(
                        "mesh_plus.evidence.clock_domain", return_value={},
                    ):
                        fleet.sources()
                elif fault == "malformed":
                    broken = copy.deepcopy(raw)
                    broken["sessions"][0]["prompt"] = "forbidden"
                    broken["mesh"]["reader"].update(sequence=3, revision=2)
                    with self.assertRaises(Exception):
                        fleet.guard.accept(broken)
                else:
                    fleet.guard.disconnect()
                    fleet.closed = True
                self.assertTrue(all(
                    not source.rows and not source.complete_scopes
                    for source in self.at(fleet, raw)
                ))


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh working-set acceptance")
class WorkingSetReconnect(unittest.IsolatedAsyncioTestCase):
    async def test_retry_uses_new_request_guard_and_closes_owned_resources(self):
        from working_set_fixture import native, new_state, response

        fleet = Fleet(["starship", "snap"], Events(io.StringIO()))
        frames = {host: native(new_state(host, 3)) for host in ("starship", "snap")}
        guards, requests, closed, authorities = [], [], [], []
        second = asyncio.Event()

        async def configured(*_args, **kwargs):
            self.assertEqual(kwargs["source"], "agent_working_set")
            self.assertEqual(kwargs["scope"], "hosts")
            self.assertTrue(
                kwargs["socket"].endswith(
                    "mesh-plus-agent-working-set/read.sock"
                )
            )
            self.assertEqual(
                kwargs["profile"].descriptor.profile_id,
                "agent-observer.mesh-working-set.v1",
            )
            self.assertFalse(kwargs["report_routes"])
            guards.append(fleet.guard)
            number = len(guards)

            async def stream(request):
                self.assertEqual(
                    request,
                    {
                        "meshProtocol": 1,
                        "requestId": request["requestId"],
                        "operation": "watch",
                        "profile": "agent-observer.mesh-working-set.v1",
                        "access": "cached",
                        "selection": {
                            "mode": "hosts",
                            "hostIds": ["starship", "snap"],
                        },
                        "extensions": {},
                    },
                )
                requests.append(request["requestId"])
                frame = response(
                    frames,
                    profile=fleet.profile,
                    source=fleet.source,
                    request_id=request["requestId"],
                )
                try:
                    yield frame
                    if number == 2:
                        second.set()
                        await asyncio.Event().wait()
                finally:
                    closed.append(number)

            return types.SimpleNamespace(execute_admitted=stream)

        def authority():
            value = types.SimpleNamespace(closed=False)
            value.close = lambda: setattr(value, "closed", True)
            authorities.append(value)
            return value

        with patch("mesh_plus.api.configured_reader", configured), patch(
            "mesh_plus.library_authority.LibraryMeshAuthority", authority,
        ):
            task = asyncio.create_task(fleet.run())
            try:
                await asyncio.wait_for(second.wait(), 4)
                self.assertIsNot(guards[0], guards[1])
                self.assertNotEqual(requests[0], requests[1])
                self.assertTrue(any(source.rows for source in fleet.sources()))
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task

        self.assertEqual(closed, [1, 2])
        self.assertTrue(all(authority.closed for authority in authorities))


if __name__ == "__main__":
    unittest.main()
