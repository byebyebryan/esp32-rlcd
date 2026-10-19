#!/usr/bin/env python3
"""Export project media through production C rendering with virtual inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "projects/agent-dashboard"
sys.path.insert(0, str(APP / "host"))
from live_dashboard.projection import Projector, Source, token
from live_dashboard.wire import encode

SAMPLE_MS = 40
FIXTURE = APP / "docs/media/story.json"
NATIVE = ROOT / "tools/native_presentation"
COMMON = [ROOT / "components/display_rlcd/rlcd_frame.c", NATIVE / "render.c"]
DASHBOARD = [APP / f"components/agent_dashboard/{name}" for name in (
    "dashboard_feed.c", "agent_dashboard.c", "agent_dashboard_motion.c",
    "fusion_pixel_12_zh_hans.c",
)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dashboard_commands():
    # This is a generic active-demo story, not a working-set membership fixture.
    sessions = json.loads(FIXTURE.read_text())["sessions"]
    projector = Projector()
    request, sequence = 0, 0
    commands = []
    for elapsed in range(0, 14000, SAMPLE_MS):
        if elapsed % 1000 == 0:
            request += 1
            commands.append(f"REQ {elapsed}\n".encode())
            if not 8000 <= elapsed < 12000:
                sources = []
                for host in ("starship", "snap"):
                    if host == "snap" and 6000 <= elapsed < 12000:
                        sources.append(Source(host, "offline"))
                        continue
                    rows = []
                    for session in sessions:
                        if session["host"] != host:
                            continue
                        phase = session["phase"]
                        if elapsed >= 4000:
                            if session["id"] in {"demo-st-01", "demo-st-04"}:
                                phase = "working"
                            if session["id"] == "demo-sn-01":
                                phase = "blocked"
                        rows.append({
                            "identity": {"hostScope": host, "provider": "codex",
                                         "namespace": "showcase", "nativeIdKind": "thread",
                                         "nativeId": session["id"]},
                            "kind": "user", "title": session["title"], "cwd": "/fictional/demo",
                            "runtime": {"health": "current", "value": "running"},
                            "phase": ({"health": "unsupported", "value": "unknown", "reason": "native_runtime_error"}
                                      if phase == "error" else {"health": "current", "value": phase}),
                            "outcome": {"health": "current", "value": "failed" if phase == "error" else "unknown"},
                            "activity": {"health": "current", "at": 1000000 - session["age_seconds"] * 1000},
                        })
                    sources.append(Source(host, "current", 10000, 1000000 + elapsed,
                                          rows, {token(row["identity"])[0] for row in rows}))
                if elapsed == 12000:
                    sequence = 0
                sequence += 1
                bridge = "1" * 16 if elapsed < 12000 else "2" * 16
                commands.append(encode(projector.project(sources), "0" * 16, request, bridge, sequence))
        commands.append(f"AT {elapsed}\n".encode())
    return b"".join(commands)


def caption(screen, title, detail):
    frame = Image.new("RGB", (400, 344), "#18211c")
    frame.paste(screen, (0, 0))
    draw = ImageDraw.Draw(frame)
    font = ImageFont.load_default(size=12)
    small = ImageFont.load_default(size=10)
    assert draw.textbbox((0, 0), title, font=font)[2] <= 380
    draw.text((10, 306), title, font=font, fill="#eef2ec")
    draw.text((10, 326), detail, font=small, fill="#aab6ab")
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-type", choices=("Debug", "Release"), default="Debug")
    parser.add_argument("--output-root", type=Path, help="write project media under an alternate directory")
    args = parser.parse_args()
    if pillow_version != "12.0.0":
        parser.error("authoring requires Pillow 12.0.0; use the documented uv command")
    build = ROOT / ".cache/presentation" / args.build_type.lower()
    build.mkdir(parents=True, exist_ok=True)
    executable = build / "native-render"
    command = [*shlex.split(os.environ.get("CC", "cc")), "-std=c11", "-g",
               "-O0" if args.build_type == "Debug" else "-O2", "-Wall", "-Wextra", "-Werror"]
    for include in (NATIVE / "stubs", ROOT / "components/display_rlcd/include",
                    APP / "components/agent_dashboard/include"):
        command += ["-I", str(include)]
    subprocess.run([*command, *(str(p) for p in COMMON + DASHBOARD), "-o", str(executable)], check=True)
    source_paths = COMMON + DASHBOARD + [Path(__file__).resolve(), FIXTURE,
        ROOT / "projects/render-bench/main/main.c",
        ROOT / "projects/bringup/main/main.c",
        APP / "host/live_dashboard/projection.py", APP / "host/live_dashboard/wire.py"]
    source_paths += sorted((NATIVE / "stubs").rglob("*.h"))
    source_paths += sorted((ROOT / "components/display_rlcd/include").glob("*.h"))
    source_paths += sorted((APP / "components/agent_dashboard/include").glob("*.h"))
    sources = {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(source_paths))}
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for project, count in (("agent-dashboard", 350), ("render-bench", 160), ("bringup", 1)):
        raw = build / project
        raw.mkdir(exist_ok=True)
        result = subprocess.run([str(executable), project, str(raw)],
                                input=dashboard_commands() if project == "agent-dashboard" else b"",
                                capture_output=True, check=True)
        if project == "agent-dashboard":
            trace = [tuple(map(int, line.split(","))) for line in result.stdout.decode().splitlines()]
            assert len(trace) == count
            assert any(health == 0 and partial == 1 for _, health, partial, _ in trace)
            assert any(health == 2 for _, health, _, _ in trace)
            assert trace[-1][1:] == (0, 0, 7)
        output = (args.output_root.resolve() / project if args.output_root
                  else ROOT / f"projects/{project}/docs/media")
        output.mkdir(parents=True, exist_ok=True)
        frames, screens = [], []
        for index in range(count):
            with Image.open(raw / f"frame-{index:03d}.pbm") as image:
                screen = image.convert("RGB")
            assert screen.size == (400, 300)
            screens.append(screen)
            if project == "agent-dashboard":
                elapsed = index * SAMPLE_MS
                title = ("Blocked and failed conversations" if elapsed < 4000 else
                         "Recovery: rows reorder" if elapsed < 6000 else
                         "One host offline: retained uncertainty" if elapsed < 10000 else
                         "Feed expired: work claims cleared" if elapsed < 12000 else
                         "Fresh feed: current observations recover")
                detail = "Native C render / Fictional data / Virtual time"
            else:
                title = "Cached ball and bar scene" if project == "render-bench" else "Panel orientation and packing pattern"
                detail = "Native C render / Virtual time / Not measured panel FPS"
            frames.append(caption(screen, title, detail))
        poster = "dashboard.png" if project == "agent-dashboard" else "benchmark.png" if project == "render-bench" else "bringup.png"
        poster_index = 25 if project == "agent-dashboard" else 0
        screens[poster_index].save(output / poster, optimize=True)
        assets = [poster]
        if count > 1:
            palette = frames[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
            indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
            animation = "dashboard-demo.gif" if project == "agent-dashboard" else "benchmark-demo.gif"
            indexed[0].save(output / animation, save_all=True, append_images=indexed[1:],
                            duration=SAMPLE_MS, loop=0, optimize=True, disposal=1)
            assets.append(animation)
            with Image.open(output / animation) as image:
                duration = 0
                for frame in range(image.n_frames):
                    image.seek(frame)
                    duration += image.info["duration"]
                assert duration == count * SAMPLE_MS
        manifest = {
            "description": {
                "agent-dashboard": "Fictional active-demo records through production projection, wire 3 admission and C motion/rendering; virtual time.",
                "render-bench": "Unchanged benchmark draw_animation scene compiled with native board stubs; virtual time.",
                "bringup": "Native initial rlcd_frame_draw_test pattern used by bring-up; no hardware access.",
            }[project],
            "source_revision": revision, "source_sha256": sources,
            "native_executable_sha256": digest(executable), "pillow_version": pillow_version,
            "screen_size": [400, 300], "animation_size": [400, 344] if count > 1 else None,
            "timing": "virtual samples; playback does not measure panel scan rate or physical contrast",
            "frames_sampled": count, "sample_ms": SAMPLE_MS if count > 1 else None,
            "duration_ms": count * SAMPLE_MS if count > 1 else None,
            "distinct_screens": len({hashlib.sha256(image.tobytes()).hexdigest() for image in screens}),
            "files": {name: {"sha256": digest(output / name), "bytes": (output / name).stat().st_size}
                      for name in assets},
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"{project}: {len(assets)} assets, {sum((output / name).stat().st_size for name in assets):,} bytes")


if __name__ == "__main__":
    main()
