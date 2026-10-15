"""Client-owned synthetic Service 4/Agent v3 data; no provider or service I/O.

The Codex-only template derives from Observer 6542b92's public wire fixture.
Provider versions in it are fictional diagnostics, not support allowlists.
"""

import copy
import json
import os
import uuid
from pathlib import Path

from agent_observer.mesh_profile import AgentProfile
from agent_observer.public import store_namespace
from mesh_plus.api import Endpoint, Reader
from mesh_plus.evidence import clock_domain, digest
from mesh_plus.transport import boottime_ms

REQUEST = "a" * 32


def native(host, rows=8, *, lease_ms=30000):
    value = json.loads((Path(__file__).parent / "fixtures/service4-codex.json").read_text())
    now, clock = boottime_ms(), clock_domain()
    value.update(hostScope=host, uid=os.getuid(), bootId=clock["bootId"],
                 clockDomain=os.readlink("/proc/self/ns/time"), emittedBoottimeMs=now - 100)
    source = value["sources"][0]
    namespace = store_namespace("codex", source["configHome"], source["configHomeKind"], os.getuid())
    source["namespace"] = namespace
    for receipt in source["components"]:
        receipt.update(sampledBoottimeMs=now - 100, expiresBoottimeMs=now + lease_ms)
    snapshot = value["snapshot"]
    snapshot["host"].update(authority=host, uid=os.getuid())
    snapshot["sources"][0]["namespace"] = namespace
    snapshot["sources"][0]["runtime"]["bootId"] = clock["bootId"]
    snapshot["sources"][0]["capabilities"]["runtime"].append("parked")
    templates = snapshot["sessions"]
    snapshot["sessions"] = []
    for index in range(rows):
        row = copy.deepcopy(templates[index % len(templates)])
        identifier = str(uuid.UUID(int=index + 1))
        row["identity"].update(hostScope=host, namespace=namespace, nativeId=identifier)
        row["nativeIds"] = {"threadId": identifier, "sessionTreeRootId": identifier}
        row.update(title="Fixture " + str(index), kind="user", hasSavedHistory=True)
        if index == 2:
            row["kind"] = "child"
        elif index == 3:
            row["kind"] = "system"
        elif index == 4:
            row["kind"] = "unknown"
        elif index >= 5:
            row.update(inventory="saved", phase=None, blockedReasons=[])
            row["runtime"]["value"] = "parked"
        snapshot["sessions"].append(row)
    AgentProfile().bind(host, "agent").inspect_native(value)
    return value


def response(*, rows=8, partial=False, unavailable=None, lease_ms=30000):
    profile, now = AgentProfile(), boottime_ms()
    endpoints = [Endpoint(host, host == "starship", None if host == "starship" else
                          "sha256:" + "b" * 64, None, profile.bind(host, "agent"))
                 for host in ("starship", "snap")]
    reader = Reader("agent", endpoints, local_host="starship",
                    catalog_revision="sha256:" + "c" * 64, profile=profile)
    outcomes = {}
    for endpoint in endpoints:
        if endpoint.host == unavailable:
            outcomes[endpoint.host] = (reader.unavailable(endpoint), [])
            continue
        frame = native(endpoint.host, rows, lease_ms=lease_ms)
        if partial and endpoint.host == "snap":
            frame["snapshot"]["sourceHealth"] = "partial"
            frame["snapshot"]["sources"][0]["sourceHealth"] = "partial"
            frame["snapshot"]["sources"][0]["coverage"]["runtime"].update(
                status="partial", reason="catalog_limit")
        state = profile.bind(endpoint.host, "agent").inspect_native(frame)
        receipts = [{**{k: v for k, v in receipt.items() if k != "expiry"},
                     "expiresAtMs": receipt["expiry"] - (0 if endpoint.local else 100),
                     "remainingMs": receipt["expiry"] - now} for receipt in state.receipts]
        proof = None if endpoint.local else {
            "nonce": "b" * 32, "bridgeId": "00000000-0000-0000-0000-000000000009",
            "bridgeClock": state.clock, "bridgeEncodedAtMs": now,
            "sentAtMs": now, "receivedAtMs": now, "marginMs": 100,
            "payloadDigest": digest(frame),
        }
        host = {"hostId": endpoint.host, "local": endpoint.local,
                "delivery": {"path": "ipc" if endpoint.local else "ssh", "status": "ready",
                             "epoch": 1, "routeToken": endpoint.route_token, "error": None,
                             "proof": proof}, "viewState": "current", "owner": state.owner,
                "receipts": receipts}
        outcomes[endpoint.host] = host, list(state.records)
    return reader.compose(endpoints, outcomes, REQUEST, "watch")


def control(frame, kind, sequence):
    mesh = frame["mesh"]
    return {"protocol": frame["protocol"], "schemaVersion": 1, "mesh": {
        **{k: mesh[k] for k in ("meshProtocol", "requestId", "operation", "access")},
        "kind": kind, "reader": {**mesh["reader"], "sequence": sequence}}}
