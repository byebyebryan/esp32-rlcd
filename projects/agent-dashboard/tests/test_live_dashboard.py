import binascii
import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "host"))
from live_dashboard.projection import (
    Projector,
    Source,
    age_label,
    project_label,
    text_width,
    token,
    visual_key,
)
from live_dashboard.wire import encode, parse_request


def row(
    identifier,
    host="starship",
    state="working",
    at=1000,
    kind="user",
    runtime="running",
    label="project",
):
    return {
        "identity": {
            "hostScope": host,
            "provider": "codex",
            "namespace": "store",
            "nativeIdKind": "thread",
            "nativeId": identifier,
        },
        "runtime": {"health": "current", "value": runtime},
        "kind": kind,
        "phase": {"health": "current", "value": state},
        "activity": {"health": "current", "at": at},
        "cwd": "/code/" + label,
        "title": label,
        "workspace": None,
        "outcome": {"value": "failed"},
    }


def source(rows, host="starship", status="current", remaining=10000, sampled=10000):
    ids = {token(r["identity"])[0] for r in rows}
    excluded = {
        token(r["identity"])[0]
        for r in rows
        if r["kind"] in {"child", "system"} or r["runtime"]["value"] == "parked"
    }
    return Source(host, status, remaining, sampled, rows, ids, excluded)


def frame(rows=None, hosts=None, sequence=1, request=1, bridge="1" * 16, boot="0" * 16):
    if rows is None:
        rows = [
            {
                "id": "a" * 64,
                "host": 0,
                "category": "active",
                "state": "blocked",
                "health": 0,
                "valid_ms": 2900,
                "label": "project",
                "age": "5s",
            }
        ]
    if hosts is None:
        hosts = [
            {
                "alias": "ST",
                "status": 0,
                "valid_ms": 2900,
                "totals": [1, 0, 0, 0, 0],
                "total": 1,
            }
        ]
    return encode({"rows": rows, "hosts": hosts}, boot, request, bridge, sequence)


def alter(payload, field, replacement):
    fields = payload.rstrip(b"\n").split(b"\t")[:-1]
    fields[field] = replacement
    body = b"\t".join(fields)
    return body + f"\t{binascii.crc32(body):08x}\n".encode()


def capacity_case():
    return json.loads((APP / "tests/fixtures/capacity-case.json").read_text())


def capacity_sources(case):
    rows = case["normalizedFailedRows"] + case["normalizedHelpers"]
    return [
        source([r for r in rows if r["identity"]["hostScope"] == host], host=host,
               sampled=case["normalizedProvenance"]["sampledAt"])
        for host in ("starship", "snap")
    ]


class Projection(unittest.TestCase):
    def test_capacity_failures_and_title_helpers(self):
        view = Projector().project(capacity_sources(capacity_case()))
        self.assertEqual([r["state"] for r in view["rows"]], ["error"] * 3)
        self.assertEqual([h["total"] for h in view["hosts"]], [0, 3])
        self.assertEqual(view["hosts"][1]["totals"], [3, 0, 0, 0, 0])
        self.assertTrue(all(r["health"] == 0 and r["age"] == "30s" for r in view["rows"]))

    def test_failure_requires_current_specific_evidence(self):
        original = capacity_case()["normalizedFailedRows"][0]
        for field, value in (
            ("phase", {"health": "unsupported", "value": "unknown", "reason": "other"}),
            ("phase", {"health": "stale", "value": "unknown", "reason": "native_runtime_error"}),
            ("outcome", {"health": "stale", "value": "failed"}),
            ("outcome", {"health": "unsupported", "value": "failed"}),
            ("outcome", {"health": "current", "value": "unknown"}),
            ("outcome", {}),
        ):
            with self.subTest(field=field, value=value):
                view = Projector(["snap"]).project([source([{**original, field: value}], host="snap")])
                self.assertEqual(view["rows"][0]["state"], "unknown")
                self.assertEqual(view["rows"][0]["age"], "?")
        for runtime in ({"health": "stale", "value": "running"}, {"health": "current", "value": "parked"}):
            self.assertEqual(Projector(["snap"]).project([source([{**original, "runtime": runtime}], host="snap")])["rows"], [])

    def test_retry_and_current_phase_override_old_failure(self):
        case = capacity_case()
        p = Projector(["snap"])
        original = case["normalizedFailedRows"][0]
        sources = lambda rows: [source(rows, host="snap", sampled=case["normalizedProvenance"]["sampledAt"])]
        self.assertEqual(p.project(sources([original]))["rows"][0]["state"], "error")
        for state in ("working", "blocked", "waiting"):
            active = {**original, "phase": {"health": "current", "value": state}}
            self.assertEqual(p.project(sources([active]))["rows"][0]["state"], state)
        retry = case["normalizedRetry"]
        self.assertEqual(p.project(sources([retry]))["rows"][0]["state"], "working")
        self.assertEqual(p.project(sources([{**original, "latestTurn": retry["latestTurn"]}]))["rows"][0]["state"], "unknown")

    def test_failure_heartbeat_does_not_renew_age_or_validity(self):
        case = capacity_case()
        failed = case["normalizedFailedRows"][0]
        p = Projector(["snap"])
        views = [p.project([source([failed], host="snap", remaining=remaining,
                                  sampled=case["normalizedProvenance"]["sampledAt"])])
                 for remaining in (2100, 1100, 100)]
        self.assertEqual([v["rows"][0]["valid_ms"] for v in views], [2000, 1000, 0])
        self.assertEqual([v["rows"][0]["age"] for v in views], ["30s", "30s", "?"])
        self.assertEqual(views[-1]["rows"][0]["state"], "unknown")

    def test_failure_age_attention_capacity_and_reclassification(self):
        original = capacity_case()["normalizedFailedRows"][0]
        failed = {**original, "identity": {**original["identity"], "hostScope": "starship"},
                  "activity": {"health": "current", "at": 500}}
        rows = [row("blocked", state="blocked", at=1000), failed, row("waiting", state="waiting"), row("working")]
        view = Projector(["starship"]).project([source(rows)])
        self.assertEqual([r["state"] for r in view["rows"]], ["error", "blocked", "waiting", "working"])
        self.assertEqual(view["hosts"][0]["totals"], [2, 1, 1, 0, 0])
        for activity in ({"health": "stale", "at": 500}, {"health": "current", "at": 20000}):
            view = Projector(["starship"]).project([source([{**failed, "activity": activity}])])
            self.assertEqual((view["rows"][0]["state"], view["rows"][0]["age"]), ("error", "?"))
        p = Projector(["starship"])
        many = [{**failed, "identity": {**failed["identity"], "nativeId": str(i)}} for i in range(40)]
        view = p.project([source(many)])
        self.assertEqual((len(view["rows"]), view["hosts"][0]["totals"]), (32, [40, 0, 0, 0, 0]))
        view = p.project([source([{**many[-1], "kind": "system"}], status="partial")])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 39])
        self.assertNotIn(token(many[-1]["identity"])[0], p.previous)

    def test_urgency_oldest_activity_and_stable_ties(self):
        p = Projector(["starship"])
        rows = [
            row("young", at=4000),
            row("old", at=1000),
            row("wait", state="waiting"),
            row("block", state="blocked"),
        ]
        view = p.project([source(rows)])
        self.assertEqual(
            [r["state"] for r in view["rows"]],
            ["blocked", "waiting", "working", "working"],
        )
        self.assertEqual(view["rows"][2]["id"], token(rows[1]["identity"])[0])
        for r in rows:
            r["activity"]["at"] = 1000
        self.assertEqual(
            [r["id"] for r in p.project([source(list(reversed(rows)))])["rows"]],
            [r["id"] for r in view["rows"]],
        )

    def test_current_phase_not_outcome_and_source_sample_age(self):
        p = Projector(["starship"])
        original = row("x", state="waiting", at=5000)
        first = p.project([source([original], sampled=10000)])
        self.assertEqual(first["rows"][0]["state"], "waiting")
        self.assertEqual(first["rows"][0]["age"], "5s")
        self.assertEqual(
            p.project([source([original], sampled=10000, remaining=8000)])["rows"][0][
                "age"
            ],
            "5s",
        )
        self.assertEqual(
            p.project([source([original], sampled=15000)])["rows"][0]["age"], "10s"
        )
        original["activity"]["at"] = 16000
        self.assertEqual(p.project([source([original])])["rows"][0]["age"], "?")

    def test_saved_children_and_unknown_kind(self):
        rows = [
            row("child", kind="child"),
            row("helper", kind="system"),
            row("parked", runtime="parked"),
            row("unknown-runtime", runtime="unknown"),
            row("old-kind", kind="unknown"),
        ]
        other = row("reserved-provider")
        other["identity"]["provider"] = "claude"
        rows.append(other)
        view = Projector(["starship"]).project([source(rows)])
        self.assertEqual(len(view["rows"]), 1)
        self.assertEqual(view["rows"][0]["id"], token(rows[4]["identity"])[0])

    def test_title_priority_and_explicit_placeholder_fallbacks(self):
        value = row("id", label="chezmoi")
        value["title"] = " agents "
        self.assertEqual(project_label(value), "agents")
        for title in ("", "  ", None, "Codex id"):
            value["title"] = title
            self.assertEqual(project_label(value), "chezmoi")
        value["cwd"] = None
        self.assertTrue(project_label(value).startswith("Codex #"))
        value["workspace"] = {"health": "current", "repo": {"root": "/git/cubey"}}
        self.assertEqual(project_label(value), "cubey")
        value["title"] = "fluid-2.5d"
        self.assertEqual(project_label(value), "fluid-2.5d")

    def test_system_reclassification_removes_retained_context_and_counts(self):
        p = Projector(["starship"])
        helper, user = row("helper", kind="unknown"), row("user")
        self.assertEqual(p.project([source([helper, user])])["hosts"][0]["total"], 2)
        helper["kind"] = "system"
        # Even a partial inventory and caller with no prepared exclusions must purge it.
        confirmed = source([helper, user], status="partial")
        confirmed.excluded_ids.clear()
        view = p.project([confirmed])
        self.assertEqual(view["hosts"][0]["total"], 1)
        self.assertEqual(view["rows"][0]["id"], token(user["identity"])[0])
        lost = p.project([source([], status="offline", remaining=0)])
        self.assertEqual(lost["hosts"][0]["total"], 1)
        self.assertEqual(len(lost["rows"]), 1)

    def test_project_context_before_suffix_and_identity_survives_rename(self):
        p = Projector(["starship"])
        a, b = row("a", label="cubey"), row("b", label="chezmoi")
        a["title"] = b["title"] = "agents"
        first = p.project([source([a, b])])
        self.assertEqual(
            {r["label"] for r in first["rows"]}, {"agents (cubey)", "agents (chezmoi)"}
        )
        a["title"] = "fluid-2.5d"
        renamed = p.project([source([a, b])])
        self.assertEqual(
            {r["id"] for r in renamed["rows"]}, {r["id"] for r in first["rows"]}
        )
        self.assertEqual(
            {r["label"] for r in renamed["rows"]}, {"fluid-2.5d", "agents"}
        )
        b["cwd"] = a["cwd"]
        b["title"] = a["title"]
        duplicate = p.project([source([a, b])])
        self.assertTrue(all(" #" in r["label"] for r in duplicate["rows"]))
        self.assertTrue(all(text_width(r["label"]) <= 288 for r in duplicate["rows"]))

    def test_roster_explains_filters_identity_ages_and_hidden_capacity(self):
        p = Projector(["starship"])
        rows = [row(str(i), label="visible " + str(i)) for i in range(40)]
        rows += [row("helper", kind="system"), row("parked", runtime="parked")]
        inputs = [source(rows)]
        view = p.project(inputs)
        report = p.explain(inputs, view)
        self.assertEqual(report["selection_counts"]["selected"], 40)
        self.assertEqual(report["selection_counts"]["system"], 1)
        self.assertEqual(report["selection_counts"]["parked"], 1)
        self.assertEqual(sum(r["visible"] for r in report["rows"]), 11)
        self.assertEqual(sum(r["sent_to_device"] for r in report["rows"]), 32)
        self.assertTrue(all("identity" in r for r in report["rows"]))
        self.assertEqual(report["rows"][0]["display_id"], view["rows"][0]["id"])
        self.assertEqual(len(p.explain(inputs, view, include_all=True)["rows"]), 42)

    def test_failure_retains_context_and_positive_recovery_removes(self):
        p = Projector(["starship", "snap"])
        a, b = row("a"), row("b", host="snap")
        p.project([source([a]), source([b], host="snap")])
        lost = p.project(
            [source([], status="offline", remaining=0), source([b], host="snap")]
        )
        self.assertEqual(lost["hosts"][0]["totals"], [0, 0, 0, 0, 1])
        self.assertEqual(lost["hosts"][1]["totals"], [0, 0, 1, 0, 0])
        self.assertEqual(lost["rows"][1]["age"], "?")
        diagnostic = p.explain(
            [source([], status="offline", remaining=0), source([b], host="snap")],
            lost,
        )
        retained = next(
            r for r in diagnostic["rows"] if r["selection"] == "retained_uncertain"
        )
        self.assertEqual(retained["identity"], a["identity"])
        self.assertEqual(retained["display_age"], "?")
        a["runtime"]["value"] = "parked"
        self.assertEqual(
            len(p.project([source([a]), source([b], host="snap")])["rows"]), 1
        )

    def test_complete_membership_and_partial_absence(self):
        p = Projector(["starship"])
        p.project([source([row("a")])])
        self.assertEqual(len(p.project([source([], status="partial")])["rows"]), 1)
        self.assertEqual(len(p.project([source([])])["rows"]), 0)

    def test_capacity_counts_and_expiry_margin(self):
        p = Projector(["starship"])
        view = p.project([source([row(str(i)) for i in range(50)], remaining=1000)])
        self.assertEqual(len(view["rows"]), 32)
        self.assertEqual(view["hosts"][0]["total"], 50)
        self.assertEqual(view["hosts"][0]["valid_ms"], 900)
        self.assertTrue(all(r["valid_ms"] == 900 for r in view["rows"]))
        self.assertEqual(
            p.project([source([], status="offline", remaining=0)])["hosts"][0][
                "totals"
            ],
            [0, 0, 0, 0, 50],
        )

    def test_whole_roster_survives_partial_loss_and_positive_exclusion(self):
        p = Projector(["starship"])
        rows = [row(str(i), label="session " + str(i)) for i in range(40)]
        p.project([source(rows)])
        partial = p.project([source(rows[:5], status="partial")])
        self.assertEqual(partial["hosts"][0]["totals"], [0, 0, 5, 0, 35])
        lost = p.project([source([], status="offline", remaining=0)])
        self.assertEqual(lost["hosts"][0]["totals"], [0, 0, 0, 0, 40])
        self.assertEqual(len(p.explain([], lost)["rows"]), 40)
        self.assertEqual(
            sum(r["sent_to_device"] for r in p.explain([], lost)["rows"]), 32
        )
        for index, kind in ((37, "system"), (38, "child")):
            rows[index]["kind"] = kind
        rows[39]["runtime"]["value"] = "parked"
        excluded = p.project([source(rows[:5] + rows[37:], status="partial")])
        self.assertEqual(excluded["hosts"][0]["totals"], [0, 0, 5, 0, 32])
        again = p.project([source(rows[:5] + rows[37:], status="partial")])
        self.assertEqual(again["hosts"], excluded["hosts"])
        final = p.project([source(rows[:5])])
        self.assertEqual(final["hosts"][0]["total"], 5)

    def test_membership_growth_bound_and_unadmitted_exclusion(self):
        p = Projector(["starship", "snap"])
        a, b = row("a"), row("b", host="snap")
        p.project([source([a]), source([b], host="snap")])
        a["kind"] = "system"
        stale = p.project(
            [source([a], status="offline", remaining=0), source([b], host="snap")]
        )
        self.assertEqual(stale["hosts"][0]["total"], 1)
        self.assertEqual(stale["hosts"][1]["totals"], [0, 0, 1, 0, 0])
        fresh = row("new")
        growth = p.project(
            [source([fresh], status="partial"), source([b], host="snap")]
        )
        self.assertEqual(growth["hosts"][0]["totals"], [0, 0, 1, 0, 1])
        with (
            patch("live_dashboard.projection.MAX_ROSTER", 2),
            self.assertRaisesRegex(ValueError, "roster_capacity"),
        ):
            p.project([source([fresh, row("another")], status="partial")])

    def test_rendered_label_collisions_and_unicode_boundaries(self):
        labels = [
            "abcdefghijklmnopqrstuvwxAAA",
            "abcdefghijklmnopqrstuvwxBBB",
            "中" * 20 + "甲",
            "中" * 20 + "乙",
            "🐈",
            "🐕",
        ]
        view = Projector(["starship"]).project(
            [source([row(str(i), label=label) for i, label in enumerate(labels)])]
        )
        rendered = [visual_key(r["label"]) for r in view["rows"]]
        self.assertEqual(len(set(rendered)), len(rendered))
        self.assertTrue(all(len(r["label"].encode()) <= 63 for r in view["rows"]))
        self.assertEqual(age_label(100 * 86400000), "+++")

    def test_namespace_and_host_identity_and_request_bounds(self):
        a = row("same")
        b = row("same", host="snap")
        c = copy.deepcopy(a)
        c["identity"]["namespace"] = "other"
        self.assertEqual(len({token(r["identity"])[0] for r in (a, b, c)}), 3)
        self.assertEqual(
            parse_request(b"RLCD?4 " + b"0" * 16 + b" 1\r\n"), ("0" * 16, 1)
        )
        self.assertIsNone(parse_request(b"RLCD?2 " + b"0" * 16 + b" 1\n"))
        self.assertIsNone(parse_request(b"RLCD?3 " + b"0" * 16 + b" 1\n"))
        for number in (b"0", b"01", b"4294967296", b"-1"):
            self.assertIsNone(parse_request(b"RLCD?4 " + b"0" * 16 + b" " + number))

    def test_suffix_cannot_collide_with_an_existing_label(self):
        a, b = row("a"), row("b")
        prefix = token(a["identity"])[0][:5]
        c = row("c", label="project #" + prefix)
        view = Projector(["starship"]).project([source([a, b, c])])
        self.assertEqual(len({visual_key(r["label"]) for r in view["rows"]}), 3)


class NativeAdmission(unittest.TestCase):
    def setUp(self):
        self.process = subprocess.Popen(
            [os.environ["RLCD_FEED_TEST"]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def tearDown(self):
        self.process.stdin.close()
        self.assertEqual(self.process.wait(timeout=5), 0)
        self.process.stdout.close()

    def request(self, now):
        self.process.stdin.write(f"REQ {now}\n".encode())
        self.process.stdin.flush()
        return self.process.stdout.readline()

    def at(self, now):
        self.process.stdin.write(f"AT {now}\n".encode())
        self.process.stdin.flush()
        return json.loads(self.process.stdout.readline())

    def send(self, payload, accepted=True):
        self.process.stdin.write(payload)
        self.process.stdin.flush()
        self.assertEqual(
            self.process.stdout.readline(), b"ACCEPT 1\n" if accepted else b"ACCEPT 0\n"
        )
        return json.loads(self.process.stdout.readline())

    def test_expiry_during_silence_and_sampled_age(self):
        self.request(100)
        state = self.send(frame())
        self.assertTrue(state["flashing"])
        self.assertEqual(self.at(1000)["entries"][0]["age"], "5s")
        expired = self.at(3000)
        self.assertFalse(expired["flashing"])
        self.assertEqual(expired["health"], 2)
        self.assertEqual(expired["totals"], [0, 0, 0, 0, 1])
        self.assertEqual(expired["entries"][0]["age"], "?")

    def test_snap_work_badge_preserves_two_host_totals_and_expired_context(self):
        rows = [
            {"id": character * 64, "host": host, "badge": badge,
             "category": "active", "state": "working", "health": 0,
             "valid_ms": 2900, "label": "Plain title " + character, "age": "5s"}
            for character, host, badge in (("a", 0, "ST"), ("b", 1, "SN"), ("c", 1, "SW"))
        ]
        hosts = [{"alias": alias, "status": 0, "valid_ms": 2900,
                  "totals": [0, 0, count, 0, 0], "total": count}
                 for alias, count in (("ST", 1), ("SN", 2))]
        self.request(0)
        accepted = self.send(frame(rows, hosts))
        self.assertEqual([r["badge"] for r in accepted["entries"]], ["ST", "SN", "SW"])
        self.assertEqual(accepted["totals"], [0, 0, 3, 0, 0])
        expired = self.at(2900)
        self.assertEqual([r["badge"] for r in expired["entries"]], ["ST", "SN", "SW"])
        self.assertEqual(expired["totals"], [0, 0, 0, 0, 3])
        with self.assertRaisesRegex(ValueError, "device_row_badge"):
            frame([{**rows[0], "badge": "SW"}], [hosts[0]])

    def test_capacity_case_error_admission_retry_and_expiry(self):
        case = capacity_case()
        p = Projector()
        self.assertIn(b"RLCD?4 ", self.request(0))
        view = p.project(capacity_sources(case))
        failed = self.send(encode(view, "0" * 16, 1, "1" * 16, 1))
        self.assertEqual(failed["totals"], [3, 0, 0, 0, 0])
        self.assertEqual([r["work"] for r in failed["entries"]], [4, 4, 4])
        self.assertTrue(failed["flashing"])
        case["normalizedFailedRows"][0] = case["normalizedRetry"]
        self.request(100)
        retry = self.send(encode(p.project(capacity_sources(case)), "0" * 16, 2, "1" * 16, 2))
        self.assertEqual(retry["totals"], [2, 0, 1, 0, 0])
        self.assertEqual(retry["entries"][-1]["work"], 0)
        expired = self.at(3100)
        self.assertEqual(expired["totals"], [0, 0, 0, 0, 3])
        self.assertFalse(expired["flashing"])
        self.assertTrue(all(r["work"] == 5 and r["age"] == "?" for r in expired["entries"]))

    def test_error_frame_version_counts_health_and_partial_host_expiry(self):
        case = capacity_case()
        failed = case["normalizedFailedRows"][0]
        view = Projector().project([
            source([row("healthy", state="working")], remaining=3000),
            source([failed], host="snap", remaining=1100, sampled=case["normalizedProvenance"]["sampledAt"]),
        ])
        self.request(0)
        payload = encode(view, "0" * 16, 1, "1" * 16, 1)
        for bad in (
            alter(payload, 0, b"RLCD!2"),
            alter(payload, 18, b"3001"),
            alter(payload, 17, b"2"),
            alter(payload, 30, b"5"),
            payload[:-10] + b"\t00000000\n",
        ):
            self.send(bad, False)
        state = self.send(payload)
        self.assertEqual(state["totals"], [1, 0, 1, 0, 0])
        expired = self.at(1000)
        self.assertTrue(expired["partial"])
        self.assertEqual(expired["totals"], [0, 0, 1, 0, 1])
        self.assertFalse(expired["flashing"])
        self.assertEqual([r["work"] for r in expired["entries"]], [0, 5])

    def test_request_anchor_shortens_delayed_response(self):
        payload = alter(alter(frame(), 9, b"1000"), 22, b"1000")
        self.request(100)
        self.at(900)
        self.send(payload)
        self.assertEqual(self.at(1099)["health"], 0)
        self.assertEqual(self.at(1100)["health"], 2)

    def test_response_already_expired_on_arrival_never_flashes(self):
        payload = alter(alter(frame(), 9, b"100"), 22, b"100")
        self.request(0)
        self.at(900)
        state = self.send(payload)
        self.assertEqual(state["health"], 2)
        self.assertFalse(state["flashing"])
        self.assertEqual(state["totals"], [0, 0, 0, 0, 1])

    def test_duplicate_old_nonce_delayed_and_sequence_rejection(self):
        self.request(0)
        good = self.send(frame())
        self.assertEqual(self.send(frame(), False), good)
        self.request(10)
        self.send(frame(request=2), False)
        self.send(frame(sequence=2, request=2, boot="f" * 16), False)
        self.at(1010)
        self.send(frame(sequence=2, request=2), False)
        self.request(1010)
        self.send(frame(sequence=1, request=3, bridge="2" * 16))

    def test_partial_host_expiry_preserves_sibling(self):
        rows = [
            {
                "id": c * 64,
                "host": i,
                "category": "active",
                "state": state,
                "health": 0,
                "valid_ms": ttl,
                "label": "project",
                "age": "5s",
            }
            for c, i, state, ttl in (
                ("a", 0, "blocked", 1000),
                ("b", 1, "working", 2900),
            )
        ]
        hosts = [
            {
                "alias": "ST",
                "status": 0,
                "valid_ms": 1000,
                "totals": [1, 0, 0, 0, 0],
                "total": 1,
            },
            {
                "alias": "SN",
                "status": 0,
                "valid_ms": 2900,
                "totals": [0, 0, 1, 0, 0],
                "total": 1,
            },
        ]
        self.request(0)
        self.send(frame(rows, hosts))
        state = self.at(1000)
        self.assertEqual(state["health"], 0)
        self.assertTrue(state["partial"])
        self.assertEqual(state["totals"], [0, 0, 1, 0, 1])
        self.assertFalse(state["flashing"])
        self.assertEqual(state["entries"][0]["id"], "b" * 64)

    def test_parked_and_unproved_recent_rows_do_not_enter_device_list(self):
        parked, unknown = row("parked", runtime="parked"), row("unknown", runtime="unknown")
        rows = [parked, unknown]
        ids = {token(r["identity"])[0] for r in rows}
        categories = {token(parked["identity"])[0]: "recent",
                      token(unknown["identity"])[0]: "recent"}
        source = Source("starship", "current", 5000, 10000, rows, ids, set(),
                        {("codex", "store")}, {identifier: 5000 for identifier in ids},
                        {identifier: 10000 for identifier in ids}, categories, True)
        view = Projector(["starship"]).project([source])
        self.assertEqual(view["hosts"][0]["totals"], [0, 0, 0, 0, 0])
        self.request(0)
        state = self.send(encode(view, "0" * 16, 1, "1" * 16, 1))
        self.assertEqual(state["totals"], [0, 0, 0, 0, 0])
        self.assertFalse(state["flashing"])
        self.assertEqual(state["entries"], [])

    def test_unloading_removes_device_rows_even_with_terminal_recent_history(self):
        rows = []
        for status in ("completed", "failed"):
            item = row(status, runtime="parked")
            item["phase"] = None
            item["outcome"] = {"health": "current", "value": status}
            item["latestTurn"] = {"health": "current", "value": {"status": status}}
            rows.append(item)
        ids = {token(r["identity"])[0] for r in rows}
        src = Source("starship", "current", 3000, 10000, rows, ids, set(),
                     {("codex", "store")}, {identifier: 3000 for identifier in ids},
                     {identifier: 10000 for identifier in ids},
                     {identifier: "recent" for identifier in ids}, True)
        p = Projector(["starship"])
        for item in rows:
            item["runtime"]["value"] = "running"
        self.request(0)
        initial = self.send(encode(p.project([src]), "0" * 16, 1, "1" * 16, 1))
        self.assertEqual(len(initial["entries"]), 2)
        for item in rows:
            item["runtime"]["value"] = "parked"
        self.request(100)
        state = self.send(encode(p.project([src]), "0" * 16, 2, "1" * 16, 2))
        self.assertEqual(state["totals"], [0, 0, 0, 0, 0])
        self.assertEqual(state["entries"], [])
        self.assertFalse(state["flashing"])

    def test_row_positive_lease_survives_expired_whole_roster_totals(self):
        rows = [{"id": "a" * 64, "host": 0, "category": "active",
                 "state": "blocked", "health": 0, "valid_ms": 900,
                 "label": "project", "age": "5s"}]
        hosts = [{"alias": "ST", "status": 1, "valid_ms": 1,
                  "totals": [1, 0, 0, 0, 0], "total": 1}]
        self.request(0)
        self.send(frame(rows, hosts))
        still_leased = self.at(100)
        self.assertEqual(still_leased["health"], 0)
        self.assertTrue(still_leased["partial"])
        self.assertEqual(still_leased["totals"], [0, 0, 0, 0, 1])
        self.assertEqual(still_leased["entries"][0]["category"], 0)
        self.assertEqual(still_leased["entries"][0]["work"], 1)
        self.assertTrue(still_leased["flashing"])
        expired = self.at(900)
        self.assertEqual(expired["health"], 2)
        self.assertEqual(expired["entries"][0]["category"], 2)
        self.assertEqual(expired["totals"], [0, 0, 0, 0, 1])
        self.assertFalse(expired["flashing"])

    def test_atomic_malformed_bounds_checksum_and_utf8(self):
        self.request(0)
        good = self.send(frame())
        self.request(10)
        base = frame(request=2, sequence=2)
        cases = [
            base[:-10] + b"\t00000000\n",
            alter(base, 5, b"3"),
            alter(base, 6, b"33"),
            alter(base, 9, b"3001"),
            alter(base, 17, b"3"),
            alter(base, 18, b"5357"),  # SW may label only Snap, not Starship.
            alter(base, 18, b"53574b"),
            alter(base, 19, b"3"),
            alter(base, 22, b"3001"),
            alter(base, 23, b"c0af"),
            alter(base, 23, b"ed a080"),
            alter(base, 23, b"41" * 64),
            alter(base, 24, b"1\x00"),
            alter(base, 14, b"4294967296"),
            base.replace(b"RLCD!4", b"OTHER1"),
            alter(base, 0, b"RLCD!3"),
        ]
        for payload in cases:
            with self.subTest(payload=payload[:20]):
                self.assertEqual(self.send(payload, False), good)
        self.send(base)

    def test_full_roster_counts_and_frame_capacity(self):
        projected = Projector(["starship"]).project(
            [source([row(str(i), state="blocked") for i in range(50)])]
        )
        self.request(0)
        state = self.send(encode(projected, "0" * 16, 1, "1" * 16, 1))
        self.assertEqual(state["rows"], 32)
        self.assertEqual(state["visible"], 11)
        self.assertEqual(state["total"], 50)
        self.assertEqual(state["totals"], [50, 0, 0, 0, 0])

    def test_partial_roster_beyond_capacity_reaches_device_as_uncertainty(self):
        p = Projector(["starship"])
        rows = [row(str(i), label="session " + str(i)) for i in range(40)]
        self.request(0)
        self.send(encode(p.project([source(rows)]), "0" * 16, 1, "1" * 16, 1))
        self.request(100)
        state = self.send(
            encode(
                p.project([source(rows[:5], status="partial")]),
                "0" * 16,
                2,
                "1" * 16,
                2,
            )
        )
        self.assertEqual(state["total"], 40)
        self.assertEqual(state["rows"], 32)
        self.assertEqual(state["totals"], [0, 0, 5, 0, 35])
        self.assertTrue(state["partial"])
        expired = self.at(3100)
        self.assertEqual(expired["totals"], [0, 0, 0, 0, 40])

    def test_warming_bridge_retains_device_context_until_positive_empty(self):
        self.request(0)
        self.send(frame())
        self.request(100)
        offline = [
            {
                "alias": "ST",
                "status": 3,
                "valid_ms": 0,
                "totals": [0, 0, 0, 0, 0],
                "total": 0,
            }
        ]
        state = self.send(frame([], offline, request=2, bridge="2" * 16))
        self.assertEqual(state["rows"], 1)
        self.assertEqual(state["totals"], [0, 0, 0, 0, 1])
        self.assertFalse(state["flashing"])
        self.request(200)
        ready = [
            {
                "alias": "ST",
                "status": 0,
                "valid_ms": 2900,
                "totals": [0, 0, 0, 0, 0],
                "total": 0,
            }
        ]
        state = self.send(frame([], ready, request=3, sequence=2, bridge="2" * 16))
        self.assertEqual(state["rows"], 0)
        self.assertEqual(state["health"], 0)

    def test_retained_context_cannot_duplicate_an_incoming_identity(self):
        self.request(0)
        before = self.send(frame())
        self.request(100)
        hosts = [
            {
                "alias": "ST",
                "status": 2,
                "valid_ms": 0,
                "totals": [0, 0, 0, 0, 0],
                "total": 0,
            },
            {
                "alias": "SN",
                "status": 0,
                "valid_ms": 2900,
                "totals": [0, 0, 1, 0, 0],
                "total": 1,
            },
        ]
        rows = [
            {
                "id": "a" * 64,
                "host": 1,
                "category": "active",
                "state": "working",
                "health": 0,
                "valid_ms": 2900,
                "label": "other",
                "age": "5s",
            }
        ]
        self.assertEqual(
            self.send(frame(rows, hosts, sequence=2, request=2), False), before
        )
        self.assertEqual(self.at(3000)["health"], 2)


if __name__ == "__main__":
    unittest.main()
