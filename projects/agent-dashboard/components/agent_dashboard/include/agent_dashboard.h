#pragma once

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

// Local presentation model for a synthetic UI study, not an observer protocol.
typedef enum {
    DASH_WORKING, DASH_NEEDS_INPUT, DASH_SETTLED, DASH_INTERRUPTED,
    DASH_ERROR, DASH_UNKNOWN,
} dashboard_work_t;

typedef enum {
    DASH_CURRENT, DASH_STALE, DASH_UNAVAILABLE, DASH_AMBIGUOUS,
    DASH_UNSUPPORTED,
} dashboard_health_t;

typedef struct {
    const char *project;
    const char *provider;
    const char *short_id; // Display hint only; never a logical identity key.
    const char *detail;   // Synthetic bounded reason/age label, not tool text.
    dashboard_work_t work;
    dashboard_health_t health;
} dashboard_session_t;

typedef struct {
    const dashboard_session_t *sessions;
    size_t count;
    dashboard_health_t feed_health;
} dashboard_view_t;

enum { DASHBOARD_VISIBLE_ROWS = 5, DASHBOARD_DENSE_VISIBLE_ROWS = 8 };

typedef enum {
    DASH_AGENT_SINGLE, DASH_AGENT_PAIR, DASH_AGENT_HIDDEN,
} dashboard_agent_label_t;

typedef struct {
    dashboard_agent_label_t agent_label;
    bool highlight_attention;
} dashboard_style_t;

// Render the supplied order. Selection, ordering and data freshness belong to
// the future host bridge. This study always labels itself DEMO.
void dashboard_draw(uint8_t *frame, const dashboard_view_t *view);
void dashboard_draw_table(uint8_t *frame, const dashboard_view_t *view);
void dashboard_draw_dense(uint8_t *frame, const dashboard_view_t *view);
// Study style choices. Highlighting applies only to current waits/errors.
// Any time-based pulse needs a separate, bounded lifecycle policy.
void dashboard_draw_styled(uint8_t *frame, const dashboard_view_t *view,
                           dashboard_style_t style);
