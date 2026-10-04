#!/usr/bin/env python3
"""Convert the study's exact-size PBMs to PNG and a local comparison page."""

import html
from pathlib import Path
import struct
import sys
import zlib


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def png_from_pbm(path: Path) -> Path:
    with path.open("rb") as source:
        if source.readline() != b"P4\n" or source.readline() != b"400 300\n":
            raise ValueError(f"Unexpected preview format: {path}")
        pixels = source.read()
    if len(pixels) != 15000:
        raise ValueError(f"Unexpected preview size: {path}")
    # PBM uses 1=black; PNG grayscale uses 1=white.
    pixels = bytes(value ^ 255 for value in pixels)
    scanlines = b"".join(b"\0" + pixels[row * 50:(row + 1) * 50] for row in range(300))
    ihdr = struct.pack(">IIBBBBB", 400, 300, 1, 0, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(scanlines)) + chunk(b"IEND", b"")
    destination = path.with_suffix(".png")
    destination.write_bytes(png)
    return destination


def main() -> None:
    directory = Path(sys.argv[1])
    previews = [png_from_pbm(path) for path in sorted(directory.glob("*.pbm"))]
    figures = "\n".join(
        f'<figure><figcaption>{html.escape(path.stem)}</figcaption>'
        f'<img src="{html.escape(path.name)}" width="400" height="300" '
        f'alt="Synthetic {html.escape(path.stem)} dashboard"></figure>'
        for path in previews
    )
    page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>RLCD roster study</title>
<style>
body { font-family: system-ui, sans-serif; margin: 24px; }
main { display: flex; flex-wrap: wrap; gap: 24px; }
figure { margin: 0; } figcaption { margin-bottom: 8px; }
img { display: block; image-rendering: pixelated; max-width: 100%; height: auto; }
</style>
<h1>RLCD roster study</h1><p>Invented data, exact 400 × 300 monochrome frames.
Native previews do not establish physical contrast or desk-distance readability;
the recorded on-board checks are in the UI study notes.</p><main>
""" + figures + "\n</main></html>\n"
    (directory / "index.html").write_text(page, encoding="utf-8")
    print(f"Preview: {(directory / 'index.html').resolve()}")


if __name__ == "__main__":
    main()
