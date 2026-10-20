#!/usr/bin/env python3
"""Freeze and verify the small host runtime without native/provider actions."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

INPUTS = (
    "scripts/live-dashboard.py",
    "scripts/dashboard-bundle.py",
    "host/live_dashboard/__init__.py",
    "host/live_dashboard/mesh.py",
    "host/live_dashboard/profiles.py",
    "host/live_dashboard/projection.py",
    "host/live_dashboard/runtime.py",
    "host/live_dashboard/serial.py",
    "host/live_dashboard/wire.py",
    "components/agent_dashboard/fusion_pixel_12_zh_hans.c",
)
EXPECTED = {
    "observer": "0.7.0a7",
    "mesh": "0.1.0a23",
    "profile": "agent-observer.mesh-working-set.v1",
    "nativeVersion": 1,
    "sdk": 1,
    "api": 4,
    "service": 4,
    "preparation": 1,
    "admission": 1,
    "selection": 1,
    "read": 2,
    "workingSetRead": 1,
    "memberLease": 1,
    "scopeLease": 1,
    "windowMs": 259200000,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def probe(python):
    code = """import json,importlib.metadata as m
from agent_observer.mesh_working_set_profile import WorkingSetAgentProfile
from agent_observer.mesh_working_set_read import WORKING_SET_READ_INTERFACE_VERSION, WORKING_SET_MEMBER_LEASE_INTERFACE_VERSION, WORKING_SET_SCOPE_LEASE_INTERFACE_VERSION
from agent_observer.working_set_policy import DEFAULT_WINDOW_MS
from agent_observer.service_public import SERVICE_PROTOCOL
from agent_observer.mesh_read import READ_INTERFACE_VERSION
from mesh_plus.api import PREPARATION_INTERFACE_VERSION, ADMISSION_INTERFACE_VERSION, SELECTION_INTERFACE_VERSION
from urllib.parse import unquote,urlsplit
import re
def wheel_sha(name):
 d=m.distribution(name)
 raw=d.read_text("direct_url.json")
 if raw is None: raise ValueError("wheel_origin_missing")
 value=json.loads(raw)
 if value.get("dir_info",{}).get("editable") is True: raise ValueError("editable_install")
 url=value.get("url")
 if not isinstance(url,str) or not unquote(urlsplit(url).path).lower().endswith(".whl"):
  raise ValueError("wheel_origin_invalid")
 sha=value.get("archive_info",{}).get("hashes",{}).get("sha256")
 if not isinstance(sha,str) or re.fullmatch(r"[0-9a-f]{64}",sha) is None:
  raise ValueError("wheel_hash_missing")
 return sha
p=WorkingSetAgentProfile()
print(json.dumps({"dependencies":{"observer":m.version("agent-observer"),"mesh":m.version("mesh-plus"),
"profile":p.descriptor.profile_id,"nativeVersion":p.descriptor.native_version,"sdk":p.descriptor.sdk_version,"service":SERVICE_PROTOCOL,
"preparation":PREPARATION_INTERFACE_VERSION,"admission":ADMISSION_INTERFACE_VERSION,
"selection":SELECTION_INTERFACE_VERSION,"read":READ_INTERFACE_VERSION,
"workingSetRead":WORKING_SET_READ_INTERFACE_VERSION,"memberLease":WORKING_SET_MEMBER_LEASE_INTERFACE_VERSION,
"scopeLease":WORKING_SET_SCOPE_LEASE_INTERFACE_VERSION,
"windowMs":DEFAULT_WINDOW_MS},"artifacts":{"observerWheelSha256":wheel_sha("agent-observer"),
"meshWheelSha256":wheel_sha("mesh-plus")}}))
"""
    result = subprocess.run(
        [str(python), "-I", "-B", "-c", code],
        capture_output=True,
        timeout=10,
        check=True,
    )
    observed = json.loads(result.stdout)
    cli = Path(python).parent / "agent-observer"
    api = subprocess.run([str(cli), "api"], capture_output=True, timeout=10, check=True)
    observed["dependencies"]["api"] = json.loads(api.stdout)["apiVersion"]
    if observed["dependencies"] != EXPECTED:
        raise ValueError("dependency_tuple_mismatch")
    return observed


def freeze(source, output, python, revision, *, source_dirty=False):
    observed = probe(python)
    files = {name: digest((source / name).read_bytes()) for name in INPUTS}
    manifest = {
        "manifestVersion": 1,
        "sourceRevision": revision,
        "sourceDirty": source_dirty,
        "deviceWire": 4,
        "python": str(python),
        "dependencies": observed["dependencies"],
        "artifacts": observed["artifacts"],
        "files": files,
    }
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    checksum = digest(payload)
    target = output / checksum[:16]
    if target.exists():
        verify(target, checksum, dependencies=False)
        return target, checksum
    target.mkdir(parents=True)
    try:
        for name in INPUTS:
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)
            destination.chmod(0o444)
        (target / "manifest.json").write_bytes(payload)
        (target / "manifest.json").chmod(0o444)
        verify(target, checksum, dependencies=False)
        for directory in sorted(
            (p for p in target.rglob("*") if p.is_dir()), reverse=True
        ):
            directory.chmod(0o555)
        target.chmod(0o555)
    except BaseException:
        for path in target.rglob("*"):
            if path.is_dir():
                path.chmod(0o755)
        target.chmod(0o755)
        shutil.rmtree(target)
        raise
    return target, checksum


def verify(bundle, checksum=None, *, dependencies=True):
    if bundle.is_symlink() or (bundle / "manifest.json").is_symlink():
        raise ValueError("bundle_symlink")
    payload = (bundle / "manifest.json").read_bytes()
    if checksum is not None and digest(payload) != checksum:
        raise ValueError("bundle_manifest_mismatch")
    manifest = json.loads(payload)
    if (
        manifest["manifestVersion"] != 1
        or manifest.get("deviceWire") != 4
        or manifest["dependencies"] != EXPECTED
        or not _valid_artifacts(manifest.get("artifacts"))
        or set(manifest["files"]) != set(INPUTS)
    ):
        raise ValueError("bundle_manifest_invalid")
    actual = set()
    for path in bundle.rglob("*"):
        if path.is_symlink():
            raise ValueError("bundle_symlink")
        if path.is_file():
            actual.add(str(path.relative_to(bundle)))
    if actual != set(INPUTS) | {"manifest.json"}:
        raise ValueError("bundle_files_mismatch")
    for name, file_checksum in manifest["files"].items():
        if digest((bundle / name).read_bytes()) != file_checksum:
            raise ValueError("bundle_file_mismatch")
    if dependencies:
        observed = probe(manifest["python"])
        if (
            observed["dependencies"] != manifest["dependencies"]
            or observed["artifacts"] != manifest["artifacts"]
        ):
            raise ValueError("dependency_artifact_mismatch")
    return manifest


def _valid_artifacts(value):
    return (
        isinstance(value, dict)
        and set(value) == {"observerWheelSha256", "meshWheelSha256"}
        and all(
            isinstance(value[name], str)
            and len(value[name]) == 64
            and all(character in "0123456789abcdef" for character in value[name])
            for name in ("observerWheelSha256", "meshWheelSha256")
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_subparsers(dest="command", required=True)
    build = command.add_parser("build")
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--python", type=Path, required=True)
    check = command.add_parser("verify")
    check.add_argument("--bundle", type=Path, required=True)
    check.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    if args.command == "build":
        source = Path(__file__).resolve().parents[1]
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--", *INPUTS], cwd=source, text=True
            )
        )
        target, checksum = freeze(
            source, args.output, args.python, revision, source_dirty=dirty
        )
        print(
            json.dumps(
                {
                    "bundle": str(target),
                    "manifestSha256": checksum,
                    "sourceRevision": revision,
                    "sourceDirty": dirty,
                }
            )
        )
    else:
        verify(args.bundle, args.manifest_sha256)
        print(json.dumps({"status": "verified", "bundle": str(args.bundle)}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - do not expose dependency exception payloads
        print(
            "dashboard bundle unavailable: verify inputs and dependency tuple",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
