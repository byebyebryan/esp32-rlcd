#pragma once

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
