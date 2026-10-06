#include "dashboard_motion.h"

#include <string.h>

enum {
    DEMO_EPOCH_MS = 86400000u,
    DEMO_PHASE_MS = 4000u,
    DEMO_RETARGET_MS = 160u,
};

static const char *const phase_names[DASHBOARD_MOTION_DEMO_PHASES] = {
    "initial-order",
    "answered-wait-to-run",
    "idle-to-run",
    "run-to-wait",
    "run-to-idle",
    "simultaneous-changes",
    "mid-motion-retarget",
    "overflow-admission",
    "same-project-identities",
    "feed-stale-during-motion",
    "feed-recovery",
    "feed-offline-during-motion",
    "feed-recovery-again",
    "attention-overflow",
    "uncertainty-section",
    "working-to-blocked",
    "blocked-to-working",
    "compact-capacity",
    "waiting-only",
    "blocked-only",
    "inactive-removal",
    "readmission",
    "empty-roster",
};

uint64_t dashboard_motion_demo_cycle_ms(void)
{
    return (uint64_t)DASHBOARD_MOTION_DEMO_PHASES * DEMO_PHASE_MS;
}

size_t dashboard_motion_demo_phase_count(void)
{
    return DASHBOARD_MOTION_DEMO_PHASES;
}

size_t dashboard_motion_demo_phase_index(uint64_t elapsed_ms)
{
    return (size_t)((elapsed_ms % dashboard_motion_demo_cycle_ms()) / DEMO_PHASE_MS);
}

const char *dashboard_motion_demo_phase_name(size_t phase_index)
{
    return phase_index < DASHBOARD_MOTION_DEMO_PHASES ? phase_names[phase_index] : "unknown";
}

uint64_t dashboard_motion_demo_now_ms(uint64_t elapsed_ms)
{
    return DEMO_EPOCH_MS + elapsed_ms;
}

static void make_sample(dashboard_motion_sample_t *sample,
                        const char *logical_id, const char *project,
                        const char *provider, const char *short_id,
                        dashboard_work_t work, dashboard_health_t health,
                        uint64_t now_ms, uint64_t age_ms)
{
    *sample = (dashboard_motion_sample_t){
        .logical_id = logical_id,
        .project = project,
        .provider = provider,
        .short_id = short_id,
        .work = work,
        .health = health,
        .state_age_known = work != DASH_UNKNOWN && health == DASH_CURRENT,
        .state_entered_ms = now_ms >= age_ms ? now_ms - age_ms : 0,
        .state_episode = 1,
    };
}

static const char *const density_ids[] = {
    "codex@local/session/density/12",
    "claude@local/session/density/13",
    "codex@local/session/density/14",
    "claude@local/session/density/15",
    "codex@local/session/density/16",
    "claude@local/session/density/17",
    "codex@local/session/density/18",
    "claude@local/session/density/19",
    "codex@local/session/density/20",
    "claude@local/session/density/21",
    "codex@local/session/density/22",
    "claude@local/session/density/23",
    "codex@local/session/density/24",
    "claude@local/session/density/25",
    "codex@local/session/density/26",
    "claude@local/session/density/27",
    "codex@local/session/density/28",
    "claude@local/session/density/29",
    "codex@local/session/density/30",
    "claude@local/session/density/31",
};

static const char *const density_labels[] = {
    "café / résumé",
    "中文 / 审批",
    "日本語 / レビュー",
    "한국어 / 대시보드",
    "naïve / façade",
    "esp32 / 屏幕",
    "gomoku2d / 五目",
    "raster90 / pixels",
    "agent / 会话",
    "queue / 排序",
    "renderer / 字体",
    "font / 한글",
    "chrome / 開発",
    "rofi / picker",
    "demo / 等待",
    "worker / 渲染",
    "data / 同步",
    "test / かな",
    "layout / 密度",
    "dashboard / 完了",
};

static void reset_fixture(dashboard_motion_t *motion, uint64_t now_ms)
{
    memset(motion->demo_samples, 0, sizeof(motion->demo_samples));
    make_sample(&motion->demo_samples[0],
                "codex@local/session/agent-observer/core", "agent-observer",
                "CODEX", "7A3D", DASH_NEEDS_INPUT, DASH_CURRENT, now_ms, 92000);
    make_sample(&motion->demo_samples[1],
                "claude@local/session/agent-observer/ui", "agent-observer",
                "CLAUDE", "FA29", DASH_ERROR, DASH_CURRENT, now_ms, 35000);
    make_sample(&motion->demo_samples[2],
                "claude@local/session/cubey/main", "cubey",
                "CLAUDE", "8B20", DASH_SETTLED, DASH_CURRENT, now_ms, 420000);
    make_sample(&motion->demo_samples[3],
                "codex@local/session/homelab/ops", "homelab",
                "CODEX", "0E64", DASH_INTERRUPTED, DASH_CURRENT, now_ms, 180000);
    make_sample(&motion->demo_samples[4],
                "codex@local/session/esp32-rlcd/ui", "esp32-rlcd",
                "CODEX", "3C91", DASH_WORKING, DASH_CURRENT, now_ms, 145000);
    make_sample(&motion->demo_samples[5],
                "claude@local/session/remote-chrome/fix", "remote-chrome",
                "CLAUDE", "632F", DASH_WORKING, DASH_CURRENT, now_ms, 42000);
    make_sample(&motion->demo_samples[6],
                "codex@local/session/powered-descent/unknown", "powered-descent",
                "CODEX", "F209", DASH_WORKING, DASH_CURRENT, now_ms, 55000);
    make_sample(&motion->demo_samples[7],
                "claude@local/session/agent-observer/review", "agent-observer",
                "CLAUDE", "C178", DASH_SETTLED, DASH_CURRENT, now_ms, 300000);
    make_sample(&motion->demo_samples[8],
                "codex@local/session/cubey/flood", "cubey",
                "CODEX", "119A", DASH_WORKING, DASH_CURRENT, now_ms, 76000);
    make_sample(&motion->demo_samples[9],
                "claude@local/session/wear-os/design", "wear-os",
                "CLAUDE", "AC04", DASH_SETTLED, DASH_CURRENT, now_ms, 250000);
    make_sample(&motion->demo_samples[10],
                "codex@local/session/rofi-agent-plus/core", "rofi-agent-plus",
                "CODEX", "D5F2", DASH_WORKING, DASH_CURRENT, now_ms, 67000);
    make_sample(&motion->demo_samples[11],
                "claude@local/session/homelab/monitor", "homelab",
                "CLAUDE", "B234", DASH_SETTLED, DASH_CURRENT, now_ms, 510000);
    for (size_t i = 12; i < DASHBOARD_MOTION_DEMO_CAPACITY; ++i)
        make_sample(&motion->demo_samples[i], density_ids[i - 12], density_labels[i - 12],
                    i % 2 ? "CLAUDE" : "CODEX", "DENS", DASH_WORKING,
                    DASH_CURRENT, now_ms, 90000 + i * 1000);
    motion->demo_count = 8;
}

static void set_state(dashboard_motion_sample_t *sample,
                      dashboard_work_t work, uint64_t now_ms)
{
    sample->work = work;
    sample->health = DASH_CURRENT;
    sample->state_age_known = work != DASH_UNKNOWN;
    sample->state_entered_ms = now_ms;
    ++sample->state_episode;
}

static void set_uncertain(dashboard_motion_sample_t *sample,
                          dashboard_health_t health)
{
    sample->work = DASH_UNKNOWN;
    sample->health = health;
    sample->state_age_known = false;
    ++sample->state_episode;
}

static bool apply_fixture(dashboard_motion_t *motion, uint64_t now_ms)
{
    const dashboard_motion_snapshot_t snapshot = {
        .sessions = motion->demo_samples,
        .count = motion->demo_count,
    };
    return dashboard_motion_apply(motion, &snapshot, now_ms) == DASHBOARD_MOTION_APPLIED;
}

static bool remove_demo_sample(dashboard_motion_t *motion, size_t index)
{
    if (index >= motion->demo_count) return false;
    const size_t tail_count = motion->demo_count - index - 1;
    dashboard_motion_sample_t removed = motion->demo_samples[index];
    if (tail_count)
        memmove(&motion->demo_samples[index], &motion->demo_samples[index + 1],
                tail_count * sizeof(motion->demo_samples[0]));
    motion->demo_samples[motion->demo_count - 1] = removed;
    --motion->demo_count;
    return true;
}

static bool begin_phase(dashboard_motion_t *motion, size_t phase, uint64_t now_ms)
{
    dashboard_motion_sample_t *s = motion->demo_samples;
    motion->demo_substep = 0;
    switch (phase) {
    case 0:
        break;
    case 1:
        set_state(&s[0], DASH_WORKING, now_ms);
        break;
    case 2:
        set_state(&s[2], DASH_WORKING, now_ms);
        break;
    case 3:
        set_state(&s[4], DASH_NEEDS_INPUT, now_ms);
        break;
    case 4:
        set_state(&s[5], DASH_SETTLED, now_ms);
        break;
    case 5:
        set_state(&s[1], DASH_WORKING, now_ms);
        set_state(&s[3], DASH_WORKING, now_ms);
        break;
    case 6:
        set_state(&s[5], DASH_NEEDS_INPUT, now_ms);
        motion->demo_substep = 1;
        break;
    case 7:
        motion->demo_count = DASHBOARD_MOTION_DEMO_CAPACITY;
        set_state(&s[9], DASH_NEEDS_INPUT, now_ms);
        break;
    case 8:
        // Samples 0 and 1 deliberately share a project label and differ only
        // by full logical identity/provider; sample 7 adds a third identity.
        set_state(&s[7], DASH_WORKING, now_ms);
        break;
    case 9:
        set_state(&s[8], DASH_NEEDS_INPUT, now_ms);
        motion->demo_substep = 1;
        break;
    case 10:
        set_state(&s[10], DASH_SETTLED, now_ms);
        break;
    case 11:
        set_state(&s[5], DASH_WORKING, now_ms);
        motion->demo_substep = 1;
        break;
    case 12:
        set_state(&s[5], DASH_SETTLED, now_ms);
        break;
    case 13:
        for (size_t i = 0; i < motion->demo_count; ++i)
            set_state(&s[i], (i % 4 == 1) ? DASH_ERROR : DASH_NEEDS_INPUT, now_ms);
        break;
    case 14:
        motion->demo_count = 8;
        set_uncertain(&s[6], DASH_CURRENT);
        set_uncertain(&s[7], DASH_STALE);
        set_state(&s[4], DASH_WORKING, now_ms);
        break;
    case 15:
        set_state(&s[4], DASH_NEEDS_INPUT, now_ms);
        break;
    case 16:
        set_state(&s[4], DASH_WORKING, now_ms);
        break;
    case 17:
        motion->demo_count = DASHBOARD_MOTION_DEMO_CAPACITY;
        for (size_t i = 0; i < motion->demo_count; ++i)
            set_state(&s[i], DASH_WORKING, now_ms);
        break;
    case 18:
        motion->demo_count = DASHBOARD_MOTION_DEMO_CAPACITY;
        for (size_t i = 0; i < motion->demo_count; ++i)
            set_state(&s[i], DASH_SETTLED, now_ms);
        break;
    case 19:
        motion->demo_count = DASHBOARD_MOTION_DEMO_CAPACITY;
        for (size_t i = 0; i < motion->demo_count; ++i)
            set_state(&s[i], (i % 4 == 1) ? DASH_ERROR : DASH_NEEDS_INPUT,
                      now_ms);
        // Keep one visible identity unmistakably first so omission animates
        // an on-screen row rather than an already hidden roster member.
        s[0].state_entered_ms = now_ms - 100000;
        break;
    case 20:
        motion->demo_count = DASHBOARD_MOTION_DEMO_CAPACITY;
        if (!remove_demo_sample(motion, 0)) return false;
        break;
    case 21:
        if (motion->demo_count >= DASHBOARD_MOTION_DEMO_CAPACITY) return false;
        set_state(&s[motion->demo_count], DASH_WORKING, now_ms);
        ++motion->demo_count;
        break;
    case 22:
        motion->demo_count = 0;
        break;
    default:
        return false;
    }
    return apply_fixture(motion, now_ms);
}

bool dashboard_motion_demo_update(dashboard_motion_t *motion, uint64_t elapsed_ms)
{
    if (!motion) return false;
    const uint64_t cycle_ms = dashboard_motion_demo_cycle_ms();
    const uint64_t cycle = elapsed_ms / cycle_ms;
    const uint64_t within_cycle = elapsed_ms % cycle_ms;
    const size_t phase = (size_t)(within_cycle / DEMO_PHASE_MS);
    const uint64_t phase_offset = within_cycle % DEMO_PHASE_MS;
    const uint64_t now_ms = dashboard_motion_demo_now_ms(elapsed_ms);

    if (!motion->demo_initialized || motion->demo_cycle != cycle) {
        reset_fixture(motion, now_ms);
        motion->demo_initialized = true;
        motion->demo_cycle = cycle;
        motion->demo_phase = SIZE_MAX;
        motion->demo_substep = 0;
    }
    if (motion->demo_phase != phase) {
        motion->demo_phase = phase;
        return begin_phase(motion, phase, now_ms);
    }
    if (motion->demo_substep == 1 && phase_offset >= DEMO_RETARGET_MS) {
        motion->demo_substep = 2;
        if (phase == 6) {
            set_state(&motion->demo_samples[0], DASH_SETTLED, now_ms);
            return apply_fixture(motion, now_ms);
        }
        if (phase == 9) {
            return dashboard_motion_feed_lost(motion, DASH_STALE, now_ms) ==
                   DASHBOARD_MOTION_APPLIED;
        }
        if (phase == 11) {
            return dashboard_motion_feed_lost(motion, DASH_UNAVAILABLE, now_ms) ==
                   DASHBOARD_MOTION_APPLIED;
        }
    }
    return false;
}
