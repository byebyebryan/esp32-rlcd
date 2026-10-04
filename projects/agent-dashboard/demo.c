#include "demo.h"

// Invented, content-free fixtures. Their ordering demonstrates one possible
// policy (input first); the renderer never interprets or reorders identities.
static const dashboard_session_t sessions[] = {
    {"agent-observer", "CODEX", "7A3D", "APPROVAL", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"esp32-rlcd", "CODEX", "3C91", "2M 14S", DASH_WORKING, DASH_CURRENT},
    {"cubey", "CLAUDE", "8B20", "48S", DASH_WORKING, DASH_CURRENT},
    {"rofi-agent-plus", "CLAUDE", "D5F2", "4M AGO", DASH_SETTLED, DASH_CURRENT},
    {"homelab", "CODEX", "0E64", "7M AGO", DASH_INTERRUPTED, DASH_CURRENT},
    {"wsnav", "CODEX", "19AB", "1M AGO", DASH_SETTLED, DASH_CURRENT},
    {"wear-os", "CLAUDE", "AC04", "3M AGO", DASH_SETTLED, DASH_CURRENT},
};
static const dashboard_session_t uncertainty[] = {
    {"agent-observer", "CODEX", "7A3D", "APPROVAL", DASH_NEEDS_INPUT, DASH_STALE},
    {"esp32-rlcd", "CODEX", "3C91", "2M 14S", DASH_WORKING, DASH_UNAVAILABLE},
    {"cubey", "CLAUDE", "8B20", "48S", DASH_WORKING, DASH_AMBIGUOUS},
    {"rofi-agent-plus", "CLAUDE", "D5F2", "", DASH_UNKNOWN, DASH_UNSUPPORTED},
    {"homelab", "CODEX", "0E64", "", DASH_UNKNOWN, DASH_CURRENT},
};
static const dashboard_session_t identity_cases[] = {
    {"agent-observer", "CODEX", "7A3D", "APPROVAL", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"agent-observer", "CODEX", "FA29", "37S", DASH_WORKING, DASH_CURRENT},
    {"a-very-long-project-name-for-testing", "CLAUDE", "8B20", "INPUT", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"missing-metadata", NULL, NULL, "", DASH_UNKNOWN, DASH_CURRENT},
    {"homelab", "CODEX", "0E64", "API", DASH_ERROR, DASH_CURRENT},
};
static const char *names[] = {
    "roster", "overflow", "stale", "offline", "empty", "uncertainty", "identity",
};

const char *dashboard_demo_name(unsigned index)
{
    return names[index % DASHBOARD_DEMO_CASES];
}

dashboard_view_t dashboard_demo_view(unsigned index)
{
    dashboard_view_t view = {sessions, 5, DASH_CURRENT};
    switch (index % DASHBOARD_DEMO_CASES) {
    case 1: view.count = sizeof(sessions) / sizeof(sessions[0]); break;
    case 2: view.feed_health = DASH_STALE; break;
    case 3: view.feed_health = DASH_UNAVAILABLE; break;
    case 4: view.count = 0; break;
    case 5: view.sessions = uncertainty; break;
    case 6: view.sessions = identity_cases; break;
    default: break;
    }
    return view;
}

static const dashboard_session_t dense_sessions[] = {
    {"agent-observer", "CODEX", "7A3D", "45S", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"cubey", "CLAUDE", "8B20", "1M", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"esp32-rlcd", "CODEX", "3C91", "2M", DASH_WORKING, DASH_CURRENT},
    {"powered-descent", "CLAUDE", "F209", "48S", DASH_WORKING, DASH_CURRENT},
    {"homelab", "CODEX", "0E64", "12M", DASH_WORKING, DASH_CURRENT},
    {"rofi-agent-plus", "CLAUDE", "D5F2", "4M", DASH_SETTLED, DASH_CURRENT},
    {"wear-os", "CODEX", "AC04", "7M", DASH_SETTLED, DASH_CURRENT},
    {"remote-chrome", "CLAUDE", "632F", "9M", DASH_INTERRUPTED, DASH_CURRENT},
    {"raster90", "CLAUDE", "983C", "3M", DASH_SETTLED, DASH_CURRENT},
    {"another-project", "CODEX", "82AA", "1M", DASH_SETTLED, DASH_CURRENT},
    {"one-more", "CODEX", "818B", "2M", DASH_SETTLED, DASH_CURRENT},
};
static const dashboard_session_t dense_identity[] = {
    {"agent-observer", "CODEX", "7A3D", "45S", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"agent-observer", "CODEX", "FA29", "37S", DASH_WORKING, DASH_CURRENT},
    {"a-very-long-project-name-for-testing", "CLAUDE", "8B20", "1M", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"missing-meta", NULL, NULL, "?", DASH_UNKNOWN, DASH_CURRENT},
    {"homelab", "CODEX", "0E64", "1M", DASH_ERROR, DASH_CURRENT},
};

dashboard_view_t dashboard_demo_dense_view(unsigned index)
{
    dashboard_view_t view = {dense_sessions, 8, DASH_CURRENT};
    switch (index % DASHBOARD_DEMO_CASES) {
    case 1: view.count = sizeof(dense_sessions) / sizeof(dense_sessions[0]); break;
    case 2: view.feed_health = DASH_STALE; break;
    case 3: view.feed_health = DASH_UNAVAILABLE; break;
    case 4: view.count = 0; break;
    case 5: view.sessions = uncertainty; view.count = 5; break;
    case 6: view.sessions = dense_identity; view.count = 5; break;
    default: break;
    }
    return view;
}

static const dashboard_session_t icon_identity[] = {
    {"agent-observer / core", "CODEX", "7A3D", "45S", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"agent-observer / ui", "CODEX", "FA29", "37S", DASH_WORKING, DASH_CURRENT},
    {"a-very-long-project-name-for-testing", "CLAUDE", "8B20", "1M", DASH_NEEDS_INPUT, DASH_CURRENT},
    {"missing-meta", NULL, NULL, "?", DASH_UNKNOWN, DASH_CURRENT},
    {"homelab", "CODEX", "0E64", "1M", DASH_ERROR, DASH_CURRENT},
};

dashboard_view_t dashboard_demo_icon_view(unsigned index)
{
    dashboard_view_t view = dashboard_demo_dense_view(index);
    if (index % DASHBOARD_DEMO_CASES == 6) view.sessions = icon_identity;
    return view;
}
