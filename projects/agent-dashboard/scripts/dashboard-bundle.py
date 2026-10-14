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
    "host/live_dashboard/projection.py",
    "host/live_dashboard/runtime.py",
    "host/live_dashboard/serial.py",
    "host/live_dashboard/wire.py",
    "components/agent_dashboard/fusion_pixel_12_zh_hans.c",
)
EXPECTED = {
    "observer": "0.7.0a1",
    "mesh": "0.1.0a17",
    "profile": "agent-observer.mesh-candidate.v3",
    "nativeVersion": 6,
    "sdk": 1,
    "api": 4,
    "service": 4,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def probe(python):
    code = """import json,importlib.metadata as m
from agent_observer.mesh_profile import AgentProfile
from agent_observer.service_public import SERVICE_PROTOCOL
p=AgentProfile().descriptor
print(json.dumps({"observer":m.version("agent-observer"),"mesh":m.version("mesh-plus"),
"profile":p.profile_id,"nativeVersion":p.native_version,"sdk":p.sdk_version,"service":SERVICE_PROTOCOL}))
"""
    result = subprocess.run(
        [str(python), "-I", "-B", "-c", code],
        capture_output=True,
        timeout=10,
        check=True,
    )
    value = json.loads(result.stdout)
    cli = Path(python).parent / "agent-observer"
    api = subprocess.run([str(cli), "api"], capture_output=True, timeout=10, check=True)
    value["api"] = json.loads(api.stdout)["apiVersion"]
    if value != EXPECTED:
        raise ValueError("dependency_tuple_mismatch")
    return value


def freeze(source, output, python, revision, *, source_dirty=False):
    files = {name: digest((source / name).read_bytes()) for name in INPUTS}
    manifest = {
        "manifestVersion": 1,
        "sourceRevision": revision,
        "sourceDirty": source_dirty,
        "deviceWire": 2,
        "python": str(python),
        "dependencies": EXPECTED,
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
        or manifest.get("deviceWire") != 2
        or manifest["dependencies"] != EXPECTED
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
        probe(manifest["python"])
    return manifest


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
        probe(args.python)
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
