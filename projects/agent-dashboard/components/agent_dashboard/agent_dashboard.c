#include "agent_dashboard.h"
#include "dashboard_motion.h"
#include "rlcd_frame.h"

#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "fusion_font_12.h"

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

// Decode within a byte bound. Invalid or truncated UTF-8 consumes one byte
// and draws the font's replacement glyph; identity strings are unaffected.
static uint32_t motion_codepoint(const char **cursor, size_t *remaining)
{
    const unsigned char *s = (const unsigned char *)*cursor;
    if (!*remaining || !s[0]) return 0;
    uint32_t cp = s[0];
    size_t count = 1;
    if (cp >= 0xc2 && cp <= 0xdf) { cp &= 0x1f; count = 2; }
    else if (cp >= 0xe0 && cp <= 0xef) { cp &= 0x0f; count = 3; }
    else if (cp >= 0xf0 && cp <= 0xf4) { cp &= 7; count = 4; }
    else if (cp >= 0x80) cp = 0xfffd;
    if (count > *remaining) { cp = 0xfffd; count = 1; }
    else if (count > 1) {
        for (size_t i = 1; i < count; ++i) {
            if (s[i] < 0x80 || s[i] > 0xbf) { cp = 0xfffd; count = 1; break; }
            cp = (cp << 6) | (s[i] & 0x3f);
        }
        if ((count == 2 && cp < 0x80) || (count == 3 && cp < 0x800) ||
            (count == 4 && cp < 0x10000) || (cp >= 0xd800 && cp <= 0xdfff) ||
            cp > 0x10ffff) { cp = 0xfffd; count = 1; }
    }
    *cursor += count;
    *remaining -= count;
    return cp;
}

static const fusion_pixel_12_glyph_t *motion_glyph(uint32_t cp)
{
    const fusion_pixel_12_glyph_t *g = fusion_pixel_12_lookup(cp);
    return g ? g : fusion_pixel_12_lookup(0xfffd);
}

static int motion_text_width(const char *s, bool compact)
{
    if (!s) s = "?";
    size_t remaining = bounded_length(s, 128);
    int width = 0;
    while (remaining) {
        const uint32_t cp = motion_codepoint(&s, &remaining);
        width += fusion_pixel_12_advance(motion_glyph(cp)) * (compact ? 1 : 2);
    }
    return width;
}

static void motion_draw_glyph(uint8_t *frame, int x, int y,
                              uint32_t cp, int scale, bool white)
{
    const fusion_pixel_12_glyph_t *g = motion_glyph(cp);
    const int width = fusion_pixel_12_width(g), height = fusion_pixel_12_height(g);
    const int left = x + fusion_pixel_12_x_offset(g) * scale;
    const int top = y + (FUSION_PIXEL_12_ASCENT - fusion_pixel_12_y_offset(g) - height) * scale;
    // Two vertical kana marks span two source lines; crop glyph ink to this
    // native cell so their source coverage cannot overwrite neighboring rows.
    for (int row = 0; row < height; ++row) {
        const int pixel_y = top + row * scale;
        if (pixel_y < y || pixel_y + scale > y + 12 * scale) continue;
        for (int col = 0; col < width; ++col) {
            const uint32_t bit = g->bitmap_bit_offset + row * width + col;
            if (fusion_pixel_12_zh_hans_bitmap[bit / 8] & (0x80u >> (bit % 8)))
                rect(frame, left + col * scale, pixel_y, scale, scale, white);
        }
    }
}

// Column limits are pixels, so wide CJK and narrow Latin glyphs share the
// same boundaries. Ellipses replace only complete codepoints.
static int motion_text(uint8_t *frame, int x, int y, const char *s,
                       bool compact, int max_width, bool white)
{
    if (!s) s = "?";
    const int scale = compact ? 1 : 2;
    const bool clipped = motion_text_width(s, compact) > max_width;
    const int dots_width = 3 * fusion_pixel_12_advance(motion_glyph('.')) * scale;
    const int content_width = clipped ? max_width - dots_width : max_width;
    size_t remaining = bounded_length(s, 128);
    int used = 0;
    while (remaining) {
        const uint32_t cp = motion_codepoint(&s, &remaining);
        const int advance = fusion_pixel_12_advance(motion_glyph(cp)) * scale;
        if (used + advance > content_width) break;
        motion_draw_glyph(frame, x + used, y, cp, scale, white);
        used += advance;
    }
    if (clipped && dots_width <= max_width)
        for (int i = 0; i < 3; ++i) {
            motion_draw_glyph(frame, x + used, y, '.', scale, white);
            used += dots_width / 3;
        }
    return used;
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

static void motion_state_symbol(uint8_t *frame, int x, int y,
                                dashboard_work_t work, dashboard_health_t health,
                                int scale, bool white)
{
    // Rows use scale two; header counts use scale three for a 15px cap height.
    static const uint8_t working[6] = {0, 0x10, 0x08, 0x04, 0x08, 0x10};
    static const uint8_t blocked[6] = {0, 0x08, 0x08, 0x08, 0, 0x08};
    static const uint8_t waiting[6] = {0, 0, 0x02, 0x14, 0x08, 0};
    static const uint8_t error[6] = {0, 0x12, 0x0c, 0x0c, 0x12, 0};
    static const uint8_t unknown[6] = {0, 0x0c, 0x02, 0x04, 0, 0x04};
    const uint8_t *bits = unknown;
    if (health == DASH_CURRENT) {
        if (work == DASH_WORKING) bits = working;
        else if (work == DASH_NEEDS_INPUT) bits = blocked;
        else if (work == DASH_ERROR) bits = error;
        else if (work == DASH_SETTLED || work == DASH_INTERRUPTED) bits = waiting;
    }
    for (int row = 0; row < 6; ++row)
        for (int col = 0; col < 6; ++col)
            if (bits[row] & (0x20u >> col))
                rect(frame, x + col * scale, y + row * scale, scale, scale, white);
}

static bool duplicate_project(const dashboard_view_t *roster,
                              const char *project)
{
    if (!roster || !roster->sessions || !project) return false;
    size_t matches = 0;
    for (size_t i = 0; i < roster->count; ++i) {
        const char *candidate = roster->sessions[i].project;
        if (candidate && strcmp(candidate, project) == 0 && ++matches > 1)
            return true;
    }
    return false;
}

static void motion_project_name(uint8_t *frame, int x, int y,
                                const dashboard_motion_render_t *view,
                                const dashboard_session_t *session,
                                bool compact, int max_width, bool white)
{
    if (!session->short_id || !session->short_id[0] ||
        !duplicate_project(&view->roster, session->project)) {
        motion_text(frame, x, y, session->project, compact, max_width, white);
        return;
    }

    char suffix[DASHBOARD_MOTION_SHORT_ID_MAX + 4];
    snprintf(suffix, sizeof(suffix), " #%s", session->short_id);
    const int suffix_width = motion_text_width(suffix, compact);
    if (suffix_width >= max_width) {
        motion_text(frame, x, y, suffix, compact, max_width, white);
        return;
    }
    const int prefix_width = motion_text(frame, x, y, session->project,
                                         compact, max_width - suffix_width, white);
    motion_text(frame, x + prefix_width, y, suffix, compact, suffix_width, white);
}

static void draw_motion_row(uint8_t *frame, const dashboard_motion_render_row_t *row,
                            const dashboard_motion_render_t *view)
{
    const int height = row->height ? row->height : DASHBOARD_MOTION_ROW_HEIGHT;
    if (row->y >= DASHBOARD_MOTION_BODY_BOTTOM ||
        row->y + height <= DASHBOARD_MOTION_BODY_TOP) return;
    const dashboard_session_t *s = row->session;
    const int y = row->y;
    const dashboard_health_t health = view->roster.feed_health == DASH_CURRENT
                                    ? s->health : view->roster.feed_health;
    const bool blocked = health == DASH_CURRENT &&
                         (s->work == DASH_NEEDS_INPUT || s->work == DASH_ERROR);
    const bool waiting = health == DASH_CURRENT &&
                         (s->work == DASH_SETTLED || s->work == DASH_INTERRUPTED);
    // One complete cycle per second, shared by all blocked rows.
    const bool highlighted = waiting || (blocked &&
        (view->now_ms / DASHBOARD_MOTION_FLASH_HALF_PERIOD_MS) % 2 == 0);
    motion_clip_enabled = true;
    motion_clip_top = DASHBOARD_MOTION_BODY_TOP;
    motion_clip_bottom = DASHBOARD_MOTION_BODY_BOTTOM;
    rect(frame, 8, y, 384, height, !highlighted);
    const bool compact = false;
    motion_state_symbol(frame, 8, y + (height - 12) / 2,
                        s->work, health, 2, highlighted);
    motion_project_name(frame, 24, y, view, s, compact, 288, highlighted);
    const char *agent = "??";
    if (s->provider && strcmp(s->provider, "CODEX") == 0) agent = "CX";
    else if (s->provider && strcmp(s->provider, "CLAUDE") == 0) agent = "CC";
    motion_text(frame, 320, y, agent, compact, 24, highlighted);
    const char *age = health == DASH_CURRENT ? s->detail : "?";
    const int age_width = motion_text_width(age, compact);
    motion_text(frame, 392 - (age_width < 40 ? age_width : 40), y,
                age, compact, 40, highlighted);
    motion_clip_enabled = false;
}

static void draw_motion_chrome(uint8_t *frame,
                               const dashboard_motion_render_t *view)
{
    const dashboard_view_t *roster = &view->roster;
    rlcd_frame_clear(frame, true);
    char summary[96];
    if (roster->feed_health != DASH_CURRENT) {
        snprintf(summary, sizeof(summary), "FEED %s", health_label(roster->feed_health));
        motion_text(frame, 8, 0, summary, false, 384, false);
    } else {
        enum { ICON_WIDTH = 18, ICON_GAP = 4, GROUP_GAP = 12 };
        const dashboard_work_t states[] = {
            DASH_NEEDS_INPUT, DASH_SETTLED, DASH_WORKING, DASH_UNKNOWN,
        };
        size_t totals[4] = {0};
        for (size_t i = 0; i < roster->count; ++i) {
            const dashboard_session_t *session = &roster->sessions[i];
            if (session->health != DASH_CURRENT || session->work == DASH_UNKNOWN) {
                ++totals[3];
                continue;
            }
            if (session->work == DASH_NEEDS_INPUT || session->work == DASH_ERROR) ++totals[0];
            else if (session->work == DASH_SETTLED || session->work == DASH_INTERRUPTED) ++totals[1];
            else if (session->work == DASH_WORKING) ++totals[2];
        }
        const size_t groups = totals[3] ? 4 : 3;
        char values[4][24];
        int widths[4];
        int total_width = (int)(groups - 1) * GROUP_GAP;
        for (size_t i = 0; i < groups; ++i) {
            snprintf(values[i], sizeof(values[i]), "%zu", totals[i]);
            widths[i] = ICON_WIDTH + ICON_GAP + motion_text_width(values[i], false);
            total_width += widths[i];
        }
        char overflow[24] = "";
        if (view->overflow_count) {
            snprintf(overflow, sizeof(overflow), "+%zu", view->overflow_count);
            total_width += GROUP_GAP + motion_text_width(overflow, false);
        }
        motion_text(frame, 8, 0, "AGENTS", false, 128, false);
        int x = 392 - total_width;
        for (size_t i = 0; i < groups; ++i) {
            motion_state_symbol(frame, x, 2, states[i], DASH_CURRENT, 3, false);
            motion_text(frame, x + ICON_WIDTH + ICON_GAP, 0,
                        values[i], false, widths[i] - ICON_WIDTH - ICON_GAP, false);
            x += widths[i] + GROUP_GAP;
        }
        if (overflow[0])
            motion_text(frame, x, 0, overflow, false,
                        motion_text_width(overflow, false), false);
    }
    // Keep two white scanlines between the divider and the first packed row.
    rect(frame, 8, DASHBOARD_MOTION_BODY_TOP - 3, 384, 1, false);
}

void dashboard_draw_motion(uint8_t *frame, const dashboard_motion_render_t *view)
{
    draw_motion_chrome(frame, view);
    if (view->row_count == 0) {
        const char *empty = view->roster.feed_health == DASH_CURRENT
                          ? "NO ACTIVE SESSIONS" : "FEED UNAVAILABLE";
        motion_text(frame, 200 - motion_text_width(empty, false) / 2, 140,
                    empty, false, 384, false);
    }
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_DOWN)
            draw_motion_row(frame, &view->rows[i], view);
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_STATIONARY)
            draw_motion_row(frame, &view->rows[i], view);
    for (size_t i = 0; i < view->row_count; ++i)
        if (view->rows[i].direction == DASHBOARD_MOTION_DIRECTION_UP)
            draw_motion_row(frame, &view->rows[i], view);
}
