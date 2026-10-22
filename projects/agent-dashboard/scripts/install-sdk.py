#!/usr/bin/env python3
"""Install the hash-locked public Observer/Mesh SDK wheels into this Python."""

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen


APP_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = APP_ROOT / "sdk-release-lock.json"
MAX_WHEEL_BYTES = 32 * 1024 * 1024


def _entry(filename, url, sha256, allowed_host):
    parsed = urlsplit(url)
    if (
        not isinstance(filename, str)
        or Path(filename).name != filename
        or not filename.endswith(".whl")
        or parsed.scheme != "https"
        or parsed.hostname != allowed_host
        or not parsed.path.endswith("/" + filename)
        or not isinstance(sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", sha256) is None
    ):
        raise ValueError("invalid locked wheel entry")
    return {"filename": filename, "url": url, "sha256": sha256}


def selected_wheels(lock, version):
    if sys.implementation.name.lower() != lock["python"]["implementation"].lower():
        raise ValueError("the SDK lock qualifies CPython only")
    if version not in lock["python"]["qualified"]:
        raise ValueError(f"Python {version} is not qualified by this SDK lock")
    if platform.system() != "Linux" or platform.machine().lower() not in {"x86_64", "amd64"}:
        raise ValueError("the SDK lock qualifies Linux x86_64 only")

    selected = []
    release_hosts = {
        "agent-observer": "github.com",
        "mesh-plus": "github.com",
    }
    for release in lock["releases"]:
        distribution = release["distribution"]
        selected.append(
            _entry(**release["wheel"], allowed_host=release_hosts[distribution])
        )

    for dependency in lock["dependencies"]:
        marker = dependency.get("marker")
        if marker is not None:
            if marker != "python_version < '3.13'":
                raise ValueError(f"unsupported dependency marker: {marker}")
            if sys.version_info >= (3, 13):
                continue
        wheels = dependency["wheels"]
        wheel = wheels.get(version, wheels.get("any"))
        if wheel is None:
            raise ValueError(
                f"no locked wheel for {dependency['distribution']} on Python {version}"
            )
        selected.append(_entry(**wheel, allowed_host="files.pythonhosted.org"))
    return selected


def download(entry, wheelhouse):
    target = wheelhouse / entry["filename"]
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == entry["sha256"]:
        return target
    target.unlink(missing_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    partial.unlink(missing_ok=True)
    digest = hashlib.sha256()
    size = 0
    try:
        with urlopen(entry["url"], timeout=60) as response, partial.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_WHEEL_BYTES:
                    raise ValueError(f"locked wheel exceeds size limit: {entry['filename']}")
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {entry['filename']}")
        partial.replace(target)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wheelhouse",
        type=Path,
        help="reuse or populate this verified wheel directory (defaults to a temporary one)",
    )
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text())
    if lock.get("lockVersion") != 1:
        raise ValueError("unsupported SDK lock version")
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    entries = selected_wheels(lock, version)

    if args.wheelhouse is None:
        with tempfile.TemporaryDirectory(prefix="rlcd-sdk-wheelhouse-") as temporary:
            wheelhouse = Path(temporary)
            wheels = [download(entry, wheelhouse) for entry in entries]
            _install(wheels)
    else:
        args.wheelhouse.mkdir(parents=True, exist_ok=True)
        wheelhouse = args.wheelhouse.resolve()
        wheels = [download(entry, wheelhouse) for entry in entries]
        _install(wheels)
    _verify_install()
    print(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "wheels": [
                    {"filename": entry["filename"], "sha256": entry["sha256"]}
                    for entry in entries
                ],
                "status": "installed",
            },
            sort_keys=True,
        )
    )


def _install(wheels):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-index",
            "--no-deps",
            *map(str, wheels),
        ],
        check=True,
    )


def _verify_install():
    subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    verifier = APP_ROOT / "scripts" / "verify-sdk.py"
    subprocess.run([sys.executable, str(verifier)], check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - keep install failures explicit
        print(f"SDK install failed: {error}", file=sys.stderr)
        raise SystemExit(1) from None
