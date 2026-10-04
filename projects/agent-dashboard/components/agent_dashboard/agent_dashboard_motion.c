#include "dashboard_motion.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

enum { Q8_ONE = 256, DEMO_EPOCH_MS = 86400000u };

static size_t bounded_string_length(const char *value, size_t maximum)
{
    if (!value) return 0;
    size_t length = 0;
    while (length <= maximum && value[length]) ++length;
    return length;
}

static bool copy_checked(char *target, size_t target_size, const char *source,
                         size_t maximum, bool required)
{
    const size_t length = bounded_string_length(source, maximum);
    if ((required && length == 0) || length > maximum || target_size <= length)
        return false;
    if (length) memcpy(target, source, length);
    target[length] = '\0';
    return true;
}

static bool valid_work(dashboard_work_t work)
{
    return work >= DASH_WORKING && work <= DASH_UNKNOWN;
}

static bool valid_health(dashboard_health_t health)
{
    return health >= DASH_CURRENT && health <= DASH_UNSUPPORTED;
}

static bool validate_snapshot(const dashboard_motion_snapshot_t *snapshot,
                              uint64_t now_ms)
{
    if (!snapshot || snapshot->count > DASHBOARD_MOTION_CAPACITY ||
        (snapshot->count && !snapshot->sessions)) return false;
    for (size_t i = 0; i < snapshot->count; ++i) {
        const dashboard_motion_sample_t *sample = &snapshot->sessions[i];
        if (!sample->logical_id ||
            bounded_string_length(sample->logical_id, DASHBOARD_MOTION_ID_MAX) == 0 ||
            bounded_string_length(sample->logical_id, DASHBOARD_MOTION_ID_MAX) > DASHBOARD_MOTION_ID_MAX ||
            !sample->project ||
            bounded_string_length(sample->project, DASHBOARD_MOTION_PROJECT_MAX) > DASHBOARD_MOTION_PROJECT_MAX ||
            (sample->provider && bounded_string_length(sample->provider, DASHBOARD_MOTION_PROVIDER_MAX) > DASHBOARD_MOTION_PROVIDER_MAX) ||
            (sample->short_id && bounded_string_length(sample->short_id, DASHBOARD_MOTION_SHORT_ID_MAX) > DASHBOARD_MOTION_SHORT_ID_MAX) ||
            !valid_work(sample->work) || !valid_health(sample->health) ||
            (sample->state_age_known && sample->state_entered_ms > now_ms)) return false;
        for (size_t earlier = 0; earlier < i; ++earlier)
            if (strcmp(sample->logical_id, snapshot->sessions[earlier].logical_id) == 0)
                return false;
    }
    return true;
}

static int group_of(const dashboard_motion_track_t *track)
{
    if (track->health != DASH_CURRENT || track->work == DASH_UNKNOWN) return 3;
    if (track->work == DASH_NEEDS_INPUT || track->work == DASH_ERROR) return 0;
    if (track->work == DASH_SETTLED || track->work == DASH_INTERRUPTED) return 1;
    return 2;
}

static bool comes_before(const dashboard_motion_track_t *left,
                         const dashboard_motion_track_t *right)
{
    const int left_group = group_of(left), right_group = group_of(right);
    if (left_group != right_group) return left_group < right_group;
    // Uncertain entries retain roster order because their cached work-age is
    // not a trustworthy ordering claim while their state is unavailable.
    if (left_group == 3) {
        if (left->prior_rank != right->prior_rank)
            return left->prior_rank < right->prior_rank;
        return left->admission_order < right->admission_order;
    }
    if (left->state_age_known != right->state_age_known) return left->state_age_known;
    if (left->state_age_known && left->state_entered_ms != right->state_entered_ms)
        return left->state_entered_ms < right->state_entered_ms;
    if (left->prior_rank != right->prior_rank)
        return left->prior_rank < right->prior_rank;
    return left->admission_order < right->admission_order;
}

static void sort_roster(dashboard_motion_t *motion)
{
    for (size_t i = 0; i < motion->count; ++i) {
        const uint8_t candidate = motion->order[i];
        size_t at = i;
        while (at > 0 && comes_before(&motion->tracks[candidate],
                                     &motion->tracks[motion->order[at - 1]])) {
            motion->order[at] = motion->order[at - 1];
            --at;
        }
        motion->order[at] = candidate;
    }
    for (size_t rank = 0; rank < motion->count; ++rank)
        motion->tracks[motion->order[rank]].prior_rank = (uint16_t)rank;
}

static int32_t target_y_q8(int rank, int boundaries)
{
    // The ninth and later rows are fully outside the body. They still retain
    // their sorted identity/order so a later promotion has a stable origin.
    if (rank >= DASHBOARD_DENSE_VISIBLE_ROWS)
        return (DASHBOARD_MOTION_BODY_BOTTOM +
                (rank - DASHBOARD_DENSE_VISIBLE_ROWS) * DASHBOARD_MOTION_ROW_HEIGHT) * Q8_ONE;
    return (DASHBOARD_MOTION_BODY_TOP + rank * DASHBOARD_MOTION_ROW_HEIGHT +
            boundaries * 2) * Q8_ONE;
}

static uint64_t burst_deadline(const dashboard_motion_t *motion)
{
    if (UINT64_MAX - motion->burst_start_ms < DASHBOARD_MOTION_BURST_LIMIT_MS)
        return UINT64_MAX;
    return motion->burst_start_ms + DASHBOARD_MOTION_BURST_LIMIT_MS;
}

static uint32_t eased_progress_q16(uint64_t elapsed_ms, uint32_t duration_ms)
{
    if (!duration_ms || elapsed_ms >= duration_ms) return 65536u;
    const uint64_t progress = elapsed_ms * 65536u / duration_ms;
    const uint64_t remaining = 65536u - progress;
    return (uint32_t)(65536u - remaining * remaining / 65536u);
}

static int32_t interpolate_q8(int32_t start, int32_t target,
                              uint32_t progress_q16)
{
    if (progress_q16 >= 65536u) return target;
    const int64_t delta = (int64_t)target - start;
    return start + (int32_t)(delta * (int64_t)progress_q16 / 65536);
}

static dashboard_motion_direction_t direction_between(int32_t start, int32_t target)
{
    if (target > start) return DASHBOARD_MOTION_DIRECTION_DOWN;
    if (target < start) return DASHBOARD_MOTION_DIRECTION_UP;
    return DASHBOARD_MOTION_DIRECTION_STATIONARY;
}

static void update_positions(dashboard_motion_t *motion, uint64_t now_ms)
{
    if (!motion->animating) return;
    const uint64_t elapsed = now_ms >= motion->motion_start_ms
                           ? now_ms - motion->motion_start_ms : 0;
    const uint32_t progress_q16 = eased_progress_q16(elapsed,
                                                      motion->motion_duration_ms);
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        dashboard_motion_track_t *track = &motion->tracks[i];
        if (track->used)
            track->y_q8 = interpolate_q8(track->start_y_q8, track->target_y_q8,
                                         progress_q16);
    }
    if (progress_q16 == 65536u) {
        motion->animating = false;
        if (now_ms >= burst_deadline(motion)) motion->burst_exhausted = true;
        for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
            dashboard_motion_track_t *track = &motion->tracks[i];
            if (track->used) {
                track->y_q8 = track->start_y_q8 = track->target_y_q8;
                track->direction = DASHBOARD_MOTION_DIRECTION_STATIONARY;
            }
        }
    }
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        dashboard_motion_track_t *track = &motion->tracks[i];
        if (track->used && track->exiting && !motion->animating &&
            track->y_q8 >= DASHBOARD_MOTION_BODY_BOTTOM * Q8_ONE)
            memset(track, 0, sizeof(*track));
    }
}

void dashboard_motion_init(dashboard_motion_t *motion)
{
    if (!motion) return;
    memset(motion, 0, sizeof(*motion));
    motion->feed_health = DASH_CURRENT;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        motion->tracks[i].prior_rank = UINT16_MAX;
}

void dashboard_motion_tick(dashboard_motion_t *motion, uint64_t now_ms)
{
    if (!motion) return;
    if (motion->initialized && now_ms < motion->now_ms) now_ms = motion->now_ms;
    update_positions(motion, now_ms);
    if (motion->burst_exhausted &&
        now_ms >= motion->last_layout_change_ms &&
        now_ms - motion->last_layout_change_ms >= DASHBOARD_MOTION_DURATION_MS)
        motion->burst_exhausted = false;
    motion->now_ms = now_ms;
}

static int find_track(const dashboard_motion_t *motion, const char *logical_id)
{
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion->tracks[i].used && strcmp(motion->tracks[i].logical_id, logical_id) == 0)
            return (int)i;
    return -1;
}

static int allocate_track(dashboard_motion_t *motion,
                          const bool was_active[DASHBOARD_MOTION_TRACK_CAPACITY],
                          const bool matched[DASHBOARD_MOTION_TRACK_CAPACITY])
{
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (!motion->tracks[i].used) return (int)i;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (!was_active[i] && !matched[i]) {
            memset(&motion->tracks[i], 0, sizeof(motion->tracks[i]));
            motion->tracks[i].prior_rank = UINT16_MAX;
            return (int)i;
        }
    return -1; // Capacity is mathematically bounded by old-active + new-active.
}

static bool copy_sample(dashboard_motion_track_t *track,
                        const dashboard_motion_sample_t *sample,
                        bool is_new)
{
    const bool new_episode = is_new || track->work != sample->work ||
                             track->state_episode != sample->state_episode;
    const bool age_became_known = !track->state_age_known && sample->state_age_known;
    if (!copy_checked(track->logical_id, sizeof(track->logical_id), sample->logical_id,
                      DASHBOARD_MOTION_ID_MAX, true) ||
        !copy_checked(track->project, sizeof(track->project), sample->project,
                      DASHBOARD_MOTION_PROJECT_MAX, false) ||
        !copy_checked(track->provider, sizeof(track->provider), sample->provider,
                      DASHBOARD_MOTION_PROVIDER_MAX, false) ||
        !copy_checked(track->short_id, sizeof(track->short_id), sample->short_id,
                      DASHBOARD_MOTION_SHORT_ID_MAX, false)) return false;
    track->work = sample->work;
    track->health = sample->health;
    if (new_episode || age_became_known || sample->state_age_known != track->state_age_known) {
        track->state_age_known = sample->state_age_known;
        track->state_entered_ms = sample->state_entered_ms;
    }
    track->state_episode = sample->state_episode;
    return true;
}

dashboard_motion_result_t dashboard_motion_apply(
    dashboard_motion_t *motion, const dashboard_motion_snapshot_t *snapshot,
    uint64_t now_ms)
{
    if (!motion || now_ms < motion->now_ms || !validate_snapshot(snapshot, now_ms))
        return snapshot && snapshot->count > DASHBOARD_MOTION_CAPACITY
             ? DASHBOARD_MOTION_REJECTED_CAPACITY : DASHBOARD_MOTION_REJECTED_INVALID;

    size_t available_tracks = 0, needed_tracks = 0;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (!motion->tracks[i].used || !motion->tracks[i].active) ++available_tracks;
    for (size_t i = 0; i < snapshot->count; ++i)
        if (find_track(motion, snapshot->sessions[i].logical_id) < 0) ++needed_tracks;
    if (needed_tracks > available_tracks) return DASHBOARD_MOTION_REJECTED_CAPACITY;

    // All input checks happen before the first controller mutation.
    if (motion->initialized) dashboard_motion_tick(motion, now_ms);
    else motion->now_ms = now_ms;

    bool was_active[DASHBOARD_MOTION_TRACK_CAPACITY] = {false};
    bool matched[DASHBOARD_MOTION_TRACK_CAPACITY] = {false};
    bool created[DASHBOARD_MOTION_TRACK_CAPACITY] = {false};
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        was_active[i] = motion->tracks[i].active;
    // Reserve every incoming existing identity before admitting any new one;
    // an early new sample must not evict a ghost needed by a later sample.
    for (size_t i = 0; i < snapshot->count; ++i) {
        const int found = find_track(motion, snapshot->sessions[i].logical_id);
        if (found >= 0) matched[found] = true;
    }

    for (size_t sample_index = 0; sample_index < snapshot->count; ++sample_index) {
        const dashboard_motion_sample_t *sample = &snapshot->sessions[sample_index];
        int found = find_track(motion, sample->logical_id);
        bool is_new = found < 0;
        if (is_new) {
            found = allocate_track(motion, was_active, matched);
            if (found < 0) return DASHBOARD_MOTION_REJECTED_CAPACITY;
            dashboard_motion_track_t *track = &motion->tracks[found];
            memset(track, 0, sizeof(*track));
            track->prior_rank = UINT16_MAX;
            track->y_q8 = track->start_y_q8 = track->target_y_q8 =
                DASHBOARD_MOTION_BODY_BOTTOM * Q8_ONE;
            track->used = true;
            track->admission_order = motion->next_admission_order++;
            created[found] = true;
        }
        dashboard_motion_track_t *track = &motion->tracks[found];
        if (!copy_sample(track, sample, is_new)) return DASHBOARD_MOTION_REJECTED_INVALID;
        track->active = true;
        track->exiting = false;
        matched[found] = true;
        motion->order[sample_index] = (uint8_t)found;
    }
    motion->count = snapshot->count;

    bool layout_changed = false;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        dashboard_motion_track_t *track = &motion->tracks[i];
        if (was_active[i] && !matched[i]) {
            const int32_t body_end = DASHBOARD_MOTION_BODY_BOTTOM * Q8_ONE;
            const bool intersects_body = track->y_q8 < body_end &&
                track->y_q8 + DASHBOARD_MOTION_ROW_HEIGHT * Q8_ONE >
                DASHBOARD_MOTION_BODY_TOP * Q8_ONE;
            if (intersects_body) {
                track->active = false;
                track->exiting = true;
                track->work = DASH_UNKNOWN;
                track->health = DASH_UNAVAILABLE;
                track->state_age_known = false;
                track->start_y_q8 = track->y_q8;
                if (track->target_y_q8 != body_end) layout_changed = true;
                track->target_y_q8 = body_end;
            } else {
                memset(track, 0, sizeof(*track));
                track->prior_rank = UINT16_MAX;
            }
        } else if (!was_active[i] && track->used && !matched[i]) {
            // A later snapshot replaces, rather than queues, an old exit pose.
            memset(track, 0, sizeof(*track));
            track->prior_rank = UINT16_MAX;
        }
    }

    sort_roster(motion);
    int previous_group = -1, boundaries = 0;
    for (size_t rank = 0; rank < motion->count; ++rank) {
        dashboard_motion_track_t *track = &motion->tracks[motion->order[rank]];
        const int group = group_of(track);
        if (previous_group >= 0 && group != previous_group) ++boundaries;
        previous_group = group;
        const int32_t next_y = target_y_q8((int)rank, boundaries);
        if (track->target_y_q8 != next_y) layout_changed = true;
        track->target_y_q8 = next_y;
        if (!motion->initialized) {
            track->y_q8 = track->start_y_q8 = track->target_y_q8;
        } else if (created[motion->order[rank]] &&
                   track->target_y_q8 >= DASHBOARD_MOTION_BODY_BOTTOM * Q8_ONE) {
            track->y_q8 = track->target_y_q8;
        }
    }

    if (!motion->initialized) {
        for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
            dashboard_motion_track_t *track = &motion->tracks[i];
            if (track->used) {
                track->y_q8 = track->start_y_q8 = track->target_y_q8;
                track->direction = DASHBOARD_MOTION_DIRECTION_STATIONARY;
            }
        }
        motion->animating = false;
        motion->initialized = true;
    } else if (layout_changed) {
        if (!motion->burst_exhausted &&
            now_ms >= motion->last_layout_change_ms &&
            now_ms - motion->last_layout_change_ms >= DASHBOARD_MOTION_DURATION_MS)
            motion->burst_exhausted = false;
        if (!motion->burst_exhausted && !motion->animating) motion->burst_start_ms = now_ms;
        motion->last_layout_change_ms = now_ms;
        const uint64_t deadline = burst_deadline(motion);
        if (motion->burst_exhausted || now_ms >= deadline) {
            for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
                dashboard_motion_track_t *track = &motion->tracks[i];
                if (track->used) {
                    track->y_q8 = track->start_y_q8 = track->target_y_q8;
                    track->direction = DASHBOARD_MOTION_DIRECTION_STATIONARY;
                }
            }
            motion->animating = false;
            motion->burst_exhausted = true;
        } else {
            uint64_t duration = DASHBOARD_MOTION_DURATION_MS;
            if (deadline - now_ms < duration) duration = deadline - now_ms;
            motion->motion_start_ms = now_ms;
            motion->motion_duration_ms = (uint32_t)duration;
            motion->animating = duration != 0;
            for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
                dashboard_motion_track_t *track = &motion->tracks[i];
                if (track->used) {
                    track->start_y_q8 = track->y_q8;
                    track->direction = direction_between(track->start_y_q8,
                                                          track->target_y_q8);
                }
            }
        }
    } else if (motion->animating) {
        // A repeated snapshot with the same layout must not restart easing.
    } else {
        for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
            dashboard_motion_track_t *track = &motion->tracks[i];
            if (track->used) {
                track->start_y_q8 = track->target_y_q8 = track->y_q8;
                track->direction = DASHBOARD_MOTION_DIRECTION_STATIONARY;
            }
        }
    }
    motion->feed_health = DASH_CURRENT;
    motion->now_ms = now_ms;
    return DASHBOARD_MOTION_APPLIED;
}

dashboard_motion_result_t dashboard_motion_feed_lost(
    dashboard_motion_t *motion, dashboard_health_t health, uint64_t now_ms)
{
    if (!motion || !valid_health(health) || health == DASH_CURRENT ||
        now_ms < motion->now_ms) return DASHBOARD_MOTION_REJECTED_INVALID;
    dashboard_motion_tick(motion, now_ms);
    motion->animating = false;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        dashboard_motion_track_t *track = &motion->tracks[i];
        if (!track->used) continue;
        track->start_y_q8 = track->target_y_q8 = track->y_q8;
        track->direction = DASHBOARD_MOTION_DIRECTION_STATIONARY;
    }
    motion->feed_health = health;
    motion->now_ms = now_ms;
    return DASHBOARD_MOTION_APPLIED;
}

static void format_age(char target[4], const dashboard_motion_track_t *track,
                       dashboard_health_t feed_health, uint64_t now_ms)
{
    if (feed_health != DASH_CURRENT || track->health != DASH_CURRENT ||
        track->work == DASH_UNKNOWN || !track->state_age_known ||
        now_ms < track->state_entered_ms) {
        memcpy(target, "?\0\0\0", 4);
        return;
    }
    const uint64_t seconds = (now_ms - track->state_entered_ms) / 1000;
    if (seconds < 60) snprintf(target, 4, "%02lluS", (unsigned long long)seconds);
    else if (seconds < 3600) snprintf(target, 4, "%02lluM",
                                      (unsigned long long)(seconds / 60));
    else if (seconds < 360000) snprintf(target, 4, "%02lluH",
                                        (unsigned long long)(seconds / 3600));
    else memcpy(target, "+++\0", 4);
}

static int rounded_y(int32_t y_q8)
{
    return y_q8 >= 0 ? (y_q8 + Q8_ONE / 2) / Q8_ONE
                     : (y_q8 - Q8_ONE / 2) / Q8_ONE;
}

void dashboard_motion_render(dashboard_motion_t *motion, uint8_t *frame)
{
    if (!motion || !frame) return;
    for (size_t rank = 0; rank < motion->count; ++rank) {
        const uint8_t index = motion->order[rank];
        const dashboard_motion_track_t *track = &motion->tracks[index];
        char *age = motion->render_age[rank];
        format_age(age, track, motion->feed_health, motion->now_ms);
        motion->render_sessions[rank] = (dashboard_session_t){
            .project = track->project,
            .provider = track->provider,
            .short_id = track->short_id,
            .detail = age,
            .work = track->work,
            .health = track->health,
        };
    }

    size_t ghost_count = 0;
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i)
        if (motion->tracks[i].used && motion->tracks[i].exiting)
            motion->render_track_index[ghost_count++] = (uint8_t)i;
    for (size_t i = 1; i < ghost_count; ++i) {
        const uint8_t candidate = motion->render_track_index[i];
        size_t at = i;
        while (at > 0) {
            const dashboard_motion_track_t *left = &motion->tracks[candidate];
            const dashboard_motion_track_t *right =
                &motion->tracks[motion->render_track_index[at - 1]];
            if (left->prior_rank > right->prior_rank ||
                (left->prior_rank == right->prior_rank &&
                 left->admission_order >= right->admission_order)) break;
            motion->render_track_index[at] = motion->render_track_index[at - 1];
            --at;
        }
        motion->render_track_index[at] = candidate;
    }
    for (size_t rank = 0; rank < motion->count; ++rank)
        motion->render_track_index[ghost_count + rank] = motion->order[rank];
    const size_t row_count = ghost_count + motion->count;
    for (size_t i = 0; i < row_count; ++i) {
        const uint8_t index = motion->render_track_index[i];
        const dashboard_motion_track_t *track = &motion->tracks[index];
        format_age(motion->render_age[DASHBOARD_MOTION_CAPACITY + i], track,
                   motion->feed_health, motion->now_ms);
        motion->render_rows[i] = (dashboard_session_t){
            .project = track->project,
            .provider = track->provider,
            .short_id = track->short_id,
            .detail = motion->render_age[DASHBOARD_MOTION_CAPACITY + i],
            .work = track->work,
            .health = track->health,
        };
        motion->render_poses[i] = (dashboard_motion_render_row_t){
            .session = &motion->render_rows[i],
            .y = (int16_t)rounded_y(track->y_q8),
            .direction = track->direction,
        };
    }

    const dashboard_motion_render_t render = {
        .roster = {
            .sessions = motion->render_sessions,
            .count = motion->count,
            .feed_health = motion->feed_health,
        },
        .rows = motion->render_poses,
        .row_count = row_count,
        .feed_lost = motion->feed_health != DASH_CURRENT,
    };
    dashboard_draw_motion(frame, &render);
}

bool dashboard_motion_active(const dashboard_motion_t *motion)
{
    return motion && motion->animating;
}

dashboard_health_t dashboard_motion_feed_health(const dashboard_motion_t *motion)
{
    return motion ? motion->feed_health : DASH_UNAVAILABLE;
}

size_t dashboard_motion_count(const dashboard_motion_t *motion)
{
    return motion ? motion->count : 0;
}

const char *dashboard_motion_identity_at(const dashboard_motion_t *motion,
                                         size_t rank)
{
    if (!motion || rank >= motion->count) return NULL;
    return motion->tracks[motion->order[rank]].logical_id;
}

int dashboard_motion_position_y(const dashboard_motion_t *motion,
                                const char *logical_id)
{
    if (!motion || !logical_id) return INT_MIN;
    const int index = find_track(motion, logical_id);
    return index < 0 ? INT_MIN : rounded_y(motion->tracks[index].y_q8);
}

bool dashboard_motion_state_entry(const dashboard_motion_t *motion,
                                  const char *logical_id, uint64_t *entered_ms)
{
    if (!motion || !logical_id) return false;
    const int index = find_track(motion, logical_id);
    if (index < 0 || !motion->tracks[index].state_age_known) return false;
    if (entered_ms) *entered_ms = motion->tracks[index].state_entered_ms;
    return true;
}
