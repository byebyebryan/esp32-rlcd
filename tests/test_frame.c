#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "rlcd_frame.h"

static uint8_t buffer[RLCD_FRAME_BYTES + 2];
static uint8_t covered[RLCD_FRAME_BYTES];

int main(void)
{
    uint8_t *frame = buffer + 1;
    buffer[0] = 0xa5;
    buffer[RLCD_FRAME_BYTES + 1] = 0x5a;

    // Known physical corners, independent reference values for the wire format.
    rlcd_frame_clear(frame, false);
    rlcd_frame_pixel(frame, 0, 0, true);
    assert(frame[74] == 0x02);
    rlcd_frame_pixel(frame, 1, 0, true);
    assert(frame[74] == 0x03);
    rlcd_frame_pixel(frame, 0, 299, true);
    assert(frame[0] == 0x80);
    rlcd_frame_pixel(frame, 399, 299, true);
    assert(frame[14925] == 0x40);
    rlcd_frame_pixel(frame, 399, 0, true);
    assert(frame[14999] == 0x01);

    // Every screen pixel must map to exactly one distinct bit in the buffer.
    // This detects overlaps, skipped bits, and transposed/incorrect dimensions.
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        for (int x = 0; x < RLCD_WIDTH; ++x) {
            rlcd_frame_clear(frame, false);
            rlcd_frame_pixel(frame, x, y, true);
            unsigned bits = 0;
            for (size_t i = 0; i < RLCD_FRAME_BYTES; ++i) {
                assert((covered[i] & frame[i]) == 0);
                covered[i] |= frame[i];
                bits += (unsigned)__builtin_popcount((unsigned)frame[i]);
            }
            assert(bits == 1);
        }
    }
    for (size_t i = 0; i < RLCD_FRAME_BYTES; ++i) {
        assert(covered[i] == 0xff);
    }

    rlcd_frame_clear(frame, true);
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        for (int x = 0; x < RLCD_WIDTH; ++x) {
            rlcd_frame_pixel(frame, x, y, false);
        }
    }
    for (size_t i = 0; i < RLCD_FRAME_BYTES; ++i) {
        assert(frame[i] == 0);
    }
    rlcd_frame_pixel(frame, -1, 0, true);
    rlcd_frame_pixel(frame, 0, -1, true);
    rlcd_frame_pixel(frame, 400, 0, true);
    rlcd_frame_pixel(frame, 0, 300, true);
    for (size_t i = 0; i < RLCD_FRAME_BYTES; ++i) {
        assert(frame[i] == 0);
    }
    for (uint32_t tick = 0; tick < 7; ++tick) {
        rlcd_frame_draw_test(frame, tick);
        assert(buffer[0] == 0xa5 && buffer[RLCD_FRAME_BYTES + 1] == 0x5a);
    }
    puts("PASS: corners, 120000 distinct pixels, colors, clipping and pattern bounds");
    return 0;
}
