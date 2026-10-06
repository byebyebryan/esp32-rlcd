// Include the renderer to test its private fill primitive without adding a
// firmware API. The reference uses the independently checked pixel writer.
#include "../components/agent_dashboard/agent_dashboard.c"

#include <assert.h>
#include <stdio.h>

static uint8_t guarded_rect[RLCD_FRAME_BYTES + 2];
static uint8_t reference_rect[RLCD_FRAME_BYTES];
static uint32_t random_state = 0x9172ad54u;

static uint32_t next_random(void)
{
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static void check_rect(int x, int y, int width, int height, bool white, bool clip)
{
    guarded_rect[0] = 0xa5;
    guarded_rect[RLCD_FRAME_BYTES + 1] = 0x5a;
    for (size_t i = 0; i < RLCD_FRAME_BYTES; ++i)
        guarded_rect[i + 1] = (uint8_t)next_random();
    memcpy(reference_rect, guarded_rect + 1, RLCD_FRAME_BYTES);
    motion_clip_enabled = clip;
    motion_clip_top = DASHBOARD_MOTION_BODY_TOP;
    motion_clip_bottom = DASHBOARD_MOTION_BODY_BOTTOM;
    rect(guarded_rect + 1, x, y, width, height, white);
    for (int row = y; row < y + height; ++row) {
        if (clip && (row < DASHBOARD_MOTION_BODY_TOP ||
                     row >= DASHBOARD_MOTION_BODY_BOTTOM)) continue;
        for (int column = x; column < x + width; ++column)
            rlcd_frame_pixel(reference_rect, column, row, white);
    }
    assert(guarded_rect[0] == 0xa5 && guarded_rect[RLCD_FRAME_BYTES + 1] == 0x5a);
    assert(memcmp(reference_rect, guarded_rect + 1, RLCD_FRAME_BYTES) == 0);
}

static void check_unicode_text(void)
{
    const char *valid[] = {"a", "é", "中", "한", "🙂"};
    const uint32_t expected[] = {'a', 0xe9, 0x4e2d, 0xd55c, 0x1f642};
    for (size_t i = 0; i < 5; ++i) {
        const char *cursor = valid[i];
        size_t remaining = strlen(cursor);
        assert(motion_codepoint(&cursor, &remaining) == expected[i]);
        assert(remaining == 0);
    }
    const char *invalid[] = {"\x80", "\xc0\xaf", "\xe0\x80\x80", "\xed\xa0\x80", "\xf4\x90\x80\x80", "\xe4\xb8", "\xf0"};
    for (size_t i = 0; i < 7; ++i) {
        const char *cursor = invalid[i];
        size_t remaining = strlen(cursor);
        assert(motion_codepoint(&cursor, &remaining) == 0xfffd);
        assert(cursor == invalid[i] + 1);
    }
    const char *bounded = "中";
    size_t one_byte = 1;
    assert(motion_codepoint(&bounded, &one_byte) == 0xfffd);
    assert(one_byte == 0);
    assert(motion_text_width("Fa中", true) == 24);
    assert(motion_text_width("Fa中", false) == 48);
    assert(fusion_pixel_12_lookup(0x4e2d));
    assert(fusion_pixel_12_lookup(0xd55c));
    assert(!fusion_pixel_12_lookup(0x1f642));
    assert(motion_glyph(0x1f642) == fusion_pixel_12_lookup(0xfffd));
    // A wide codepoint that cannot fit is replaced by a complete ellipsis,
    // with the following column untouched; malformed tails remain bounded.
    rlcd_frame_clear(reference_rect, true);
    rlcd_frame_clear(guarded_rect + 1, true);
    motion_clip_enabled = false;
    motion_text(reference_rect, 24, 100, "a...", true, 24, false);
    motion_text(guarded_rect + 1, 24, 100, "a中中中", true, 24, false);
    assert(memcmp(reference_rect, guarded_rect + 1, RLCD_FRAME_BYTES) == 0);
    // The source's two-line vertical kana mark is cropped to one cell.
    rlcd_frame_clear(guarded_rect + 1, true);
    motion_text(guarded_rect + 1, 24, 100, "〱", true, 12, false);
    for (int y = 0; y < RLCD_HEIGHT; ++y)
        if (y < 100 || y >= 112)
            for (int x = 0; x < RLCD_WIDTH; ++x) {
                const unsigned iy = RLCD_HEIGHT - 1 - (unsigned)y;
                const size_t at = ((unsigned)x / 2) * (RLCD_HEIGHT / 4) + iy / 4;
                assert(guarded_rect[1 + at] & (1u << (7 - (iy % 4) * 2 - (x % 2))));
            }
    motion_text(guarded_rect + 1, 24, 150, "\xe4\xb8", true, 40, false);
    puts("PASS: UTF-8 valid, malformed, truncated, fallback, widths and codepoint ellipsis");
}

int main(void)
{
    check_unicode_text();
    size_t cases = 0;
    // All edge masks for a single tile and neighboring tiles, in both colors.
    for (int x = 0; x < 4; ++x)
        for (int y = 48; y < 56; ++y)
            for (int width = 1; width <= 5; ++width)
                for (int height = 1; height <= 6; ++height)
                    for (int white = 0; white <= 1; ++white)
                        for (int clip = 0; clip <= 1; ++clip) {
                            check_rect(x, y, width, height, white, clip);
                            ++cases;
                        }
    const int large[][4] = {
        {0, 0, 400, 300}, {-5, -7, 412, 316}, {12, 52, 376, 26},
        {13, 53, 374, 23}, {399, 299, 4, 4}, {-10, 260, 430, 50},
        {-20, -20, 10, 10}, {410, 310, 20, 20}, {0, 0, 0, 300},
        {0, 0, 400, 0}, {12, 50, -1, 26}, {12, 50, 376, -1},
    };
    for (size_t i = 0; i < sizeof(large) / sizeof(large[0]); ++i)
        for (int white = 0; white <= 1; ++white)
            for (int clip = 0; clip <= 1; ++clip) {
                check_rect(large[i][0], large[i][1], large[i][2], large[i][3], white, clip);
                ++cases;
            }
    for (int i = 0; i < 600; ++i) {
        const int x = (int)(next_random() % 460) - 30;
        const int y = (int)(next_random() % 360) - 30;
        const int width = (int)(next_random() % 140) + 1;
        const int height = (int)(next_random() % 100) + 1;
        check_rect(x, y, width, height, (i & 1) != 0, (i & 2) != 0);
        ++cases;
    }
    motion_clip_enabled = false;
    printf("PASS: %zu packed rectangles equal pixel reference; edge masks, colors, clipping and guards\n", cases);
    return 0;
}
