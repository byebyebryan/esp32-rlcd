// Pixel mapping adapted from Waveshare's display_bsp.cpp (Apache-2.0).
// Modified: pure C packing, bounds checks, and a standalone bring-up pattern.
// See UPSTREAM.md and LICENSE.waveshare.
#include "rlcd_frame.h"

#include <stdio.h>
#include <string.h>

void rlcd_frame_clear(uint8_t *buffer, bool white)
{
    memset(buffer, white ? 0xff : 0, RLCD_FRAME_BYTES);
}

void rlcd_frame_pixel(uint8_t *buffer, int x, int y, bool white)
{
    if (x < 0 || y < 0 || x >= RLCD_WIDTH || y >= RLCD_HEIGHT) {
        return;
    }

    const unsigned inverted_y = RLCD_HEIGHT - 1 - (unsigned)y;
    const size_t index = ((unsigned)x / 2) * (RLCD_HEIGHT / 4) + inverted_y / 4;
    const uint8_t mask = (uint8_t)(1u << (7 - (inverted_y % 4) * 2 - (x % 2)));
    if (white) {
        buffer[index] |= mask;
    } else {
        buffer[index] &= (uint8_t)~mask;
    }
}

static void box(uint8_t *buffer, int x, int y, int w, int h)
{
    for (int row = y; row < y + h; ++row) {
        for (int col = x; col < x + w; ++col) {
            rlcd_frame_pixel(buffer, col, row, false);
        }
    }
}

// Small hand-authored 5x7 glyphs used only by this diagnostic screen.
static const struct {
    char letter;
    uint8_t columns[5];
} glyphs[] = {
    {'A', {0x7e, 0x11, 0x11, 0x11, 0x7e}},
    {'C', {0x3e, 0x41, 0x41, 0x41, 0x22}},
    {'D', {0x7f, 0x41, 0x41, 0x22, 0x1c}},
    {'E', {0x7f, 0x49, 0x49, 0x49, 0x41}},
    {'L', {0x7f, 0x40, 0x40, 0x40, 0x40}},
    {'R', {0x7f, 0x09, 0x19, 0x29, 0x46}},
    {'X', {0x63, 0x14, 0x08, 0x14, 0x63}},
    {'Y', {0x03, 0x04, 0x78, 0x04, 0x03}},
    {'0', {0x3e, 0x51, 0x49, 0x45, 0x3e}},
    {'1', {0x00, 0x42, 0x7f, 0x40, 0x00}},
    {'2', {0x42, 0x61, 0x51, 0x49, 0x46}},
    {'3', {0x21, 0x41, 0x45, 0x4b, 0x31}},
    {'4', {0x18, 0x14, 0x12, 0x7f, 0x10}},
    {'5', {0x27, 0x45, 0x45, 0x45, 0x39}},
    {'6', {0x3c, 0x4a, 0x49, 0x49, 0x30}},
    {'7', {0x01, 0x71, 0x09, 0x05, 0x03}},
    {'8', {0x36, 0x49, 0x49, 0x49, 0x36}},
    {'9', {0x06, 0x49, 0x49, 0x29, 0x1e}},
};

static void text(uint8_t *buffer, int x, int y, const char *value, int scale)
{
    for (; *value; ++value, x += 6 * scale) {
        for (size_t g = 0; g < sizeof(glyphs) / sizeof(glyphs[0]); ++g) {
            if (glyphs[g].letter != *value) {
                continue;
            }
            for (int col = 0; col < 5; ++col) {
                for (int row = 0; row < 7; ++row) {
                    if (glyphs[g].columns[col] & (1u << row)) {
                        box(buffer, x + col * scale, y + row * scale, scale, scale);
                    }
                }
            }
            break;
        }
    }
}

void rlcd_frame_draw_test(uint8_t *buffer, uint32_t frame)
{
    rlcd_frame_clear(buffer, true);
    box(buffer, 1, 1, 398, 2);
    box(buffer, 1, 297, 398, 2);
    box(buffer, 1, 1, 2, 298);
    box(buffer, 397, 1, 2, 298);
    box(buffer, 12, 12, 16, 16); // Asymmetric top-left orientation marker.
    text(buffer, 82, 32, "RLCD READY", 4);
    text(buffer, 147, 76, "400 X 300", 2);

    for (int x = 24; x < 376; x += 32) {
        box(buffer, x, 112, 16, 40);
    }
    for (int y = 184; y < 248; ++y) {
        for (int x = 24; x < 120; ++x) {
            rlcd_frame_pixel(buffer, x, y, ((x / 4 + y / 4) & 1) != 0);
        }
        for (int x = 140; x < 236; ++x) {
            rlcd_frame_pixel(buffer, x, y, ((x + y) & 1) != 0);
        }
    }
    box(buffer, 270 + (int)(frame % 6) * 16, 196, 16, 16);
    box(buffer, 266, 224, 108, 2);
    char count[5];
    snprintf(count, sizeof(count), "%04u", (unsigned)(frame % 10000));
    text(buffer, 292, 242, count, 2);
}
