#!/usr/bin/env python3
"""Regenerate the pinned, flash-resident Fusion Pixel Font 12px C data."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = APP_ROOT / "assets/fonts/fusion-pixel-font-2026.09.25"
BDF = ASSET_ROOT / "fusion-pixel-12px-monospaced-zh_hans.bdf"
HEADER = APP_ROOT / "include/fusion_font_12.h"
SOURCE = APP_ROOT / "fusion_pixel_12_zh_hans.c"
EXPECTED_BDF_SHA256 = "bb2cdfa029674d83ad9fc6b01bba11752f61779cae1219a722c7ccee96b2d0ae"
EXPECTED_ARCHIVE_SHA256 = "d75f5262f108757edb0f47ee8e3d2dfdfbecfd94558faf5ffb0c06dc5866fb3b"
EXPECTED_GLYPHS = 36981
EXPECTED_METRICS = (10, 2, 8, EXPECTED_GLYPHS)
EXPECTED_CELL_OVERFLOW = (0x3031, 0x3032)


HEADER_TEXT = """#pragma once

#include <stddef.h>
#include <stdint.h>

// Fusion Pixel Font 12px monospaced, zh_hans, release 2026.09.25.
// The source's U+FFFE default/noncharacter entry is retained with all glyphs.
enum {
    FUSION_PIXEL_12_ASCENT = 10,
    FUSION_PIXEL_12_DESCENT = 2,
    FUSION_PIXEL_12_CAP_HEIGHT = 8,
    FUSION_PIXEL_12_GLYPH_COUNT = 36981,
};

typedef struct {
    uint32_t codepoint;
    uint32_t bitmap_bit_offset;
    // Packed fields: advance:5, width:5, height:5, x offset:signed 6,
    // y offset:signed 6. Bitmaps are tightly packed MSB-first, row-major.
    uint32_t metrics;
} fusion_pixel_12_glyph_t;

extern const fusion_pixel_12_glyph_t
    fusion_pixel_12_zh_hans_glyphs[FUSION_PIXEL_12_GLYPH_COUNT];
extern const uint8_t fusion_pixel_12_zh_hans_bitmap[];

const fusion_pixel_12_glyph_t *fusion_pixel_12_lookup(uint32_t codepoint);

static inline uint8_t fusion_pixel_12_advance(const fusion_pixel_12_glyph_t *glyph)
{
    return (uint8_t)(glyph->metrics & 0x1fu);
}

static inline uint8_t fusion_pixel_12_width(const fusion_pixel_12_glyph_t *glyph)
{
    return (uint8_t)((glyph->metrics >> 5) & 0x1fu);
}

static inline uint8_t fusion_pixel_12_height(const fusion_pixel_12_glyph_t *glyph)
{
    return (uint8_t)((glyph->metrics >> 10) & 0x1fu);
}

static inline int8_t fusion_pixel_12_x_offset(const fusion_pixel_12_glyph_t *glyph)
{
    const uint8_t value = (uint8_t)((glyph->metrics >> 15) & 0x3fu);
    return (int8_t)((int16_t)value - ((value & 0x20u) ? 64 : 0));
}

static inline int8_t fusion_pixel_12_y_offset(const fusion_pixel_12_glyph_t *glyph)
{
    const uint8_t value = (uint8_t)((glyph->metrics >> 21) & 0x3fu);
    return (int8_t)((int16_t)value - ((value & 0x20u) ? 64 : 0));
}
"""


def one(pattern: str, source: str, label: str) -> int:
    match = re.search(pattern, source, re.MULTILINE)
    if not match:
        raise ValueError(f"missing BDF {label}")
    return int(match.group(1))


def signed_fits(value: int, bits: int) -> bool:
    return -(1 << (bits - 1)) <= value < (1 << (bits - 1))


def pack_metrics(advance: int, width: int, height: int,
                 x_offset: int, y_offset: int) -> int:
    if not 0 <= advance <= 31 or not 0 <= width <= 31 or not 0 <= height <= 31:
        raise ValueError("glyph metrics exceed packed field width")
    if not signed_fits(x_offset, 6) or not signed_fits(y_offset, 6):
        raise ValueError("glyph offset exceeds packed field width")
    return (advance | (width << 5) | (height << 10) |
            ((x_offset & 0x3f) << 15) | ((y_offset & 0x3f) << 21))


def parse_bdf(source: bytes) -> tuple[list[tuple[int, int, int]], bytes, dict[str, int | tuple[int, ...]]]:
    digest = hashlib.sha256(source).hexdigest()
    if digest != EXPECTED_BDF_SHA256:
        raise ValueError(f"unexpected BDF SHA-256: {digest}")
    text = source.decode("ascii").replace("\r\n", "\n")
    header = text.split("STARTCHAR", 1)[0]
    ascent = one(r"^FONT_ASCENT (\d+)$", header, "FONT_ASCENT")
    descent = one(r"^FONT_DESCENT (\d+)$", header, "FONT_DESCENT")
    cap_height = one(r"^CAP_HEIGHT (\d+)$", header, "CAP_HEIGHT")
    declared = one(r"^CHARS (\d+)$", header, "CHARS")
    if (ascent, descent, cap_height, declared) != EXPECTED_METRICS:
        raise ValueError("BDF release metrics or glyph count changed")

    bitmap = bytearray()
    bit_count = 0
    glyphs: list[tuple[int, int, int]] = []
    seen: set[int] = set()
    advances: list[int] = []
    widths: list[int] = []
    heights: list[int] = []
    x_offsets: list[int] = []
    y_offsets: list[int] = []
    cell_overflow: list[int] = []

    for raw_block in text.split("STARTCHAR")[1:]:
        block = raw_block.split("ENDCHAR", 1)[0]
        encoding = one(r"^ENCODING (-?\d+)$", block, "ENCODING")
        if encoding < 0:
            raise ValueError("release contains a glyph without a Unicode encoding")
        if encoding > 0x10ffff or encoding in seen:
            raise ValueError(f"invalid or duplicate Unicode codepoint U+{encoding:04X}")
        seen.add(encoding)
        advance = one(r"^DWIDTH (\d+) -?\d+$", block, "DWIDTH")
        box = re.search(r"^BBX (\d+) (\d+) (-?\d+) (-?\d+)$", block, re.MULTILINE)
        if not box:
            raise ValueError(f"missing BBX for U+{encoding:04X}")
        width, height, x_offset, y_offset = map(int, box.groups())
        metrics = pack_metrics(advance, width, height, x_offset, y_offset)
        if "BITMAP\n" not in block:
            raise ValueError(f"missing BITMAP for U+{encoding:04X}")
        bitmap_text = block.split("BITMAP\n", 1)[1]
        rows = bitmap_text.strip().splitlines() if height else []
        if len(rows) != height:
            raise ValueError(f"bad bitmap height for U+{encoding:04X}")
        row_bytes = (width + 7) // 8
        bitmap_bit_offset = bit_count
        for row in rows:
            if len(row) != row_bytes * 2:
                raise ValueError(f"bad bitmap row width for U+{encoding:04X}")
            bits = int(row, 16) >> (row_bytes * 8 - width) if width else 0
            for col in range(width):
                if bit_count % 8 == 0:
                    bitmap.append(0)
                if bits & (1 << (width - 1 - col)):
                    bitmap[-1] |= 0x80 >> (bit_count % 8)
                bit_count += 1
        glyphs.append((encoding, bitmap_bit_offset, metrics))
        advances.append(advance)
        widths.append(width)
        heights.append(height)
        x_offsets.append(x_offset)
        y_offsets.append(y_offset)
        if y_offset < -12 or y_offset + height > 12:
            cell_overflow.append(encoding)

    if len(glyphs) != declared:
        raise ValueError(f"declared {declared} glyphs but parsed {len(glyphs)}")
    if 0xfffd not in seen or 0xfffe not in seen:
        raise ValueError("source replacement/default glyph coverage is incomplete")
    if tuple(sorted(cell_overflow)) != EXPECTED_CELL_OVERFLOW:
        raise ValueError("unexpected glyphs extend outside the 12px cell")
    if bit_count > 0xffffffff:
        raise ValueError("bitmap bit offsets exceed the uint32 table field")

    glyphs.sort(key=lambda glyph: glyph[0])
    return glyphs, bytes(bitmap), dict(
        ascent=ascent, descent=descent, cap_height=cap_height,
        glyph_count=len(glyphs), max_advance=max(advances),
        max_width=max(widths), max_height=max(heights),
        min_x_offset=min(x_offsets), max_x_offset=max(x_offsets),
        min_y_offset=min(y_offsets), max_y_offset=max(y_offsets),
        bitmap_bits=bit_count, cell_overflow=tuple(sorted(cell_overflow)))


def render_source(glyphs: list[tuple[int, int, int]], bitmap: bytes) -> str:
    lines = [
        "// Generated by scripts/generate_fusion_font_12.py; do not edit.",
        "#include \"fusion_font_12.h\"",
        "",
        "const fusion_pixel_12_glyph_t",
        "fusion_pixel_12_zh_hans_glyphs[FUSION_PIXEL_12_GLYPH_COUNT] = {",
    ]
    for codepoint, bit_offset, metrics in glyphs:
        lines.append(f"    {{0x{codepoint:06x}u, {bit_offset}u, 0x{metrics:08x}u}},")
    lines.extend(["};", "", "const uint8_t fusion_pixel_12_zh_hans_bitmap[] = {"])
    for start in range(0, len(bitmap), 12):
        chunk = bitmap[start:start + 12]
        lines.append("    " + ", ".join(f"0x{byte:02x}" for byte in chunk) + ",")
    lines.extend([
        "};",
        "",
        "const fusion_pixel_12_glyph_t *fusion_pixel_12_lookup(uint32_t codepoint)",
        "{",
        "    size_t low = 0, high = FUSION_PIXEL_12_GLYPH_COUNT;",
        "    while (low < high) {",
        "        const size_t middle = low + (high - low) / 2;",
        "        const uint32_t candidate = fusion_pixel_12_zh_hans_glyphs[middle].codepoint;",
        "        if (candidate < codepoint) low = middle + 1;",
        "        else high = middle;",
        "    }",
        "    if (low < FUSION_PIXEL_12_GLYPH_COUNT &&",
        "        fusion_pixel_12_zh_hans_glyphs[low].codepoint == codepoint)",
        "        return &fusion_pixel_12_zh_hans_glyphs[low];",
        "    return NULL;",
        "}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify generated files without writing them")
    args = parser.parse_args()

    try:
        bdf_bytes = BDF.read_bytes()
        glyphs, bitmap, metrics = parse_bdf(bdf_bytes)
        generated_source = render_source(glyphs, bitmap)
        expected = ((HEADER, HEADER_TEXT), (SOURCE, generated_source))
        if args.check:
            stale = [path for path, content in expected
                     if not path.is_file() or path.read_text() != content]
            if stale:
                print("stale generated font files: " + ", ".join(map(str, stale)),
                      file=sys.stderr)
                return 1
        else:
            for path, content in expected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

        print("Fusion Pixel Font 12px zh_hans "
              f"release=2026.09.25 glyphs={metrics['glyph_count']} "
              f"advance_max={metrics['max_advance']} "
              f"bbox_max={metrics['max_width']}x{metrics['max_height']} "
              f"offset_x={metrics['min_x_offset']}..{metrics['max_x_offset']} "
              f"offset_y={metrics['min_y_offset']}..{metrics['max_y_offset']} "
              f"bitmap={len(bitmap)} bytes "
              f"source={SOURCE.stat().st_size if SOURCE.exists() and not args.check else len(generated_source.encode())} bytes "
              f"cell_overflow=" + ",".join(f"U+{codepoint:04X}"
                                           for codepoint in metrics['cell_overflow']) + " "
              f"bdf_sha256={hashlib.sha256(bdf_bytes).hexdigest()} "
              f"archive_sha256={EXPECTED_ARCHIVE_SHA256}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"font generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
