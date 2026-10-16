"""Installed active-feed lifecycle and whole-roster presentation acceptance."""

import asyncio
import copy
import importlib.util
import io
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector, token
from live_dashboard.runtime import Events

AVAILABLE = importlib.util.find_spec("mesh_plus") is not None


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh acceptance")
class ActiveFleet(unittest.TestCase):
    def fleet(self, frames, *, admitted=False):
        from active_fixture import REQUEST, response
        fleet = Fleet(list(frames))
        fleet.request_id = REQUEST
        fleet.guard = fleet.new_guard()
        frame = response(frames, profile=fleet.profile, admitted=admitted)
        fleet.guard.accept(frame)
        self.addCleanup(fleet.guard.disconnect)
        raw = frame.snapshot() if admitted else frame
        return fleet, raw

    def at(self, fleet, frame, now=None):
        now = frame["mesh"]["reader"]["encodedAtMs"] if now is None else now
        with patch("mesh_plus.transport.boottime_ms", return_value=now), patch(
                "mesh_plus.evidence.clock_domain", return_value=frame["mesh"]["reader"]["clock"]):
            return fleet.sources()

    def test_nominal_owned_selected_bodies_and_full_diagnostics(self):
        from active_fixture import active
        from mesh_fixture import response
        frames = {h: active(h, 100) for h in ("starship", "snap")}
        fleet, raw = self.fleet(frames, admitted=True)
        sources = self.at(fleet, raw)
        self.assertEqual(sum(len(s.rows) for s in sources), 6)
        self.assertTrue(all(s.complete_scopes for s in sources))
        full = Fleet(list(frames), full_roster=True)
        full.request_id = "a" * 32
        full.guard = full.new_guard()
        self.addCleanup(full.guard.disconnect)
        legacy = response(rows=100, profile=full.profile, admitted=True)
        full.guard.accept(legacy)
        full_sources = self.at(full, legacy.snapshot())
        self.assertEqual(sum(len(s.rows) for s in full_sources), 200)
        self.assertEqual(Projector().project(sources), Projector().project(full_sources))
        sources[0].rows.clear()
        self.assertEqual(len(self.at(fleet, raw)[0].rows), 3)
        self.assertEqual(len(fleet.guard.snapshot()["sessions"]), 6)

    def test_complete_empty_then_its_independent_expiry(self):
        from active_fixture import active
        positive = active("starship")
        fleet, raw = self.fleet({"starship": positive})
        projector = Projector(["starship"])
        self.assertEqual(projector.project(self.at(fleet, raw))["hosts"][0]["total"], 3)
        empty = copy.deepcopy(positive)
        scope = empty["projection"]["scopes"][0]
        empty["projection"]["sessions"].clear()
        scope["members"].clear()
        # Completeness uses runtime only while history stays current longer.
        scope["coverage"]["supports"] = [scope["coverage"]["supports"][0]]
        empty["sources"][0]["components"][1]["expiresBoottimeMs"] += 10000
        other, frame = self.fleet({"starship": empty})
        deadline = frame["mesh"]["hosts"][0]["receipts"][0]["expiresAtMs"]
        before = self.at(other, frame, deadline - 1000)
        self.assertEqual(projector.project(before)["hosts"][0]["total"], 0)
        # An already proved retirement stays retired. A missed expired empty
        # generation cannot retire an independently retained prior context.
        projector.project(self.at(fleet, raw))
        expired = self.at(other, frame, deadline)
        self.assertEqual(expired[0].status, "partial")
        self.assertFalse(expired[0].complete_scopes)
        view = projector.project(expired)
        self.assertEqual(view["hosts"][0]["total"], 3)
        self.assertTrue(all(r["valid_ms"] == 0 for r in projector.roster))

    def test_partial_missed_negative_never_retires_context(self):
        from active_fixture import active
        positive = active("starship")
        fleet, raw = self.fleet({"starship": positive})
        projector = Projector(["starship"])
        projector.project(self.at(fleet, raw))
        partial = copy.deepcopy(positive)
        partial["projection"]["sessions"].clear()
        scope = partial["projection"]["scopes"][0]
        scope["members"].clear()
        scope["coverage"].update(status="partial", reason="missed_negative", supports=[])
        other, frame = self.fleet({"starship": partial})
        projector.project(self.at(other, frame))
        self.assertEqual(len(projector.roster), 3)
        deadline = max(r["expiresAtMs"] for r in frame["mesh"]["hosts"][0]["receipts"])
        projector.project(self.at(other, frame, deadline + 1000))
        self.assertEqual(len(projector.roster), 3)
        self.assertTrue(all(r["state"] == "unknown" for r in projector.roster))

    def test_original_activity_anchor_and_independent_field_expiry(self):
        from active_fixture import active
        value = active("starship")
        scope = value["projection"]["scopes"][0]
        history = next(r for r in scope["coverage"]["supports"] if r["component"] == "history")
        runtime = next(r for r in scope["coverage"]["supports"] if r["component"] == "runtime")
        history["expiresBoottimeMs"] -= 15000
        value["sources"][0]["components"][1]["expiresBoottimeMs"] -= 15000
        for row, entry in zip(value["projection"]["sessions"], scope["members"], strict=True):
            row["activity"].update(at=row["runtime"]["observedAt"] - 30000,
                                   source="codex_rpc", health="current", reason="fixture_activity")
            entry["fieldSupports"]["activity"] = copy.deepcopy(history)
        fleet, raw = self.fleet({"starship": value})
        projector = Projector(["starship"])
        initial = projector.project(self.at(fleet, raw))
        self.assertTrue(all(r["age"] == "30s" for r in initial["rows"]))
        # Neither a cached read nor a changed service emission is an age anchor.
        later = raw["mesh"]["reader"]["encodedAtMs"] + 1000
        self.assertTrue(all(r["age"] == "30s" for r in projector.project(self.at(fleet, raw, later))["rows"]))
        deadline = raw["mesh"]["hosts"][0]["receipts"][1]["expiresAtMs"]
        expired = self.at(fleet, raw, deadline)
        self.assertEqual(len(expired[0].rows), 3)
        view = projector.project(expired)
        self.assertTrue(all(r["age"] == "?" and r["valid_ms"] > 0 for r in view["rows"]))
        self.assertFalse(expired[0].complete_scopes)
        self.assertLess(deadline, runtime["expiresBoottimeMs"])

    def test_new_same_key_receipt_cannot_renew_old_membership_support(self):
        from active_fixture import active
        value = active("starship")
        fleet, raw = self.fleet({"starship": value})
        broken = copy.deepcopy(raw)
        host = broken["mesh"]["hosts"][0]
        component = host["owner"]["service"]["sources"][0]["components"][0]
        component["accepted"] += 1
        component["attempts"] += 1
        host["receipts"][0]["accepted"] += 1
        # A same-key replacement cannot smuggle an old member/coverage support
        # into a newly accepted receipt. Failed admission revokes the helper.
        with self.assertRaises(ValueError):
            fleet.guard.accept(broken)
        source = self.at(fleet, raw)[0]
        self.assertFalse(source.rows)
        self.assertFalse(source.complete_scopes)
        self.assertFalse(source.excluded_ids)

    def test_exact_nonmember_reconciles_beyond_display_limit(self):
        from active_fixture import active
        from mesh_fixture import native
        frame = active("starship", 40)
        # All 40 rows are selected for this capacity fixture.
        rows = native("starship", 40)["snapshot"]["sessions"]
        template = copy.deepcopy(frame["projection"]["sessions"][0])
        scope = frame["projection"]["scopes"][0]
        fields = scope["members"][0]["fieldSupports"]
        for row in rows:
            identity, native_ids = row["identity"], row["nativeIds"]
            row.clear()
            row.update(copy.deepcopy(template), identity=identity, nativeIds=native_ids)
        frame["projection"]["sessions"] = rows
        scope["members"] = [{"identity": r["identity"], "fieldSupports": copy.deepcopy(fields)} for r in rows]
        fleet, raw = self.fleet({"starship": frame})
        projector = Projector(["starship"])
        self.assertEqual(len(projector.project(self.at(fleet, raw))["rows"]), 32)
        self.assertEqual(len(projector.roster), 40)
        identifier = projector.roster[-1]["id"]
        removed = next(r for r in rows if token(r["identity"])[0] == identifier)
        negative = copy.deepcopy(frame)
        scope = negative["projection"]["scopes"][0]
        negative["projection"]["sessions"] = [r for r in rows if r is not removed]
        scope["members"] = [m for m in scope["members"] if m["identity"] != removed["identity"]]
        support = fields["runtime"]
        scope["coverage"].update(status="partial", supports=[], reason="fixture_partial")
        scope["nonmembers"] = [{"identity": removed["identity"], "reason": "parked", "value": "parked",
                                 "supports": [support], "horizonBoottimeMs": support["expiresBoottimeMs"]}]
        other, current = self.fleet({"starship": negative})
        projector.project(self.at(other, current))
        self.assertEqual(len(projector.roster), 39)
        self.assertNotIn(identifier, projector.previous)

    def test_namespace_switch_scope_failure_and_other_host_do_not_clear_context(self):
        from active_fixture import active
        original = {h: active(h) for h in ("starship", "snap")}
        fleet, raw = self.fleet(original)
        projector = Projector()
        projector.project(self.at(fleet, raw))
        changed = copy.deepcopy(original)
        snap = changed["snap"]
        old_namespace = snap["sources"][0]["namespace"]
        from agent_observer.public import store_namespace
        import os
        snap["sources"][0]["configHome"] = "/fixture/codex-new"
        new_namespace = store_namespace("codex", "/fixture/codex-new", "explicit", os.getuid())
        def rewrite(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "namespace" and item == old_namespace:
                        value[key] = new_namespace
                    else:
                        rewrite(item)
            elif isinstance(value, list):
                for item in value:
                    rewrite(item)
        rewrite(snap)
        snap["projection"]["sessions"].clear()
        snap["projection"]["scopes"][0]["members"].clear()
        # Healthy ST complete-empty may retire ST only.
        changed["starship"]["projection"]["sessions"].clear()
        changed["starship"]["projection"]["scopes"][0]["members"].clear()
        other, current = self.fleet(changed)
        projector.project(self.at(other, current))
        self.assertEqual(len(projector.roster), 3)
        self.assertTrue(all(r["host"] == 1 and r["valid_ms"] == 0 for r in projector.roster))

    def test_gap_heartbeat_bad_clock_and_disconnect_revoke_authority(self):
        from active_fixture import active
        from mesh_fixture import control
        for fault in ("gap", "clock", "disconnect", "malformed"):
            fleet, raw = self.fleet({"starship": active("starship")})
            initial = self.at(fleet, raw)
            fleet.guard.accept(control(raw, "heartbeat", 2))
            self.assertEqual(initial, self.at(fleet, raw))
            if fault == "gap":
                fleet.guard.accept(control(raw, "gap", 3))
            elif fault == "clock":
                with self.assertRaises(ValueError), patch("mesh_plus.evidence.clock_domain", return_value={}):
                    fleet.sources()
            elif fault == "malformed":
                broken = copy.deepcopy(raw)
                broken["sessions"][0]["prompt"] = "forbidden"
                with self.assertRaises(Exception):
                    fleet.guard.accept(broken)
            else:
                fleet.guard.disconnect()
                fleet.closed = True
            self.assertTrue(all(not s.rows and not s.complete_scopes for s in self.at(fleet, raw)))


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh acceptance")
class ActiveReconnect(unittest.IsolatedAsyncioTestCase):
    async def test_new_guard_separate_source_profile_and_owned_authority_cleanup(self):
        from active_fixture import response
        fleet = Fleet(["starship", "snap"], Events(io.StringIO()))
        guards, closed, authorities = [], [], []
        second = asyncio.Event()
        async def configured(*a, **kw):
            self.assertEqual(kw["source"], "agent_active")
            self.assertEqual(kw["profile"].descriptor.profile_id, "agent-observer.mesh-active.v1")
            self.assertFalse(kw["report_routes"])
            guards.append(fleet.guard)
            number = len(guards)
            async def stream(request):
                value = response(profile=fleet.profile)
                value["mesh"]["requestId"] = request["requestId"]
                try:
                    yield value
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
                "mesh_plus.library_authority.LibraryMeshAuthority", authority):
            task = asyncio.create_task(fleet.run())
            try:
                await asyncio.wait_for(second.wait(), 4)
                self.assertIsNot(guards[0], guards[1])
                self.assertTrue(any(s.rows for s in fleet.sources()))
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
        self.assertEqual(closed, [1, 2])
        self.assertTrue(all(a.closed for a in authorities))


if __name__ == "__main__":
    unittest.main()
