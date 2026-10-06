#!/usr/bin/env python3
"""Regenerate the pinned, flash-resident Fusion Pixel Font C data."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = APP_ROOT / "assets/fonts/fusion-pixel-font-2026.09.25"
BDF = ASSET_ROOT / "fusion-pixel-8px-monospaced-zh_hans.bdf"
HEADER = APP_ROOT / "include/fusion_font.h"
SOURCE = APP_ROOT / "fusion_pixel_8_zh_hans.c"
EXPECTED_BDF_SHA256 = "3c00ccab762c0c75967eea724f5cd57feb544be7a0814d06233160ef9482a50b"
EXPECTED_ARCHIVE_SHA256 = "bd76834c43d6882184356394cfdd8c9c5e5623d9d1c9020564fe545b7ba769ce"
EXPECTED_GLYPHS = 28410


HEADER_TEXT = """#pragma once

#include <stddef.h>
#include <stdint.h>

// Fusion Pixel Font 8px monospaced, zh_hans, release 2026.09.25.
// This table includes the source's U+FFFE default/noncharacter entry as well
// as its 28,409 documented character glyphs.
enum {
    FUSION_PIXEL_8_ASCENT = 7,
    FUSION_PIXEL_8_DESCENT = 1,
    FUSION_PIXEL_8_CAP_HEIGHT = 6,
    FUSION_PIXEL_8_GLYPH_COUNT = 28410,
};

typedef struct {
    uint32_t codepoint;
    uint32_t bitmap_bit_offset;
    // Packed fields: advance:5, width:4, height:4, x offset:signed 5,
    // y offset:signed 6. Bitmaps are tightly packed MSB-first, row-major.
    uint32_t metrics;
} fusion_pixel_8_glyph_t;

extern const fusion_pixel_8_glyph_t
    fusion_pixel_8_zh_hans_glyphs[FUSION_PIXEL_8_GLYPH_COUNT];
extern const uint8_t fusion_pixel_8_zh_hans_bitmap[];

const fusion_pixel_8_glyph_t *fusion_pixel_8_lookup(uint32_t codepoint);

static inline uint8_t fusion_pixel_8_advance(const fusion_pixel_8_glyph_t *glyph)
{
    return (uint8_t)(glyph->metrics & 0x1fu);
}

static inline uint8_t fusion_pixel_8_width(const fusion_pixel_8_glyph_t *glyph)
{
    return (uint8_t)((glyph->metrics >> 5) & 0x0fu);
}

static inline uint8_t fusion_pixel_8_height(const fusion_pixel_8_glyph_t *glyph)
{
    return (uint8_t)((glyph->metrics >> 9) & 0x0fu);
}

static inline int8_t fusion_pixel_8_x_offset(const fusion_pixel_8_glyph_t *glyph)
{
    const uint8_t value = (uint8_t)((glyph->metrics >> 13) & 0x1fu);
    return (int8_t)((value ^ 0x10u) - 0x10u);
}

static inline int8_t fusion_pixel_8_y_offset(const fusion_pixel_8_glyph_t *glyph)
{
    const uint8_t value = (uint8_t)((glyph->metrics >> 18) & 0x3fu);
    return (int8_t)((value ^ 0x20u) - 0x20u);
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
    if not 0 <= advance <= 31 or not 0 <= width <= 15 or not 0 <= height <= 15:
        raise ValueError("glyph metrics exceed packed field width")
    if not signed_fits(x_offset, 5) or not signed_fits(y_offset, 6):
        raise ValueError("glyph offset exceeds packed field width")
    return (advance | (width << 5) | (height << 9) |
            ((x_offset & 0x1f) << 13) | ((y_offset & 0x3f) << 18))


def parse_bdf(source: bytes) -> tuple[list[tuple[int, int, int]], bytes, dict[str, int]]:
    digest = hashlib.sha256(source).hexdigest()
    if digest != EXPECTED_BDF_SHA256:
        raise ValueError(f"unexpected BDF SHA-256: {digest}")
    text = source.decode("ascii").replace("\r\n", "\n")
    header = text.split("STARTCHAR", 1)[0]
    ascent = one(r"^FONT_ASCENT (\d+)$", header, "FONT_ASCENT")
    descent = one(r"^FONT_DESCENT (\d+)$", header, "FONT_DESCENT")
    cap_height = one(r"^CAP_HEIGHT (\d+)$", header, "CAP_HEIGHT")
    declared = one(r"^CHARS (\d+)$", header, "CHARS")
    if (ascent, descent, cap_height, declared) != (7, 1, 6, EXPECTED_GLYPHS):
        raise ValueError("BDF release metrics or glyph count changed")

    bitmap = bytearray()
    bit_count = 0
    glyphs: list[tuple[int, int, int]] = []
    seen: set[int] = set()
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
            bits = int(row, 16) >> (row_bytes * 8 - width)
            for col in range(width):
                if bit_count % 8 == 0:
                    bitmap.append(0)
                if bits & (1 << (width - 1 - col)):
                    bitmap[-1] |= 0x80 >> (bit_count % 8)
                bit_count += 1
        glyphs.append((encoding, bitmap_bit_offset, metrics))

    if len(glyphs) != declared:
        raise ValueError(f"declared {declared} glyphs but parsed {len(glyphs)}")
    if 0xfffd not in seen or 0xfffe not in seen:
        raise ValueError("source replacement/default glyph coverage is incomplete")
    glyphs.sort(key=lambda glyph: glyph[0])
    return glyphs, bytes(bitmap), dict(ascent=ascent, descent=descent,
                                       cap_height=cap_height, glyph_count=len(glyphs))


def render_source(glyphs: list[tuple[int, int, int]], bitmap: bytes) -> str:
    lines = [
        "// Generated by scripts/generate_fusion_font.py; do not edit.",
        "#include \"fusion_font.h\"",
        "",
        "const fusion_pixel_8_glyph_t",
        "fusion_pixel_8_zh_hans_glyphs[FUSION_PIXEL_8_GLYPH_COUNT] = {",
    ]
    for codepoint, bit_offset, metrics in glyphs:
        lines.append(f"    {{0x{codepoint:06x}u, {bit_offset}u, 0x{metrics:06x}u}},")
    lines.extend(["};", "", "const uint8_t fusion_pixel_8_zh_hans_bitmap[] = {"])
    for start in range(0, len(bitmap), 12):
        chunk = bitmap[start:start + 12]
        lines.append("    " + ", ".join(f"0x{byte:02x}" for byte in chunk) + ",")
    lines.extend([
        "};",
        "",
        "const fusion_pixel_8_glyph_t *fusion_pixel_8_lookup(uint32_t codepoint)",
        "{",
        "    size_t low = 0, high = FUSION_PIXEL_8_GLYPH_COUNT;",
        "    while (low < high) {",
        "        const size_t middle = low + (high - low) / 2;",
        "        const uint32_t candidate = fusion_pixel_8_zh_hans_glyphs[middle].codepoint;",
        "        if (candidate < codepoint) low = middle + 1;",
        "        else high = middle;",
        "    }",
        "    if (low < FUSION_PIXEL_8_GLYPH_COUNT &&",
        "        fusion_pixel_8_zh_hans_glyphs[low].codepoint == codepoint)",
        "        return &fusion_pixel_8_zh_hans_glyphs[low];",
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

        print("Fusion Pixel Font 8px zh_hans "
              f"release=2026.09.25 glyphs={metrics['glyph_count']} "
              f"bitmap={len(bitmap)} bytes source={SOURCE.stat().st_size if SOURCE.exists() and not args.check else len(generated_source.encode())} bytes "
              f"bdf_sha256={hashlib.sha256(bdf_bytes).hexdigest()}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"font generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
