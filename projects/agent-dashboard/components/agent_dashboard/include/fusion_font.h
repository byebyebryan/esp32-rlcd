#pragma once

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
