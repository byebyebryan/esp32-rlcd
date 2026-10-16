import asyncio
import contextlib
import io
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.mesh import Fleet
from live_dashboard.runtime import Events, Failure, supervise


class Lifetime(unittest.IsolatedAsyncioTestCase):
    async def test_failed_or_returned_worker_retires_sibling(self):
        for returned in (True, False):
            closed = asyncio.Event()

            async def watcher(returned=returned):
                await asyncio.sleep(0)
                if not returned:
                    raise RuntimeError("private upstream payload")

            async def serial(closed=closed):
                try:
                    await asyncio.Event().wait()
                finally:
                    closed.set()

            code = "mesh_worker_returned" if returned else "mesh_worker_failed"
            with self.assertRaisesRegex(Failure, code):
                await supervise(watcher(), serial(), asyncio.Event())
            self.assertTrue(closed.is_set())

    async def test_stop_cleans_both_and_surfaces_cleanup_failure(self):
        stop = asyncio.Event()
        entered = asyncio.Event()
        closed = []

        async def worker(name):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                closed.append(name)
                if name == "mesh":
                    raise Failure("mesh_cleanup_failed")

        task = asyncio.create_task(supervise(worker("mesh"), worker("serial"), stop))
        await entered.wait()
        stop.set()
        with self.assertRaisesRegex(Failure, "worker_cleanup_failed"):
            await task
        self.assertCountEqual(closed, ["mesh", "serial"])

    async def test_uncooperative_cleanup_has_finite_grace(self):
        stop = asyncio.Event()
        release = asyncio.Event()
        entered = asyncio.Event()

        async def slow():
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                while not release.is_set():
                    with contextlib.suppress(asyncio.CancelledError):
                        await release.wait()

        async def serial():
            await asyncio.Event().wait()

        task = asyncio.create_task(
            supervise(slow(), serial(), stop, cleanup_seconds=0.02)
        )
        await entered.wait()
        stop.set()
        with self.assertRaisesRegex(Failure, "worker_cleanup_timeout"):
            await asyncio.wait_for(task, 0.3)
        release.set()
        await asyncio.sleep(0.01)

    async def test_mesh_cleanup_failure_reaches_supervisor_without_payload(self):
        class Guard:
            def disconnect(self):
                pass

        class Stream:
            def __aiter__(self):
                return self

            async def __anext__(self):
                raise ValueError("private stream body")

            async def aclose(self):
                raise RuntimeError("private cleanup body")

        async def configured(*args, **kwargs):
            return types.SimpleNamespace(execute_admitted=lambda _: Stream())

        fake = {
            "mesh_plus": types.ModuleType("mesh_plus"),
            "mesh_plus.api": types.SimpleNamespace(configured_reader=configured),
            "mesh_plus.catalog": types.SimpleNamespace(SSHPlusAuthority=lambda: None),
        }
        output = io.StringIO()
        fleet = Fleet.__new__(Fleet)
        fleet.hosts = ["starship"]
        fleet.guard = Guard()
        fleet.request_id = "0" * 32
        fleet.profile = None
        fleet.events = Events(output)

        async def serial():
            await asyncio.Event().wait()

        with (
            patch.dict(sys.modules, fake),
            self.assertRaisesRegex(Failure, "mesh_cleanup_failed"),
        ):
            await supervise(fleet.run(), serial(), asyncio.Event())
        self.assertTrue(fleet.closed)
        self.assertNotIn("private", output.getvalue())
        self.assertIn("mesh_retry", output.getvalue())

    def test_repeated_failure_events_are_limited(self):
        output = io.StringIO()
        now = [0]
        events = Events(output, lambda: now[0])
        for _ in range(100):
            events.emit("serial_retry", interval=30, reason="serial_missing")
        now[0] = 31
        events.emit("serial_retry", interval=30, reason="serial_missing")
        self.assertEqual(len(output.getvalue().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
