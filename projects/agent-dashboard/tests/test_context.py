"""Restart context is uncertain metadata and must be durable before USB output."""

import asyncio
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "host"))
sys.path.insert(0, str(APP / "tests"))

from live_dashboard import context as context_module
from live_dashboard.context import ContextPolicyError, ContextStore, route_binding
from live_dashboard.profiles import ProfileProjector, combine_sources
from live_dashboard.projection import Projector, token
from live_dashboard.runtime import Events, Failure
from live_dashboard.serial import serve_serial
from live_dashboard.wire import encode
from test_home_profiles import route, row as profile_row, source as profile_source
from test_live_dashboard import row as native_row, source as native_source

DEVICE = "/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:DE:D0:04-if00"


def profile_binding(routes=None):
    routes = routes or [route(), route("work")]
    return route_binding(DEVICE, ["snap"], [vars(item) for item in routes])


def profile_pair(default=None, work=None, *, default_status="current", work_status="current"):
    return combine_sources(["snap"], [
        (route(), profile_source(default, status=default_status)),
        (route("work"), profile_source(work, namespace="work", status=work_status)),
    ])


def no_positive_claims(value):
    forbidden = {
        "activeExpiresAtMs", "age", "category", "health", "lease",
        "membershipExpiresAtMs", "outcome", "phase", "recentExpiresAtMs",
        "state", "status", "valid_ms", "validity",
    }
    if isinstance(value, dict):
        return not (forbidden & value.keys()) and all(no_positive_claims(item) for item in value.values())
    if isinstance(value, list):
        return all(no_positive_claims(item) for item in value)
    return True


class NativeFeed:
    def __init__(self, path):
        self.process = subprocess.Popen(
            [str(path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def send(self, view, sequence, now):
        self.process.stdin.write(f"REQ {now}\n".encode())
        self.process.stdin.flush()
        request = self.process.stdout.readline()
        if not request.startswith(b"REQUEST RLCD?6 "):
            raise AssertionError(request)
        self.process.stdin.write(encode(view, "0" * 16, sequence, "1" * 16, sequence))
        self.process.stdin.flush()
        accepted = self.process.stdout.readline()
        if accepted != b"ACCEPT 1\n":
            raise AssertionError(accepted)
        return json.loads(self.process.stdout.readline())

    def request(self, now):
        self.process.stdin.write(f"REQ {now}\n".encode())
        self.process.stdin.flush()
        request = self.process.stdout.readline()
        if not request.startswith(b"REQUEST RLCD?6 "):
            raise AssertionError(request)
        return request.removeprefix(b"REQUEST ")

    def accept_at(self, response, now):
        self.process.stdin.write(f"AT {now}\n".encode())
        self.process.stdin.flush()
        self.process.stdout.readline()  # State before the delayed response arrives.
        self.process.stdin.write(response)
        self.process.stdin.flush()
        accepted = self.process.stdout.readline()
        if accepted != b"ACCEPT 1\n":
            raise AssertionError(accepted)
        return json.loads(self.process.stdout.readline())

    def close(self):
        self.process.stdin.close()
        if self.process.wait(timeout=5) != 0:
            raise AssertionError("native feed exited unsuccessfully")
        self.process.stdout.close()


class RestartContext(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.path = self.directory / "context.json"
        self.binding = profile_binding()

    def open_store(self, *, binding=None):
        store = ContextStore(self.path, binding or self.binding, ["snap"])
        restored = store.open()
        self.addCleanup(store.close)
        return store, restored

    @staticmethod
    def save(store, projector):
        initialized, rows = projector.context_state()
        return store.save(initialized, rows)

    def test_restart_partial_and_complete_empty_default_survive_native_feed(self):
        feed_path = Path(os.environ.get("RLCD_FEED_TEST", APP / "build/native-live/feed"))
        if not feed_path.is_file():
            self.skipTest("native C feed helper has not been built")
        default = profile_row(identifier="same-native-id")
        work = profile_row(namespace="work", identifier="same-native-id")
        both = profile_pair(default, work)
        board = NativeFeed(feed_path)
        self.addCleanup(board.close)

        first_store, restored = self.open_store()
        first = ProfileProjector(["snap"])
        first.restore_context(restored.rows, restored.initialized_hosts)
        initial_view = first.project(both)
        self.save(first_store, first)
        initial = board.send(initial_view, 1, 0)
        self.assertEqual(initial["rows"], 2)
        self.assertEqual(
            {entry["badge"] for entry in initial["entries"]}, {"SN", "SW"}
        )
        initial_store_bytes = self.path.read_bytes()
        document = json.loads(initial_store_bytes)
        self.assertTrue(no_positive_claims(document))
        self.assertEqual(len(document["body"]["rows"]), 2)
        self.assertTrue(all(set(row) == {
            "identity", "host", "order", "label", "project", "badge"
        } for row in document["body"]["rows"]))

        first_store.close()
        second_store, restored = self.open_store()
        restarted = ProfileProjector(["snap"])
        restarted.restore_context(restored.rows, restored.initialized_hosts)
        partial_view = restarted.project(profile_pair(
            default, None, default_status="current", work_status="offline"
        ))
        self.save(second_store, restarted)
        partial = board.send(partial_view, 2, 100)
        default_id = token(default["identity"])[0]
        work_id = token(work["identity"])[0]
        self.assertEqual(partial["rows"], 2)
        self.assertTrue(partial["partial"])
        self.assertEqual(partial["totals"], [0, 0, 1, 0, 1])
        by_id = {entry["id"]: entry for entry in partial["entries"]}
        self.assertEqual(by_id[default_id]["work"], 0)
        self.assertEqual(by_id[default_id]["category"], 0)
        self.assertEqual(
            (by_id[work_id]["badge"], by_id[work_id]["category"],
             by_id[work_id]["work"], by_id[work_id]["age"]),
            ("SW", 2, 5, "?"),
        )

        empty_default_view = restarted.project(profile_pair(
            None, None, default_status="current", work_status="offline"
        ))
        self.save(second_store, restarted)
        empty_default = board.send(empty_default_view, 3, 200)
        self.assertEqual(empty_default["rows"], 1)
        self.assertEqual([entry["id"] for entry in empty_default["entries"]], [work_id])
        self.assertEqual(empty_default["entries"][0]["badge"], "SW")
        self.assertEqual(empty_default["totals"], [0, 0, 0, 0, 1])

    def test_exact_exclusion_retires_only_its_namespace_and_unloaded_rows_stay_gone(self):
        default = profile_row(identifier="same-native-id")
        work = profile_row(namespace="work", identifier="same-native-id")
        store, restored = self.open_store()
        projector = ProfileProjector(["snap"])
        projector.restore_context(restored.rows, restored.initialized_hosts)
        projector.project(profile_pair(default, work))
        self.save(store, projector)

        parked = dict(default)
        parked["runtime"] = {"health": "current", "value": "parked"}
        excluded = profile_source(parked, status="partial")
        lost = combine_sources(["snap"], [
            (route(), excluded),
            (route("work"), profile_source(status="offline", namespace="work")),
        ])
        view = projector.project(lost)
        self.save(store, projector)
        work_id = token(work["identity"])[0]
        self.assertEqual([row["id"] for row in view["rows"]], [work_id])
        self.assertEqual(view["rows"][0]["badge"], "SW")

        no_rows = combine_sources(["snap"], [
            (route(), profile_source(status="offline")),
            (route("work"), profile_source(status="offline", namespace="work")),
        ])
        after_loss = projector.project(no_rows)
        self.assertEqual([row["id"] for row in after_loss["rows"]], [work_id])

    def test_cold_invalid_or_changed_binding_fences_then_recovers(self):
        default = profile_row(identifier="default-row")
        work = profile_row(namespace="work", identifier="work-row")
        partial = profile_pair(default, None, default_status="current", work_status="offline")

        for mode in ("missing", "corrupt", "binding"):
            with self.subTest(mode=mode):
                path = self.directory / (mode + ".json")
                binding = self.binding
                if mode == "corrupt":
                    path.write_bytes(b"{not json")
                    path.chmod(0o600)
                elif mode == "binding":
                    original = ContextStore(path, self.binding, ["snap"])
                    restored = original.open()
                    original_projector = ProfileProjector(["snap"])
                    original_projector.restore_context(
                        restored.rows, restored.initialized_hosts
                    )
                    original_projector.project(profile_pair(default, work))
                    self.save(original, original_projector)
                    original.close()
                    changed_route = route("work")
                    changed_route = type(changed_route)(
                        changed_route.host, changed_route.profile, changed_route.label,
                        changed_route.codex_home, changed_route.source,
                        changed_route.socket + ".changed",
                    )
                    binding = profile_binding([route(), changed_route])

                store = ContextStore(path, binding, ["snap"])
                restored = store.open()
                projector = ProfileProjector(["snap"])
                projector.restore_context(restored.rows, restored.initialized_hosts)
                cold = projector.project(partial)
                self.assertEqual(cold["hosts"][0]["status"], 3)
                self.assertEqual(cold["rows"], [])

                recovered = projector.project(profile_pair(default, work))
                self.assertEqual(recovered["hosts"][0]["status"], 0)
                self.assertEqual({row["id"] for row in recovered["rows"]}, {
                    token(default["identity"])[0], token(work["identity"])[0]
                })
                self.save(store, projector)
                store.close()

    def test_each_physical_host_initializes_independently_across_restart(self):
        path = self.directory / "fleet.json"
        hosts = ["starship", "snap"]
        binding = route_binding(DEVICE, hosts, [
            {"host": "starship", "profile": "working_set", "source": "agent_working_set",
             "socket": "/run/starship.sock", "codex_home": None, "label": "Default"},
            {"host": "snap", "profile": "working_set", "source": "agent_working_set",
             "socket": "/run/snap.sock", "codex_home": None, "label": "Default"},
        ])
        store = ContextStore(path, binding, hosts)
        restored = store.open()
        star = native_row("star", host="starship")
        snap = native_row("snap")
        projector = Projector(hosts)
        projector.restore_context(restored.rows, restored.initialized_hosts)
        initial = projector.project([
            native_source([star], host="starship"),
            native_source([snap], host="snap", status="partial"),
        ])
        self.assertEqual([host["status"] for host in initial["hosts"]], [0, 3])
        self.assertEqual(projector.initialized_hosts, {"starship"})
        self.save(store, projector)
        store.close()

        restarted_store = ContextStore(path, binding, hosts)
        restored = restarted_store.open()
        restarted = Projector(hosts)
        restarted.restore_context(restored.rows, restored.initialized_hosts)
        next_view = restarted.project([
            native_source([star], host="starship", status="partial"),
            native_source([snap], host="snap", status="partial"),
        ])
        self.assertEqual([host["status"] for host in next_view["hosts"]], [1, 3])
        self.assertEqual([row["id"] for row in next_view["rows"]], [token(star["identity"])[0]])
        self.assertEqual(restarted.initialized_hosts, {"starship"})
        restarted_store.close()

    def test_full_roster_is_saved_and_unchanged_state_does_not_fsync(self):
        binding = route_binding(DEVICE, ["starship"], [{
            "host": "starship", "profile": "working_set", "label": "Default",
            "codex_home": None, "source": "agent_working_set",
            "socket": "/run/starship.sock",
        }])
        store = ContextStore(self.path, binding, ["starship"])
        restored = store.open()
        self.addCleanup(store.close)
        projector = Projector(["starship"])
        projector.restore_context(restored.rows, restored.initialized_hosts)
        rows = [native_row(str(index), host="starship", label="session " + str(index))
                for index in range(40)]
        from test_live_dashboard import source as standard_source
        view = projector.project([standard_source(rows, host="starship")])
        self.assertEqual(len(view["rows"]), 32)
        initialized, saved_rows = projector.context_state()
        self.assertEqual(len(saved_rows), 40)
        self.assertTrue(store.save(initialized, saved_rows))
        before = self.path.read_bytes()
        with patch("live_dashboard.context.os.fsync") as fsync:
            self.assertFalse(store.save(initialized, saved_rows))
            fsync.assert_not_called()
        self.assertEqual(self.path.read_bytes(), before)

    def test_lock_policy_atomic_refusal_and_private_file(self):
        store, _ = self.open_store()
        competing = ContextStore(self.path, self.binding, ["snap"])
        with self.assertRaisesRegex(ContextPolicyError, "context_lock_busy"):
            competing.open()

        default = profile_row(identifier="row")
        work = profile_row(namespace="work", identifier="work-row")
        projector = ProfileProjector(["snap"])
        projector.restore_context((), ())
        projector.project(profile_pair(default, work))
        initialized, rows = projector.context_state()
        store.save(initialized, rows)
        original = self.path.read_bytes()
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertTrue(self.path.is_file())
        self.assertFalse(self.path.is_symlink())

        changed = [dict(row) for row in rows]
        changed[0]["label"] += " changed"
        with patch("live_dashboard.context.os.replace", side_effect=OSError("refused")):
            with self.assertRaisesRegex(OSError, "refused"):
                store.save(initialized, changed)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

        store.close()
        reopened = ContextStore(self.path, self.binding, ["snap"])
        reopened.open()
        reopened.close()

    def test_policy_rejects_symlink_broad_mode_and_nonregular_state(self):
        cases = ("symlink", "mode", "directory")
        for case in cases:
            with self.subTest(case=case):
                path = self.directory / (case + ".json")
                if case == "symlink":
                    target = self.directory / "target"
                    target.write_text("{}"); target.chmod(0o600)
                    path.symlink_to(target)
                elif case == "mode":
                    path.write_text("{}"); path.chmod(0o644)
                else:
                    path.mkdir(mode=0o700)
                store = ContextStore(path, self.binding, ["snap"])
                with self.assertRaises(ContextPolicyError):
                    store.open()

    def test_oversized_or_bad_checksum_cache_is_cold_and_bounded(self):
        path = self.directory / "oversized.json"
        path.write_bytes(b"x" * 33)
        path.chmod(0o600)
        with patch.object(context_module, "MAX_STATE_BYTES", 32):
            store = ContextStore(path, self.binding, ["snap"])
            restored = store.open()
            self.assertEqual(restored.rows, ())
            self.assertEqual(restored.initialized_hosts, frozenset())
            store.close()

        path = self.directory / "checksum.json"
        path.write_text(json.dumps({"body": {}, "sha256": "0" * 64}))
        path.chmod(0o600)
        store = ContextStore(path, self.binding, ["snap"])
        restored = store.open()
        self.assertEqual(restored.rows, ())
        store.close()

        path = self.directory / "deep.json"
        path.write_bytes(b'{"body":' + b"[" * 1200 + b"0" + b"]" * 1200 + b'}')
        path.chmod(0o600)
        store = ContextStore(path, self.binding, ["snap"])
        restored = store.open()
        self.assertEqual(restored.rows, ())
        self.assertEqual(restored.initialized_hosts, frozenset())
        store.close()

    def test_state_size_ceiling_refuses_before_replacing_file(self):
        store, restored = self.open_store()
        projector = ProfileProjector(["snap"])
        projector.restore_context(restored.rows, restored.initialized_hosts)
        row = profile_row(identifier="large")
        projector.project(profile_pair(row, None, work_status="offline"))
        initialized, rows = projector.context_state()
        with patch.object(context_module, "MAX_STATE_BYTES", 64):
            with self.assertRaisesRegex(ValueError, "context_state_capacity"):
                store.save(initialized, rows)
        self.assertFalse(self.path.exists())


class SerialDurability(unittest.IsolatedAsyncioTestCase):
    async def test_failed_context_save_emits_no_usb_response(self):
        class Port:
            def __init__(self):
                self.read_once = False
                self.writes = []
                self.closed = False

            def read(self):
                if self.read_once:
                    return b""
                self.read_once = True
                return b"RLCD?6 " + b"0" * 16 + b" 1\n"

            def write(self, data):
                self.writes.append(data)
                return len(data)

            def close(self):
                self.closed = True

        class Fleet:
            hosts = ["snap"]

            def sources(self):
                return [native_source([native_row("row")], host="snap")]

        class FailingStore:
            def save(self, *_args):
                raise OSError("disk full")

        port = Port()
        projector = Projector(["snap"])
        with self.assertRaisesRegex(Failure, "context_save_failed"):
            await serve_serial(
                "/unused", Fleet(), projector, Events(),
                context_store=FailingStore(), opener=lambda _path: port,
                retry_initial=0, idle_seconds=0,
            )
        self.assertEqual(port.writes, [])
        self.assertTrue(port.closed)

    async def test_slow_durable_save_does_not_renew_request_anchored_lease(self):
        feed_path = Path(os.environ.get("RLCD_FEED_TEST", APP / "build/native-live/feed"))
        if not feed_path.is_file():
            self.skipTest("native C feed helper has not been built")

        for delay_ms in (0, 100):
            with self.subTest(save_delay_ms=delay_ms):
                now_ms = 0
                written = asyncio.Event()
                timeline = []
                board = NativeFeed(feed_path)
                request = board.request(0)
                self.addCleanup(board.close)

                class Fleet:
                    hosts = ["starship"]

                    def sources(self):
                        row = native_row("slow-save", host="starship")
                        return [native_source([row], host="starship", remaining=160)]

                class Store:
                    def save(self, *_args):
                        nonlocal now_ms
                        timeline.append(("save", now_ms))
                        now_ms += delay_ms

                class Port:
                    def __init__(self):
                        self.read_request = False
                        self.state = None
                        self.closed = False

                    def read(self):
                        if not self.read_request:
                            self.read_request = True
                            return request
                        return b""

                    def write(self, response):
                        timeline.append(("write", now_ms))
                        self.state = board.accept_at(response, now_ms)
                        written.set()
                        return len(response)

                    def close(self):
                        self.closed = True

                port = Port()
                task = asyncio.create_task(serve_serial(
                    "/unused", Fleet(), Projector(["starship"]),
                    Events(io.StringIO(), clock=lambda: now_ms / 1000),
                    context_store=Store(), opener=lambda _path: port,
                    retry_initial=0, idle_seconds=0, clock=lambda: now_ms / 1000,
                ))
                try:
                    await asyncio.wait_for(written.wait(), 1)
                finally:
                    task.cancel()
                    with self.assertRaises(asyncio.CancelledError):
                        await task
                self.assertEqual([event for event, _ in timeline], ["save", "write"])
                self.assertEqual(timeline[-1][1], delay_ms)
                self.assertTrue(port.closed)
                self.assertEqual(port.state["rows"], 1)
                entry = port.state["entries"][0]
                if delay_ms == 0:
                    self.assertEqual((entry["work"], entry["health"]), (0, 0))
                else:
                    # A 60 ms wire lease arrived 100 ms after the board's request.
                    # The native consumer anchors it to that request and never
                    # presents the expired row as current.
                    self.assertEqual((entry["work"], entry["health"]), (5, 1))
                    self.assertEqual(entry["age"], "?")


if __name__ == "__main__":
    unittest.main()
