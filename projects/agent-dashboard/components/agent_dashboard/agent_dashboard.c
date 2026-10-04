#include "agent_dashboard.h"
#include "dashboard_motion.h"
#include "rlcd_frame.h"

#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Hand-authored 5x7 uppercase study font. Two-pixel strokes give 14px text;
// typography/Unicode remain design questions, not a production font choice.
static const uint8_t letters[][5] = {
    {0x7e,0x11,0x11,0x11,0x7e}, {0x7f,0x49,0x49,0x49,0x36},
    {0x3e,0x41,0x41,0x41,0x22}, {0x7f,0x41,0x41,0x22,0x1c},
    {0x7f,0x49,0x49,0x49,0x41}, {0x7f,0x09,0x09,0x09,0x01},
    {0x3e,0x41,0x49,0x49,0x7a}, {0x7f,0x08,0x08,0x08,0x7f},
    {0x00,0x41,0x7f,0x41,0x00}, {0x20,0x40,0x41,0x3f,0x01},
    {0x7f,0x08,0x14,0x22,0x41}, {0x7f,0x40,0x40,0x40,0x40},
    {0x7f,0x02,0x0c,0x02,0x7f}, {0x7f,0x04,0x08,0x10,0x7f},
    {0x3e,0x41,0x41,0x41,0x3e}, {0x7f,0x09,0x09,0x09,0x06},
    {0x3e,0x41,0x51,0x21,0x5e}, {0x7f,0x09,0x19,0x29,0x46},
    {0x46,0x49,0x49,0x49,0x31}, {0x01,0x01,0x7f,0x01,0x01},
    {0x3f,0x40,0x40,0x40,0x3f}, {0x1f,0x20,0x40,0x20,0x1f},
    {0x3f,0x40,0x38,0x40,0x3f}, {0x63,0x14,0x08,0x14,0x63},
    {0x03,0x04,0x78,0x04,0x03}, {0x61,0x51,0x49,0x45,0x43},
};
static const uint8_t digits[][5] = {
    {0x3e,0x51,0x49,0x45,0x3e}, {0x00,0x42,0x7f,0x40,0x00},
    {0x42,0x61,0x51,0x49,0x46}, {0x21,0x41,0x45,0x4b,0x31},
    {0x18,0x14,0x12,0x7f,0x10}, {0x27,0x45,0x45,0x45,0x39},
    {0x3c,0x4a,0x49,0x49,0x30}, {0x01,0x71,0x09,0x05,0x03},
    {0x36,0x49,0x49,0x49,0x36}, {0x06,0x49,0x49,0x29,0x1e},
};

static bool motion_clip_enabled;
static int motion_clip_top;
static int motion_clip_bottom;

static void put_pixel(uint8_t *f, int x, int y, bool white)
{
    if (!motion_clip_enabled || (y >= motion_clip_top && y < motion_clip_bottom))
        rlcd_frame_pixel(f, x, y, white);
}

static void fill_masked(uint8_t *byte, uint8_t mask, bool white)
{
    if (white) *byte |= mask;
    else *byte &= (uint8_t)~mask;
}

static void rect(uint8_t *f, int x, int y, int w, int h, bool white)
{
    if (w <= 0 || h <= 0) return;
    int first_col = x;
    int last_col = x + w;
    int first_row = y;
    int last_row = y + h;
    if (first_col < 0) first_col = 0;
    if (last_col > RLCD_WIDTH) last_col = RLCD_WIDTH;
    if (first_row < 0) first_row = 0;
    if (last_row > RLCD_HEIGHT) last_row = RLCD_HEIGHT;
    if (motion_clip_enabled) {
        if (first_row < motion_clip_top) first_row = motion_clip_top;
        if (last_row > motion_clip_bottom) last_row = motion_clip_bottom;
    }
    if (first_col >= last_col || first_row >= last_row) return;

    // Each panel byte stores two adjacent columns and four inverted rows.
    // Fill complete bytes directly; mask the edge rows/columns so opaque
    // moving tiles stay cheap without altering neighboring pixels.
    const int low_y = RLCD_HEIGHT - last_row;
    const int high_y = RLCD_HEIGHT - 1 - first_row;
    const int first_byte = low_y / 4, last_byte = high_y / 4;
    const uint8_t low_mask = (uint8_t)(0xffu >> (2 * (low_y % 4)));
    const uint8_t high_mask = (uint8_t)(0xffu << (2 * (3 - high_y % 4)));
    const int first_pair = first_col / 2, last_pair = (last_col - 1) / 2;
    for (int pair = first_pair; pair <= last_pair; ++pair) {
        uint8_t columns = 0xff;
        if (pair == first_pair && (first_col & 1)) columns &= 0x55;
        if (pair == last_pair && (last_col & 1)) columns &= 0xaa;
        uint8_t *column = f + pair * (RLCD_HEIGHT / 4);
        if (first_byte == last_byte) {
            fill_masked(column + first_byte, columns & low_mask & high_mask, white);
            continue;
        }
        fill_masked(column + first_byte, columns & low_mask, white);
        const size_t middle_bytes = (size_t)(last_byte - first_byte - 1);
        if (columns == 0xff) {
            memset(column + first_byte + 1, white ? 0xff : 0, middle_bytes);
        } else {
            for (int at = first_byte + 1; at < last_byte; ++at)
                fill_masked(column + at, columns, white);
        }
        fill_masked(column + last_byte, columns & high_mask, white);
    }
}

static void glyph(unsigned char c, uint8_t columns[5])
{
    memset(columns, 0, 5);
    if (c >= 'a' && c <= 'z') c -= 'a' - 'A';
    if (c >= 'A' && c <= 'Z') memcpy(columns, letters[c - 'A'], 5);
    else if (c >= '0' && c <= '9') memcpy(columns, digits[c - '0'], 5);
    else if (c == '-') memset(columns, 0x08, 5);
    else if (c == '.') columns[2] = 0x40;
    else if (c == '/') {
        for (int i = 0; i < 5; ++i) columns[i] = (uint8_t)(1u << (5 - i));
    } else if (c == '+') {
        memset(columns, 0x08, 5);
        columns[2] = 0x3e;
    } else if (c != ' ') {
        const uint8_t question[5] = {0x02,0x01,0x51,0x09,0x06};
        memcpy(columns, question, 5);
    }
}

static size_t bounded_length(const char *s, size_t limit)
{
    size_t n = 0;
    if (s) while (n < limit && s[n]) ++n;
    return n;
}

static void text(uint8_t *f, int x, int y, const char *s,
                 int scale, size_t limit, bool white)
{
    if (!s) s = "?";
    const size_t n = bounded_length(s, limit + 1);
    for (size_t i = 0; i < n && i < limit; ++i) {
        uint8_t columns[5];
        unsigned char c = (unsigned char)s[i];
        if (n > limit && i + 3 >= limit) c = '.';
        glyph(c, columns);
        for (int col = 0; col < 5; ++col)
            for (int row = 0; row < 7; ++row)
                if (columns[col] & (1u << row))
                    rect(f, x + (int)i * 6 * scale + col * scale,
                         y + row * scale, scale, scale, white);
    }
}

static const char *work_label(dashboard_work_t work)
{
    switch (work) {
    case DASH_WORKING: return "WORK";
    case DASH_NEEDS_INPUT: return "INPUT";
    case DASH_SETTLED: return "SETTLED";
    case DASH_INTERRUPTED: return "STOPPED";
    case DASH_ERROR: return "ERROR";
    default: return "UNKNOWN";
    }
}

static const char *health_label(dashboard_health_t health)
{
    switch (health) {
    case DASH_CURRENT: return "LIVE";
    case DASH_STALE: return "STALE";
    case DASH_UNAVAILABLE: return "OFFLINE";
    case DASH_AMBIGUOUS: return "CONFLICT";
    default: return "NO FEED";
    }
}

void dashboard_draw(uint8_t *f, const dashboard_view_t *view)
{
    rlcd_frame_clear(f, true);
    text(f, 12, 9, "AGENTS", 3, 6, false);
    size_t waiting = 0;
    if (view->feed_health == DASH_CURRENT) {
        for (size_t i = 0; i < view->count; ++i)
            if (view->sessions[i].health == DASH_CURRENT &&
                view->sessions[i].work == DASH_NEEDS_INPUT) ++waiting;
    }
    char summary[32];
    if (view->feed_health == DASH_CURRENT)
        snprintf(summary, sizeof(summary), "%zu WAIT", waiting);
    else snprintf(summary, sizeof(summary), "%s", health_label(view->feed_health));
    text(f, 388 - (int)bounded_length(summary, 11) * 12, 13,
         summary, 2, 11, false);
    rect(f, 12, 37, 376, 2, false);

    size_t visible = view->count < DASHBOARD_VISIBLE_ROWS
                   ? view->count : DASHBOARD_VISIBLE_ROWS;
    for (size_t i = 0; i < visible; ++i) {
        const dashboard_session_t *s = &view->sessions[i];
        const int y = 42 + (int)i * 44;
        const dashboard_health_t health = view->feed_health == DASH_CURRENT
                                       ? s->health : view->feed_health;
        const bool attention = health == DASH_CURRENT &&
                              (s->work == DASH_NEEDS_INPUT || s->work == DASH_ERROR);
        const char *label = health == DASH_CURRENT ? work_label(s->work)
                                                  : health_label(health);
        text(f, 12, y + 3, s->project, 2, 20, false);
        if (attention) rect(f, 278, y, 112, 21, false);
        text(f, 386 - (int)bounded_length(label, 8) * 12, y + 3,
             label, 2, 8, attention);
        char identity[24];
        snprintf(identity, sizeof(identity), "%.6s / %.4s",
                 s->provider ? s->provider : "?", s->short_id ? s->short_id : "?");
        text(f, 12, y + 24, identity, 2, 16, false);
        const char *detail = health == DASH_CURRENT ? s->detail : "UNPROVEN";
        text(f, 386 - (int)bounded_length(detail, 8) * 12, y + 24,
             detail, 2, 8, false);
        if (i + 1 < visible) rect(f, 12, y + 42, 376, 1, false);
    }
    if (!visible) {
        const char *empty = view->feed_health == DASH_CURRENT ? "NO LIVE SESSIONS"
                                                            : "FEED UNAVAILABLE";
        text(f, 200 - (int)strlen(empty) * 6, 135, empty, 2, 25, false);
    }
    rect(f, 12, 267, 376, 2, false);
    char footer[64];
    if (view->count > visible)
        snprintf(footer, sizeof(footer), "DEMO %s / +%zu MORE",
                 health_label(view->feed_health), view->count - visible);
    else snprintf(footer, sizeof(footer), "DEMO %s / %zu SESSIONS",
                  health_label(view->feed_health), view->count);
    text(f, 12, 279, footer, 2, 31, false);
}

static const char *dense_state(const dashboard_session_t *s, dashboard_health_t health)
{
    if (health != DASH_CURRENT) {
        switch (health) {
        case DASH_STALE: return "OLD";
        case DASH_UNAVAILABLE: return "OFF";
        case DASH_AMBIGUOUS: return "AMB";
        default: return "N/A";
        }
    }
    switch (s->work) {
    case DASH_WORKING: return "RUN";
    case DASH_NEEDS_INPUT: return "WAIT";
    case DASH_SETTLED: return "IDLE";
    case DASH_INTERRUPTED: return "STOP";
    case DASH_ERROR: return "ERR";
    default: return "?";
    }
}

void dashboard_draw_table(uint8_t *f, const dashboard_view_t *view)
{
    rlcd_frame_clear(f, true);
    text(f, 12, 9, "AGENTS", 3, 6, false);
    size_t running = 0, waiting = 0;
    bool partial = false;
    if (view->feed_health == DASH_CURRENT) {
        for (size_t i = 0; i < view->count; ++i) {
            const dashboard_session_t *s = &view->sessions[i];
            if (s->health != DASH_CURRENT || s->work == DASH_UNKNOWN) partial = true;
            else if (s->work == DASH_WORKING) ++running;
            else if (s->work == DASH_NEEDS_INPUT) ++waiting;
        }
    }
    char summary[64];
    if (view->feed_health != DASH_CURRENT)
        snprintf(summary, sizeof(summary), "%s", health_label(view->feed_health));
    else if (partial) snprintf(summary, sizeof(summary), "PARTIAL");
    else snprintf(summary, sizeof(summary), "%zu RUN %zu WAIT", running, waiting);
    text(f, 388 - (int)bounded_length(summary, 19) * 12, 13,
         summary, 2, 19, false);
    rect(f, 12, 36, 376, 1, false);
    text(f, 12, 41, "PROJECT", 1, 14, false);
    text(f, 189, 41, "A", 1, 1, false);
    text(f, 214, 41, "ID", 1, 4, false);
    text(f, 285, 41, "STATE", 1, 5, false);
    text(f, 370, 41, "AGE", 1, 3, false);

    const size_t visible = view->count < DASHBOARD_DENSE_VISIBLE_ROWS
                         ? view->count : DASHBOARD_DENSE_VISIBLE_ROWS;
    for (size_t i = 0; i < visible; ++i) {
        const dashboard_session_t *s = &view->sessions[i];
        const int y = 52 + (int)i * 26;
        const dashboard_health_t health = view->feed_health == DASH_CURRENT
                                       ? s->health : view->feed_health;
        const bool attention = health == DASH_CURRENT &&
                              (s->work == DASH_NEEDS_INPUT || s->work == DASH_ERROR);
        const char *agent = "?";
        if (s->provider && strcmp(s->provider, "CODEX") == 0) agent = "X";
        else if (s->provider && strcmp(s->provider, "CLAUDE") == 0) agent = "C";
        text(f, 12, y + 5, s->project, 2, 14, false);
        text(f, 188, y + 5, agent, 2, 1, false);
        text(f, 212, y + 5, s->short_id, 2, 4, false);
        if (attention) rect(f, 274, y + 1, 56, 22, false);
        const char *state = dense_state(s, health);
        text(f, 328 - (int)bounded_length(state, 4) * 12, y + 5,
             state, 2, 4, attention);
        // Synthetic labels carry state-age examples. Feed age is independent.
        const char *age = health == DASH_CURRENT ? s->detail : "?";
        text(f, 388 - (int)bounded_length(age, 4) * 12, y + 5, age, 2, 4, false);
        if (i + 1 < visible) rect(f, 12, y + 25, 376, 1, false);
    }
    if (!visible) {
        const char *empty = view->feed_health == DASH_CURRENT ? "NO LIVE SESSIONS"
                                                            : "FEED UNAVAILABLE";
        text(f, 200 - (int)strlen(empty) * 6, 135, empty, 2, 25, false);
    }
    rect(f, 12, 267, 376, 2, false);
    char footer[64];
    if (view->count > visible)
        snprintf(footer, sizeof(footer), "DEMO X/C / +%zu MORE", view->count - visible);
    else snprintf(footer, sizeof(footer), "DEMO X CODEX C CLAUDE / %zu", view->count);
    text(f, 12, 279, footer, 2, 31, false);
}

static void state_symbol(uint8_t *f, int x, int y,
                         dashboard_work_t work, dashboard_health_t health,
                         bool white)
{
    if (health == DASH_UNAVAILABLE) {
        rect(f, x - 6, y - 1, 13, 3, white);
        return;
    }
    if (health == DASH_AMBIGUOUS || (health == DASH_CURRENT && work == DASH_UNKNOWN)) {
        text(f, x - 5, y - 7, "?", 2, 1, white);
        return;
    }
    if (health == DASH_STALE || health == DASH_UNSUPPORTED || work == DASH_SETTLED) {
        for (int dy = -6; dy <= 6; ++dy)
            for (int dx = -6; dx <= 6; ++dx) {
                const int distance = dx * dx + dy * dy;
                if (distance >= 23 && distance <= 42)
                    put_pixel(f, x + dx, y + dy, white);
            }
        if (health == DASH_STALE) {
            rect(f, x, y - 4, 2, 5, white);
            rect(f, x, y, 4, 2, white);
        } else if (health == DASH_UNSUPPORTED) {
            for (int i = -5; i <= 5; ++i) rect(f, x + i, y + i, 2, 2, white);
        }
        return;
    }
    if (work == DASH_WORKING) {
        for (int dx = 0; dx < 9; ++dx)
            rect(f, x - 5 + dx, y - 6 + dx / 2, 1, 13 - dx, white);
    } else if (work == DASH_INTERRUPTED) {
        rect(f, x - 5, y - 5, 11, 11, white);
    } else if (work == DASH_NEEDS_INPUT || work == DASH_ERROR) {
        rect(f, x - 9, y - 9, 18, 18, white);
        if (work == DASH_NEEDS_INPUT) {
            rect(f, x - 1, y - 6, 3, 8, !white);
            rect(f, x - 1, y + 4, 3, 3, !white);
        } else {
            for (int i = -5; i <= 5; ++i) {
                rect(f, x + i, y + i, 2, 2, !white);
                rect(f, x + i, y - i, 2, 2, !white);
            }
        }
    }
}

void dashboard_draw_dense(uint8_t *f, const dashboard_view_t *view)
{
    const dashboard_style_t style = {DASH_AGENT_SINGLE, false};
    dashboard_draw_styled(f, view, style);
}

static void draw_styled_chrome(uint8_t *f, const dashboard_view_t *view,
                               dashboard_style_t style)
{
    rlcd_frame_clear(f, true);
    text(f, 12, 9, "AGENTS", 3, 6, false);
    size_t running = 0, waiting = 0;
    bool partial = false;
    if (view->feed_health == DASH_CURRENT) {
        for (size_t i = 0; i < view->count; ++i) {
            const dashboard_session_t *s = &view->sessions[i];
            if (s->health != DASH_CURRENT || s->work == DASH_UNKNOWN) partial = true;
            else if (s->work == DASH_WORKING) ++running;
            else if (s->work == DASH_NEEDS_INPUT) ++waiting;
        }
    }
    char summary[64];
    if (view->feed_health != DASH_CURRENT)
        snprintf(summary, sizeof(summary), "%s", health_label(view->feed_health));
    else if (partial) snprintf(summary, sizeof(summary), "PARTIAL");
    else snprintf(summary, sizeof(summary), "%zu RUN %zu WAIT", running, waiting);
    text(f, 388 - (int)bounded_length(summary, 19) * 12, 13,
         summary, 2, 19, false);
    rect(f, 12, 36, 376, 1, false);
    text(f, 38, 41, "SESSION", 1, 24, false);
    if (style.agent_label != DASH_AGENT_HIDDEN)
        text(f, style.agent_label == DASH_AGENT_PAIR ? 316 : 329,
             41, "AGENT", 1, 5, false);
    text(f, 370, 41, "AGE", 1, 3, false);

    rect(f, 12, 267, 376, 2, false);
    text(f, 12, 279, "DEMO", 2, 4, false);
    state_symbol(f, 81, 286, DASH_WORKING, DASH_CURRENT, false);
    text(f, 95, 279, "RUN", 2, 3, false);
    state_symbol(f, 160, 286, DASH_NEEDS_INPUT, DASH_CURRENT, false);
    text(f, 176, 279, "WAIT", 2, 4, false);
    char count[32];
    const size_t visible = view->count < DASHBOARD_DENSE_VISIBLE_ROWS
                         ? view->count : DASHBOARD_DENSE_VISIBLE_ROWS;
    if (view->count > visible) {
        snprintf(count, sizeof(count), "+%zu MORE", view->count - visible);
        text(f, 388 - (int)bounded_length(count, 12) * 12, 279, count, 2, 12, false);
    } else {
        state_symbol(f, 247, 286, DASH_SETTLED, DASH_CURRENT, false);
        text(f, 263, 279, "IDLE", 2, 4, false);
        snprintf(count, sizeof(count), "%zu", view->count);
        text(f, 388 - (int)bounded_length(count, 5) * 12, 279, count, 2, 5, false);
    }
}

static void draw_styled_empty(uint8_t *f, const dashboard_view_t *view)
{
    const char *empty = view->feed_health == DASH_CURRENT ? "NO LIVE SESSIONS"
                                                        : "FEED UNAVAILABLE";
    text(f, 200 - (int)strlen(empty) * 6, 135, empty, 2, 25, false);
}

void dashboard_draw_styled(uint8_t *f, const dashboard_view_t *view,
                           dashboard_style_t style)
{
    draw_styled_chrome(f, view, style);

    const size_t visible = view->count < DASHBOARD_DENSE_VISIBLE_ROWS
                         ? view->count : DASHBOARD_DENSE_VISIBLE_ROWS;
    for (size_t i = 0; i < visible; ++i) {
        const dashboard_session_t *s = &view->sessions[i];
        const int y = 52 + (int)i * 26;
        const dashboard_health_t health = view->feed_health == DASH_CURRENT
                                       ? s->health : view->feed_health;
        const bool highlighted = style.highlight_attention && health == DASH_CURRENT &&
                                 (s->work == DASH_NEEDS_INPUT || s->work == DASH_ERROR);
        if (highlighted) rect(f, 12, y + 1, 376, 23, false);
        // Status marks keep their own polarity when the row text is reversed.
        state_symbol(f, 21, y + 12, s->work, health, false);
        const size_t name_limit = style.agent_label == DASH_AGENT_HIDDEN ? 26
                               : style.agent_label == DASH_AGENT_PAIR ? 23 : 24;
        text(f, 38, y + 5, s->project, 2, name_limit, highlighted);
        if (style.agent_label != DASH_AGENT_HIDDEN) {
            const bool pair = style.agent_label == DASH_AGENT_PAIR;
            const char *agent = pair ? "??" : "?";
            if (s->provider && strcmp(s->provider, "CODEX") == 0) agent = pair ? "CX" : "X";
            else if (s->provider && strcmp(s->provider, "CLAUDE") == 0) agent = pair ? "CC" : "C";
            text(f, pair ? 320 : 336, y + 5, agent, 2, pair ? 2 : 1, highlighted);
        }
        const char *age = health == DASH_CURRENT ? s->detail : "?";
        text(f, 388 - (int)bounded_length(age, 3) * 12, y + 5, age, 2, 3, highlighted);
        if (i + 1 < visible) rect(f, 12, y + 25, 376, 1, false);
    }
    if (!visible) {
        draw_styled_empty(f, view);
    }
}

static void draw_motion_row(uint8_t *frame, const dashboard_motion_render_row_t *row,
                            dashboard_health_t feed_health)
{
    if (row->y >= DASHBOARD_MOTION_BODY_BOTTOM ||
        row->y + DASHBOARD_MOTION_ROW_HEIGHT <= DASHBOARD_MOTION_BODY_TOP) return;
    const dashboard_session_t *s = row->session;
    const int y = row->y;
    const dashboard_health_t health = feed_health == DASH_CURRENT
                                    ? s->health : feed_health;
    const bool highlighted = health == DASH_CURRENT &&
                             (s->work == DASH_NEEDS_INPUT || s->work == DASH_ERROR);
    motion_clip_enabled = true;
    motion_clip_top = DASHBOARD_MOTION_BODY_TOP;
    motion_clip_bottom = DASHBOARD_MOTION_BODY_BOTTOM;
    rect(frame, 12, y, 376, DASHBOARD_MOTION_ROW_HEIGHT, true);
    if (highlighted) rect(frame, 12, y + 1, 376, 23, false);
    // Status symbols retain white marks on black tiles, including inverse rows.
    state_symbol(frame, 21, y + 12, s->work, health, false);
    text(frame, 38, y + 5, s->project, 2, 23, highlighted);
    const char *agent = "??";
    if (s->provider && strcmp(s->provider, "CODEX") == 0) agent = "CX";
    else if (s->provider && strcmp(s->provider, "CLAUDE") == 0) agent = "CC";
    text(frame, 320, y + 5, agent, 2, 2, highlighted);
    const char *age = health == DASH_CURRENT ? s->detail : "?";
    text(frame, 388 - (int)bounded_length(age, 3) * 12,
         y + 5, age, 2, 3, highlighted);
    motion_clip_enabled = false;
}

void dashboard_draw_motion(uint8_t *frame, const dashboard_motion_render_t *view)
{
    const dashboard_style_t style = {DASH_AGENT_PAIR, true};
    draw_styled_chrome(frame, &view->roster, style);
    if (view->row_count == 0) draw_styled_empty(frame, &view->roster);
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_DOWN)
            draw_motion_row(frame, &view->rows[i], view->roster.feed_health);
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY)
            draw_motion_row(frame, &view->rows[i], view->roster.feed_health);
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_UP)
            draw_motion_row(frame, &view->rows[i], view->roster.feed_health);
    if (!view->feed_lost && view->roster.count > DASHBOARD_DENSE_VISIBLE_ROWS) {
        char total[64];
        snprintf(total, sizeof(total), "%zu TOTAL +%zu",
                 view->roster.count,
                 view->roster.count - DASHBOARD_DENSE_VISIBLE_ROWS);
        rect(frame, 240, 269, 148, 31, true);
        text(frame, 388 - (int)bounded_length(total, 12) * 12,
             279, total, 2, 12, false);
    }
    if (view->feed_lost) {
        // The footer remains in place and reports health without cached counts.
        rect(frame, 12, 269, 376, 31, true);
        text(frame, 12, 279, "DEMO", 2, 4, false);
        text(frame, 95, 279, health_label(view->roster.feed_health), 2, 12, false);
    }
}
