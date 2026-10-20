"""Private bounded restart context for the host-side dashboard bridge.

The cache retains identity and presentation only. It never stores source leases
or state claims, and every restored row starts as uncertain context.
"""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import secrets
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .projection import ALIASES, MAX_ROSTER, token_key

VERSION = 1
MAX_STATE_BYTES = 8 * 1024 * 1024
MAX_CONTEXT_ROWS = 2 * MAX_ROSTER
MAX_IDENTITY_FIELD_BYTES = 1024
MAX_LABEL_BYTES = 63
MAX_BINDING_BYTES = 64 * 1024
STATE_DIRECTORY = Path.home() / ".local/state/rlcd-agent-dashboard"
STATE_FILE = re.compile(r"[A-Za-z0-9._-]{1,240}\.json\Z")
DEVICES = frozenset({
    "usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:F3:43:74-if00",
    "usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:DE:D0:04-if00",
})


class ContextPolicyError(ValueError):
    """The state location or its ownership policy is unsafe."""


@dataclass(frozen=True)
class RestoredContext:
    rows: tuple[dict, ...]
    initialized_hosts: frozenset[str]


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def default_context_path(device):
    """Return a stable per-board path without trusting an arbitrary path name."""
    name = Path(device).name
    if name not in DEVICES:
        raise ValueError("context_device_unknown")
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    suffix = hashlib.sha256(name.encode("ascii")).hexdigest()[:12]
    return STATE_DIRECTORY / f"{safe}-{suffix}.json"


def route_binding(device, hosts, routes):
    """Build the exact binding stored beside a cache's native identities."""
    return {
        "device": Path(device).name,
        "hosts": list(hosts),
        "routes": [dict(route) for route in routes],
    }


def _open_directory(path):
    """Walk without following symlinks, creating a private final directory."""
    path = Path(os.path.abspath(os.fspath(path)))
    if not path.is_absolute() or path == Path("/"):
        raise ContextPolicyError("context_directory_invalid")
    parts = path.parts[1:]
    descriptor = os.open(
        "/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
    )
    try:
        for index, part in enumerate(parts):
            try:
                child = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=descriptor,
                )
            except FileNotFoundError:
                os.mkdir(part, 0o700, dir_fd=descriptor)
                child = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=descriptor,
                )
            node = os.fstat(child)
            if not stat.S_ISDIR(node.st_mode):
                os.close(child)
                raise ContextPolicyError("context_directory_type")
            if index == len(parts) - 1:
                if node.st_uid != os.getuid() or node.st_mode & 0o077:
                    os.close(child)
                    raise ContextPolicyError("context_directory_policy")
            elif (
                node.st_uid not in {0, os.getuid()}
                or (node.st_mode & 0o022 and not (node.st_uid == 0 and node.st_mode & stat.S_ISVTX))
            ):
                os.close(child)
                raise ContextPolicyError("context_parent_policy")
            os.close(descriptor)
            descriptor = child
        return descriptor, path.name
    except BaseException:
        os.close(descriptor)
        raise


def _pairs_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("context_duplicate_key")
        result[key] = value
    return result


def _text(value, *, limit, field):
    if not isinstance(value, str) or not value:
        raise ValueError("context_" + field)
    try:
        encoded = value.encode("utf-8")
    except UnicodeError:
        raise ValueError("context_" + field) from None
    if len(encoded) > limit or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("context_" + field)
    return value


def _validate_document(document, expected_binding, hosts):
    if type(document) is not dict or set(document) != {"body", "sha256"}:
        raise ValueError("context_shape")
    body = document["body"]
    checksum = document["sha256"]
    if (
        type(body) is not dict
        or set(body) != {"version", "binding", "initialized_hosts", "rows"}
        or type(body["version"]) is not int
        or body["version"] != VERSION
        or not isinstance(checksum, str)
        or not re.fullmatch(r"[0-9a-f]{64}", checksum)
        or hashlib.sha256(canonical(body)).hexdigest() != checksum
    ):
        raise ValueError("context_checksum_or_version")
    binding = body["binding"]
    if type(binding) is not dict or binding != expected_binding:
        raise ValueError("context_binding")
    if (
        type(body["initialized_hosts"]) is not list
        or type(body["rows"]) is not list
        or len(body["initialized_hosts"]) > len(hosts)
        or len(body["rows"]) > MAX_CONTEXT_ROWS
    ):
        raise ValueError("context_capacity")

    initialized = body["initialized_hosts"]
    if any(type(host) is not str or host not in hosts for host in initialized):
        raise ValueError("context_initialized_host")
    if len(initialized) != len(set(initialized)):
        raise ValueError("context_initialized_duplicate")

    result, identities, ids, orders, per_host = [], set(), set(), set(), {}
    for entry in body["rows"]:
        fields = {"identity", "host", "order", "label", "project", "badge"}
        if type(entry) is not dict or set(entry) != fields:
            raise ValueError("context_row_shape")
        host = entry["host"]
        if type(host) is not str or host not in hosts:
            raise ValueError("context_row_host")
        identity = entry["identity"]
        if type(identity) is not list or len(identity) != 5:
            raise ValueError("context_identity_shape")
        identity = tuple(
            _text(value, limit=MAX_IDENTITY_FIELD_BYTES, field="identity_string")
            for value in identity
        )
        if identity[0] != host or identity[1] != "codex":
            raise ValueError("context_identity_scope")
        label = _text(entry["label"], limit=MAX_LABEL_BYTES, field="label")
        project = entry["project"]
        if project is not None:
            project = _text(project, limit=MAX_LABEL_BYTES, field="project")
        order = entry["order"]
        if type(order) is not int or not 0 <= order < MAX_CONTEXT_ROWS:
            raise ValueError("context_row_order")
        badge = entry["badge"]
        if badge not in {"ST", "SN", "SW"} or (badge == "SW" and host != "snap"):
            raise ValueError("context_row_badge")
        identifier, key = token_key(identity)
        if key in identities or identifier in ids or order in orders:
            raise ValueError("context_row_duplicate")
        identities.add(key)
        ids.add(identifier)
        orders.add(order)
        per_host[host] = per_host.get(host, 0) + 1
        if per_host[host] > MAX_ROSTER:
            raise ValueError("context_host_capacity")
        result.append(
            {
                "identity": identity,
                "host": host,
                "order": order,
                "label": label,
                "project": project,
                "badge": badge,
            }
        )
    return RestoredContext(tuple(sorted(result, key=lambda row: row["order"])),
                           frozenset(initialized))


class ContextStore:
    """One locked, atomic context file for one physical dashboard device."""

    def __init__(self, path, binding, hosts):
        self.path = Path(os.path.abspath(os.fspath(path)))
        self.binding = json.loads(canonical(binding))
        self.hosts = tuple(hosts)
        if (
            not self.hosts
            or len(self.hosts) > 2
            or len(set(self.hosts)) != len(self.hosts)
            or any(host not in ALIASES for host in self.hosts)
            or not STATE_FILE.fullmatch(self.path.name)
            or len(canonical(self.binding)) > MAX_BINDING_BYTES
        ):
            raise ValueError("context_binding_invalid")
        self.directory_fd = None
        self.lock_fd = None
        self.name = self.path.name
        self.last_payload = None
        self._validate_binding()

    def _validate_binding(self):
        fields = {"device", "hosts", "routes"}
        if (
            type(self.binding) is not dict
            or set(self.binding) != fields
            or type(self.binding["device"]) is not str
            or self.binding["device"] not in DEVICES
            or self.binding["hosts"] != list(self.hosts)
            or type(self.binding["routes"]) is not list
            or not 1 <= len(self.binding["routes"]) <= 4
        ):
            raise ValueError("context_binding_invalid")
        route_fields = {"host", "profile", "label", "codex_home", "source", "socket"}
        seen = set()
        routed_hosts = set()
        for route in self.binding["routes"]:
            if type(route) is not dict or set(route) != route_fields:
                raise ValueError("context_route_invalid")
            host = route["host"]
            profile = route["profile"]
            label = route["label"]
            source = route["source"]
            socket = route["socket"]
            home = route["codex_home"]
            if (
                type(host) is not str
                or host not in self.hosts
                or type(profile) is not str
                or re.fullmatch(r"[a-z][a-z0-9_]{0,31}", profile) is None
                or type(label) is not str
                or not 1 <= len(label) <= 32
                or type(source) is not str
                or re.fullmatch(r"[a-z][a-z0-9_]{0,127}", source) is None
                or type(socket) is not str
                or not socket.startswith("/")
                or len(socket.encode("utf-8")) > 4096
                or (home is not None and (
                    type(home) is not str or not home.startswith("/")
                    or len(home.encode("utf-8")) > 4096
                ))
                or (host, profile) in seen
            ):
                raise ValueError("context_route_invalid")
            seen.add((host, profile))
            routed_hosts.add(host)
        if routed_hosts != set(self.hosts):
            raise ValueError("context_route_hosts")

    def open(self):
        if self.directory_fd is not None:
            raise ContextPolicyError("context_already_open")
        try:
            self.directory_fd, name = _open_directory(self.path.parent)
            if name != self.path.parent.name:
                raise ContextPolicyError("context_directory_name")
            self.lock_fd = os.open(
                ".context.lock",
                os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
                0o600,
                dir_fd=self.directory_fd,
            )
            lock_node = os.fstat(self.lock_fd)
            if (
                not stat.S_ISREG(lock_node.st_mode)
                or lock_node.st_uid != os.getuid()
                or lock_node.st_mode & 0o077
                or lock_node.st_size != 0
            ):
                raise ContextPolicyError("context_lock_policy")
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ContextPolicyError("context_lock_busy") from None
            return self._load()
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None
        if self.directory_fd is not None:
            os.close(self.directory_fd)
            self.directory_fd = None

    def _load(self):
        try:
            descriptor = os.open(
                self.name,
                os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=self.directory_fd,
            )
        except FileNotFoundError:
            self.last_payload = None
            return RestoredContext((), frozenset())
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise ContextPolicyError("context_file_symlink") from None
            raise
        try:
            node = os.fstat(descriptor)
            if (
                not stat.S_ISREG(node.st_mode)
                or node.st_uid != os.getuid()
                or node.st_mode & 0o077
            ):
                raise ContextPolicyError("context_file_policy")
            if node.st_size > MAX_STATE_BYTES:
                self.last_payload = None
                return RestoredContext((), frozenset())
            with os.fdopen(descriptor, "rb") as stream:
                descriptor = None
                payload = stream.read(MAX_STATE_BYTES + 1)
        finally:
            if descriptor is not None:
                os.close(descriptor)
        if len(payload) > MAX_STATE_BYTES or len(payload) != node.st_size:
            self.last_payload = None
            return RestoredContext((), frozenset())
        try:
            document = json.loads(payload, object_pairs_hook=_pairs_without_duplicates)
            restored = _validate_document(document, self.binding, self.hosts)
            self.last_payload = payload
            return restored
        except (UnicodeError, ValueError, TypeError, json.JSONDecodeError,
                RecursionError):
            self.last_payload = None
            return RestoredContext((), frozenset())

    @staticmethod
    def _document(binding, initialized_hosts, rows):
        body = {
            "version": VERSION,
            "binding": binding,
            "initialized_hosts": sorted(initialized_hosts),
            "rows": rows,
        }
        return {
            "body": body,
            "sha256": hashlib.sha256(canonical(body)).hexdigest(),
        }

    def save(self, initialized_hosts, rows):
        if self.directory_fd is None or self.lock_fd is None:
            raise ContextPolicyError("context_not_locked")
        document = self._document(self.binding, initialized_hosts, rows)
        payload = canonical(document) + b"\n"
        if len(payload) > MAX_STATE_BYTES:
            raise ValueError("context_state_capacity")
        # Validate the exact bytes through the same strict reader used at startup.
        checked = json.loads(payload, object_pairs_hook=_pairs_without_duplicates)
        _validate_document(checked, self.binding, self.hosts)
        if payload == self.last_payload:
            return False

        try:
            node = os.stat(self.name, dir_fd=self.directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            node = None
        if node is not None and (
            not stat.S_ISREG(node.st_mode)
            or node.st_uid != os.getuid()
            or node.st_mode & 0o077
        ):
            raise ContextPolicyError("context_file_policy")

        temporary = f".{self.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
        descriptor = None
        try:
            descriptor = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o600,
                dir_fd=self.directory_fd,
            )
            temp_node = os.fstat(descriptor)
            if (
                not stat.S_ISREG(temp_node.st_mode)
                or temp_node.st_uid != os.getuid()
                or temp_node.st_mode & 0o077
            ):
                raise ContextPolicyError("context_temp_policy")
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError(errno.EIO, "short context write")
                view = view[written:]
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = None
            os.replace(
                temporary,
                self.name,
                src_dir_fd=self.directory_fd,
                dst_dir_fd=self.directory_fd,
            )
            os.fsync(self.directory_fd)
            self.last_payload = payload
            return True
        except BaseException:
            if descriptor is not None:
                os.close(descriptor)
            try:
                os.unlink(temporary, dir_fd=self.directory_fd)
            except FileNotFoundError:
                pass
            raise
