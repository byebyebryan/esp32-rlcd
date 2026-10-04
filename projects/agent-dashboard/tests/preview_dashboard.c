#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "demo.h"
#include "rlcd_frame.h"

static uint8_t guarded[RLCD_FRAME_BYTES + 2];

// Convert panel pixels to ordinary top-left PBM. This uses the accepted wire
// mapping; the existing test_frame check independently validates its corners.
static void save_pbm(const char *path, const uint8_t *frame)
{
    FILE *out = fopen(path, "wb");
    if (!out) { perror(path); exit(1); }
    fprintf(out, "P4\n%d %d\n", RLCD_WIDTH, RLCD_HEIGHT);
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        for (int x = 0; x < RLCD_WIDTH; x += 8) {
            uint8_t pixels = 0;
            for (int i = 0; i < 8; ++i) {
                const int col = x + i, inverted_y = RLCD_HEIGHT - 1 - y;
                const size_t slot = (size_t)(col / 2) * (RLCD_HEIGHT / 4) + inverted_y / 4;
                const uint8_t bit = (uint8_t)(1u << (7 - (inverted_y % 4) * 2 - col % 2));
                if (!(frame[slot] & bit)) pixels |= (uint8_t)(1u << (7 - i));
            }
            assert(fputc(pixels, out) != EOF);
        }
    }
    if (fclose(out) != 0) { perror(path); exit(1); }
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: %s OUTPUT_DIRECTORY\n", argv[0]); return 1; }
    uint8_t *frame = guarded + 1;
    guarded[0] = 0xa5;
    guarded[RLCD_FRAME_BYTES + 1] = 0x5a;
    for (unsigned i = 0; i < DASHBOARD_DEMO_CASES; ++i) {
        const dashboard_view_t view = dashboard_demo_view(i);
        dashboard_draw(frame, &view);
        assert(guarded[0] == 0xa5 && guarded[RLCD_FRAME_BYTES + 1] == 0x5a);
        char path[4096];
        const int n = snprintf(path, sizeof(path), "%s/%s.pbm", argv[1], dashboard_demo_name(i));
        if (n < 0 || (size_t)n >= sizeof(path)) return 1;
        save_pbm(path, frame);
        const dashboard_view_t dense = dashboard_demo_dense_view(i);
        dashboard_draw_table(frame, &dense);
        assert(guarded[0] == 0xa5 && guarded[RLCD_FRAME_BYTES + 1] == 0x5a);
        const int dense_n = snprintf(path, sizeof(path), "%s/table-%s.pbm", argv[1], dashboard_demo_name(i));
        if (dense_n < 0 || (size_t)dense_n >= sizeof(path)) return 1;
        save_pbm(path, frame);
        const dashboard_view_t icons = dashboard_demo_icon_view(i);
        dashboard_draw_dense(frame, &icons);
        assert(guarded[0] == 0xa5 && guarded[RLCD_FRAME_BYTES + 1] == 0x5a);
        const int icons_n = snprintf(path, sizeof(path), "%s/dense-%s.pbm", argv[1], dashboard_demo_name(i));
        if (icons_n < 0 || (size_t)icons_n >= sizeof(path)) return 1;
        save_pbm(path, frame);
        const dashboard_style_t styles[] = {
            {DASH_AGENT_PAIR, false}, {DASH_AGENT_PAIR, true}, {DASH_AGENT_HIDDEN, true},
        };
        const char *prefixes[] = {"labels", "attention", "no-agent"};
        uint8_t plain[RLCD_FRAME_BYTES];
        dashboard_draw_styled(plain, &icons, styles[0]);
        for (size_t style = 0; style < sizeof(styles) / sizeof(styles[0]); ++style) {
            dashboard_draw_styled(frame, &icons, styles[style]);
            assert(guarded[0] == 0xa5 && guarded[RLCD_FRAME_BYTES + 1] == 0x5a);
            // Source loss/conflict must suppress attention even when a cached
            // work state was waiting. Health cases contain no current waits/errors.
            if (style == 1 && (i == 2 || i == 3 || i == 4 || i == 5))
                assert(memcmp(plain, frame, sizeof(plain)) == 0);
            const int styled_n = snprintf(path, sizeof(path), "%s/%s-%s.pbm",
                                          argv[1], prefixes[style], dashboard_demo_name(i));
            if (styled_n < 0 || (size_t)styled_n >= sizeof(path)) return 1;
            save_pbm(path, frame);
        }
    }
    puts("PASS: 42 synthetic frames; bounds and stale/unavailable attention suppression");
    return 0;
}
