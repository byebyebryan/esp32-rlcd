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
    assert(dashboard_motion_position_y(&motion, expected[0]) == 52);
    assert(dashboard_motion_position_y(&motion, expected[2]) == 106);
    assert(dashboard_motion_position_y(&motion, expected[4]) == 160);
    assert(dashboard_motion_position_y(&motion, expected[7]) == 240);

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
    const size_t old_count = motion.count;
    memcpy(model_before_rejection, &motion, sizeof(motion));
    dashboard_motion_sample_t duplicates[] = {items[0], items[0]};
    const dashboard_motion_snapshot_t duplicate_snapshot = {duplicates, 2};
    assert(dashboard_motion_apply(&motion, &duplicate_snapshot, 20000) ==
           DASHBOARD_MOTION_REJECTED_INVALID);
    assert(motion.now_ms == old_now && motion.count == old_count);
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
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") == 52);
    assert(dashboard_motion_position_y(&motion, "claude@host/run") == 80);

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
    assert(run_y >= 58 && run_y <= 60);
    assert(wait_y >= 70 && wait_y <= 73);

    // Motion frame header/footer equal the settled render for the same snapshot.
    const dashboard_view_t settled_view = {
        .sessions = motion.render_sessions,
        .count = motion.count,
        .feed_health = DASH_CURRENT,
    };
    dashboard_draw_styled(expected_frame, &settled_view,
                          (dashboard_style_t){DASH_AGENT_PAIR, true});
    for (int y = 0; y < RLCD_HEIGHT; ++y) {
        if (y >= DASHBOARD_MOTION_BODY_TOP && y < DASHBOARD_MOTION_BODY_BOTTOM) continue;
        for (int x = 0; x < RLCD_WIDTH; ++x)
            assert(pixel(frame_halfway, x, y) == pixel(expected_frame, x, y));
    }
    render_at(&motion, 1360, frame_endpoint);
    assert(!dashboard_motion_active(&motion));
    assert(dashboard_motion_position_y(&motion, "claude@host/run") == 52);
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") == 80);
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
    // Waiting and error tile glyphs remain white on black even though the row
    // also uses steady inverse text/background.
    assert(!pixel(expected_frame, 12, 54));
    assert(pixel(expected_frame, 21, 60));
    assert(!pixel(expected_frame, 12, 80));
    assert(pixel(expected_frame, 16, 85));

    items[0].work = DASH_WORKING;
    items[0].state_episode++;
    items[0].state_entered_ms = 1000;
    items[1].work = DASH_NEEDS_INPUT;
    items[1].state_episode++;
    items[1].state_entered_ms = 1000;
    apply_ok(&motion, items, 3, 1000);
    render_at(&motion, 1100, frame_overlap);
    // The upward-moving wait is drawn over the downward-moving run row.
    assert(!pixel(frame_overlap, 12, 100));
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

static void test_direction_tier_compositing(void)
{
    const dashboard_session_t down = {
        .project = "DOWN", .provider = "CODEX", .short_id = "DOWN",
        .detail = "01S", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t stationary = {
        .project = "STILL", .provider = "CLAUDE", .short_id = "STIL",
        .detail = "02S", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t up = {
        .project = "UP", .provider = "CODEX", .short_id = "UPUP",
        .detail = "03S", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_motion_render_row_t down_row = {
        .session = &down, .y = 100,
        .direction = DASHBOARD_MOTION_DIRECTION_DOWN,
    };
    const dashboard_motion_render_row_t stationary_row = {
        .session = &stationary, .y = 100,
        .direction = DASHBOARD_MOTION_DIRECTION_STATIONARY,
    };
    const dashboard_motion_render_row_t up_row = {
        .session = &up, .y = 100,
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
        .detail = "01S", .work = DASH_WORKING, .health = DASH_CURRENT,
    };
    const dashboard_session_t second_up = {
        .project = "SECOND", .provider = "CLAUDE", .short_id = "SECO",
        .detail = "02S", .work = DASH_WORKING, .health = DASH_CURRENT,
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
    assert(motion.tracks[a].start_y_q8 == 52 * 256);
    assert(motion.tracks[a].target_y_q8 == 108 * 256);
    assert(motion.tracks[b].start_y_q8 == 108 * 256);
    assert(motion.tracks[b].target_y_q8 == 80 * 256);
    assert(motion.tracks[c].start_y_q8 == 80 * 256);
    assert(motion.tracks[c].target_y_q8 == 52 * 256);
    assert(motion.tracks[a].direction == DASHBOARD_MOTION_DIRECTION_DOWN);
    assert(motion.tracks[b].direction == DASHBOARD_MOTION_DIRECTION_UP);
    assert(motion.tracks[c].direction == DASHBOARD_MOTION_DIRECTION_UP);

    // At 180/360 ms, ease-out progress is exactly 0.75 for every row even
    // though A travels 56 px and B/C travel 28 px.
    dashboard_motion_tick(&motion, 1180);
    assert(motion.tracks[a].y_q8 == 94 * 256);
    assert(motion.tracks[b].y_q8 == 87 * 256);
    assert(motion.tracks[c].y_q8 == 59 * 256);
    assert(motion.tracks[a].target_y_q8 - motion.tracks[a].start_y_q8 == 56 * 256);
    assert(motion.tracks[b].target_y_q8 - motion.tracks[b].start_y_q8 == -28 * 256);

    dashboard_motion_tick(&motion, 1360);
    assert(!dashboard_motion_active(&motion));
    assert(motion.tracks[a].y_q8 == 108 * 256);
    assert(motion.tracks[b].y_q8 == 80 * 256);
    assert(motion.tracks[c].y_q8 == 52 * 256);
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
        .project = "edge", .provider = "CODEX", .short_id = "EDGE", .detail = "01S",
        .work = DASH_NEEDS_INPUT, .health = DASH_CURRENT,
    }, .y = 260};
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
    assert(!pixel(guarded + 1, 12, 265));
    assert(pixel(expected_frame, 12, 265));
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
    // Feed loss during the exit movement freezes every current pose and
    // replaces cached claims in both active rows and departing ghosts.
    dashboard_motion_tick(&motion, 1200);
    const int frozen_b = dashboard_motion_position_y(&motion, "claude@host/b");
    assert(dashboard_motion_feed_lost(&motion, DASH_STALE, 1200) ==
           DASHBOARD_MOTION_APPLIED);
    assert(!dashboard_motion_active(&motion));
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used)
            assert(motion.tracks[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    dashboard_motion_tick(&motion, 1450);
    assert(dashboard_motion_position_y(&motion, "claude@host/b") == frozen_b);
    render_at(&motion, 1450, frame_feed_lost);
    assert(motion.render_age[0][0] == '?');
    for (int y = 269; y < RLCD_HEIGHT; ++y)
        for (int x = 240; x < RLCD_WIDTH; ++x) assert(pixel(frame_feed_lost, x, y));

    apply_ok(&motion, only_b, 1, 1500);
    assert(dashboard_motion_feed_health(&motion) == DASH_CURRENT);
    assert(dashboard_motion_active(&motion));
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
    items[1].work = DASH_NEEDS_INPUT;
    items[1].state_episode++;
    items[1].state_entered_ms = 1200;
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
    assert(dashboard_motion_position_y(&motion, "claude@host/run") == 52);
    assert(dashboard_motion_position_y(&motion, "codex@host/idle") == 80);
    assert(dashboard_motion_position_y(&motion, "codex@host/wait") == 108);
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion.tracks[i].used)
            assert(motion.tracks[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY);
    render_at(&motion, 1720, frame_endpoint);
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
                          i < 10 ? ((i % 3) ? DASH_NEEDS_INPUT : DASH_ERROR) : DASH_WORKING,
                          DASH_CURRENT, true, i * 10, 1);
    }
    apply_ok(&motion, items, DASHBOARD_MOTION_CAPACITY, 100000);
    assert(dashboard_motion_count(&motion) == 16);
    for (size_t rank = 0; rank < 10; ++rank) {
        const int index = atoi(strrchr(dashboard_motion_identity_at(&motion, rank), '-') + 1);
        assert(index < 10);
    }
    assert(dashboard_motion_position_y(&motion,
           dashboard_motion_identity_at(&motion, 8)) == DASHBOARD_MOTION_BODY_BOTTOM);
    render_at(&motion, 100000, frame_overflow);

    // Build a full 16-row model with 8 visible ghosts, then put new identities
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
    char third_ids[12][32];
    for (size_t i = 0; i < 12; ++i) {
        snprintf(third_ids[i], sizeof(third_ids[i]), "codex@host/third-%02zu", i);
        mixed[i] = sample(third_ids[i], "third", "CODEX", "SAME", DASH_SETTLED,
                          DASH_CURRENT, true, 1000 + i, 1);
    }
    for (size_t i = 0; i < 4; ++i) mixed[12 + i] = old_items[i];
    apply_ok(&stress, mixed, DASHBOARD_MOTION_CAPACITY, 2200);
    for (size_t i = 0; i < 4; ++i)
        assert(dashboard_motion_position_y(&stress, old_ids[i]) != INT32_MIN);
    for (size_t i = 0; i < 4; ++i)
        assert(strcmp(dashboard_motion_identity_at(&stress, 12 + i), old_ids[i]) == 0);
    size_t used_tracks = 0;
    size_t exiting_tracks = 0;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (stress.tracks[i].used) {
            ++used_tracks;
            exiting_tracks += stress.tracks[i].exiting ? 1u : 0u;
        }
    assert(used_tracks > DASHBOARD_MOTION_CAPACITY);
    assert(exiting_tracks == 8);
    // Exercise every active row and exit ghost through the packed renderer;
    // the eight ghosts plus sixteen current rows exceed the 32-byte age
    // scratch used by an earlier implementation and stay within the 48 slots.
    render_at(&stress, 2200, frame_endpoint);
    assert(stress.render_poses[used_tracks - 1].session != NULL);
    assert(stress.render_rows[used_tracks - 1].detail != NULL);
}

static void test_demo_driver(void)
{
    static dashboard_motion_t motion;
    dashboard_motion_init(&motion);
    assert(dashboard_motion_demo_cycle_ms() == 60000);
    assert(dashboard_motion_demo_phase_count() == DASHBOARD_MOTION_DEMO_PHASES);
    assert(dashboard_motion_demo_phase_index(0) == 0);
    assert(dashboard_motion_demo_phase_index(60000) == 0);
    assert(strcmp(dashboard_motion_demo_phase_name(6), "mid-motion-retarget") == 0);
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
    }
    assert(seen == (UINT64_C(1) << DASHBOARD_MOTION_DEMO_PHASES) - 1);
    assert(dashboard_motion_demo_update(&motion, 60000)); // Fixed-epoch cycle reset.
    assert(dashboard_motion_demo_phase_index(60000) == 0);
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
    save_pbm(argv[1], "feed-lost-frozen", frame_feed_lost);
    save_pbm(argv[1], "attention-overflow", frame_overflow);
    capture_demo_previews(argv[1]);
    printf("PASS: ordering, identity, atomic input, shared progress, direction layers, motion bounds, clipping, source loss, polarity; sizeof(controller)=%zu\n",
           sizeof(dashboard_motion_t));
    return 0;
}
