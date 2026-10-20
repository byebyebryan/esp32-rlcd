import asyncio
import errno
import io
import json
import os
import pty
import select
import signal
import subprocess
import sys
import unittest
from pathlib import Path

from test_live_dashboard import row, source

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host"))
from live_dashboard.projection import Projector
from live_dashboard.runtime import Events, Failure
from live_dashboard.serial import Port, parse_health, serve_serial


def health_line(**overrides):
    values = dict(health=0, partial=0, rows=1, attention=0, waiting=0, working=1,
                  recent=0, uncertain=0, frame_us=16000, miss=0, heap=292171, stack=4776)
    values.update(overrides)
    return ("RLCD_HEALTH " + " ".join(f"{k}={v}" for k, v in values.items()) + "\n").encode()


class HealthDiagnostics(unittest.TestCase):
    def test_health_fields_are_bounded_and_unambiguous(self):
        self.assertEqual(parse_health(health_line())["rows"], 1)
        for invalid in (
            health_line(health=5), health_line(partial=2), health_line(rows=33),
            health_line(working=131071), health_line(frame_us=-1),
            health_line(miss=2), health_line(heap=0x100000000),
            health_line(stack="9" * 100), health_line(extra=1),
            health_line().replace(b"stack=4776", b"health=0"),
            health_line().replace(b"frame_us=16000", b"frame_us=secret"),
            health_line().replace(b"frame_us=16000", b"frame_us=\xff"),
        ):
            with self.subTest(invalid=invalid):
                self.assertIsNone(parse_health(invalid))


class PortLifetime(unittest.TestCase):
    def test_sigterm_of_real_supervisor_releases_port(self):
        master, slave = pty.openpty()
        path = os.ttyname(slave)
        code = """import asyncio,importlib.util,sys,types
spec=importlib.util.spec_from_file_location("bridge",sys.argv[1])
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from live_dashboard.projection import Source
class Fleet:
 def __init__(self,hosts,*args,**kwargs):self.hosts=hosts
 async def run(self):await asyncio.Event().wait()
 def sources(self):return [Source("starship","current",10000,10000)]
m.Fleet=Fleet
asyncio.run(m.main(types.SimpleNamespace(hosts=["starship"],seconds=0,preview=None,roster=False,inspect=False,profiles_config=None,profile=[],port=sys.argv[2],verbose=False)))
"""
        app = Path(__file__).resolve().parents[1]
        child = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                code,
                str(app / "scripts/live-dashboard.py"),
                path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertTrue(select.select([child.stderr], [], [], 2)[0])
            # Send repeatedly until its private tty has been configured.
            response = bytearray()
            for _ in range(20):
                os.write(master, b"RLCD?4 " + b"0" * 16 + b" 1\n")
                if select.select([master], [], [], 0.05)[0]:
                    response.extend(os.read(master, 4096))
                if b"RLCD!4\t" in response:
                    break
            self.assertIn(b"RLCD!4\t", response)
            child.send_signal(signal.SIGTERM)
            self.assertEqual(child.wait(timeout=2), 0)
            reopened = Port(path)
            reopened.close()
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=2)
            child.stderr.close()
            os.close(master)
            os.close(slave)

    def test_no_data_is_not_hangup_and_busy_owner_is_preserved(self):
        master, slave = pty.openpty()
        path = os.ttyname(slave)
        os.close(slave)
        port = Port(path)
        try:
            self.assertEqual(port.read(), b"")
            with self.assertRaises(OSError):
                Port(path)
            os.fstat(port.fd)
            os.close(master)
            master = None
            with self.assertRaisesRegex(Failure, "serial_disconnected"):
                port.read()
        finally:
            port.close()
            if master is not None:
                os.close(master)
        self.assertIsNone(port.fd)


class Reconnect(unittest.IsolatedAsyncioTestCase):
    async def test_ack_reports_change_in_source_admission(self):
        finished = asyncio.Event()
        output = io.StringIO()

        class FakePort:
            def __init__(self):
                self.queue = [b"RLCD?4 " + b"0" * 16 + b" 1\n"]
                self.request = 0

            def read(self):
                if self.queue:
                    line = self.queue.pop(0)
                    if line.startswith(b"RLCD?4 "):
                        self.request += 1
                    return line
                finished.set()
                return b""

            def write(self, payload):
                f = payload.rstrip(b"\n").split(b"\t")
                self.queue.append(b"RLCD_ACK seq=" + f[4] + b" rows=" + f[6]
                                  + b" request=" + f[2] + b" crc=" + f[-1] + b"\n")
                if self.request == 1:
                    self.queue.append(b"RLCD?4 " + b"0" * 16 + b" 2\n")
                return len(payload)

            def close(self):
                pass

        port = FakePort()
        fleet = type("Fleet", (), {"sources": lambda _: [
            source([], status="warming", remaining=0) if port.request == 1
            else source([row("active")])
        ]})()
        task = asyncio.create_task(serve_serial(
            Path("unused"), fleet, Projector(["starship"]), Events(output),
            opener=lambda _: port, idle_seconds=0.001,
        ))
        try:
            await asyncio.wait_for(finished.wait(), 0.5)
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        events = [json.loads(line.removeprefix("RLCD_EVENT "))
                  for line in output.getvalue().splitlines()]
        admitted = [e["source_admitted"] for e in events if e["event"] == "device_ack_recovered"]
        self.assertEqual(admitted, [False, True])

    async def test_quiet_health_sampling_transitions_and_verbose_opt_in(self):
        for verbose in (False, True):
            now = 0
            finished = asyncio.Event()
            events_output, output = io.StringIO(), io.StringIO()

            class FakePort:
                def __init__(self):
                    self.queue = [
                        (0, b"RLCD?4 " + b"0" * 16 + b" 1\n"),
                        (1, health_line()),
                        (2, health_line(working=0, waiting=1)),
                        (3, health_line(miss="invalid")),
                        (61, health_line()),
                        (62, health_line(health=2, working=0, uncertain=1)),
                        (63, health_line()),
                        (64, health_line(miss=1)),
                        (65, health_line()),
                    ]
                    self.closed = False

                def read(self):
                    nonlocal now
                    if self.queue:
                        now, data = self.queue.pop(0)
                        return data
                    finished.set()
                    return b""

                def write(self, payload):
                    fields = payload.rstrip(b"\n").split(b"\t")
                    self.queue.insert(0, (0, b"RLCD_ACK seq=1 rows=1 request=1 crc=" + fields[-1] + b"\n"))
                    return len(payload)

                def close(self):
                    self.closed = True

            port = FakePort()
            fleet = type("Fleet", (), {"sources": lambda _: [source([row("active")])]})()
            task = asyncio.create_task(serve_serial(
                Path("unused"), fleet, Projector(["starship"]),
                Events(events_output, clock=lambda: now), verbose=verbose, output=output,
                opener=lambda _: port, idle_seconds=0.001, clock=lambda: now,
            ))
            try:
                await asyncio.wait_for(finished.wait(), 0.5)
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
            events = [json.loads(line.removeprefix("RLCD_EVENT "))
                      for line in events_output.getvalue().splitlines()]
            health = [e for e in events if e["event"] == "device_health"]
            self.assertEqual([(h["health"], h["miss"]) for h in health],
                             [(0, 0), (0, 0), (2, 0), (0, 0), (0, 1), (0, 0)])
            # Health reports are diagnostics and cannot acknowledge a request.
            self.assertEqual(sum(e["event"] == "device_ack_recovered" for e in events), 1)
            missing = next(e for e in events if e["event"] == "device_ack_missing")
            self.assertEqual(missing["last_ack_request"], 1)
            self.assertGreaterEqual(missing["ack_age_ms"], 60000)
            self.assertTrue(port.closed)
            if verbose:
                self.assertIn("RLCD_ACK ", output.getvalue())
                self.assertIn("RLCD_HEALTH ", output.getvalue())
                self.assertIn('"sequence": 1', output.getvalue())
            else:
                self.assertEqual(output.getvalue(), "")

    async def test_ack_retained_rows_during_warmup_and_wrong_healthy_count(self):
        for status, accepted in (("warming", True), ("current", False)):
            output = io.StringIO()
            acknowledged = asyncio.Event()

            class FakePort:
                def __init__(self):
                    self.queue = [b"RLCD?4 " + b"0" * 16 + b" 1\n"]

                def read(self):
                    return self.queue.pop(0) if self.queue else b""

                def write(self, payload, acknowledged=acknowledged):
                    fields = payload.rstrip(b"\n").split(b"\t")
                    self.queue.append(
                        b"RLCD_ACK seq=1 rows=7 request=1 crc=" + fields[-1] + b"\n"
                    )
                    acknowledged.set()
                    return len(payload)

                def close(self):
                    pass

            port = FakePort()
            inputs = [
                source([], status=status, remaining=0 if status == "warming" else 10000)
            ]
            fleet = type("Fleet", (), {"sources": lambda _, inputs=inputs: inputs})()
            task = asyncio.create_task(
                serve_serial(
                    Path("unused"),
                    fleet,
                    Projector(["starship"]),
                    Events(output),
                    opener=lambda _, port=port: port,
                    output=io.StringIO(),
                    idle_seconds=0.001,
                )
            )
            await asyncio.wait_for(acknowledged.wait(), 0.2)
            await asyncio.sleep(0.01)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertEqual("device_ack_recovered" in output.getvalue(), accepted)

    async def test_absent_busy_hangup_then_fresh_incarnation(self):
        inputs = [source([row("active")])]
        fleet = type("Fleet", (), {"sources": lambda _: inputs})()
        ready = asyncio.Event()
        frames, ports = [], []
        opens = 0

        class FakePort:
            def __init__(self, number):
                self.number = number
                boot = str(number) * 16
                self.queue = [b"ignored boot log\n", f"RLCD?4 {boot} ".encode(), b"1\n"]
                self.closed = False

            def read(self):
                if self.queue:
                    return self.queue.pop(0)
                if self.number == 1:
                    raise Failure("serial_disconnected")
                return b""

            def write(self, payload):
                frames.append(payload)
                fields = payload.rstrip(b"\n").split(b"\t")
                self.queue.append(
                    b"RLCD_ACK seq="
                    + fields[4]
                    + b" rows="
                    + fields[6]
                    + b" request="
                    + fields[2]
                    + b" crc="
                    + fields[-1]
                    + b"\n"
                )
                if self.number == 2:
                    ready.set()
                return len(payload)

            def close(self):
                self.closed = True

        def opener(_):
            nonlocal opens
            opens += 1
            if opens == 1:
                raise OSError(errno.ENOENT, "missing")
            if opens == 2:
                raise OSError(errno.EBUSY, "busy")
            port = FakePort(opens - 2)
            ports.append(port)
            return port

        events_output, output = io.StringIO(), io.StringIO()
        task = asyncio.create_task(
            serve_serial(
                Path("unused"),
                fleet,
                Projector(["starship"]),
                Events(events_output),
                opener=opener,
                output=output,
                retry_initial=0.001,
                retry_max=0.004,
                idle_seconds=0.001,
            )
        )
        await asyncio.wait_for(ready.wait(), 0.5)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(all(p.closed for p in ports))
        first, second = [frame.split(b"\t") for frame in frames]
        self.assertEqual((first[1], second[1]), (b"1" * 16, b"2" * 16))
        self.assertNotEqual(first[3], second[3])
        self.assertEqual(first[4], second[4])
        for code in ("serial_missing", "serial_busy", "serial_disconnected"):
            self.assertIn(code, events_output.getvalue())

    async def test_absent_device_retry_is_promptly_cancelled(self):
        def missing(_):
            raise OSError(errno.ENOENT, "missing")

        fleet = type("Fleet", (), {"sources": lambda _: []})()
        task = asyncio.create_task(
            serve_serial(
                Path("unused"),
                fleet,
                Projector(["starship"]),
                Events(io.StringIO()),
                opener=missing,
                retry_initial=30,
            )
        )
        await asyncio.sleep(0.01)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, 0.2)


if __name__ == "__main__":
    unittest.main()
