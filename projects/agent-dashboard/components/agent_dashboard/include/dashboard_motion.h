#pragma once

#include "agent_dashboard.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    DASHBOARD_MOTION_CAPACITY = 32,
    DASHBOARD_MOTION_TRACK_CAPACITY = DASHBOARD_MOTION_CAPACITY * 2,
    DASHBOARD_MOTION_ID_MAX = 96,
    DASHBOARD_MOTION_PROJECT_MAX = 64,
    DASHBOARD_MOTION_PROVIDER_MAX = 16,
    DASHBOARD_MOTION_SHORT_ID_MAX = 12,
    DASHBOARD_MOTION_DURATION_MS = 360,
    DASHBOARD_MOTION_BURST_LIMIT_MS = 720,
    DASHBOARD_MOTION_ROW_HEIGHT = 24,
    DASHBOARD_MOTION_WORKING_ROW_HEIGHT = 24,
    DASHBOARD_MOTION_TEXT_HEIGHT = 24,
    DASHBOARD_MOTION_WORKING_TEXT_HEIGHT = 24,
    DASHBOARD_MOTION_FLASH_HALF_PERIOD_MS = 500,
    DASHBOARD_MOTION_BODY_TOP = 24,
    DASHBOARD_MOTION_BODY_BOTTOM = 300,
    DASHBOARD_MOTION_RENDER_AGE_CAPACITY = DASHBOARD_MOTION_TRACK_CAPACITY + DASHBOARD_MOTION_CAPACITY,
    DASHBOARD_MOTION_DEMO_CAPACITY = 32,
    DASHBOARD_MOTION_DEMO_PHASES = 23,
};

// Local fixed-capacity presentation input. logical_id is the full provider-
// qualified identity; the visible fields are never used to match sessions.
typedef struct {
    const char *logical_id;
    const char *project;
    const char *provider;
    const char *short_id;
    dashboard_work_t work;
    dashboard_health_t health;
    bool state_age_known;
    uint64_t state_entered_ms;
    // Increment for every new state episode, including a repeated work label.
    uint64_t state_episode;
} dashboard_motion_sample_t;

typedef struct {
    const dashboard_motion_sample_t *sessions;
    size_t count;
} dashboard_motion_snapshot_t;

typedef enum {
    DASHBOARD_MOTION_APPLIED,
    DASHBOARD_MOTION_REJECTED_INVALID,
    DASHBOARD_MOTION_REJECTED_CAPACITY,
} dashboard_motion_result_t;

typedef enum {
    DASHBOARD_MOTION_DIRECTION_STATIONARY = 0,
    DASHBOARD_MOTION_DIRECTION_DOWN,
    DASHBOARD_MOTION_DIRECTION_UP,
} dashboard_motion_direction_t;

typedef struct {
    bool used;
    bool active;
    bool exiting;
    char logical_id[DASHBOARD_MOTION_ID_MAX + 1];
    char project[DASHBOARD_MOTION_PROJECT_MAX + 1];
    char provider[DASHBOARD_MOTION_PROVIDER_MAX + 1];
    char short_id[DASHBOARD_MOTION_SHORT_ID_MAX + 1];
    dashboard_work_t work;
    dashboard_health_t health;
    uint8_t row_height;
    bool admitted;
    bool state_age_known;
    uint64_t state_entered_ms;
    uint64_t state_episode;
    uint64_t admission_order;
    uint16_t prior_rank;
    int32_t y_q8;
    int32_t start_y_q8;
    int32_t target_y_q8;
    dashboard_motion_direction_t direction;
} dashboard_motion_track_t;

typedef struct {
    const dashboard_session_t *session;
    int16_t y;
    uint8_t height;
    dashboard_motion_direction_t direction;
} dashboard_motion_render_row_t;

typedef struct {
    dashboard_view_t roster;
    // Input order is stable within each direction tier. The controller places
    // departing ghosts in prior order, followed by active rows in target order.
    const dashboard_motion_render_row_t *rows;
    size_t row_count;
    size_t visible_count;
    size_t overflow_count;
    size_t hidden_blocked_count;
    bool feed_lost;
    uint64_t now_ms;
    uint64_t last_healthy_update_ms;
    bool last_healthy_update_known;
} dashboard_motion_render_t;

// Called by the motion controller; public so the two C translation units can
// share the bounded render description without an opaque allocator.
void dashboard_draw_motion(uint8_t *frame, const dashboard_motion_render_t *view);

// Caller-owned fixed storage; keep this object static on embedded targets.
// Apply, tick, and render use no dynamic allocation.
typedef struct {
    dashboard_motion_track_t tracks[DASHBOARD_MOTION_TRACK_CAPACITY];
    uint8_t order[DASHBOARD_MOTION_CAPACITY];
    size_t count;
    uint64_t next_admission_order;
    uint64_t now_ms;
    uint64_t last_healthy_update_ms;
    uint64_t motion_start_ms;
    uint64_t burst_start_ms;
    uint64_t last_layout_change_ms;
    uint32_t motion_duration_ms;
    size_t visible_count;
    size_t hidden_blocked_count;
    dashboard_health_t feed_health;
    bool initialized;
    bool animating;
    bool burst_exhausted;
    bool last_healthy_update_known;
    dashboard_session_t render_sessions[DASHBOARD_MOTION_CAPACITY];
    dashboard_session_t render_rows[DASHBOARD_MOTION_TRACK_CAPACITY];
    dashboard_motion_render_row_t render_poses[DASHBOARD_MOTION_TRACK_CAPACITY];
    char render_age[DASHBOARD_MOTION_RENDER_AGE_CAPACITY][4];
    uint8_t render_track_index[DASHBOARD_MOTION_TRACK_CAPACITY];
    dashboard_motion_sample_t demo_samples[DASHBOARD_MOTION_DEMO_CAPACITY];
    size_t demo_count;
    size_t demo_phase;
    uint64_t demo_cycle;
    dashboard_health_t demo_feed_health;
    uint8_t demo_substep;
    bool demo_initialized;
} dashboard_motion_t;

void dashboard_motion_init(dashboard_motion_t *motion);
dashboard_motion_result_t dashboard_motion_apply(
    dashboard_motion_t *motion, const dashboard_motion_snapshot_t *snapshot,
    uint64_t now_ms);
// Whole-feed loss settles tracks at the newest accepted targets and suppresses
// cached state claims while retaining accepted row geometry.
// Only non-current health values are accepted.
dashboard_motion_result_t dashboard_motion_feed_lost(
    dashboard_motion_t *motion, dashboard_health_t health, uint64_t now_ms);
void dashboard_motion_tick(dashboard_motion_t *motion, uint64_t now_ms);
void dashboard_motion_render(dashboard_motion_t *motion, uint8_t *frame);
bool dashboard_motion_active(const dashboard_motion_t *motion);
bool dashboard_motion_flashing(const dashboard_motion_t *motion);
dashboard_health_t dashboard_motion_feed_health(const dashboard_motion_t *motion);
size_t dashboard_motion_count(const dashboard_motion_t *motion);
const char *dashboard_motion_identity_at(const dashboard_motion_t *motion,
                                         size_t rank);
int dashboard_motion_position_y(const dashboard_motion_t *motion,
                                const char *logical_id);
size_t dashboard_motion_visible_count(const dashboard_motion_t *motion);
size_t dashboard_motion_overflow_count(const dashboard_motion_t *motion);
size_t dashboard_motion_hidden_blocked_count(const dashboard_motion_t *motion);
bool dashboard_motion_state_entry(const dashboard_motion_t *motion,
                                  const char *logical_id, uint64_t *entered_ms);

// Absolute-time fixture clock plus a frame-polled phase driver. Start at
// elapsed_ms=0 and poll continuously; intermediate demo transitions are not
// replayed after a skipped phase. The clock uses a fixed epoch so entry ages
// remain valid when the device's monotonic clock starts at zero.
uint64_t dashboard_motion_demo_cycle_ms(void);
size_t dashboard_motion_demo_phase_count(void);
size_t dashboard_motion_demo_phase_index(uint64_t elapsed_ms);
const char *dashboard_motion_demo_phase_name(size_t phase_index);
uint64_t dashboard_motion_demo_now_ms(uint64_t elapsed_ms);
// Applies only scheduled fixture snapshots; true means the model changed.
bool dashboard_motion_demo_update(dashboard_motion_t *motion,
                                  uint64_t elapsed_ms);
