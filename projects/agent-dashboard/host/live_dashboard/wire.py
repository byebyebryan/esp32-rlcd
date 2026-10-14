"""Device wire 1: bounded tagged ASCII, UTF-8 hex fields and CRC32."""

import binascii
import re

from .projection import WORK

MAX_BYTES = 16384
REQUEST = re.compile(rb"RLCD\?1 ([0-9a-f]{16}) ([1-9][0-9]{0,9})\Z")


def parse_request(line):
    match = REQUEST.fullmatch(line.rstrip(b"\r\n"))
    if match is None:
        return None
    request = int(match[2])
    return (match[1].decode(), request) if request <= 0xFFFFFFFF else None


def encode(view, boot, request, bridge, sequence):
    fields = [
        "RLCD!1",
        boot,
        str(request),
        bridge,
        str(sequence),
        str(len(view["hosts"])),
        str(len(view["rows"])),
    ]
    for host in view["hosts"]:
        fields.extend(
            [
                host["alias"].encode().hex(),
                str(host["status"]),
                str(host["valid_ms"]),
                *(str(n) for n in host["totals"]),
                str(host["total"]),
            ]
        )
    for row in view["rows"]:
        fields.extend(
            [
                row["id"],
                str(row["host"]),
                str(WORK[row["state"]]),
                str(row["health"]),
                str(row["valid_ms"]),
                row["label"].encode().hex(),
                row["age"],
            ]
        )
    payload = "\t".join(fields).encode("ascii")
    result = payload + f"\t{binascii.crc32(payload):08x}\n".encode()
    if len(result) > MAX_BYTES:
        raise ValueError("device_frame_capacity")
    return result
