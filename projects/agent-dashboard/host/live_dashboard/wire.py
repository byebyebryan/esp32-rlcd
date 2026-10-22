"""Device wire 6: numeric activity age, opaque event key and CRC32."""

import binascii
import re

from .projection import CATEGORY, MAX_AGE_MS, WORK

MAX_BYTES = 16384
REQUEST = re.compile(rb"RLCD\?6 ([0-9a-f]{16}) ([1-9][0-9]{0,9})\Z")


def parse_request(line):
    match = REQUEST.fullmatch(line.rstrip(b"\r\n"))
    if match is None:
        return None
    request = int(match[2])
    return (match[1].decode(), request) if request <= 0xFFFFFFFF else None


def encode(view, boot, request, bridge, sequence):
    fields = [
        "RLCD!6",
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
        age_ms, age_key = row.get("age_ms"), row.get("age_key")
        if age_ms is None:
            if age_key is not None:
                raise ValueError("device_row_age")
        elif (type(age_ms) is not int or not 0 <= age_ms <= MAX_AGE_MS
              or row["health"] != 0 or row["valid_ms"] <= 0
              or not isinstance(age_key, str)
              or re.fullmatch(r"[0-9a-f]{64}", age_key) is None):
            raise ValueError("device_row_age")
        host_alias = view["hosts"][row["host"]]["alias"]
        badge = row.get("badge", host_alias)
        if badge != host_alias and not (host_alias == "SN" and badge == "SW"):
            raise ValueError("device_row_badge")
        fields.extend(
            [
                row["id"],
                str(row["host"]),
                badge.encode().hex(),
                str(CATEGORY[row["category"]]),
                str(WORK[row["state"]]),
                str(row["health"]),
                str(row["valid_ms"]),
                row["label"].encode().hex(),
                str(age_ms) if age_ms is not None else "?",
                age_key if age_ms is not None else "?",
            ]
        )
    payload = "\t".join(fields).encode("ascii")
    result = payload + f"\t{binascii.crc32(payload):08x}\n".encode()
    if len(result) > MAX_BYTES:
        raise ValueError("device_frame_capacity")
    return result
