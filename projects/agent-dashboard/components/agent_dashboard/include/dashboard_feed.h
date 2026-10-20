#pragma once

#include "dashboard_motion.h"

enum { DASH_FEED_BYTES = 16384, DASH_FEED_HOSTS = 2, DASH_FEED_VALID_MS = 3000,
       DASH_FEED_REQUEST_MS = 1000, DASH_FEED_LABEL_BYTES = 63 };

typedef struct {
    char alias[3];
    uint32_t status, valid_ms, totals[5], total;
} dashboard_feed_host_t;

typedef struct {
    char identity[65], label[DASH_FEED_LABEL_BYTES + 1], age[4], badge[3];
    uint32_t host, category, work, health, valid_ms;
} dashboard_feed_row_t;

typedef struct {
    char bridge[17];
    uint32_t sequence;
    size_t host_count, row_count;
    dashboard_feed_host_t hosts[DASH_FEED_HOSTS];
    dashboard_feed_row_t rows[DASHBOARD_MOTION_CAPACITY];
} dashboard_feed_view_t;

typedef struct {
    char boot[17];
    uint32_t request;
    uint64_t requested_ms, accepted_request_ms;
    bool pending, has_view;
    dashboard_feed_view_t view, candidate;
    dashboard_motion_sample_t samples[DASHBOARD_MOTION_CAPACITY];
    uint8_t order[DASHBOARD_MOTION_CAPACITY];
    uint32_t effective_health[DASHBOARD_MOTION_CAPACITY];
    bool dirty;
} dashboard_feed_t;

void dashboard_feed_init(dashboard_feed_t *feed, const char *boot);
// Creates one new outstanding request; never extends the accepted view.
int dashboard_feed_request(dashboard_feed_t *feed, uint64_t now_ms,
                           char *output, size_t capacity);
// Rejects atomically; the caller supplies a complete line without CR/LF.
bool dashboard_feed_accept(dashboard_feed_t *feed, const char *line,
                          size_t length, uint64_t now_ms);
// Projects admission/expiry into the caller-owned renderer, even during silence.
bool dashboard_feed_tick(dashboard_feed_t *feed, dashboard_motion_t *motion,
                        uint64_t now_ms);
