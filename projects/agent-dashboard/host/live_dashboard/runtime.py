"""Owned worker lifetime and finite operational diagnostics."""

import asyncio
import contextlib
import json
import sys
import time


class Failure(RuntimeError):
    """A caller-selected finite failure code, never an exception payload."""


class Events:
    def __init__(self, output=None, clock=time.monotonic):
        self.output = output or sys.stderr
        self.clock = clock
        self.last = {}

    def emit(self, event, *, interval=0, **fields):
        now = self.clock()
        key = (event, fields.get("reason"), fields.get("host"))
        if interval and now - self.last.get(key, float("-inf")) < interval:
            return
        self.last[key] = now
        print(
            "RLCD_EVENT " + json.dumps({"event": event, **fields}),
            file=self.output,
            flush=True,
        )


async def supervise(fleet, serial, stop, *, cleanup_seconds=5):
    """Unexpected worker termination fails the owner; stopping retires both."""
    workers = {
        asyncio.create_task(fleet): "mesh",
        asyncio.create_task(serial): "serial",
    }
    stopper = asyncio.create_task(stop.wait())
    failure = None
    try:
        done, _ = await asyncio.wait(
            [*workers, stopper], return_when=asyncio.FIRST_COMPLETED
        )
        for worker in done & workers.keys():
            try:
                worker.result()
            except Failure as error:
                failure = error
            except asyncio.CancelledError:
                if not stop.is_set():
                    failure = Failure(workers[worker] + "_worker_cancelled")
            except Exception:  # noqa: BLE001 - finite worker failure boundary
                failure = Failure(workers[worker] + "_worker_failed")
            else:
                if not stop.is_set():
                    failure = Failure(workers[worker] + "_worker_returned")
    finally:
        for task in [*workers, stopper]:
            if not task.done():
                task.cancel()
        done, pending = await asyncio.wait([*workers, stopper], timeout=cleanup_seconds)
        for task in done:
            with contextlib.suppress(asyncio.CancelledError):
                try:
                    task.result()
                except Exception:  # noqa: BLE001 - finite cleanup failure boundary
                    failure = failure or Failure("worker_cleanup_failed")
        if pending:
            for task in pending:
                task.cancel()
            failure = Failure("worker_cleanup_timeout")
    if failure is not None:
        raise failure
