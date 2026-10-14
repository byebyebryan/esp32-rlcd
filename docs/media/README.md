# Project gallery media

The gallery uses the production packed framebuffer, dashboard feed/renderer and
benchmark drawing code. A native exporter replaces board calls; it never calls
firmware `app_main`, opens USB or reads provider sessions. Dashboard records are
fictional, and animation time is virtual.

| Project | Media and source |
| --- | --- |
| Agent dashboard | [Roster, row motion, source loss and recovery](../../projects/agent-dashboard/docs/media/README.md) |
| Render bench | [Ball/bar scene and animation](../../projects/render-bench/docs/media/README.md) |
| Bring-up | [Orientation and pixel-packing pattern](../../projects/bringup/docs/media/README.md) |

Static PNGs preserve the exact 400 × 300 screen area. GIFs add a 44-pixel caption
band outside that area to identify the native source and virtual inputs.
Playback does not measure panel scan rate, physical contrast or viewing distance.
Recorded hardware results remain in each project's acceptance/findings links.

## Regenerate

From the repository root, with a host C compiler and uv:

```sh
uv run --no-project --with pillow==12.0.0 python scripts/render-presentation.py
python3 scripts/check-docs.py
```

No ESP-IDF installation is needed for media authoring. Compilation uses native
stubs for board/RTOS calls and the same C drawing functions as firmware. Raw PBMs
and native executables stay under ignored `.cache/presentation/` output.

For an independent optimized export:

```sh
uv run --no-project --with pillow==12.0.0 python scripts/render-presentation.py \
    --build-type Release --output-root .cache/presentation/release-media
```

The three project output directories contain matching PNG/GIF bytes in Debug and
Release modes. [CI](../../.github/workflows/checks.yml) reproduces and compares
them. Each manifest records input/output hashes, native binary identity, Pillow
version, dimensions and staged timing. `source_revision` is the base checkout;
individual source hashes cover authoring changes made before the media commit.

Pillow supplies the caption font. The dashboard uses its existing
[Fusion Pixel source and notices](../../projects/agent-dashboard/components/agent_dashboard/assets/fonts/fusion-pixel-font-2026.09.25/PROVENANCE.md).
Bring-up and benchmark text use the shared component's hand-authored bitmap
glyphs. Application pixels remain unchanged by the caption band.

For future photographs/video, identify the board revision, application, firmware
build and capture date. Keep raw footage outside Git and publish selected,
compressed material with its physical acceptance record.
