"""Synthetic current Observer working-set owners composed through public Mesh APIs."""

import copy
import json
import os
import time
import uuid
from pathlib import Path


APP = Path(__file__).resolve().parents[1]
FIXTURE = APP / "tests/fixtures/service-v4/view.json"
REQUEST = "a" * 32
WINDOW_MS = 72 * 60 * 60 * 1000


def sample(host, rows=3, *, home=None, activity_offset_ms=-5000, row_specs=None):
    """Build a valid current-v4 Codex source snapshot for public ServiceState admission."""
    from agent_observer.contract import store_namespace

    uid = os.geteuid()
    home = f"/fixture/{host}-codex-working-set" if home is None else str(home)
    namespace = store_namespace("codex", home, "explicit", uid)
    wall = time.time_ns() // 1_000_000
    envelope = json.loads(FIXTURE.read_text(encoding="utf-8"))
    value = copy.deepcopy(envelope["snapshot"])
    templates = [row for row in value["sessions"] if row["identity"]["provider"] == "codex"]
    templates = [row for row in templates if row["kind"] in {"unknown", "user"}]
    value["sources"] = [source for source in value["sources"] if source["provider"] == "codex"]
    value["sessions"] = []
    value["collectionId"] = str(uuid.uuid4())
    value["collectedAt"] = wall
    value["sourceHealth"] = "current"
    value["host"].update(authority=host, uid=uid)

    source = value["sources"][0]
    source.update(configHome=home, configHomeKind="explicit", namespace=namespace)
    source["capabilities"]["activity"] = True

    for index in range(rows):
        spec = {} if row_specs is None else dict(row_specs[index])
        row = copy.deepcopy(templates[index % len(templates)])
        identifier = str(uuid.UUID(int=index + 1))
        row["identity"].update(hostScope=host, namespace=namespace, nativeId=identifier)
        row["nativeIds"].update(threadId=identifier, sessionTreeRootId=identifier)
        row["title"] = f"Fixture {index}"

        runtime = spec.get("runtime", "running")
        kind = spec.get("kind", "user")
        row["kind"] = kind
        row["hasSavedHistory"] = True
        row["runtime"].update(
            value=runtime,
            observedAt=wall,
            source="codex_rpc",
            health="current",
            reason="native_timestamp",
            clock="sample",
        )
        if runtime == "parked":
            row["inventory"] = "saved"
            row["phase"] = None
            row["blockedReasons"] = []
        else:
            phase_value = spec.get("phase", row["phase"]["value"])
            row["phase"].update(
                value=phase_value,
                observedAt=wall,
                source="codex_rpc",
                health="current",
                reason="native_timestamp",
                clock="sample",
            )
            if phase_value == "blocked":
                row["blockedReasons"] = ["approval"]
            else:
                row["blockedReasons"] = []

        activity_offset = spec.get("activity_offset_ms", activity_offset_ms)
        if activity_offset is None:
            row["activity"].update(
                at=None,
                source=None,
                health="unsupported",
                reason="activity_source_unproved",
            )
        else:
            row["activity"].update(
                at=wall + activity_offset,
                source="codex_rpc",
                health="current",
                reason="native_timestamp",
            )
        value["sessions"].append(row)

    return value


def new_state(host, rows=3, *, home=None, activity_offset_ms=-5000,
              row_specs=None, history_ttl_ms=30000, runtime_ttl_ms=30000,
              split_activity=False):
    """Seed a public Observer service owner through its accepted history API."""
    from agent_observer.service_state import ServiceState

    home = f"/fixture/{host}-codex-working-set" if home is None else str(home)
    value = sample(
        host,
        rows,
        home=home,
        activity_offset_ms=activity_offset_ms,
        row_specs=row_specs,
    )
    state = ServiceState(
        host_scope=host,
        configs={"codex": (home, "explicit")},
        uid=os.geteuid(),
        working_set_window_ms=WINDOW_MS,
    )
    accept(state, value, history_ttl_ms=history_ttl_ms, runtime_ttl_ms=runtime_ttl_ms)
    if split_activity:
        runtime_value = sample(
            host,
            rows,
            home=home,
            activity_offset_ms=None,
            row_specs=row_specs,
        )
        accept_runtime(state, runtime_value, ttl_ms=runtime_ttl_ms)
    return state


def accept(state, value, *, history_ttl_ms=30000, runtime_ttl_ms=30000):
    sampled = state.clock()
    state.attempt("codex", "history")
    if not state.accept(
        "codex",
        "history",
        value,
        sampled_ms=sampled - 100,
        ttl_ms=history_ttl_ms,
        runtime_ttl_ms=runtime_ttl_ms,
        accepted_boottime_ms=sampled,
    ):
        raise AssertionError("fixture_acceptance_required")
    return state


def accept_runtime(state, value, *, ttl_ms=30000):
    sampled = state.clock()
    state.attempt("codex", "runtime")
    if not state.accept(
        "codex",
        "runtime",
        value,
        sampled_ms=sampled - 100,
        ttl_ms=ttl_ms,
        accepted_boottime_ms=sampled,
    ):
        raise AssertionError("fixture_runtime_acceptance_required")
    return state


def native(state, *, sequence=1, full=False):
    """Return one valid Observer service frame using its public frame API."""
    return (
        state.frame("view", sequence)
        if full
        else state.working_set_frame("view", sequence)
    )


def response(frames, *, profile, source="agent_working_set", admitted=True,
             request_id=REQUEST):
    """Compose public Observer frames with Mesh; admission remains the caller's guard."""
    from mesh_plus.api import Endpoint, Reader
    from mesh_plus.evidence import digest
    from mesh_plus.transport import boottime_ms

    endpoints = [
        Endpoint(
            host,
            host == "starship",
            None if host == "starship" else "sha256:" + "b" * 64,
            None,
            profile.bind(host, source),
        )
        for host in frames
    ]
    reader = Reader(
        "agent",
        endpoints,
        local_host="starship",
        profile=profile,
        catalog_revision="sha256:" + "c" * 64,
    )
    encoded_at = boottime_ms()
    outcomes = {}
    for endpoint in endpoints:
        frame = frames[endpoint.host]
        state = profile.bind(endpoint.host, source).inspect_native(frame)
        receipts = [
            {
                **{key: value for key, value in receipt.items() if key != "expiry"},
                "expiresAtMs": receipt["expiry"] - (0 if endpoint.local else 100),
                "remainingMs": receipt["expiry"] - encoded_at,
            }
            for receipt in state.receipts
        ]
        proof = None if endpoint.local else {
            "nonce": "b" * 32,
            "bridgeId": "00000000-0000-0000-0000-000000000009",
            "bridgeClock": state.clock,
            "bridgeEncodedAtMs": encoded_at,
            "sentAtMs": encoded_at,
            "receivedAtMs": encoded_at,
            "marginMs": 100,
            "payloadDigest": digest(frame),
        }
        outcomes[endpoint.host] = (
            {
                "hostId": endpoint.host,
                "local": endpoint.local,
                "delivery": {
                    "path": "ipc" if endpoint.local else "ssh",
                    "status": "ready",
                    "epoch": 1,
                    "routeToken": endpoint.route_token,
                    "error": None,
                    "proof": proof,
                },
                "viewState": "current",
                "owner": state.owner,
                "receipts": receipts,
            },
            list(state.records),
        )
    compose = reader.compose_admitted if admitted else reader.compose
    return compose(endpoints, outcomes, request_id, "watch")


def control(frame, kind, sequence):
    mesh = frame["mesh"]
    return {
        "protocol": frame["protocol"],
        "schemaVersion": 1,
        "mesh": {
            **{key: mesh[key] for key in ("meshProtocol", "requestId", "operation", "access")},
            "kind": kind,
            "reader": {**mesh["reader"], "sequence": sequence},
        },
    }
