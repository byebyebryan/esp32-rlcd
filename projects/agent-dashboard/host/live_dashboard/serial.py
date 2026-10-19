"""Exclusive stable-device serial lifetime, reconnect and fresh requests."""

import asyncio
import errno
import fcntl
import json
import os
import secrets
import select
import termios
import time

from .projection import CAPACITY
from .runtime import Failure
from .wire import encode, parse_request


KNOWN_RLCD_DEVICE_NAMES = frozenset({
    "usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:F3:43:74-if00",  # Starship
    "usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:DE:D0:04-if00",  # Snap
})


HEALTH_LIMITS = {
    "health": 4,
    "partial": 1,
    "rows": CAPACITY,
    "attention": 131070,
    "waiting": 131070,
    "working": 131070,
    "recent": 131070,
    "uncertain": 131070,
    "frame_us": 0x7FFFFFFFFFFFFFFF,
    "miss": 1,
    "heap": 0xFFFFFFFF,
    "stack": 0xFFFFFFFF,
}


def parse_health(line):
    """Bound diagnostic fields; device reports never grant source authority."""
    if not line.startswith(b"RLCD_HEALTH "):
        return None
    try:
        pairs = [field.split("=", 1) for field in line.decode("ascii").split()[1:]]
        fields = dict(pairs)
        if len(pairs) != len(fields) or fields.keys() != HEALTH_LIMITS.keys():
            return None
        result = {}
        for name, value in fields.items():
            if not value.isascii() or not value.isdecimal() or len(value) > 19:
                return None
            number = int(value)
            if number > HEALTH_LIMITS[name]:
                return None
            result[name] = number
        return result
    except (ValueError, UnicodeError):
        return None


def io_reason(error):
    if error.errno in {errno.ENOENT, errno.ENODEV, errno.ENXIO}:
        return "serial_missing"
    if error.errno in {errno.EBUSY, errno.EAGAIN, errno.EACCES}:
        return "serial_busy" if error.errno != errno.EACCES else "serial_permission"
    if error.errno in {errno.EIO, errno.EBADF}:
        return "serial_disconnected"
    return "serial_io_failed"


class Port:
    def __init__(self, path):
        self.fd = None
        self.old = None
        self.exclusive = False
        try:
            self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.ioctl(self.fd, termios.TIOCEXCL)
            self.exclusive = True
            self.old = termios.tcgetattr(self.fd)
            config = termios.tcgetattr(self.fd)
            config[0] = 0
            config[1] = 0
            config[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
            config[3] = 0
            config[4] = termios.B115200
            config[5] = termios.B115200
            config[6][termios.VMIN] = 0
            config[6][termios.VTIME] = 0
            termios.tcsetattr(self.fd, termios.TCSANOW, config)
            self.poller = select.poll()
            self.poller.register(
                self.fd, select.POLLIN | select.POLLHUP | select.POLLERR
            )
        except BaseException:
            self.close()
            raise

    def read(self):
        if any(
            flags & (select.POLLHUP | select.POLLERR | select.POLLNVAL)
            for _, flags in self.poller.poll(0)
        ):
            raise Failure("serial_disconnected")
        try:
            return os.read(self.fd, 4096)
        except BlockingIOError:
            return b""

    def write(self, data):
        return os.write(self.fd, data)

    def close(self):
        if self.fd is None:
            return
        try:
            if self.old is not None:
                try:
                    termios.tcsetattr(self.fd, termios.TCSANOW, self.old)
                except (OSError, termios.error):
                    pass  # Removed hardware cannot restore its old tty settings.
            if self.exclusive:
                try:
                    fcntl.ioctl(self.fd, termios.TIOCNXCL)
                except OSError:
                    pass
        finally:
            os.close(self.fd)
            self.fd = None


async def serve_serial(
    path,
    fleet,
    projector,
    events,
    *,
    verbose=False,
    output=None,
    opener=Port,
    retry_initial=1,
    retry_max=30,
    idle_seconds=0.01,
    clock=time.monotonic,
):
    """A serial incarnation resets framing/sequence but never native evidence."""
    import sys

    output = output or sys.stdout
    delay = retry_initial
    previous_reason = None
    while True:
        port = None
        try:
            port = opener(path)
            epoch = secrets.token_hex(8)
            sequence = 0
            pending = bytearray()
            discard = False
            last_request = None
            acknowledged = {}
            last_sent = None
            last_ack = None
            last_ack_request = None
            last_ack_admitted = None
            source_status = None
            reported_health = None
            health_reported_at = float("-inf")
            connected_at = clock()
            events.emit("serial_connected")
            previous_reason = None
            while True:
                part = port.read()
                if part:
                    # Discard an excessive physical line through its delimiter.
                    for byte in part:
                        if byte != 10:
                            if not discard:
                                if len(pending) >= 16384:
                                    pending.clear()
                                    discard = True
                                else:
                                    pending.append(byte)
                            continue
                        line = bytes(pending)
                        pending.clear()
                        if discard:
                            discard = False
                            continue
                        request = parse_request(line)
                        if request is None:
                            if line.startswith(b"RLCD_ACK "):
                                try:
                                    values = dict(
                                        field.split("=", 1)
                                        for field in line.decode("ascii").split()[1:]
                                    )
                                    seq = int(values["seq"])
                                    sent = acknowledged.pop(seq, None)
                                    rows = int(values["rows"])
                                    if (
                                        sent
                                        and values.get("crc") == sent[0]
                                        and int(values["request"]) == sent[1]
                                        and (
                                            rows == sent[2]
                                            if sent[3]
                                            else sent[2] <= rows <= CAPACITY
                                        )
                                    ):
                                        now = clock()
                                        if (
                                            last_ack is None
                                            or now - last_ack >= 5
                                            or sent[3] != last_ack_admitted
                                        ):
                                            events.emit(
                                                "device_ack_recovered",
                                                request=sent[1],
                                                sequence=seq,
                                                rows=rows,
                                                source_admitted=sent[3],
                                            )
                                        last_ack = now
                                        last_ack_request = sent[1]
                                        last_ack_admitted = sent[3]
                                        delay = retry_initial
                                except (ValueError, KeyError, UnicodeError):
                                    pass
                            health = parse_health(line)
                            if health is not None:
                                now = clock()
                                state = (health["health"], health["partial"], health["miss"])
                                if state != reported_health or now - health_reported_at >= 60:
                                    events.emit("device_health", **health)
                                    reported_health = state
                                    health_reported_at = now
                            if verbose and line.startswith((b"RLCD_ACK ", b"RLCD_HEALTH ")):
                                print(
                                    line.decode("ascii", "replace"),
                                    file=output,
                                    flush=True,
                                )
                            continue
                        if request == last_request:
                            continue
                        last_request = request
                        sequence += 1
                        if sequence > 0xFFFFFFFF:
                            raise Failure("serial_sequence_exhausted")
                        sources = fleet.sources()
                        statuses = tuple((s.host, s.status) for s in sources)
                        if statuses != source_status:
                            for host, status in statuses:
                                events.emit("source_health", host=host, status=status)
                            source_status = statuses
                        try:
                            view = projector.project(sources)
                            response = encode(view, *request, epoch, sequence)
                        except ValueError as error:
                            code = str(error)
                            raise Failure(
                                code
                                if code
                                in {
                                    "roster_capacity",
                                    "identity_collision",
                                    "display_label_collision",
                                    "device_frame_capacity",
                                }
                                else "projection_failed"
                            ) from None
                        checksum = response[-9:-1].decode()
                        acknowledged[sequence] = (
                            checksum,
                            request[1],
                            len(view["rows"]),
                            all(h["status"] < 2 for h in view["hosts"]),
                        )
                        if len(acknowledged) > 4:
                            del acknowledged[min(acknowledged)]
                        deadline = clock() + 0.5
                        while response:
                            if clock() >= deadline:
                                raise Failure("serial_write_timeout")
                            try:
                                sent = port.write(response)
                                if sent:
                                    response = response[sent:]
                                else:
                                    await asyncio.sleep(idle_seconds)
                            except BlockingIOError:
                                await asyncio.sleep(idle_seconds)
                        last_sent = clock()
                        if verbose:
                            print(
                                json.dumps(
                                    {
                                        "sequence": sequence,
                                        "request": request[1],
                                        "crc": checksum,
                                        "rows": len(view["rows"]),
                                        "hosts": view["hosts"],
                                    }
                                ),
                                file=output,
                                flush=True,
                            )
                now = clock()
                if now - (last_ack if last_ack is not None else connected_at) >= 5:
                    events.emit(
                        "device_ack_missing",
                        interval=30,
                        request_seen=last_sent is not None,
                        last_request=last_request[1]
                        if last_request is not None
                        else None,
                        request_age_ms=int((now - last_sent) * 1000)
                        if last_sent is not None
                        else None,
                        last_ack_request=last_ack_request,
                        ack_age_ms=int((now - last_ack) * 1000)
                        if last_ack is not None
                        else None,
                    )
                await asyncio.sleep(idle_seconds)
        except asyncio.CancelledError:
            raise
        except OSError as error:
            reason = io_reason(error)
        except Failure as error:
            reason = str(error)
            if reason not in {
                "serial_disconnected",
                "serial_write_timeout",
                "serial_sequence_exhausted",
            }:
                raise
        finally:
            if port is not None:
                port.close()
        events.emit(
            "serial_retry",
            interval=30 if reason == previous_reason else 0,
            reason=reason,
            retry_ms=int(delay * 1000),
        )
        previous_reason = reason
        await asyncio.sleep(delay)
        delay = min(retry_max, delay * 2)
