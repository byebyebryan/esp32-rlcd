#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "agent_dashboard.h"
#include "dashboard_motion.h"
#include "rlcd_frame.h"

static uint8_t guarded[RLCD_FRAME_BYTES + 2];
static uint8_t expected_frame[RLCD_FRAME_BYTES];
static uint8_t frame_initial[RLCD_FRAME_BYTES];
static uint8_t frame_halfway[RLCD_FRAME_BYTES];
static uint8_t frame_endpoint[RLCD_FRAME_BYTES];
static uint8_t frame_overlap[RLCD_FRAME_BYTES];
static uint8_t frame_feed_lost[RLCD_FRAME_BYTES];
static uint8_t frame_overflow[RLCD_FRAME_BYTES];
static uint8_t frame_tier_down[RLCD_FRAME_BYTES];
static uint8_t frame_tier_stationary[RLCD_FRAME_BYTES];
static uint8_t frame_tier_up[RLCD_FRAME_BYTES];
static uint8_t frame_partial_header[RLCD_FRAME_BYTES];
static uint8_t frame_duplicate_names[RLCD_FRAME_BYTES];
static uint8_t frame_feed_lost_packed[RLCD_FRAME_BYTES];
static uint8_t model_before_rejection[sizeof(dashboard_motion_t)];

static dashboard_motion_sample_t sample(const char *id, const char *project,
                                        const char *provider, const char *short_id,
                                        dashboard_work_t work, dashboard_health_t health,
                                        bool age_known, uint64_t entered,
                                        uint64_t episode)
{
    return (dashboard_motion_sample_t){
        .logical_id = id,
        .project = project,
        .provider = provider,
        .short_id = short_id,
        .work = work,
        .health = health,
        .state_age_known = age_known,
        .state_entered_ms = entered,
        .state_episode = episode,
    };
}

static void apply_ok(dashboard_motion_t *motion,
                     const dashboard_motion_sample_t *samples, size_t count,
                     uint64_t now_ms)
{
    const dashboard_motion_snapshot_t snapshot = {samples, count};
    assert(dashboard_motion_apply(motion, &snapshot, now_ms) == DASHBOARD_MOTION_APPLIED);
}

static bool pixel(const uint8_t *frame, int x, int y)
{
    const unsigned inverted_y = RLCD_HEIGHT - 1 - (unsigned)y;
    const size_t slot = ((unsigned)x / 2) * (RLCD_HEIGHT / 4) + inverted_y / 4;
    const uint8_t bit = (uint8_t)(1u << (7 - (inverted_y % 4) * 2 - (x % 2)));
    return (frame[slot] & bit) != 0;
}

static void render_at(dashboard_motion_t *motion, uint64_t now_ms, uint8_t *output)
{
    dashboard_motion_tick(motion, now_ms);
    memset(guarded, 0x6b, sizeof(guarded));
    dashboard_motion_render(motion, guarded + 1);
    assert(guarded[0] == 0x6b && guarded[RLCD_FRAME_BYTES + 1] == 0x6b);
    memcpy(output, guarded + 1, RLCD_FRAME_BYTES);
}

static void save_pbm(const char *directory, const char *name, const uint8_t *frame)
{
    char path[4096];
    const int length = snprintf(path, sizeof(path), "%s/%s.pbm", directory, name);
    assert(length > 0 && (size_t)length < sizeof(path));
    FILE *out = fopen(path, "wb");
    if (!out) { perror(path); exit(1); }
    assert(fprintf(out, "P4\n%d %d\n", RLCD_WIDTH, RLCD_HEIGHT) > 0);
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        for (int x = 0; x < RLCD_WIDTH; x += 8) {
            uint8_t pixels = 0;
            for (int i = 0; i < 8; ++i)
                if (!pixel(frame, x + i, y)) pixels |= (uint8_t)(1u << (7 - i));
            assert(fputc(pixels, out) != EOF);
        }
    }
    assert(fclose(out) == 0);
}

static void assert_order(const dashboard_motion_t *motion,
                         const char *const *ids, size_t count)
{
    assert(dashboard_motion_count(motion) == count);
    for (size_t i = 0; i < count; ++i)
        assert(strcmp(dashboard_motion_identity_at(motion, i), ids[i]) == 0);
}

static int track_index(const dashboard_motion_t *motion, const char *logical_id)
{
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion->tracks[i].used &&
            strcmp(motion->tracks[i].logical_id, logical_id) == 0) return (int)i;
    return -1;
}

static void assert_loss_snapped(const dashboard_motion_t *motion)
{
    assert(!dashboard_motion_active(motion));
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        const dashboard_motion_track_t *track = &motion->tracks[i];
        if (!track->used) continue;
        assert(track->y_q8 == track->target_y_q8);
        assert(track->start_y_q8 == track->target_y_q8);
        assert(track->direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
        assert(!track->exiting || track->y_q8 < DASHBOARD_MOTION_BODY_BOTTOM * 256);
    }
}

static bool band_has_ink(const uint8_t *frame, int x0, int x1, int y0, int y1)
{
    for (int y = y0; y < y1; ++y)
        for (int x = x0; x < x1; ++x)
            if (!pixel(frame, x, y)) return true;
    return false;
}

static void assert_band_white(const uint8_t *frame, int x0, int x1,
                              int y0, int y1)
{
    for (int y = y0; y < y1; ++y)
        for (int x = x0; x < x1; ++x)
            assert(pixel(frame, x, y));
}

static bool band_differs(const uint8_t *left, const uint8_t *right,
                         int x0, int x1, int y0, int y1)
{
    for (int y = y0; y < y1; ++y)
        for (int x = x0; x < x1; ++x)
            if (pixel(left, x, y) != pixel(right, x, y)) return true;
    return false;
}

static void assert_band_equal(const uint8_t *left, const uint8_t *right,
                              int x0, int x1, int y0, int y1)
{
    assert(!band_differs(left, right, x0, x1, y0, y1));
}

static void test_priority_age_and_identity(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/a", "A", "CODEX", "0001", DASH_NEEDS_INPUT, DASH_CURRENT, true, 10000, 1),
        sample("claude@host/b", "B", "CLAUDE", "0002", DASH_ERROR, DASH_CURRENT, true, 20000, 1),
        sample("claude@host/c", "C", "CLAUDE", "0003", DASH_SETTLED, DASH_CURRENT, true, 5000, 1),
        sample("codex@host/d", "D", "CODEX", "0004", DASH_INTERRUPTED, DASH_CURRENT, true, 7000, 1),
        sample("codex@host/e", "E", "CODEX", "0005", DASH_WORKING, DASH_CURRENT, true, 1000, 1),
        sample("claude@host/f", "F", "CLAUDE", "0006", DASH_WORKING, DASH_CURRENT, true, 50000, 1),
        sample("codex@host/g", "G", "CODEX", "0007", DASH_UNKNOWN, DASH_CURRENT, false, 0, 1),
        sample("claude@host/h", "H", "CLAUDE", "0008", DASH_WORKING, DASH_STALE, true, 100, 1),
        sample("codex@host/i", "I", "CODEX", "0009", DASH_WORKING, DASH_CURRENT, false, 0, 1),
    };
    const char *const expected[] = {
        "codex@host/a", "claude@host/b", "claude@host/c", "codex@host/d",
        "codex@host/e", "claude@host/f", "codex@host/i", "codex@host/g",
        "claude@host/h",
    };
    apply_ok(&motion, items, sizeof(items) / sizeof(items[0]), 100000);
    assert_order(&motion, expected, sizeof(expected) / sizeof(expected[0]));
    assert(!dashboard_motion_active(&motion));
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used)
            assert(motion.tracks[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    assert(dashboard_motion_position_y(&motion, expected[0]) == DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_position_y(&motion, expected[2]) == DASHBOARD_MOTION_BODY_TOP + 48);
    assert(dashboard_motion_position_y(&motion, expected[4]) == DASHBOARD_MOTION_BODY_TOP + 96);
    assert(dashboard_motion_position_y(&motion, expected[7]) == DASHBOARD_MOTION_BODY_TOP + 168);
    assert(dashboard_motion_position_y(&motion, expected[8]) == DASHBOARD_MOTION_BODY_TOP + 192);

    // Full logical IDs distinguish same-project entries; project/short ID do not.
    dashboard_motion_sample_t same_project[] = {
        sample("codex@host/project/core", "same-project", "CODEX", "SAME", DASH_WORKING, DASH_CURRENT, true, 1000, 1),
        sample("claude@host/project/ui", "same-project", "CLAUDE", "SAME", DASH_WORKING, DASH_CURRENT, true, 1000, 1),
    };
    static dashboard_motion_t identities;
    dashboard_motion_init(&identities);
    apply_ok(&identities, same_project, 2, 10000);
    assert_order(&identities, (const char *const[]){"codex@host/project/core", "claude@host/project/ui"}, 2);
}

static void test_ties_reset_and_atomic_rejection(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/first", "same", "CODEX", "SAME", DASH_WORKING, DASH_CURRENT, true, 100, 7),
        sample("claude@host/second", "same", "CLAUDE", "SAME", DASH_WORKING, DASH_CURRENT, true, 100, 7),
    };
    apply_ok(&motion, items, 2, 200);
    const char *const ties[] = {"codex@host/first", "claude@host/second"};
    assert_order(&motion, ties, 2);
    dashboard_motion_sample_t reordered[] = {items[1], items[0]};
    reordered[0].state_entered_ms = 50; // Same episode: repeated polling cannot reset age.
    apply_ok(&motion, reordered, 2, 9000);
    assert_order(&motion, ties, 2);
    uint64_t entered = 0;
    assert(dashboard_motion_state_entry(&motion, ties[0], &entered) && entered == 100);
    assert(!dashboard_motion_active(&motion));

    const uint64_t old_now = motion.now_ms;
    const uint64_t old_last_healthy = motion.last_healthy_update_ms;
    const bool old_last_healthy_known = motion.last_healthy_update_known;
    const size_t old_count = motion.count;
    memcpy(model_before_rejection, &motion, sizeof(motion));
    dashboard_motion_sample_t duplicates[] = {items[0], items[0]};
    const dashboard_motion_snapshot_t duplicate_snapshot = {duplicates, 2};
    assert(dashboard_motion_apply(&motion, &duplicate_snapshot, 20000) ==
           DASHBOARD_MOTION_REJECTED_INVALID);
    assert(motion.now_ms == old_now && motion.count == old_count);
    assert(motion.last_healthy_update_ms == old_last_healthy &&
           motion.last_healthy_update_known == old_last_healthy_known);
    assert(memcmp(model_before_rejection, &motion, sizeof(motion)) == 0);
    assert_order(&motion, ties, 2);
    dashboard_motion_sample_t over_capacity[DASHBOARD_MOTION_CAPACITY];
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i) over_capacity[i] = items[0];
    const dashboard_motion_snapshot_t too_many = {
        .sessions = over_capacity,
        .count = DASHBOARD_MOTION_CAPACITY + 1,
    };
    assert(dashboard_motion_apply(&motion, &too_many, 20000) ==
           DASHBOARD_MOTION_REJECTED_CAPACITY);
    assert(motion.now_ms == old_now && motion.count == old_count);
    assert(motion.last_healthy_update_ms == old_last_healthy &&
           motion.last_healthy_update_known == old_last_healthy_known);
    assert(memcmp(model_before_rejection, &motion, sizeof(motion)) == 0);
    assert_order(&motion, ties, 2);

    items[0].work = DASH_SETTLED;
    items[0].state_episode = 8;
    items[0].state_entered_ms = 8500;
    items[1].state_entered_ms = 50;
    apply_ok(&motion, items, 2, 9000);
    assert(dashboard_motion_state_entry(&motion, ties[0], &entered) && entered == 8500);
}

static void test_transitions_and_stationary_chrome(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/wait", "wait", "CODEX", "WAit", DASH_NEEDS_INPUT, DASH_CURRENT, true, 900, 1),
        sample("claude@host/run", "run", "CLAUDE", "RUN1", DASH_WORKING, DASH_CURRENT, true, 800, 1),
    };
    apply_ok(&motion, items, 2, 1000);
    render_at(&motion, 1000, frame_initial);
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") == DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_position_y(&motion, "claude@host/run") ==
           DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT);

    // Resolved wait updates its icon/style at apply time while it moves.
    items[0].work = DASH_WORKING;
    items[0].state_episode = 2;
    items[0].state_entered_ms = 1000;
    items[1].work = DASH_NEEDS_INPUT;
    items[1].state_episode = 2;
    items[1].state_entered_ms = 1000;
    apply_ok(&motion, items, 2, 1000);
    assert(strcmp(dashboard_motion_identity_at(&motion, 0), "claude@host/run") == 0);
    assert(dashboard_motion_active(&motion));
    render_at(&motion, 1180, frame_halfway);
    const int run_y = dashboard_motion_position_y(&motion, "claude@host/run");
    const int wait_y = dashboard_motion_position_y(&motion, "codex@host/wait");
    assert(run_y == DASHBOARD_MOTION_BODY_TOP + 6);
    assert(wait_y == DASHBOARD_MOTION_BODY_TOP + 18);

    // Motion header/footer stay stationary while body rows transition.
    render_at(&motion, 1360, frame_endpoint);
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        if (y >= DASHBOARD_MOTION_BODY_TOP && y < DASHBOARD_MOTION_BODY_BOTTOM) continue;
        for (int x = 0; x < RLCD_WIDTH; ++x)
            assert(pixel(frame_halfway, x, y) == pixel(frame_endpoint, x, y));
    }
    assert(!dashboard_motion_active(&motion));
    assert(dashboard_motion_position_y(&motion, "claude@host/run") == DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") ==
           DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT);
}

static void test_overlap_priority_and_icon_polarity(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/core", "agent-observer / core", "CODEX", "AAAA", DASH_NEEDS_INPUT, DASH_CURRENT, true, 0, 1),
        sample("claude@host/ui", "agent-observer / ui", "CLAUDE", "BBBB", DASH_WORKING, DASH_CURRENT, true, 0, 1),
        sample("codex@host/error", "homelab", "CODEX", "CCCC", DASH_ERROR, DASH_CURRENT, true, 0, 1),
    };
    apply_ok(&motion, items, 3, 1000);
    render_at(&motion, 1000, expected_frame);
    // Full inverse rows contain white marks directly on their black background.
    assert(!pixel(expected_frame, 22, DASHBOARD_MOTION_BODY_TOP + 2));
    assert(pixel(expected_frame, 12, DASHBOARD_MOTION_BODY_TOP + 8));
    assert(!pixel(expected_frame, 22, DASHBOARD_MOTION_BODY_TOP + 26));
    assert(pixel(expected_frame, 10, DASHBOARD_MOTION_BODY_TOP + 32));

    items[0].work = DASH_WORKING;
    items[0].state_episode++;
    items[0].state_entered_ms = 1000;
    items[1].work = DASH_NEEDS_INPUT;
    items[1].state_episode++;
    items[1].state_entered_ms = 1000;
    apply_ok(&motion, items, 3, 1000);
    render_at(&motion, 1100, frame_overlap);
    // The upward-moving wait is drawn over the downward-moving run row.
    assert(!pixel(frame_overlap, 22, DASHBOARD_MOTION_BODY_TOP + 26));
}

static void render_rows(const dashboard_motion_render_row_t *rows,
                       size_t row_count, uint8_t *frame)
{
    const dashboard_motion_render_t view = {
        .roster = {.sessions = NULL, .count = 0, .feed_health = DASH_CURRENT},
        .rows = rows,
        .row_count = row_count,
        .feed_lost = false,
    };
    dashboard_draw_motion(frame, &view);
}

static void test_row_icon_polarity(void)
{
    // Ink samples belong to each mark. Blank tile corners must retain the
    // row background, so white rows cannot accidentally acquire black boxes.
    const struct {
        dashboard_work_t work;
        dashboard_health_t row_health, feed_health;
        bool inverse;
        int ink_col, ink_row;
    } cases[] = {
        {DASH_WORKING, DASH_CURRENT, DASH_CURRENT, false, 1, 1},
        {DASH_SETTLED, DASH_CURRENT, DASH_CURRENT, true, 4, 2},
        {DASH_INTERRUPTED, DASH_CURRENT, DASH_CURRENT, true, 4, 2},
        {DASH_UNKNOWN, DASH_CURRENT, DASH_CURRENT, false, 2, 1},
        {DASH_NEEDS_INPUT, DASH_CURRENT, DASH_CURRENT, true, 2, 1},
        {DASH_ERROR, DASH_CURRENT, DASH_CURRENT, true, 1, 1},
        {DASH_NEEDS_INPUT, DASH_STALE, DASH_CURRENT, false, 2, 1},
        {DASH_NEEDS_INPUT, DASH_CURRENT, DASH_STALE, false, 2, 1},
        {DASH_WORKING, DASH_CURRENT, DASH_UNAVAILABLE, false, 2, 1},
    };
    for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        const dashboard_session_t session = {
            .project = "", .provider = "CODEX", .detail = "?",
            .work = cases[i].work, .health = cases[i].row_health,
        };
        const int scale = 2;
        const int height = DASHBOARD_MOTION_ROW_HEIGHT;
        const int top = 100 + (height - 6 * scale) / 2;
        const dashboard_motion_render_row_t row = {
            .session = &session, .y = 100, .height = height,
        };
        const dashboard_motion_render_t view = {
            .roster = {.feed_health = cases[i].feed_health},
            .rows = &row, .row_count = 1,
            .feed_lost = cases[i].feed_health != DASH_CURRENT,
        };
        dashboard_draw_motion(expected_frame, &view);
        for (int dy = 0; dy < scale; ++dy)
            for (int dx = 0; dx < scale; ++dx)
                assert(pixel(expected_frame, 8 + cases[i].ink_col * scale + dx,
                             top + cases[i].ink_row * scale + dy) == cases[i].inverse);
        assert(pixel(expected_frame, 8, top) == !cases[i].inverse);
        assert(pixel(expected_frame, 8 + 6 * scale - 1, top) == !cases[i].inverse);
        assert(pixel(expected_frame, 8, top + 6 * scale - 1) == !cases[i].inverse);
        assert(pixel(expected_frame, 8 + 6 * scale - 1,
                     top + 6 * scale - 1) == !cases[i].inverse);
    }
}

static void test_state_polarity_and_slow_flash(const char *directory)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/question", "question", "CODEX", "ASK1", DASH_NEEDS_INPUT,
               DASH_CURRENT, false, 0, 1),
        sample("claude@host/error", "error", "CLAUDE", "ERR1", DASH_ERROR,
               DASH_CURRENT, false, 0, 1),
        sample("codex@host/wait", "waiting", "CODEX", "WAIT", DASH_SETTLED,
               DASH_CURRENT, false, 0, 1),
        sample("claude@host/work", "working", "CLAUDE", "WORK", DASH_WORKING,
               DASH_CURRENT, false, 0, 1),
    };
    apply_ok(&motion, items, 4, 1000);
    assert(dashboard_motion_flashing(&motion)); // Existing blocked rows also flash.
    assert(!dashboard_motion_active(&motion)); // No movement is needed to flash.
    render_at(&motion, 1000, frame_initial);
    save_pbm(directory, "blocked-flash-black", frame_initial);
    render_at(&motion, 1499, frame_endpoint);
    assert(memcmp(frame_initial, frame_endpoint, RLCD_FRAME_BYTES) == 0);
    render_at(&motion, 1500, frame_halfway);
    save_pbm(directory, "blocked-flash-white", frame_halfway);
    // Only the two blocked rows invert, including their text and icons.
    // Waiting stays inverse and working stays normal in both halves.
    for (int y = 0; y < RLCD_HEIGHT; ++y)
        for (int x = 0; x < RLCD_WIDTH; ++x) {
            const bool blocked_tile = x >= 8 && x < 392 && y >= 24 && y < 72;
            assert(pixel(frame_initial, x, y) ==
                   (pixel(frame_halfway, x, y) != blocked_tile));
        }
    assert(!pixel(frame_halfway, 22, 74)); // Waiting background remains black.
    assert(pixel(frame_halfway, 22, 98)); // Working background remains white.
    apply_ok(&motion, items, 4, 1600); // Repeated snapshots retain the shared phase.
    render_at(&motion, 1600, frame_endpoint);
    assert(memcmp(frame_halfway, frame_endpoint, RLCD_FRAME_BYTES) == 0);
    render_at(&motion, 1999, frame_endpoint);
    assert(memcmp(frame_halfway, frame_endpoint, RLCD_FRAME_BYTES) == 0);
    render_at(&motion, 2000, frame_endpoint);
    assert(memcmp(frame_initial, frame_endpoint, RLCD_FRAME_BYTES) == 0);
    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 2100) == DASHBOARD_MOTION_APPLIED);
    assert(!dashboard_motion_flashing(&motion));
    render_at(&motion, 2100, frame_initial);
    render_at(&motion, 2600, frame_halfway);
    assert_band_equal(frame_initial, frame_halfway, 8, 392, 24, 288);
    assert(pixel(frame_halfway, 22, 74)); // Cached waiting claims lose inverse styling.
    apply_ok(&motion, items, 4, 2700);
    assert(dashboard_motion_flashing(&motion));
    items[0].work = DASH_SETTLED;
    items[1].work = DASH_WORKING;
    ++items[0].state_episode;
    ++items[1].state_episode;
    apply_ok(&motion, items, 4, 2800);
    assert(!dashboard_motion_flashing(&motion)); // Resolution stops further flash frames.
    for (size_t i = 0; i < 4; ++i) items[i].health = DASH_STALE;
    items[0].work = DASH_NEEDS_INPUT;
    apply_ok(&motion, items, 4, 2900);
    assert(!dashboard_motion_flashing(&motion)); // Stale evidence cannot flash.
}

static void test_direction_tier_compositing(void)
{
    const dashboard_session_t down = {
        .project = "DOWN", .provider = "CODEX", .short_id = "DOWN",
        .detail = "1s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t stationary = {
        .project = "STILL", .provider = "CLAUDE", .short_id = "STIL",
        .detail = "2s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t up = {
        .project = "UP", .provider = "CODEX", .short_id = "UPUP",
        .detail = "3s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_motion_render_row_t down_row = {
        .session = &down, .y = 100,
        .height = DASHBOARD_MOTION_ROW_HEIGHT,
        .direction = DASHBOARD_MOTION_DIRECTION_DOWN,
    };
    const dashboard_motion_render_row_t stationary_row = {
        .session = &stationary, .y = 100,
        .height = DASHBOARD_MOTION_ROW_HEIGHT,
        .direction = DASHBOARD_MOTION_DIRECTION_STATIONARY,
    };
    const dashboard_motion_render_row_t up_row = {
        .session = &up, .y = 100,
        .height = DASHBOARD_MOTION_ROW_HEIGHT,
        .direction = DASHBOARD_MOTION_DIRECTION_UP,
    };

    render_rows(&down_row, 1, frame_tier_down);
    render_rows(&stationary_row, 1, frame_tier_stationary);
    render_rows(&up_row, 1, frame_tier_up);

    // Input order is intentionally up, down, stationary. Tier order is
    // downward first, stationary second, upward last.
    const dashboard_motion_render_row_t mixed[] = {
        up_row, down_row, stationary_row,
    };
    render_rows(mixed, sizeof(mixed) / sizeof(mixed[0]), expected_frame);
    assert(memcmp(expected_frame, frame_tier_up, RLCD_FRAME_BYTES) == 0);

    const dashboard_motion_render_row_t down_then_stationary[] = {
        stationary_row, down_row,
    };
    render_rows(down_then_stationary,
                sizeof(down_then_stationary) / sizeof(down_then_stationary[0]),
                expected_frame);
    assert(memcmp(expected_frame, frame_tier_stationary, RLCD_FRAME_BYTES) == 0);

    const dashboard_session_t first_up = {
        .project = "FIRST", .provider = "CODEX", .short_id = "FIRS",
        .detail = "1s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t second_up = {
        .project = "SECOND", .provider = "CLAUDE", .short_id = "SECO",
        .detail = "2s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_motion_render_row_t ordered_up[] = {
        {.session = &first_up, .y = 100,
         .direction = DASHBOARD_MOTION_DIRECTION_UP},
        {.session = &second_up, .y = 100,
         .direction = DASHBOARD_MOTION_DIRECTION_UP},
    };
    const dashboard_motion_render_row_t reversed_up[] = {
        ordered_up[1], ordered_up[0],
    };
    const dashboard_motion_render_row_t second_only = ordered_up[1];
    const dashboard_motion_render_row_t first_only = ordered_up[0];
    render_rows(&second_only, 1, frame_tier_stationary);
    render_rows(ordered_up, 2, expected_frame);
    assert(memcmp(expected_frame, frame_tier_stationary, RLCD_FRAME_BYTES) == 0);
    render_rows(&first_only, 1, frame_tier_down);
    render_rows(reversed_up, 2, expected_frame);
    assert(memcmp(expected_frame, frame_tier_down, RLCD_FRAME_BYTES) == 0);
}

static void make_progress_fixture(dashboard_motion_t *motion,
                                  dashboard_motion_sample_t samples[3],
                                  uint64_t now_ms)
{
    dashboard_motion_init(motion);
    samples[0] = sample("codex@host/progress/a", "a", "CODEX", "AAAA",
                        DASH_NEEDS_INPUT, DASH_CURRENT, true, now_ms, 1);
    samples[1] = sample("claude@host/progress/b", "b", "CLAUDE", "BBBB",
                        DASH_WORKING, DASH_CURRENT, true, now_ms, 1);
    samples[2] = sample("codex@host/progress/c", "c", "CODEX", "CCCC",
                        DASH_SETTLED, DASH_CURRENT, true, now_ms, 1);
    apply_ok(motion, samples, 3, now_ms);
    samples[0].work = DASH_WORKING;
    samples[0].state_episode++;
    samples[1].work = DASH_SETTLED;
    samples[1].state_episode++;
    samples[2].work = DASH_NEEDS_INPUT;
    samples[2].state_episode++;
    for (size_t i = 0; i < 3; ++i) samples[i].state_entered_ms = now_ms;
    apply_ok(motion, samples, 3, now_ms);
}

static void test_shared_progress_directions_and_endpoints(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_sample_t items[3];
    make_progress_fixture(&motion, items, 1000);
    const int a = track_index(&motion, "codex@host/progress/a");
    const int b = track_index(&motion, "claude@host/progress/b");
    const int c = track_index(&motion, "codex@host/progress/c");
    assert(a >= 0 && b >= 0 && c >= 0);
    assert(motion.tracks[a].start_y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
    assert(motion.tracks[a].target_y_q8 == (DASHBOARD_MOTION_BODY_TOP + 48) * 256);
    assert(motion.tracks[b].start_y_q8 == (DASHBOARD_MOTION_BODY_TOP + 48) * 256);
    assert(motion.tracks[b].target_y_q8 == (DASHBOARD_MOTION_BODY_TOP + 24) * 256);
    assert(motion.tracks[c].start_y_q8 == (DASHBOARD_MOTION_BODY_TOP + 24) * 256);
    assert(motion.tracks[c].target_y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
    assert(motion.tracks[a].direction == DASHBOARD_MOTION_DIRECTION_DOWN);
    assert(motion.tracks[b].direction == DASHBOARD_MOTION_DIRECTION_UP);
    assert(motion.tracks[c].direction == DASHBOARD_MOTION_DIRECTION_UP);

    // At 180/360 ms, ease-out progress is exactly 0.75 for every moving row.
    dashboard_motion_tick(&motion, 1180);
    assert(motion.tracks[a].y_q8 == (DASHBOARD_MOTION_BODY_TOP + 36) * 256);
    assert(motion.tracks[b].y_q8 == (DASHBOARD_MOTION_BODY_TOP + 30) * 256);
    assert(motion.tracks[c].y_q8 == (DASHBOARD_MOTION_BODY_TOP + 6) * 256);
    assert(motion.tracks[a].target_y_q8 - motion.tracks[a].start_y_q8 == 48 * 256);
    assert(motion.tracks[b].target_y_q8 - motion.tracks[b].start_y_q8 == -24 * 256);

    dashboard_motion_tick(&motion, 1360);
    assert(!dashboard_motion_active(&motion));
    assert(motion.tracks[a].y_q8 == (DASHBOARD_MOTION_BODY_TOP + 48) * 256);
    assert(motion.tracks[b].y_q8 == (DASHBOARD_MOTION_BODY_TOP + 24) * 256);
    assert(motion.tracks[c].y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
    assert(motion.tracks[a].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    assert(motion.tracks[b].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    assert(motion.tracks[c].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
}

static void test_retarget_preserves_current_pose(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_sample_t items[3];
    make_progress_fixture(&motion, items, 2000);
    const int a = track_index(&motion, "codex@host/progress/a");
    const int b = track_index(&motion, "claude@host/progress/b");
    const int c = track_index(&motion, "codex@host/progress/c");
    assert(a >= 0 && b >= 0 && c >= 0);
    dashboard_motion_tick(&motion, 2100);
    const int32_t current[] = {
        motion.tracks[a].y_q8, motion.tracks[b].y_q8, motion.tracks[c].y_q8,
    };

    items[2].work = DASH_WORKING;
    ++items[2].state_episode;
    items[2].state_entered_ms = 2100;
    apply_ok(&motion, items, 3, 2100);
    assert(motion.burst_start_ms == 2000);
    assert(motion.motion_start_ms == 2100);
    assert(motion.tracks[a].y_q8 == current[0]);
    assert(motion.tracks[b].y_q8 == current[1]);
    assert(motion.tracks[c].y_q8 == current[2]);
    assert(motion.tracks[a].start_y_q8 == current[0]);
    assert(motion.tracks[b].start_y_q8 == current[1]);
    assert(motion.tracks[c].start_y_q8 == current[2]);
    assert(motion.tracks[a].direction == DASHBOARD_MOTION_DIRECTION_DOWN);
    assert(motion.tracks[b].direction == DASHBOARD_MOTION_DIRECTION_UP);
    assert(motion.tracks[c].direction == DASHBOARD_MOTION_DIRECTION_DOWN);

    dashboard_motion_tick(&motion, 2280);
    assert(motion.tracks[a].y_q8 == current[0] +
           (motion.tracks[a].target_y_q8 - current[0]) * 3 / 4);
    assert(motion.tracks[b].y_q8 == current[1] +
           (motion.tracks[b].target_y_q8 - current[1]) * 3 / 4);
    assert(motion.tracks[c].y_q8 == current[2] +
           (motion.tracks[c].target_y_q8 - current[2]) * 3 / 4);
    dashboard_motion_tick(&motion, 2460);
    assert(!dashboard_motion_active(&motion));
    assert(motion.tracks[a].y_q8 == motion.tracks[a].target_y_q8);
    assert(motion.tracks[b].y_q8 == motion.tracks[b].target_y_q8);
    assert(motion.tracks[c].y_q8 == motion.tracks[c].target_y_q8);
    assert(motion.tracks[a].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    assert(motion.tracks[b].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    assert(motion.tracks[c].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
}

static void test_clipping_ghosts_and_feed_loss(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/a", "alpha", "CODEX", "AAAA", DASH_NEEDS_INPUT, DASH_CURRENT, true, 0, 1),
        sample("claude@host/b", "beta", "CLAUDE", "BBBB", DASH_WORKING, DASH_CURRENT, true, 0, 1),
    };
    apply_ok(&motion, items, 2, 1000);

    dashboard_motion_render_row_t edge_row = {.session = &(dashboard_session_t){
        .project = "edge", .provider = "CODEX", .short_id = "EDGE", .detail = "1s",
        .work = DASH_NEEDS_INPUT, .health = DASH_CURRENT,
    }, .y = DASHBOARD_MOTION_BODY_BOTTOM - 6, .height = DASHBOARD_MOTION_ROW_HEIGHT};
    const dashboard_motion_render_t base = {
        .roster = {.sessions = NULL, .count = 0, .feed_health = DASH_CURRENT},
        .rows = NULL, .row_count = 0, .feed_lost = false,
    };
    memset(guarded, 0x4d, sizeof(guarded));
    dashboard_draw_motion(guarded + 1, &base);
    memcpy(expected_frame, guarded + 1, RLCD_FRAME_BYTES);
    const dashboard_motion_render_t edge = {
        .roster = base.roster, .rows = &edge_row, .row_count = 1,
        .feed_lost = false,
    };
    dashboard_draw_motion(guarded + 1, &edge);
    assert(guarded[0] == 0x4d && guarded[RLCD_FRAME_BYTES + 1] == 0x4d);
    assert(!pixel(guarded + 1, 22, DASHBOARD_MOTION_BODY_BOTTOM - 2));
    assert(pixel(expected_frame, 22, DASHBOARD_MOTION_BODY_BOTTOM - 2));
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        if (y >= DASHBOARD_MOTION_BODY_TOP && y < DASHBOARD_MOTION_BODY_BOTTOM) continue;
        for (int x = 0; x < RLCD_WIDTH; ++x)
            assert(pixel(expected_frame, x, y) == pixel(guarded + 1, x, y));
    }

    dashboard_motion_tick(&motion, 1100);
    dashboard_motion_sample_t only_b[] = {items[1]};
    apply_ok(&motion, only_b, 1, 1100);
    int a_track = -1;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used && strcmp(motion.tracks[i].logical_id, "codex@host/a") == 0)
            a_track = (int)i;
    assert(a_track >= 0 && motion.tracks[a_track].exiting);
    assert(motion.tracks[a_track].health == DASH_UNAVAILABLE);
    assert(motion.tracks[a_track].work == DASH_UNKNOWN);
    assert(!motion.tracks[a_track].state_age_known);
    assert(motion.tracks[a_track].row_height == DASHBOARD_MOTION_ROW_HEIGHT);
    // Feed loss during the exit movement commits the accepted packed target,
    // preserves active row heights, and clears departed ghosts at the edge.
    dashboard_motion_tick(&motion, 1200);
    const int b_track = track_index(&motion, "claude@host/b");
    assert(b_track >= 0);
    const uint8_t frozen_b_height = motion.tracks[b_track].row_height;
    const size_t frozen_visible_count = dashboard_motion_visible_count(&motion);
    const uint64_t accepted_update = motion.last_healthy_update_ms;
    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 1200) ==
           DASHBOARD_MOTION_APPLIED);
    assert(!dashboard_motion_active(&motion));
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used) {
            assert(motion.tracks[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
            assert(motion.tracks[i].y_q8 == motion.tracks[i].target_y_q8);
            assert(motion.tracks[i].start_y_q8 == motion.tracks[i].target_y_q8);
        }
    assert(track_index(&motion, "codex@host/a") < 0);
    assert(motion.last_healthy_update_known &&
           motion.last_healthy_update_ms == accepted_update && accepted_update == 1100);
    assert(dashboard_motion_position_y(&motion, "claude@host/b") ==
           DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_feed_lost(&motion, DASH_UNAVAILABLE, 1400) ==
           DASHBOARD_MOTION_APPLIED);
    assert(motion.last_healthy_update_ms == accepted_update);
    dashboard_motion_tick(&motion, 1450);
    assert(dashboard_motion_position_y(&motion, "claude@host/b") ==
           DASHBOARD_MOTION_BODY_TOP);
    assert(motion.tracks[b_track].row_height == frozen_b_height);
    assert(dashboard_motion_visible_count(&motion) == frozen_visible_count);
    assert(dashboard_motion_overflow_count(&motion) == 0);
    assert(dashboard_motion_hidden_blocked_count(&motion) == 0);
    render_at(&motion, 1450, frame_feed_lost);
    memcpy(frame_feed_lost_packed, frame_feed_lost, sizeof(frame_feed_lost));
    assert(motion.render_age[0][0] == '?');

    only_b[0].work = DASH_SETTLED;
    only_b[0].state_episode++;
    only_b[0].state_entered_ms = 1500;
    apply_ok(&motion, only_b, 1, 1500);
    assert(dashboard_motion_feed_health(&motion) == DASH_CURRENT);
    assert(!dashboard_motion_active(&motion));
    assert(motion.tracks[b_track].row_height == DASHBOARD_MOTION_ROW_HEIGHT);
}

static void test_urgency_geometry_and_admission(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_sample_t items[DASHBOARD_MOTION_CAPACITY];
    char ids[DASHBOARD_MOTION_CAPACITY][40];
    dashboard_motion_init(&motion);
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i) {
        snprintf(ids[i], sizeof(ids[i]), "codex@host/density-%02zu", i);
        items[i] = sample(ids[i], "density", "CODEX", "SAME",
                          DASH_WORKING, DASH_CURRENT, true, i, 1);
    }
    apply_ok(&motion, items, DASHBOARD_MOTION_CAPACITY, 1000);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    assert(dashboard_motion_position_y(&motion, ids[10]) == 264);

    // Promoting the final worker admits it first and displaces the last
    // visible worker, while every row retains the same height.
    items[31].work = DASH_NEEDS_INPUT;
    items[31].state_entered_ms = 1000;
    ++items[31].state_episode;
    apply_ok(&motion, items, 32, 1000);
    assert(strcmp(dashboard_motion_identity_at(&motion, 0), ids[31]) == 0);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    const int displaced = track_index(&motion, ids[10]);
    assert(!motion.tracks[displaced].admitted);
    assert(motion.tracks[displaced].y_q8 == 264 * 256);
    assert(motion.tracks[displaced].target_y_q8 == DASHBOARD_MOTION_BODY_BOTTOM * 256);
    assert(motion.tracks[displaced].direction == DASHBOARD_MOTION_DIRECTION_DOWN);
    dashboard_motion_tick(&motion, 1360);
    assert(motion.tracks[displaced].y_q8 == DASHBOARD_MOTION_BODY_BOTTOM * 256);

    // Mixed states still admit eleven complete rows in urgency order.
    dashboard_motion_init(&motion);
    for (size_t i = 0; i < 32; ++i)
        items[i].work = i < 2 ? DASH_NEEDS_INPUT : i < 6 ? DASH_SETTLED : DASH_WORKING;
    apply_ok(&motion, items, 32, 2000);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    assert(dashboard_motion_hidden_blocked_count(&motion) == 0);
    assert(dashboard_motion_position_y(&motion, ids[0]) == DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_position_y(&motion, ids[2]) == DASHBOARD_MOTION_BODY_TOP + 48);
    assert(dashboard_motion_position_y(&motion, ids[6]) == DASHBOARD_MOTION_BODY_TOP + 144);
    assert(dashboard_motion_position_y(&motion, ids[10]) == 264);

    dashboard_motion_init(&motion);
    for (size_t i = 0; i < 32; ++i) items[i].work = DASH_SETTLED;
    apply_ok(&motion, items, 32, 2000);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    assert(dashboard_motion_position_y(&motion, ids[10]) == 264);
    assert(dashboard_motion_position_y(&motion, ids[11]) == DASHBOARD_MOTION_BODY_BOTTOM);

    dashboard_motion_init(&motion);
    for (size_t i = 0; i < 32; ++i) items[i].work = i % 2 ? DASH_ERROR : DASH_NEEDS_INPUT;
    apply_ok(&motion, items, 32, 2000);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    assert(dashboard_motion_hidden_blocked_count(&motion) == 21);

    // Unknown evidence uses full geometry at the end of the urgency order.
    dashboard_motion_init(&motion);
    items[0].work = DASH_NEEDS_INPUT;
    items[1].work = DASH_SETTLED;
    items[2].work = DASH_WORKING;
    items[3].work = DASH_UNKNOWN;
    items[3].state_age_known = false;
    apply_ok(&motion, items, 4, 2000);
    assert(dashboard_motion_position_y(&motion, ids[3]) == DASHBOARD_MOTION_BODY_TOP + 72);
    assert(motion.tracks[track_index(&motion, ids[3])].row_height == 24);
}

static void test_uniform_height_changes_and_retarget(void)
{
    static dashboard_motion_t single;
    dashboard_motion_init(&single);
    dashboard_motion_sample_t one = sample("codex@host/height/one", "one", "CODEX", "ONE1",
                                           DASH_WORKING, DASH_CURRENT, true, 0, 1);
    apply_ok(&single, &one, 1, 1000);
    const int one_track = track_index(&single, one.logical_id);
    const dashboard_work_t states[] = {DASH_UNKNOWN, DASH_NEEDS_INPUT, DASH_SETTLED,
                                       DASH_WORKING};
    for (size_t i = 0; i < sizeof(states) / sizeof(states[0]); ++i) {
        one.work = states[i];
        one.state_age_known = states[i] != DASH_UNKNOWN;
        ++one.state_episode;
        apply_ok(&single, &one, 1, 1000 + i * 100);
        assert(single.tracks[one_track].row_height == 24);
        assert(single.tracks[one_track].y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
        assert(!dashboard_motion_active(&single)); // Style changes need no reflow.
    }
    assert(dashboard_motion_feed_lost(&single, DASH_STALE, 1400) ==
           DASHBOARD_MOTION_APPLIED);
    assert(single.tracks[one_track].row_height == 24);
    assert(!dashboard_motion_flashing(&single));

    static dashboard_motion_t retarget;
    dashboard_motion_init(&retarget);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/retarget/a", "a", "CODEX", "AAAA",
               DASH_WORKING, DASH_CURRENT, true, 0, 1),
        sample("claude@host/retarget/b", "b", "CLAUDE", "BBBB",
               DASH_WORKING, DASH_CURRENT, true, 1, 1),
        sample("codex@host/retarget/c", "c", "CODEX", "CCCC",
               DASH_WORKING, DASH_CURRENT, true, 2, 1),
    };
    apply_ok(&retarget, items, 3, 2000);
    items[0].work = DASH_NEEDS_INPUT;
    items[0].state_entered_ms = 2000;
    ++items[0].state_episode;
    apply_ok(&retarget, items, 3, 2000);
    assert(retarget.tracks[track_index(&retarget, items[0].logical_id)].row_height ==
           DASHBOARD_MOTION_ROW_HEIGHT);
    dashboard_motion_tick(&retarget, 2180);
    const int32_t displayed_b = retarget.tracks[track_index(&retarget,
                                             items[1].logical_id)].y_q8;
    items[0].work = DASH_WORKING;
    items[0].state_entered_ms = 2180;
    ++items[0].state_episode;
    apply_ok(&retarget, items, 3, 2180);
    const int first = track_index(&retarget, items[0].logical_id);
    const int second = track_index(&retarget, items[1].logical_id);
    assert(first >= 0 && second >= 0);
    assert(retarget.tracks[first].row_height == DASHBOARD_MOTION_WORKING_ROW_HEIGHT);
    assert(retarget.tracks[second].start_y_q8 == displayed_b);
    assert(retarget.tracks[second].y_q8 == displayed_b);
    assert(retarget.tracks[second].target_y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
    assert(dashboard_motion_active(&retarget));
}

static void test_inactive_removal_and_readmission(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/inactive/session", "session", "CODEX", "SAME",
               DASH_WORKING, DASH_CURRENT, true, 100, 1),
        sample("claude@host/inactive/other", "other", "CLAUDE", "SAME",
               DASH_SETTLED, DASH_CURRENT, true, 200, 1),
    };
    apply_ok(&motion, items, 2, 1000);
    const int original = track_index(&motion, items[0].logical_id);
    assert(original >= 0);
    const uint64_t old_admission = motion.tracks[original].admission_order;
    const uint8_t old_height = motion.tracks[original].row_height;
    apply_ok(&motion, &items[1], 1, 1100); // Healthy absence means inactive.
    assert(motion.tracks[original].exiting);
    assert(!motion.tracks[original].active);
    assert(motion.tracks[original].row_height == old_height);
    assert(motion.tracks[original].work == DASH_UNKNOWN);
    assert(!motion.tracks[original].state_age_known);
    dashboard_motion_tick(&motion, 1460);
    assert(track_index(&motion, items[0].logical_id) < 0);

    items[0].work = DASH_NEEDS_INPUT;
    items[0].state_episode = 2;
    items[0].state_entered_ms = 1500;
    apply_ok(&motion, items, 2, 1500);
    const int readmitted = track_index(&motion, items[0].logical_id);
    assert(readmitted >= 0 && motion.tracks[readmitted].active);
    assert(motion.tracks[readmitted].row_height == DASHBOARD_MOTION_ROW_HEIGHT);
    assert(motion.tracks[readmitted].admission_order > old_admission);
    uint64_t entered = 0;
    assert(dashboard_motion_state_entry(&motion, items[0].logical_id, &entered));
    assert(entered == 1500);

    static dashboard_motion_t reuse;
    dashboard_motion_init(&reuse);
    dashboard_motion_sample_t returning = sample(
        "codex@host/inactive/reused", "reused", "CODEX", "REUS",
        DASH_WORKING, DASH_CURRENT, true, 900, 1);
    apply_ok(&reuse, &returning, 1, 1000);
    const int original_track = track_index(&reuse, returning.logical_id);
    assert(original_track >= 0);
    const uint64_t prior_admission = reuse.tracks[original_track].admission_order;
    assert(reuse.tracks[original_track].row_height ==
           DASHBOARD_MOTION_WORKING_ROW_HEIGHT);

    const dashboard_motion_snapshot_t empty = {.sessions = NULL, .count = 0};
    assert(dashboard_motion_apply(&reuse, &empty, 1100) == DASHBOARD_MOTION_APPLIED);
    assert(reuse.tracks[original_track].exiting);
    dashboard_motion_tick(&reuse, 1200);
    const int32_t exit_pose = reuse.tracks[original_track].y_q8;
    assert(exit_pose > DASHBOARD_MOTION_BODY_TOP * 256);

    returning.work = DASH_NEEDS_INPUT;
    returning.state_episode = 2;
    returning.state_entered_ms = 1150;
    apply_ok(&reuse, &returning, 1, 1200);
    const int reused_track = track_index(&reuse, returning.logical_id);
    assert(reused_track == original_track);
    assert(reuse.tracks[reused_track].active && !reuse.tracks[reused_track].exiting);
    assert(reuse.tracks[reused_track].row_height == DASHBOARD_MOTION_ROW_HEIGHT);
    assert(reuse.tracks[reused_track].admission_order > prior_admission);
    assert(reuse.tracks[reused_track].y_q8 == exit_pose);
    assert(reuse.tracks[reused_track].start_y_q8 == exit_pose);
    assert(reuse.tracks[reused_track].target_y_q8 == DASHBOARD_MOTION_BODY_TOP * 256);
    assert(reuse.tracks[reused_track].direction == DASHBOARD_MOTION_DIRECTION_UP);
    assert(dashboard_motion_active(&reuse));
    assert(dashboard_motion_state_entry(&reuse, returning.logical_id, &entered));
    assert(entered == 1150);
}

static void test_motion_chrome_states(void)
{
    const dashboard_session_t blocked = {
        .project = "blocked", .provider = "CODEX", .short_id = "BLCK",
        .detail = "1m", .work = DASH_NEEDS_INPUT, .health = DASH_CURRENT,
    };
    const dashboard_session_t waiting = {
        .project = "waiting", .provider = "CLAUDE", .short_id = "WAIT",
        .detail = "2m", .work = DASH_SETTLED, .health = DASH_CURRENT,
    };
    const dashboard_session_t working = {
        .project = "working", .provider = "CODEX", .short_id = "WORK",
        .detail = "5s", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t uncertain = {
        .project = "uncertain", .provider = "CODEX", .short_id = "UNKN",
        .detail = "?", .work = DASH_UNKNOWN, .health = DASH_CURRENT,
    };
    const dashboard_session_t cached_error = {
        .project = "cached", .provider = "CLAUDE", .short_id = "CACH",
        .detail = "?", .work = DASH_ERROR, .health = DASH_STALE,
    };
    const dashboard_session_t known[] = {blocked, waiting, working};
    const dashboard_session_t partial[] = {
        blocked, waiting, working, uncertain, cached_error,
    };
    const dashboard_motion_render_row_t known_rows[] = {
        {.session = &blocked, .y = DASHBOARD_MOTION_BODY_TOP,
         .height = DASHBOARD_MOTION_ROW_HEIGHT},
        {.session = &waiting,
         .y = DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT,
         .height = DASHBOARD_MOTION_ROW_HEIGHT},
        {.session = &working,
         .y = DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT * 2,
         .height = DASHBOARD_MOTION_WORKING_ROW_HEIGHT},
    };
    const dashboard_motion_render_row_t partial_rows[] = {
        known_rows[0], known_rows[1], known_rows[2],
        {.session = &uncertain,
         .y = DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT * 2 +
              DASHBOARD_MOTION_WORKING_ROW_HEIGHT,
         .height = DASHBOARD_MOTION_ROW_HEIGHT},
        {.session = &cached_error,
         .y = DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT * 3 +
              DASHBOARD_MOTION_WORKING_ROW_HEIGHT,
         .height = DASHBOARD_MOTION_ROW_HEIGHT},
    };
    const dashboard_motion_render_t known_view = {
        .roster = {.sessions = known, .count = 3, .feed_health = DASH_CURRENT},
        .rows = known_rows,
        .row_count = 3,
    };
    const dashboard_motion_render_t partial_view = {
        .roster = {.sessions = partial, .count = 5, .feed_health = DASH_CURRENT},
        .rows = partial_rows,
        .row_count = 5,
    };
    const dashboard_motion_render_t empty_view = {
        .roster = {.sessions = NULL, .count = 0, .feed_health = DASH_CURRENT},
    };
    uint8_t known_frame[RLCD_FRAME_BYTES], empty_frame[RLCD_FRAME_BYTES];
    dashboard_draw_motion(known_frame, &known_view);
    dashboard_draw_motion(frame_partial_header, &partial_view);
    dashboard_draw_motion(empty_frame, &empty_view);
    // Unknown counts are explicit in the footer; they leave the title and
    // known-state summary unchanged, including its right alignment.
    assert_band_equal(known_frame, frame_partial_header,
                      0, RLCD_WIDTH, 0, DASHBOARD_MOTION_BODY_TOP);
    assert(band_differs(known_frame, frame_partial_header,
                        8, 136, DASHBOARD_MOTION_BODY_BOTTOM, RLCD_HEIGHT));
    assert(band_has_ink(frame_partial_header, 74, 136,
                        DASHBOARD_MOTION_BODY_BOTTOM, RLCD_HEIGHT));
    assert_band_white(frame_partial_header, 0, 8, 0, DASHBOARD_MOTION_BODY_TOP);
    for (int x = 8; x < 392; ++x)
        assert(!pixel(known_frame, x, DASHBOARD_MOTION_BODY_TOP - 3));
    assert_band_white(known_frame, 0, RLCD_WIDTH,
                      DASHBOARD_MOTION_BODY_TOP - 2, DASHBOARD_MOTION_BODY_TOP);
    assert(band_has_ink(known_frame, 8, 80, 12, DASHBOARD_MOTION_BODY_TOP - 3));
    assert_band_white(known_frame, 200, RLCD_WIDTH, 16,
                      DASHBOARD_MOTION_BODY_TOP - 3);
    assert_band_white(empty_frame, 0, RLCD_WIDTH, DASHBOARD_MOTION_BODY_TOP,
                      DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT);
    assert_band_white(empty_frame, 0, RLCD_WIDTH,
                      DASHBOARD_MOTION_BODY_BOTTOM - 1,
                      DASHBOARD_MOTION_BODY_BOTTOM);
    assert_band_white(empty_frame, 120, RLCD_WIDTH,
                      DASHBOARD_MOTION_BODY_BOTTOM,
                      RLCD_HEIGHT);
    assert(band_has_ink(empty_frame, 8, 120, DASHBOARD_MOTION_BODY_BOTTOM,
                        RLCD_HEIGHT));

    dashboard_session_t all_working[DASHBOARD_MOTION_CAPACITY];
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i)
        all_working[i] = working;
    const dashboard_motion_render_t all_roster = {
        .roster = {.sessions = all_working,
                   .count = DASHBOARD_MOTION_CAPACITY,
                   .feed_health = DASH_CURRENT},
        .visible_count = 22,
        .overflow_count = 10,
    };
    dashboard_motion_render_t visible_only = all_roster;
    visible_only.roster.count = visible_only.visible_count;
    visible_only.overflow_count = 0;
    uint8_t whole_header[RLCD_FRAME_BYTES], visible_header[RLCD_FRAME_BYTES];
    dashboard_draw_motion(whole_header, &all_roster);
    dashboard_draw_motion(visible_header, &visible_only);
    bool header_differs = false;
    for (int y = 0; y < DASHBOARD_MOTION_BODY_TOP - 1; ++y)
        for (int x = 0; x < RLCD_WIDTH; ++x)
            header_differs |= pixel(whole_header, x, y) !=
                              pixel(visible_header, x, y);
    assert(header_differs); // Counts include the ten offscreen sessions.
    assert(band_has_ink(whole_header, 200, 392,
                        DASHBOARD_MOTION_BODY_BOTTOM, RLCD_HEIGHT));
    assert_band_white(visible_header, 120, RLCD_WIDTH,
                      DASHBOARD_MOTION_BODY_BOTTOM, RLCD_HEIGHT);

    // Lost-feed chrome depends on health and last-update provenance, never
    // the cached roster count or work labels.
    const dashboard_motion_render_t stale_small = {
        .roster = {.sessions = &blocked, .count = 1, .feed_health = DASH_STALE},
        .feed_lost = true,
        .now_ms = 90000,
    };
    const dashboard_motion_render_t stale_large = {
        .roster = {.sessions = partial, .count = 4, .feed_health = DASH_STALE},
        .overflow_count = 9,
        .hidden_blocked_count = 4,
        .feed_lost = true,
        .now_ms = 90000,
    };
    uint8_t stale_a[RLCD_FRAME_BYTES], stale_b[RLCD_FRAME_BYTES];
    dashboard_draw_motion(stale_a, &stale_small);
    dashboard_draw_motion(stale_b, &stale_large);
    assert(memcmp(stale_a, stale_b, RLCD_FRAME_BYTES) == 0);
    const dashboard_motion_render_t stale_known = {
        .roster = {.sessions = &blocked, .count = 1, .feed_health = DASH_STALE},
        .feed_lost = true,
        .now_ms = 90000,
        .last_healthy_update_ms = 30000,
        .last_healthy_update_known = true,
    };
    dashboard_draw_motion(expected_frame, &stale_known);
    assert(memcmp(stale_a, expected_frame, RLCD_FRAME_BYTES) != 0);
}

static void test_duplicate_project_labels(void)
{
    static dashboard_motion_t motion;
    static dashboard_motion_t no_id_motion;
    dashboard_motion_init(&motion);
    dashboard_motion_init(&no_id_motion);
    char long_project[DASHBOARD_MOTION_PROJECT_MAX + 1];
    size_t at = 0;
    for (size_t i = 0; i < 19; ++i) {
        memcpy(long_project + at, "中", 3);
        at += 3;
    }
    memcpy(long_project + at, "ABCDEFG", 7);
    at += 7;
    long_project[at] = '\0';
    assert(at == DASHBOARD_MOTION_PROJECT_MAX);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/duplicate/a", long_project, "CODEX", "AAAA",
               DASH_WORKING, DASH_CURRENT, true, 0, 1),
        sample("claude@host/duplicate/b", long_project, "CLAUDE", "BBBB",
               DASH_WORKING, DASH_CURRENT, true, 0, 1),
        sample("codex@host/duplicate/no-id", long_project, "CODEX", "",
               DASH_WORKING, DASH_CURRENT, true, 0, 1),
    };
    apply_ok(&motion, items, 3, 1000);
    assert_order(&motion, (const char *const[]){
        "codex@host/duplicate/a", "claude@host/duplicate/b",
        "codex@host/duplicate/no-id",
    }, 3);
    render_at(&motion, 1000, frame_duplicate_names);
    dashboard_motion_sample_t no_ids[] = {items[0], items[1], items[2]};
    for (size_t i = 0; i < 3; ++i) no_ids[i].short_id = "";
    apply_ok(&no_id_motion, no_ids, 3, 1000);
    render_at(&no_id_motion, 1000, expected_frame);
    // Supplied IDs change the two duplicate-name rows; an empty ID leaves its
    // row byte-identical. All suffix pixels remain inside the name column.
    const int top = DASHBOARD_MOTION_BODY_TOP;
    assert(band_differs(frame_duplicate_names, expected_frame,
                        24, 312, top, top + 24));
    assert(band_differs(frame_duplicate_names, expected_frame,
                        24, 312, top + 24, top + 48));
    assert_band_equal(frame_duplicate_names, expected_frame,
                      8, 392, top + 48, top + 72);
    assert_band_equal(frame_duplicate_names, expected_frame,
                      312, 360, top, top + 72);

    static dashboard_motion_t full_ids;
    static dashboard_motion_t full_no_ids;
    dashboard_motion_init(&full_ids);
    dashboard_motion_init(&full_no_ids);
    dashboard_motion_sample_t full_items[] = {items[0], items[1], items[2]};
    dashboard_motion_sample_t full_reference[] = {no_ids[0], no_ids[1], no_ids[2]};
    for (size_t i = 0; i < 2; ++i) {
        full_items[i].work = DASH_NEEDS_INPUT;
        full_items[i].state_episode++;
        full_items[i].state_entered_ms = 2000;
        full_reference[i].work = DASH_NEEDS_INPUT;
        full_reference[i].state_episode++;
        full_reference[i].state_entered_ms = 2000;
    }
    apply_ok(&full_ids, full_items, 3, 2000);
    apply_ok(&full_no_ids, full_reference, 3, 2000);
    uint8_t full_with_ids[RLCD_FRAME_BYTES], full_without_ids[RLCD_FRAME_BYTES];
    render_at(&full_ids, 2000, full_with_ids);
    render_at(&full_no_ids, 2000, full_without_ids);
    assert(band_differs(full_with_ids, full_without_ids, 24, 312, top, top + 24));
    assert(band_differs(full_with_ids, full_without_ids,
                        24, 312, top + 24, top + 48));
    assert_band_equal(full_with_ids, full_without_ids,
                      8, 392, top + 48, top + 72);
    assert_band_equal(full_with_ids, full_without_ids, 312, 360, top, top + 48);
    memcpy(frame_duplicate_names, full_with_ids, sizeof(frame_duplicate_names));
}

static void assert_render_age(const dashboard_motion_t *motion,
                              const char *logical_id, const char *expected)
{
    for (size_t rank = 0; rank < motion->count; ++rank) {
        if (strcmp(dashboard_motion_identity_at(motion, rank), logical_id) == 0) {
            assert(strcmp(motion->render_sessions[rank].detail, expected) == 0);
            return;
        }
    }
    assert(false && "age identity missing from rendered roster");
}

static void test_compact_ages_and_healthy_provenance(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/age/blocked", "blocked", "CODEX", "BLCK",
               DASH_NEEDS_INPUT, DASH_CURRENT, true, 3600000, 1),
        sample("claude@host/age/waiting", "waiting", "CLAUDE", "WAIT",
               DASH_SETTLED, DASH_CURRENT, true, 7080000, 1),
        sample("codex@host/age/working", "working", "CODEX", "WORK",
               DASH_WORKING, DASH_CURRENT, true, 7195000, 1),
        sample("claude@host/age/unknown", "unknown", "CLAUDE", "UNKN",
               DASH_UNKNOWN, DASH_CURRENT, false, 0, 1),
    };
    apply_ok(&motion, items, 4, 7200000);
    assert(motion.last_healthy_update_known &&
           motion.last_healthy_update_ms == 7200000);
    render_at(&motion, 7200000, expected_frame);
    assert_render_age(&motion, items[0].logical_id, "1h");
    assert_render_age(&motion, items[1].logical_id, "2m");
    assert_render_age(&motion, items[2].logical_id, "5s");
    assert_render_age(&motion, items[3].logical_id, "?");

    dashboard_motion_tick(&motion, 7210000);
    assert(motion.last_healthy_update_ms == 7200000);
    render_at(&motion, 7210000, expected_frame);
    assert_render_age(&motion, items[2].logical_id, "15s");

    const uint64_t accepted = motion.last_healthy_update_ms;
    items[0].state_entered_ms = 7210001;
    const dashboard_motion_snapshot_t future_age = {.sessions = items, .count = 4};
    assert(dashboard_motion_apply(&motion, &future_age, 7210000) ==
           DASHBOARD_MOTION_REJECTED_INVALID);
    assert(motion.last_healthy_update_known &&
           motion.last_healthy_update_ms == accepted);

    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 7230000) ==
           DASHBOARD_MOTION_APPLIED);
    assert(motion.last_healthy_update_ms == accepted);
    render_at(&motion, 7230000, expected_frame);
    assert_render_age(&motion, items[2].logical_id, "?");
    apply_ok(&motion, items, 4, 7240000);
    assert(dashboard_motion_feed_health(&motion) == DASH_CURRENT);
    assert(motion.last_healthy_update_ms == 7240000);
}

static void test_feed_loss_settles_retargeted_layouts(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[4];
    char ids[4][40];
    for (size_t i = 0; i < 4; ++i) {
        snprintf(ids[i], sizeof(ids[i]), "codex@host/loss-layout/%zu", i);
        items[i] = sample(ids[i], "loss-layout", "CODEX", "LAYT",
                          DASH_WORKING, DASH_CURRENT, true, 0, 1);
    }
    apply_ok(&motion, items, 4, 1000);

    // Promotion: the accepted blocked target is packed above the
    // workers even when loss arrives before their animation finishes.
    items[1].work = DASH_NEEDS_INPUT;
    items[1].state_episode++;
    items[1].state_entered_ms = 1100;
    apply_ok(&motion, items, 4, 1100);
    dashboard_motion_tick(&motion, 1120);
    assert(dashboard_motion_active(&motion));
    const uint64_t promoted_update = motion.last_healthy_update_ms;
    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 1130) ==
           DASHBOARD_MOTION_APPLIED);
    assert_loss_snapped(&motion);
    const int promoted = track_index(&motion, ids[1]);
    assert(promoted >= 0 && motion.tracks[promoted].row_height ==
           DASHBOARD_MOTION_ROW_HEIGHT);
    assert(motion.last_healthy_update_ms == promoted_update);
    assert(dashboard_motion_feed_lost(&motion, DASH_UNAVAILABLE, 1200) ==
           DASHBOARD_MOTION_APPLIED);
    assert_loss_snapped(&motion);
    assert(motion.last_healthy_update_ms == promoted_update);

    // Healthy recovery establishes a new provenance point. Demoting the
    // blocked row then commits its newest packed layout on a second loss.
    apply_ok(&motion, items, 4, 1300);
    assert(motion.last_healthy_update_ms == 1300);
    items[1].work = DASH_WORKING;
    items[1].state_episode++;
    items[1].state_entered_ms = 1320;
    apply_ok(&motion, items, 4, 1320);
    dashboard_motion_tick(&motion, 1340);
    const int compact = track_index(&motion, ids[1]);
    assert(compact >= 0 && motion.tracks[compact].row_height ==
           DASHBOARD_MOTION_WORKING_ROW_HEIGHT);
    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 1350) ==
           DASHBOARD_MOTION_APPLIED);
    assert_loss_snapped(&motion);
    assert(motion.tracks[compact].row_height == DASHBOARD_MOTION_WORKING_ROW_HEIGHT);

    // A new state transition retargets an in-flight layout; loss settles the
    // latest targets rather than the intermediate poses from either change.
    apply_ok(&motion, items, 4, 1400);
    items[0].work = DASH_NEEDS_INPUT;
    items[0].state_episode++;
    items[0].state_entered_ms = 1410;
    apply_ok(&motion, items, 4, 1410);
    dashboard_motion_tick(&motion, 1440);
    items[3].work = DASH_NEEDS_INPUT;
    items[3].state_episode++;
    items[3].state_entered_ms = 1450;
    apply_ok(&motion, items, 4, 1450);
    dashboard_motion_tick(&motion, 1460);
    const uint64_t retarget_update = motion.last_healthy_update_ms;
    assert(dashboard_motion_feed_lost(&motion, DASH_UNAVAILABLE, 1470) ==
           DASHBOARD_MOTION_APPLIED);
    assert_loss_snapped(&motion);
    assert(motion.last_healthy_update_ms == retarget_update);
    assert(motion.tracks[track_index(&motion, ids[0])].row_height ==
           DASHBOARD_MOTION_ROW_HEIGHT);
    assert(motion.tracks[track_index(&motion, ids[3])].row_height ==
           DASHBOARD_MOTION_ROW_HEIGHT);
}

static void test_native_row_font_sizes(void)
{
    const dashboard_session_t blocked = {
        .project = "Fa中", .provider = "CODEX", .detail = "FF",
        .work = DASH_NEEDS_INPUT, .health = DASH_CURRENT,
    };
    const dashboard_session_t working = {
        .project = "Fa中", .provider = "CLAUDE", .detail = "FF",
        .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_motion_render_row_t rows[] = {
        {.session = &blocked, .y = 100, .height = DASHBOARD_MOTION_ROW_HEIGHT},
        {.session = &working, .y = 150, .height = DASHBOARD_MOTION_WORKING_ROW_HEIGHT},
    };
    render_rows(rows, 2, expected_frame);
    // Exact BDF F, a, and 中 pixels at scale two in both polarities. These golden
    // rows were copied from the pinned BDF, independent of the generator.
    const uint16_t f[12] = {0,0,0xf800,0x8000,0x8000,0xf000,0x8000,0x8000,0x8000,0x8000,0,0};
    const uint16_t a[12] = {0,0,0,0,0x7000,0x0800,0x7800,0x8800,0x8800,0x7800,0,0};
    const uint16_t cjk[12] = {0,0x0400,0x0400,0xffe0,0x8420,0x8420,0x8420,0xffe0,0x0400,0x0400,0x0400,0x0400};
    const uint16_t *glyphs[] = {f, a, cjk};
    const int offsets[] = {0, 6, 12};
    const int advances[] = {6, 6, 12};
    for (size_t g = 0; g < 3; ++g)
        for (int y = 0; y < 12; ++y)
            for (int x = 0; x < advances[g]; ++x) {
                const bool ink = (glyphs[g][y] & (0x8000u >> x)) != 0;
                for (int dy = 0; dy < 2; ++dy)
                    for (int dx = 0; dx < 2; ++dx)
                        assert(pixel(expected_frame, 24 + (offsets[g] + x) * 2 + dx,
                                     150 + y * 2 + dy) == !ink);
                for (int dy = 0; dy < 2; ++dy)
                    for (int dx = 0; dx < 2; ++dx)
                        assert(pixel(expected_frame, 24 + (offsets[g] + x) * 2 + dx,
                                     100 + y * 2 + dy) == ink);
            }
    // Neither row spills outside its own twenty-four-pixel tile.
    for (int x = 24; x < 72; ++x) {
        assert(pixel(expected_frame, x, 99));
        assert(pixel(expected_frame, x, 124));
        assert(pixel(expected_frame, x, 149));
        assert(pixel(expected_frame, x, 174));
    }
    for (int y = DASHBOARD_MOTION_BODY_TOP; y < DASHBOARD_MOTION_BODY_BOTTOM; ++y)
        for (int x = 392; x < RLCD_WIDTH; ++x) assert(pixel(expected_frame, x, y));
}

static void test_newest_target_and_burst_bound(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[] = {
        sample("codex@host/wait", "wait", "CODEX", "AAAA", DASH_NEEDS_INPUT, DASH_CURRENT, true, 0, 1),
        sample("claude@host/run", "run", "CLAUDE", "BBBB", DASH_WORKING, DASH_CURRENT, true, 0, 1),
        sample("codex@host/idle", "idle", "CODEX", "CCCC", DASH_SETTLED, DASH_CURRENT, true, 0, 1),
    };
    apply_ok(&motion, items, 3, 1000);
    items[0].work = DASH_WORKING;
    items[0].state_episode++;
    items[0].state_entered_ms = 1000;
    apply_ok(&motion, items, 3, 1000);
    const uint64_t original_start = motion.burst_start_ms;
    assert(original_start == 1000);
    const int tracked = track_index(&motion, "codex@host/wait");
    assert(tracked >= 0);
    const dashboard_motion_direction_t repeated_direction =
        motion.tracks[tracked].direction;
    uint8_t original_order[DASHBOARD_MOTION_CAPACITY];
    memcpy(original_order, motion.order, sizeof(original_order));
    dashboard_motion_tick(&motion, 1040);
    const int32_t repeated_pose = motion.tracks[tracked].y_q8;
    const int32_t repeated_start_y = motion.tracks[tracked].start_y_q8;
    const int32_t repeated_target_y = motion.tracks[tracked].target_y_q8;
    apply_ok(&motion, items, 3, 1040); // Repeated polls do not restart motion.
    assert(motion.motion_start_ms == 1000);
    assert(motion.tracks[tracked].y_q8 == repeated_pose);
    assert(motion.tracks[tracked].start_y_q8 == repeated_start_y);
    assert(motion.tracks[tracked].target_y_q8 == repeated_target_y);
    assert(motion.tracks[tracked].direction == repeated_direction);
    assert(memcmp(original_order, motion.order, sizeof(original_order)) == 0);

    items[2].work = DASH_WORKING;
    items[2].state_episode++;
    items[2].state_entered_ms = 1120;
    apply_ok(&motion, items, 3, 1120);
    assert(motion.burst_start_ms == original_start);
    items[0].work = DASH_NEEDS_INPUT;
    items[0].state_episode++;
    items[0].state_entered_ms = 1200;
    apply_ok(&motion, items, 3, 1200);
    assert(motion.burst_start_ms == original_start);
    items[2].work = DASH_SETTLED;
    items[2].state_episode++;
    items[2].state_entered_ms = 1500;
    apply_ok(&motion, items, 3, 1500);
    assert(motion.motion_duration_ms <= 220);
    assert(motion.burst_start_ms + DASHBOARD_MOTION_BURST_LIMIT_MS == 1720);

    for (uint64_t now = 1540; now <= 1720; now += 40)
        apply_ok(&motion, items, 3, now);
    dashboard_motion_tick(&motion, 1720);
    assert(!dashboard_motion_active(&motion));
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") == DASHBOARD_MOTION_BODY_TOP);
    assert(dashboard_motion_position_y(&motion, "codex@host/idle") ==
           DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT);
    assert(dashboard_motion_position_y(&motion, "claude@host/run") ==
           DASHBOARD_MOTION_BODY_TOP + DASHBOARD_MOTION_ROW_HEIGHT * 2);
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used)
            assert(motion.tracks[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    render_at(&motion, 1720, frame_endpoint);

    // A quiet interval rearms a new independent transition after the burst cap.
    items[0].work = DASH_WORKING;
    items[0].state_episode++;
    items[0].state_entered_ms = 2120;
    apply_ok(&motion, items, 3, 2120);
    assert(motion.burst_start_ms == 2120);
    assert(!motion.burst_exhausted);
    assert(dashboard_motion_active(&motion));
}

static void test_overflow_priority_and_ghost_reservation(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    dashboard_motion_sample_t items[DASHBOARD_MOTION_CAPACITY];
    char ids[DASHBOARD_MOTION_CAPACITY][32];
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i) {
        snprintf(ids[i], sizeof(ids[i]), "codex@host/priority-%02zu", i);
        items[i] = sample(ids[i], "same-project", "CODEX", "SAME",
                          i < 20 ? ((i % 3) ? DASH_NEEDS_INPUT : DASH_ERROR) : DASH_WORKING,
                          DASH_CURRENT, true, i * 10, 1);
    }
    apply_ok(&motion, items, DASHBOARD_MOTION_CAPACITY, 100000);
    assert(dashboard_motion_count(&motion) == 32);
    assert(dashboard_motion_visible_count(&motion) == 11);
    assert(dashboard_motion_overflow_count(&motion) == 21);
    assert(dashboard_motion_hidden_blocked_count(&motion) == 9);
    for (size_t rank = 0; rank < 20; ++rank) {
        const int index = atoi(strrchr(dashboard_motion_identity_at(&motion, rank), '-') + 1);
        assert(index < 20);
    }
    assert(dashboard_motion_position_y(&motion,
           dashboard_motion_identity_at(&motion, 11)) == DASHBOARD_MOTION_BODY_BOTTOM);
    render_at(&motion, 100000, frame_overflow);

    // Build a full 32-worker model with 22 visible ghosts, then put new identities
    // before identities being restored from those ghost slots.
    static dashboard_motion_t stress;
    dashboard_motion_init(&stress);
    dashboard_motion_sample_t old_items[DASHBOARD_MOTION_CAPACITY];
    char old_ids[DASHBOARD_MOTION_CAPACITY][32];
    char second_ids[DASHBOARD_MOTION_CAPACITY][32];
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i) {
        snprintf(old_ids[i], sizeof(old_ids[i]), "codex@host/old-%02zu", i);
        old_items[i] = sample(old_ids[i], "old", "CODEX", "SAME", DASH_WORKING,
                              DASH_CURRENT, true, i, 1);
    }
    apply_ok(&stress, old_items, DASHBOARD_MOTION_CAPACITY, 2000);
    dashboard_motion_sample_t new_items[DASHBOARD_MOTION_CAPACITY];
    for (size_t i = 0; i < DASHBOARD_MOTION_CAPACITY; ++i) {
        snprintf(second_ids[i], sizeof(second_ids[i]), "claude@host/new-%02zu", i);
        new_items[i] = sample(second_ids[i], "new", "CLAUDE", "SAME", DASH_WORKING,
                              DASH_CURRENT, true, i, 1);
    }
    apply_ok(&stress, new_items, DASHBOARD_MOTION_CAPACITY, 2100);
    dashboard_motion_sample_t mixed[DASHBOARD_MOTION_CAPACITY];
    char third_ids[20][32];
    for (size_t i = 0; i < 20; ++i) {
        snprintf(third_ids[i], sizeof(third_ids[i]), "codex@host/third-%02zu", i);
        mixed[i] = sample(third_ids[i], "third", "CODEX", "SAME", DASH_SETTLED,
                          DASH_CURRENT, true, 1000 + i, 1);
    }
    for (size_t i = 0; i < 12; ++i) mixed[20 + i] = old_items[i];
    apply_ok(&stress, mixed, DASHBOARD_MOTION_CAPACITY, 2200);
    for (size_t i = 0; i < 12; ++i)
        assert(dashboard_motion_position_y(&stress, old_ids[i]) != INT32_MIN);
    for (size_t i = 0; i < 12; ++i)
        assert(strcmp(dashboard_motion_identity_at(&stress, 20 + i), old_ids[i]) == 0);
    size_t used_tracks = 0;
    size_t exiting_tracks = 0;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (stress.tracks[i].used) {
            ++used_tracks;
            exiting_tracks += stress.tracks[i].exiting ? 1u : 0u;
        }
    assert(used_tracks > DASHBOARD_MOTION_CAPACITY);
    assert(exiting_tracks == 11);
    // Exercise every active row and exit ghost through the packed renderer;
    // eleven exit ghosts plus thirty-two current rows remain within bounded
    // scratch storage even with a complete identity turnover.
    render_at(&stress, 2200, frame_endpoint);
    assert(stress.render_poses[used_tracks - 1].session != NULL);
    assert(stress.render_rows[used_tracks - 1].detail != NULL);
}

static void test_demo_driver(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    assert(dashboard_motion_demo_cycle_ms() ==
           (uint64_t)DASHBOARD_MOTION_DEMO_PHASES * 4000);
    assert(dashboard_motion_demo_phase_count() == DASHBOARD_MOTION_DEMO_PHASES);
    assert(dashboard_motion_demo_phase_index(0) == 0);
    assert(dashboard_motion_demo_phase_index(dashboard_motion_demo_cycle_ms()) == 0);
    assert(strcmp(dashboard_motion_demo_phase_name(6), "mid-motion-retarget") == 0);
    assert(strcmp(dashboard_motion_demo_phase_name(15), "working-to-blocked") == 0);
    assert(strcmp(dashboard_motion_demo_phase_name(16), "blocked-to-working") == 0);
    assert(strcmp(dashboard_motion_demo_phase_name(99), "unknown") == 0);
    uint64_t seen = 0;
    for (uint64_t elapsed = 0; elapsed < dashboard_motion_demo_cycle_ms(); elapsed += 40) {
        const size_t phase = dashboard_motion_demo_phase_index(elapsed);
        seen |= UINT64_C(1) << phase;
        (void)dashboard_motion_demo_update(&motion, elapsed);
        dashboard_motion_tick(&motion, dashboard_motion_demo_now_ms(elapsed));
        assert(motion.now_ms == dashboard_motion_demo_now_ms(elapsed));
        if (elapsed == 0) {
            assert(motion.demo_count == 8);
            assert(motion.demo_samples[6].work == DASH_WORKING);
            assert(motion.demo_samples[6].state_age_known);
        }
        if (elapsed == 56000) {
            assert(phase == 14 && motion.demo_count == 8);
            assert(motion.demo_samples[6].work == DASH_UNKNOWN);
            assert(motion.demo_samples[6].health == DASH_CURRENT);
            assert(motion.demo_samples[7].health == DASH_STALE);
            assert(strcmp(dashboard_motion_identity_at(&motion, 6),
                          "codex@local/session/powered-descent/unknown") == 0);
            assert(strcmp(dashboard_motion_identity_at(&motion, 7),
                          "claude@local/session/agent-observer/review") == 0);
            render_at(&motion, motion.now_ms, frame_endpoint);
            assert(strcmp(motion.render_sessions[6].detail, "?") == 0);
            assert(strcmp(motion.render_sessions[7].detail, "?") == 0);
        }
        if (elapsed == 68000) {
            assert(phase == 17 && motion.demo_count == DASHBOARD_MOTION_DEMO_CAPACITY);
            for (size_t i = 0; i < motion.demo_count; ++i) {
                const dashboard_motion_sample_t *entry = &motion.demo_samples[i];
                const char *prefix = strcmp(entry->provider, "CODEX") == 0 ? "codex@" : "claude@";
                assert(strncmp(entry->logical_id, prefix, strlen(prefix)) == 0);
            }
            assert(dashboard_motion_visible_count(&motion) == 11);
            assert(dashboard_motion_overflow_count(&motion) == 21);
            assert(dashboard_motion_hidden_blocked_count(&motion) == 0);
        }
        if (elapsed == 72000) {
            assert(phase == 18 && motion.demo_count == DASHBOARD_MOTION_DEMO_CAPACITY);
            assert(dashboard_motion_visible_count(&motion) == 11);
            assert(dashboard_motion_overflow_count(&motion) == 21);
            assert(dashboard_motion_hidden_blocked_count(&motion) == 0);
        }
        if (elapsed == 76000) {
            assert(phase == 19 && motion.demo_count == DASHBOARD_MOTION_DEMO_CAPACITY);
            assert(dashboard_motion_visible_count(&motion) == 11);
            assert(dashboard_motion_overflow_count(&motion) == 21);
            assert(dashboard_motion_hidden_blocked_count(&motion) == 21);
        }
        if (elapsed == 80000) {
            assert(phase == 20 && motion.demo_count == DASHBOARD_MOTION_DEMO_CAPACITY - 1);
            const int inactive = track_index(&motion,
                "codex@local/session/agent-observer/core");
            assert(inactive >= 0 && motion.tracks[inactive].exiting);
            assert(!motion.tracks[inactive].state_age_known);
            assert(motion.tracks[inactive].row_height == DASHBOARD_MOTION_ROW_HEIGHT);
        }
        if (elapsed == 84000) {
            assert(phase == 21 && motion.demo_count == DASHBOARD_MOTION_DEMO_CAPACITY);
            const int readmitted = track_index(&motion,
                "codex@local/session/agent-observer/core");
            assert(readmitted >= 0 && motion.tracks[readmitted].active);
            assert(motion.tracks[readmitted].row_height ==
                   DASHBOARD_MOTION_WORKING_ROW_HEIGHT);
        }
        if (elapsed == 88000) {
            assert(phase == 22 && motion.demo_count == 0);
            assert(dashboard_motion_visible_count(&motion) == 0);
            assert(dashboard_motion_overflow_count(&motion) == 0);
            assert(dashboard_motion_hidden_blocked_count(&motion) == 0);
        }
    }
    assert(seen == (UINT64_C(1) << DASHBOARD_MOTION_DEMO_PHASES) - 1);
    const uint64_t cycle_ms = dashboard_motion_demo_cycle_ms();
    assert(dashboard_motion_demo_update(&motion, cycle_ms)); // Fixed-epoch cycle reset.
    assert(dashboard_motion_demo_phase_index(cycle_ms) == 0);
}

static void capture_demo_previews(const char *directory)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    const uint64_t cycle_ms = dashboard_motion_demo_cycle_ms();

    // Replay from elapsed zero at the firmware polling cadence. All preview
    // frames below come from the same packed renderer used by the controller.
    for (uint64_t elapsed_ms = 0; elapsed_ms < cycle_ms; elapsed_ms += 40) {
        (void)dashboard_motion_demo_update(&motion, elapsed_ms);
        const uint64_t now_ms = dashboard_motion_demo_now_ms(elapsed_ms);
        dashboard_motion_tick(&motion, now_ms);

        if (elapsed_ms == 0) {
            assert(dashboard_motion_count(&motion) == 8);
            render_at(&motion, now_ms, frame_initial);
            save_pbm(directory, "demo-initial-order", frame_initial);
        }

        const size_t phase = dashboard_motion_demo_phase_index(elapsed_ms);
        const uint64_t phase_offset = elapsed_ms % 4000;
        if (phase == 1 && phase_offset <= 360) {
            char name[96];
            const int length = snprintf(name, sizeof(name), "demo-answered-wait-%02" PRIu64,
                                        phase_offset / 40);
            assert(length > 0 && (size_t)length < sizeof(name));
            render_at(&motion, now_ms, frame_halfway);
            save_pbm(directory, name, frame_halfway);
        }

        if (phase >= 15 && phase_offset <= 360 &&
            (phase_offset % 80 == 0 || phase_offset == 360)) {
            char name[128];
            const int length = snprintf(name, sizeof(name),
                "demo-transition-%02zu-%s-%03" PRIu64,
                phase, dashboard_motion_demo_phase_name(phase), phase_offset);
            assert(length > 0 && (size_t)length < sizeof(name));
            render_at(&motion, now_ms, frame_halfway);
            save_pbm(directory, name, frame_halfway);
        }

        if (phase_offset == 1000) {
            char name[128];
            const int length = snprintf(name, sizeof(name), "demo-settled-%02zu-%s",
                                        phase,
                                        dashboard_motion_demo_phase_name(phase));
            assert(length > 0 && (size_t)length < sizeof(name));
            render_at(&motion, now_ms, frame_endpoint);
            save_pbm(directory, name, frame_endpoint);
        }
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s OUTPUT_DIRECTORY\n", argv[0]);
        return 1;
    }
    test_priority_age_and_identity();
    test_ties_reset_and_atomic_rejection();
    test_transitions_and_stationary_chrome();
    test_overlap_priority_and_icon_polarity();
    test_row_icon_polarity();
    test_state_polarity_and_slow_flash(argv[1]);
    test_direction_tier_compositing();
    test_shared_progress_directions_and_endpoints();
    test_retarget_preserves_current_pose();
    test_clipping_ghosts_and_feed_loss();
    test_newest_target_and_burst_bound();
    test_overflow_priority_and_ghost_reservation();
    test_demo_driver();

    save_pbm(argv[1], "initial-order", frame_initial);
    save_pbm(argv[1], "answered-wait-mid-motion", frame_halfway);
    save_pbm(argv[1], "newest-target-endpoint", frame_endpoint);
    save_pbm(argv[1], "crossing-motion-layers", frame_overlap);
    save_pbm(argv[1], "attention-overflow", frame_overflow);
    capture_demo_previews(argv[1]);
    test_urgency_geometry_and_admission();
    test_uniform_height_changes_and_retarget();
    test_inactive_removal_and_readmission();
    test_motion_chrome_states();
    test_duplicate_project_labels();
    test_compact_ages_and_healthy_provenance();
    test_feed_loss_settles_retargeted_layouts();
    test_native_row_font_sizes();
    save_pbm(argv[1], "ui-polish-feed-lost-packed", frame_feed_lost_packed);
    save_pbm(argv[1], "ui-polish-partial-header", frame_partial_header);
    save_pbm(argv[1], "ui-polish-duplicate-long-name", frame_duplicate_names);
    printf("PASS: urgency geometry, prefix admission, identity, atomic input, shared progress, direction layers, burst rearming, clipping, source loss, polarity; sizeof(controller)=%zu\n",
           sizeof(dashboard_motion_t));
    return 0;
}
