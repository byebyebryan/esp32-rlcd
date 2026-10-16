"""Synthetic active/1 frames, with explicit original support; no native I/O."""

import copy

from mesh_fixture import REQUEST, native
from agent_observer.active_contract import SELECTOR, SELECTOR_DIGEST, validate_frame
from agent_observer.mesh_active_profile import ActiveAgentProfile
from mesh_plus.api import Endpoint, Reader
from mesh_plus.evidence import digest
from mesh_plus.transport import boottime_ms


def active(host, rows=8, *, lease_ms=30000):
    full = native(host, rows, lease_ms=lease_ms)
    source = full["sources"][0]
    refs = {c["name"]: {
        "serviceId": full["serviceId"], "provider": source["provider"],
        "namespace": source["namespace"], "contextGeneration": source["contextGeneration"],
        "component": c["name"], **{k: c[k] for k in
            ("accepted", "sampledBoottimeMs", "expiresBoottimeMs")},
    } for c in source["components"]}
    selected = [r for r in full["snapshot"]["sessions"]
                if r["kind"] in {"unknown", "user"} and r["runtime"]["value"] == "running"]
    fields = {name: refs["runtime"] if name in {"runtime", "phase", "kind", "savedIdentity"}
              else None for name in ("runtime", "phase", "kind", "savedIdentity", "activity",
                                     "outcome", "workspace", "lastUpdated", "latestTurn")}
    frame = {k: v for k, v in full.items() if k not in {"serviceProtocol", "snapshot"}}
    frame.update(activeFeedProtocol=1, selector=copy.deepcopy(SELECTOR), selectorDigest=SELECTOR_DIGEST,
                 projection={"sessions": selected, "scopes": [{
                     "provider": source["provider"], "namespace": source["namespace"],
                     "contextGeneration": source["contextGeneration"], "continuity": 1,
                     "coverage": {"status": "complete", "reason": "fixture_complete_census",
                                  "supports": list(refs.values())},
                     "members": [{"identity": copy.deepcopy(r["identity"]),
                                  "fieldSupports": copy.deepcopy(fields)} for r in selected],
                     "uncertain": [], "nonmembers": [],
                 }]})
    validate_frame(frame, expected_host=host)
    return frame


def response(frames=None, *, profile=None, admitted=False):
    profile = ActiveAgentProfile() if profile is None else profile
    frames = {h: active(h) for h in ("starship", "snap")} if frames is None else frames
    endpoints = [Endpoint(h, h == "starship", None if h == "starship" else "sha256:" + "b" * 64,
                          None, profile.bind(h, "agent_active")) for h in frames]
    reader = Reader("agent", endpoints, local_host="starship", profile=profile,
                    catalog_revision="sha256:" + "c" * 64)
    outcomes, now = {}, boottime_ms()
    for endpoint in endpoints:
        frame = frames[endpoint.host]
        state = profile.bind(endpoint.host, "agent_active").inspect_native(frame)
        receipts = [{**{k: v for k, v in r.items() if k != "expiry"},
                     "expiresAtMs": r["expiry"] - (0 if endpoint.local else 100),
                     "remainingMs": r["expiry"] - now} for r in state.receipts]
        proof = None if endpoint.local else {
            "nonce": "b" * 32, "bridgeId": "00000000-0000-0000-0000-000000000009",
            "bridgeClock": state.clock, "bridgeEncodedAtMs": now,
            "sentAtMs": now, "receivedAtMs": now, "marginMs": 100,
            "payloadDigest": digest(frame),
        }
        outcomes[endpoint.host] = ({
            "hostId": endpoint.host, "local": endpoint.local,
            "delivery": {"path": "ipc" if endpoint.local else "ssh", "status": "ready", "epoch": 1,
                         "routeToken": endpoint.route_token, "error": None, "proof": proof},
            "viewState": "current", "owner": state.owner, "receipts": receipts,
        }, list(state.records))
    return (reader.compose_admitted if admitted else reader.compose)(endpoints, outcomes, REQUEST, "watch")
