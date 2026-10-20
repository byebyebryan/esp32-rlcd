"""Focused working-set facade adapter and active/recent projection checks."""

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.projection import Projector, Source, token

INSTALLED = (
    importlib.util.find_spec("agent_observer") is not None
    and importlib.util.find_spec("agent_observer.mesh_working_set_profile") is not None
)

FIELDS = {
    "activity", "kind", "lastUpdated", "latestTurn", "outcome", "phase",
    "runtime", "savedIdentity", "workspace",
}
MISSING = object()


def session(identifier, *, host="starship", runtime="running", phase="working", at=9000):
    return {
        "identity": {
            "hostScope": host,
            "provider": "codex",
            "namespace": "store",
            "nativeIdKind": "thread",
            "nativeId": identifier,
        },
        "kind": "user",
        "runtime": {"health": "current", "value": runtime, "observedAt": 10000,
                    "clock": "sample"},
        "phase": {"health": "current", "value": phase},
        "activity": {"health": "current", "at": at},
        "outcome": {"health": "unsupported", "value": None},
        "latestTurn": {"health": "unsupported", "value": None},
        "workspace": {"health": "unavailable", "repo": None},
        "title": "Cached label",
        "cwd": "/cached/path",
    }


def member_lease(row, *, active=None, recent=None, membership=15000,
                 runtime=15000, phase=15000, activity=15000):
    fields = {name: None for name in FIELDS}
    fields.update(runtime=runtime, phase=phase, activity=activity, kind=membership)
    return {
        "identity": dict(row["identity"]),
        "activeExpiresAtMs": active,
        "recentExpiresAtMs": recent,
        "membershipExpiresAtMs": membership,
        "fieldExpiresAtMs": fields,
    }


def public_read(rows, leases, *, status="complete", coverage_expires=15000,
                uncertain=(), nonmembers=()):
    scopes = []
    for host in ("starship", "snap"):
        coverage = {"status": status}
        if status == "complete" and coverage_expires is not MISSING:
            coverage["expiresAtMs"] = coverage_expires
        scopes.append({
            "hostScope": host,
            "provider": "codex",
            "namespace": "store",
            "coverage": coverage,
        })
    return SimpleNamespace(
        context={"hosts": []}, sessions=list(rows), scopes=scopes,
        member_leases=list(leases), uncertain=list(uncertain), nonmembers=list(nonmembers),
    )


def adapter(read, now=10000, hosts=("starship", "snap")):
    fleet = Fleet.__new__(Fleet)
    fleet.hosts = list(hosts)
    by_host = {host: [] for host in hosts}
    for row in read.sessions:
        by_host[row["identity"]["hostScope"]].append(row)
    return fleet.working_set_sources(read, now, by_host)


class InstalledProfile(unittest.TestCase):
    @unittest.skipUnless(INSTALLED, "optional installed Observer/Mesh working-set API")
    def test_default_and_full_roster_are_explicit_distinct_contracts(self):
        from agent_observer.mesh_profile import AgentProfile
        from agent_observer.mesh_read import PreparedAgentWatch
        from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
        from agent_observer.mesh_working_set_read import PreparedWorkingSetAgentWatch

        default = Fleet(["starship", "snap"])
        self.assertEqual(default.source, "agent_working_set")
        self.assertIsInstance(default.profile, WorkingSetAgentProfile)
        self.assertIsInstance(default.guard, PreparedWorkingSetAgentWatch)
        default.guard.disconnect()

        full = Fleet(["starship", "snap"], full_roster=True)
        self.assertEqual(full.source, "agent")
        self.assertIsInstance(full.profile, AgentProfile)
        self.assertIsInstance(full.guard, PreparedAgentWatch)
        full.guard.disconnect()


class WorkingSetAdapter(unittest.TestCase):
    def test_unloaded_terminal_results_are_excluded_from_loaded_view(self):
        row = session("completed", runtime="parked", phase="unknown")
        row["phase"] = None
        row["outcome"] = {"health": "current", "value": "completed"}
        row["latestTurn"] = {"health": "current", "value": {"status": "completed"}}
        lease = member_lease(row, recent=14000, phase=None)
        lease["fieldExpiresAtMs"].update(outcome=12000, latestTurn=13000)
        source, = adapter(public_read([row], [lease]), hosts=("starship",))
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["rows"], [])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 0])

        row["outcome"]["value"] = "failed"
        row["latestTurn"]["value"]["status"] = "failed"
        source, = adapter(public_read([row], [lease]), hosts=("starship",))
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["rows"], [])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 0])

    def test_parked_runtime_overrides_prior_phase_and_turn_result(self):
        for outcome_health, turn_health, outcome, status in (
            ("current", "current", "completed", "completed"),
            ("current", "current", "failed", "failed"),
            ("stale", "current", "completed", "completed"),
            ("current", "stale", "completed", "completed"),
            ("current", "current", "completed", "in_progress"),
            ("current", "current", "completed", "failed"),
            ("current", "current", "cancelled", "interrupted"),
        ):
            with self.subTest(case=(outcome_health, turn_health, outcome, status)):
                row = session("terminal", runtime="parked", phase="waiting")
                row["outcome"] = {"health": outcome_health, "value": outcome}
                row["latestTurn"] = {"health": turn_health, "value": {"status": status}}
                source = Source("starship", "current", 5000, rows=[row],
                                row_categories={token(row["identity"])[0]: "recent"},
                                working_set=True)
                view = Projector(["starship"]).project([source])
                self.assertEqual(view["rows"], [])
                self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 0])

    def test_unloading_removes_exact_session_despite_positive_recent_membership(self):
        row = session("transition", phase="waiting")
        row["outcome"] = {"health": "current", "value": "completed"}
        row["latestTurn"] = {"health": "current", "value": {"status": "completed"}}
        lease = member_lease(row, active=14000, recent=14000)
        lease["fieldExpiresAtMs"].update(outcome=15000, latestTurn=15000)
        projector = Projector(["starship"])

        source, = adapter(public_read([row], [lease]), hosts=("starship",))
        view = projector.project([source])
        self.assertEqual(view["rows"][0]["state"], "waiting")
        self.assertEqual(view["hosts"][0]["totals"], [0, 1, 0, 0, 0])
        row["runtime"]["value"] = "parked"
        lease["activeExpiresAtMs"] = None
        source, = adapter(public_read([row], [lease]), hosts=("starship",))
        view = projector.project([source])
        self.assertEqual(view["rows"], [])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 0])

        row["runtime"]["value"] = "unknown"
        source, = adapter(public_read([row], [lease]), hosts=("starship",))
        view = projector.project([source])
        self.assertEqual(view["rows"], [])

    def test_exact_member_lease_uses_independent_branch_and_field_deadlines(self):
        old_active = session("old-active", phase="blocked", at=1000)
        recent_parked = session("parked", runtime="parked", phase="unknown", at=7000)
        recent_unknown = session("unknown", runtime="unknown", phase="unknown", at=8000)
        old_active["title"] = "Retained title"
        rows = [old_active, recent_parked, recent_unknown]
        leases = [
            member_lease(old_active, active=14000, recent=None, membership=14000,
                         activity=12000),
            member_lease(recent_parked, recent=13500, membership=13500),
            member_lease(recent_unknown, recent=14500, membership=14500),
        ]
        source, = adapter(public_read(rows, leases), hosts=("starship",))
        self.assertEqual(source.row_categories, {
            token(row["identity"])[0]: category
            for row, category in zip(rows, ("active", "recent", "recent"), strict=True)
        })
        # Activity expires first for the active row; row TTL is independently
        # capped by its current activity proof and the shared margin.
        active_id = token(old_active["identity"])[0]
        self.assertEqual(source.row_remaining_ms[active_id], 2000)
        self.assertEqual(source.sampled_by_id[active_id], 10000)

        view = Projector(["starship"]).project([source])
        self.assertEqual(view["hosts"][0]["totals"], [1, 0, 0, 0, 0])
        by_id = {r["id"]: r for r in view["rows"]}
        self.assertNotIn(token(recent_parked["identity"])[0], by_id)
        self.assertNotIn(token(recent_unknown["identity"])[0], by_id)
        self.assertEqual(by_id[active_id]["state"], "blocked")

    def test_expired_or_missing_display_field_deadlines_fail_closed(self):
        row = session("lease")
        dead_field = member_lease(row, active=14000, activity=10000)
        source, = adapter(public_read([row], [dead_field]), hosts=("starship",))
        self.assertEqual(source.rows, [])

        missing_field = member_lease(row, active=14000)
        missing_field["fieldExpiresAtMs"]["phase"] = None
        source, = adapter(public_read([row], [missing_field]), hosts=("starship",))
        self.assertEqual(source.rows, [])

    def test_branch_expiry_can_leave_the_other_positive_branch(self):
        row = session("branch")
        # The public helper removes the expired active branch and leaves only
        # the still-live recent branch at this receiving-clock sample.
        source, = adapter(public_read([row], [member_lease(
            row, active=None, recent=14000, membership=14000,
        )]), hosts=("starship",))
        identifier = token(row["identity"])[0]
        self.assertEqual(source.row_categories[identifier], "recent")

    def test_selected_branch_deadline_bounds_row_and_host_category_claims(self):
        both = session("both-branches")
        recent_only = session("recent-only", runtime="parked", phase="unknown")
        leases = [
            member_lease(both, active=11000, recent=14500, membership=14500),
            member_lease(recent_only, recent=11000, membership=15000),
        ]
        source, = adapter(public_read([both, recent_only], leases), hosts=("starship",))
        active_id = token(both["identity"])[0]
        recent_id = token(recent_only["identity"])[0]
        self.assertEqual(source.row_remaining_ms[active_id], 1000)
        self.assertEqual(source.row_remaining_ms[recent_id], 1000)
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["hosts"][0]["valid_ms"], 900)
        self.assertTrue(all(row["valid_ms"] == 900 for row in view["rows"]))

    def test_host_totals_lease_includes_members_beyond_usb_capacity(self):
        rows = [session(f"member-{index}") for index in range(40)]
        leases = [member_lease(row, active=15000, membership=15000)
                  for row in rows]
        leases[-1]["activeExpiresAtMs"] = 10500
        read = public_read(rows, leases)
        source, = adapter(read, hosts=("starship",))
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 40, 0, 0])
        self.assertEqual(len(view["rows"]), 32)
        self.assertEqual(view["hosts"][0]["valid_ms"], 400)

    def test_complete_empty_scope_expiring_inside_margin_is_partial_on_wire(self):
        source, = adapter(public_read([], [], coverage_expires=10090),
                          now=10000, hosts=("starship",))
        self.assertEqual(source.status, "current")
        self.assertEqual(source.remaining_ms, 90)
        self.assertEqual(source.complete_scopes, {("codex", "store")})
        host, = Projector(["starship"]).project([source])["hosts"]
        self.assertEqual(host["status"], 1)
        self.assertEqual(host["valid_ms"], 1)
        self.assertEqual(host["total"], 0)

    def test_complete_scope_lease_is_required_for_negative_coverage(self):
        for expires in (MISSING, None, True, "15000", 10000):
            with self.subTest(expires=expires):
                source, = adapter(public_read([], [], coverage_expires=expires),
                                  now=10000, hosts=("starship",))
                self.assertEqual(source.status, "partial")
                self.assertEqual(source.complete_scopes, set())

    def test_scope_expiry_bounds_host_totals_but_not_member_row_lease(self):
        row = session("scope-short")
        lease = member_lease(row, active=15000, membership=15000)
        source, = adapter(public_read([row], [lease], coverage_expires=10500),
                          now=10000, hosts=("starship",))
        self.assertEqual(source.remaining_ms, 500)
        self.assertEqual(source.row_remaining_ms[token(row["identity"])[0]], 5000)
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["hosts"][0]["valid_ms"], 400)
        self.assertEqual(view["rows"][0]["valid_ms"], 3000)

    def test_context_waits_for_complete_census_or_positive_exclusion(self):
        prior = session("prior")
        identity = prior["identity"]
        p = Projector(["starship"])
        initial = Source("starship", "current", 5000, 10000, [prior],
                         {token(identity)[0]}, set(), {("codex", "store")},
                         {token(identity)[0]: 5000}, {token(identity)[0]: 10000},
                         {token(identity)[0]: "active"}, True)
        self.assertEqual(p.project([initial])["hosts"][0]["total"], 1)

        uncertain = Source("starship", "partial", 5000, None, [], set(), set(), set(),
                           working_set=True)
        retained = p.project([uncertain])
        self.assertEqual(retained["hosts"][0]["totals"], [0, 0, 0, 0, 1])
        self.assertEqual(retained["rows"][0]["category"], "uncertain")
        self.assertEqual(retained["rows"][0]["valid_ms"], 0)

        excluded = Source("starship", "partial", 5000, None, [],
                          {token(identity)[0]}, {token(identity)[0]}, set(),
                          working_set=True)
        self.assertEqual(p.project([excluded])["hosts"][0]["total"], 0)

        p.project([initial])
        complete_empty = Source("starship", "current", 5000, None, [], set(), set(),
                                {("codex", "store")}, working_set=True)
        self.assertEqual(p.project([complete_empty])["hosts"][0]["total"], 0)


class WorkingSetPriority(unittest.TestCase):
    def test_recent_history_never_fills_loaded_device_capacity(self):
        active = [session("active-blocked", phase="blocked", at=1000),
                  session("active-working", at=2000)]
        recent = [session(f"recent-{i}", runtime="parked", phase="unknown", at=3000 + i)
                  for i in range(40)]
        rows = active + recent
        categories = {token(r["identity"])[0]:
                      ("active" if r in active else "recent") for r in rows}
        ids = {token(r["identity"])[0] for r in rows}
        source = Source("starship", "current", 5000, 10000, rows, ids, set(),
                        {("codex", "store")}, {i: 5000 for i in ids},
                        {i: 10000 for i in ids}, categories, True)
        p = Projector(["starship"])
        view = p.project([source])
        self.assertEqual(view["hosts"][0]["totals"], [1, 0, 1, 0, 0])
        self.assertEqual(len(view["rows"]), 2)
        self.assertEqual([r["id"] for r in view["rows"]],
                         [token(r["identity"])[0] for r in active])
        self.assertTrue(all(r["category"] == "active" for r in view["rows"]))
        report = p.explain([source], view)
        self.assertEqual(sum(r["sent_to_device"] for r in report["rows"]), 2)
        self.assertEqual(sum(r["visible"] for r in report["rows"]), 2)


if __name__ == "__main__":
    unittest.main()
