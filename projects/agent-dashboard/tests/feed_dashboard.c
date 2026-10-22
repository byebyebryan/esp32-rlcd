#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dashboard_feed.h"
#include "rlcd_frame.h"

static dashboard_feed_t feed;
static dashboard_motion_t motion;
static uint8_t guarded[RLCD_FRAME_BYTES + 2];
static char line[DASH_FEED_BYTES * 2 + 2];

static void state(uint64_t now)
{
    bool changed = dashboard_feed_tick(&feed, &motion, now);
    memset(guarded, 0x5b, sizeof(guarded));
    dashboard_motion_render(&motion, guarded + 1);
    assert(guarded[0] == 0x5b && guarded[RLCD_FRAME_BYTES + 1] == 0x5b);
    printf("{\"health\":%d,\"partial\":%s,\"rows\":%zu,\"visible\":%zu,\"total\":%zu,"
           "\"changed\":%s,"
           "\"totals\":[%u,%u,%u,%u,%u],\"flashing\":%s,\"entries\":[",
           motion.feed_health, motion.live_partial ? "true" : "false", motion.count,
           motion.visible_count, motion.live_total,
           changed ? "true" : "false",
           (unsigned)motion.live_totals[0], (unsigned)motion.live_totals[1],
           (unsigned)motion.live_totals[2], (unsigned)motion.live_totals[3],
           (unsigned)motion.live_totals[4],
           dashboard_motion_flashing(&motion) ? "true" : "false");
    for (size_t i = 0; i < motion.count; ++i) {
        const dashboard_motion_track_t *track = &motion.tracks[motion.order[i]];
        printf("%s{\"id\":\"%s\",\"category\":%d,\"work\":%d,\"health\":%d,\"age\":\"%s\",\"badge\":\"%s\"}",
               i ? "," : "", track->logical_id, track->category, track->work,
               track->health, track->supplied_age, track->provider);
    }
    puts("]}");
}

static void save(const char *path)
{
    FILE *out = fopen(path, "wb"); assert(out);
    fprintf(out, "P4\n400 300\n");
    const uint8_t *frame = guarded + 1;
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
    setbuf(stdout, NULL);
    dashboard_feed_init(&feed, "0000000000000000");
    dashboard_motion_init(&motion);
    uint64_t now = 0;
    if (argc == 3) {
        FILE *input = fopen(argv[1], "rb"); assert(input);
        assert(fgets(line, sizeof(line), input)); assert(fclose(input) == 0);
        size_t length = strlen(line); if (length && line[length - 1] == '\n') --length;
        char request[64]; dashboard_feed_request(&feed, 0, request, sizeof(request));
        assert(dashboard_feed_accept(&feed, line, length, 0));
        state(360); save(argv[2]); return 0;
    }
    while (fgets(line, sizeof(line), stdin)) {
        size_t length = strlen(line); if (length && line[length - 1] == '\n') --length;
        if (!strncmp(line, "REQ ", 4)) {
            now = strtoull(line + 4, NULL, 10);
            char request[64]; dashboard_feed_request(&feed, now, request, sizeof(request));
            printf("REQUEST %s", request);
        } else if (!strncmp(line, "AT ", 3)) {
            now = strtoull(line + 3, NULL, 10); state(now);
        } else {
            printf("ACCEPT %d\n", dashboard_feed_accept(&feed, line, length, now));
            state(now);
        }
    }
    return 0;
}
