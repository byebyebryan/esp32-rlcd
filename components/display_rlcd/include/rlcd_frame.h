#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    RLCD_WIDTH = 400,
    RLCD_HEIGHT = 300,
    RLCD_FRAME_BYTES = RLCD_WIDTH * RLCD_HEIGHT / 8,
};

// Landscape panel packing: each byte holds a 2-column by 4-row pixel block.
// White is a set bit; black is a cleared bit. Out-of-bounds writes are ignored.
void rlcd_frame_clear(uint8_t *buffer, bool white);
void rlcd_frame_pixel(uint8_t *buffer, int x, int y, bool white);
void rlcd_frame_draw_test(uint8_t *buffer, uint32_t frame);
