"""Installed optional read-contract parity; run with the accepted SDK Python."""

import asyncio
import copy
import io
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet, _runtime_sample_at
from live_dashboard.projection import Projector, selection_reason

AVAILABLE = importlib.util.find_spec("mesh_plus") is not None


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh acceptance")
class PreparedFleet(unittest.TestCase):
    def fleet(self, frame, *, full_roster=True):
        from mesh_fixture import REQUEST
        from agent_observer.mesh_read import PreparedAgentWatch
        fleet = Fleet(["starship", "snap"], full_roster=full_roster)
        fleet.request_id = REQUEST
        fleet.guard = PreparedAgentWatch(REQUEST, host_ids=fleet.hosts, profile=fleet.profile)
        fleet.guard.accept(frame)
        self.addCleanup(fleet.guard.disconnect)
        return fleet

    def legacy(self, frame, now):
        from mesh_plus.api import ReadGuard, reconstructed
        from agent_observer.public import identity_key
        from live_dashboard.projection import Source, token, exclusion
        from mesh_fixture import REQUEST
        from agent_observer.mesh_profile import AgentProfile
        profile = AgentProfile()
        guard = ReadGuard("agent", REQUEST, profile=profile)
        try:
            baseline = copy.deepcopy(frame)
            baseline["mesh"]["reader"].update(sequence=1, revision=1)
            guard.accept(baseline)
            current = {identity_key(r["identity"]) for r in guard.current(now, frame["mesh"]["reader"]["clock"])}
            result = []
            for host in guard.view["mesh"]["hosts"]:
                remaining = min((r["expiresAtMs"] - now for r in host["receipts"]
                                 if r["health"] in {"current", "partial"}), default=0)
                status = "current"
                if host["delivery"]["status"] != "ready" or host["viewState"] != "current" or remaining <= 0:
                    status = "offline"
                snapshot = reconstructed(frame, host, profile=profile)["snapshot"] if host["owner"] else None
                rows = [] if snapshot is None else [r for r in snapshot["sessions"] if identity_key(r["identity"]) in current]
                if snapshot and status == "current" and (snapshot["sourceHealth"] != "current" or
                        any(s["coverage"]["runtime"]["status"] != "complete" for s in snapshot["sources"])):
                    status = "partial"
                sampled_by_id = {
                    token(row["identity"])[0]: _runtime_sample_at(row)
                    for row in rows
                }
                result.append(Source(
                    host["hostId"], status, max(0, remaining),
                    None if snapshot is None else snapshot["collectedAt"], rows,
                    {token(row["identity"])[0] for row in rows},
                    {token(row["identity"])[0] for row in rows if exclusion(row)},
                    sampled_by_id=sampled_by_id,
                ))
            return result
        finally:
            guard.disconnect()

    def at(self, fleet, frame, now):
        with patch("mesh_plus.transport.boottime_ms", return_value=now), patch(
                "mesh_plus.evidence.clock_domain", return_value=frame["mesh"]["reader"]["clock"]):
            return fleet.sources()

    def test_complete_partial_missing_host_and_expiry_match_legacy(self):
        from mesh_fixture import response
        for kwargs in ({"rows": 40}, {"partial": True}, {"unavailable": "snap"}):
            frame = response(**kwargs)
            fleet = self.fleet(frame)
            boundaries = [frame["mesh"]["reader"]["encodedAtMs"]]
            boundaries += sorted({r["expiresAtMs"] for h in frame["mesh"]["hosts"] for r in h["receipts"]})
            for now in boundaries:
                with self.subTest(input=kwargs, now=now):
                    current, reference = self.at(fleet, frame, now), self.legacy(frame, now)
                    self.assertEqual(current, reference)
                    self.assertEqual(Projector(fleet.hosts).project(current), Projector(fleet.hosts).project(reference))

    def test_mutation_heartbeat_gap_and_resync_preserve_authority(self):
        from mesh_fixture import response, control
        frame = response()
        fleet = self.fleet(frame)
        now = frame["mesh"]["reader"]["encodedAtMs"]
        first = self.at(fleet, frame, now)
        first[0].rows.clear()
        self.assertTrue(self.at(fleet, frame, now)[0].rows)
        fleet.guard.accept(control(frame, "heartbeat", 2))
        self.assertEqual(self.at(fleet, frame, now), self.legacy(frame, now))
        fleet.guard.accept(control(frame, "gap", 3))
        self.assertTrue(all(not s.rows for s in self.at(fleet, frame, now)))
        resync = copy.deepcopy(frame)
        resync["mesh"]["kind"] = "resync"
        resync["mesh"]["reader"].update(sequence=4, revision=2)
        fleet.guard.accept(resync)
        self.assertEqual(self.at(fleet, frame, now), self.legacy(frame, now))

    def test_failed_admission_clock_and_disconnect_revoke_rows(self):
        from mesh_fixture import response
        from jsonschema import ValidationError
        for fault in ("shape", "clock", "disconnect"):
            frame = response()
            fleet = self.fleet(frame)
            now = frame["mesh"]["reader"]["encodedAtMs"]
            if fault == "shape":
                bad = copy.deepcopy(frame)
                bad["sessions"][0]["prompt"] = "forbidden"
                with self.assertRaises((ValueError, ValidationError)):
                    fleet.guard.accept(bad)
            elif fault == "clock":
                with patch("mesh_plus.evidence.clock_domain", return_value={}):
                    with self.assertRaises(ValueError):
                        fleet.sources()
            else:
                fleet.guard.disconnect()
                fleet.closed = True
            self.assertTrue(all(not s.rows for s in self.at(fleet, frame, now)))

    def test_changed_whole_roster_and_independent_component_expiry_match_legacy(self):
        from mesh_fixture import native, response
        from live_dashboard.projection import token
        def changed(host, rows, **kwargs):
            value = native(host, rows, **kwargs)
            roster = value["snapshot"]["sessions"]
            first = copy.deepcopy(roster[0])
            for index, row in enumerate(roster):
                identity, native_ids = row["identity"], row["nativeIds"]
                row.clear()
                row.update(copy.deepcopy(first), identity=identity, nativeIds=native_ids,
                           title="Roster " + str(index))
            if stage and host == "snap":
                roster[39]["kind"] = "system"
                roster[38].update(inventory="saved", phase=None, blockedReasons=[])
                roster[38]["runtime"]["value"] = "parked"
                roster[36]["runtime"]["value"] = "unknown"
                roster[35]["runtime"].update(value="unknown", health="unavailable")
                for index in (35, 36):
                    roster[index]["phase"]["value"] = "unknown"
                    roster[index]["blockedReasons"] = []
                roster.pop(37)  # Partial omission retains membership until complete.
            if stage == 3 and host == "snap":
                for component in value["sources"][0]["components"]:
                    if component["name"] == "history":
                        component["expiresBoottimeMs"] -= 15000
            return value

        actual, reference = Projector(["starship", "snap"]), Projector(["starship", "snap"])
        fleet = None
        reader_id = None
        for stage in range(4):
            with patch("mesh_fixture.native", changed):
                frame = response(rows=40, partial=stage == 1)
            frame["mesh"]["reader"].update(sequence=stage + 1, revision=stage + 1)
            reader_id = reader_id or frame["mesh"]["reader"]["id"]
            frame["mesh"]["reader"]["id"] = reader_id
            if fleet is None:
                fleet = self.fleet(frame)
                removed = token(next(r["identity"] for r in frame["sessions"]
                                     if r["identity"]["hostScope"] == "snap"
                                     and r["title"] == "Roster 39"))[0]
            else:
                fleet.guard.accept(frame)
            now = frame["mesh"]["reader"]["encodedAtMs"]
            boundaries = [now]
            if stage == 3:
                boundaries += sorted({r["expiresAtMs"] for h in frame["mesh"]["hosts"]
                                      for r in h["receipts"]})
            for now in boundaries:
                current, old = self.at(fleet, frame, now), self.legacy(frame, now)
                self.assertEqual(current, old)
                view = actual.project(current)
                self.assertEqual(view, reference.project(old))
                if stage == 1:
                    self.assertIn(removed, current[1].excluded_ids)
                    self.assertEqual(view["hosts"][1]["total"], 38)
                    retained = {r["id"]: r for r in actual.roster if r["host"] == 1}
                    for row in frame["sessions"]:
                        if (row["identity"]["hostScope"] == "snap"
                                and row["title"] in {"Roster 35", "Roster 36"}):
                            prior = retained[token(row["identity"])[0]]
                            self.assertEqual(prior["state"], "unknown")
                            self.assertEqual(prior["valid_ms"], 0)

    def test_owned_replacement_matches_strict_projection_and_full_membership(self):
        from mesh_fixture import REQUEST, response
        from agent_observer.mesh_read import PreparedAgentWatch
        fleet = Fleet(["starship", "snap"], full_roster=True)
        fleet.request_id = REQUEST
        fleet.guard = PreparedAgentWatch(REQUEST, host_ids=fleet.hosts, profile=fleet.profile)
        self.addCleanup(fleet.guard.disconnect)
        admitted = response(rows=40, profile=fleet.profile, admitted=True)
        fleet.guard.accept(admitted)
        raw = admitted.snapshot()
        now = raw["mesh"]["reader"]["encodedAtMs"]
        current, reference = self.at(fleet, raw, now), self.legacy(raw, now)
        self.assertEqual(current, reference)
        self.assertEqual(sum(len(s.admitted_ids) for s in current), 80)
        self.assertEqual(sum(len(s.rows) for s in current), 80)
        self.assertTrue(any(r["kind"] == "unknown" for s in current for r in s.rows))
        self.assertEqual(Projector(fleet.hosts).project(current),
                         Projector(fleet.hosts).project(reference))
        raw["sessions"].clear()
        self.assertEqual(len(fleet.guard.snapshot()["sessions"]), 80)

    def test_roster_diagnostic_retains_excluded_rows_and_reasons(self):
        from mesh_fixture import response
        frame = response(rows=40)
        fleet = self.fleet(frame, full_roster=True)
        now = frame["mesh"]["reader"]["encodedAtMs"]
        current = self.at(fleet, frame, now)
        self.assertEqual(current, self.legacy(frame, now))
        projector = Projector(fleet.hosts)
        diagnostic = projector.explain(current, projector.project(current), include_all=True)
        self.assertEqual(len(diagnostic["rows"]), 80)
        for reason in ("selected", "child", "system", "parked"):
            self.assertGreater(diagnostic["selection_counts"][reason], 0)


@unittest.skipUnless(AVAILABLE, "optional installed Observer/Mesh acceptance")
class PreparedReconnect(unittest.IsolatedAsyncioTestCase):
    async def test_retry_uses_a_new_guard_and_closes_both_owned_streams(self):
        from mesh_fixture import response
        from live_dashboard.runtime import Events
        import types
        fleet = Fleet(["starship", "snap"], Events(io.StringIO()), full_roster=True)
        guards, closed = [], []
        second = asyncio.Event()
        async def configured(*a, **kw):
            guards.append(fleet.guard)
            number = len(guards)
            async def stream(request):
                frame = response()
                frame["mesh"]["requestId"] = request["requestId"]
                try:
                    yield frame
                    if number == 2:
                        second.set()
                        await asyncio.Event().wait()
                finally:
                    closed.append(number)
            return types.SimpleNamespace(execute_admitted=stream)
        with patch("mesh_plus.api.configured_reader", configured):
            task = asyncio.create_task(fleet.run())
            try:
                await asyncio.wait_for(second.wait(), 4)
                self.assertEqual(len(guards), 2)
                self.assertIsNot(guards[0], guards[1])
                self.assertTrue(any(s.rows for s in fleet.sources()))
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
        self.assertEqual(closed, [1, 2])
        self.assertTrue(fleet.closed)


if __name__ == "__main__":
    unittest.main()
