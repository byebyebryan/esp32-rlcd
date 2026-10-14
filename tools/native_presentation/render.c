// Native gallery exporter. Board calls are stubs; app_main is never invoked.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dashboard_feed.h"
#include "rlcd_frame.h"
#include "rlcd_panel.h"

// Compile the unchanged benchmark's drawing and bounce functions directly.
#include "../../projects/render-bench/main/main.c"

static uint8_t native_guarded[RLCD_FRAME_BYTES + 2];
static dashboard_feed_t native_feed;
static dashboard_motion_t native_motion;
esp_err_t rlcd_panel_init(void) { return ESP_OK; }
uint8_t *rlcd_panel_framebuffer(void) { return native_guarded + 1; }
esp_err_t rlcd_panel_present(void) { return ESP_OK; }
esp_err_t rlcd_panel_present_queued(void) { return ESP_OK; }

static void save_pbm(const char *path)
{
    assert(native_guarded[0] == 0x5b && native_guarded[RLCD_FRAME_BYTES + 1] == 0x5b);
    FILE *out = fopen(path, "wb"); assert(out);
    assert(fprintf(out, "P4\n400 300\n") > 0);
    const uint8_t *frame = native_guarded + 1;
    for (unsigned y = 0; y < 300; ++y) for (unsigned x = 0; x < 400; x += 8) {
        unsigned char value = 0;
        for (unsigned j = 0; j < 8; ++j) {
            unsigned inverted_y = 299 - y;
            size_t offset = ((x + j) / 2) * 75 + inverted_y / 4;
            unsigned mask = 1u << (7 - (inverted_y % 4) * 2 - ((x + j) % 2));
            if (!(frame[offset] & mask)) value |= 1u << (7 - j);
        }
        assert(fputc(value, out) != EOF);
    }
    assert(fclose(out) == 0);
}

int main(int argc, char **argv)
{
    assert(argc == 3);
    memset(native_guarded, 0x5b, sizeof(native_guarded));
    if (!strcmp(argv[1], "bringup") || !strcmp(argv[1], "render-bench")) {
        const bool benchmark = !strcmp(argv[1], "render-bench");
        rlcd_frame_draw_test(background, 0);
        const unsigned frames = benchmark ? 160 : 1;
        for (unsigned i = 0; i < frames; ++i) {
            if (benchmark) draw_animation(native_guarded + 1, i * 2);
            else rlcd_frame_draw_test(native_guarded + 1, 0);
            char path[4096];
            int length = snprintf(path, sizeof(path), "%s/frame-%03u.pbm", argv[2], i);
            assert(length > 0 && (size_t)length < sizeof(path));
            save_pbm(path);
        }
        return 0;
    }
    assert(!strcmp(argv[1], "agent-dashboard"));
    dashboard_feed_init(&native_feed, "0000000000000000");
    dashboard_motion_init(&native_motion);
    char line[DASH_FEED_BYTES + 128];
    uint64_t now = 0;
    unsigned index = 0;
    while (fgets(line, sizeof(line), stdin)) {
        size_t length = strlen(line);
        if (length && line[length - 1] == '\n') line[--length] = '\0';
        if (!strncmp(line, "REQ ", 4)) {
            now = strtoull(line + 4, NULL, 10);
            char request[64];
            assert(dashboard_feed_request(&native_feed, now, request, sizeof(request)) > 0);
        } else if (!strncmp(line, "AT ", 3)) {
            now = strtoull(line + 3, NULL, 10);
            dashboard_feed_tick(&native_feed, &native_motion, now);
            dashboard_motion_render(&native_motion, native_guarded + 1);
            char path[4096];
            int size = snprintf(path, sizeof(path), "%s/frame-%03u.pbm", argv[2], index++);
            assert(size > 0 && (size_t)size < sizeof(path));
            save_pbm(path);
            printf("%llu,%d,%d,%zu\n", (unsigned long long)now,
                   native_motion.feed_health, native_motion.live_partial, native_motion.count);
        } else {
            assert(dashboard_feed_accept(&native_feed, line, length, now));
        }
    }
    assert(index == 350);
    return 0;
}
