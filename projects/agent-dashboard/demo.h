#pragma once

#include "agent_dashboard.h"

enum { DASHBOARD_DEMO_CASES = 7 };
const char *dashboard_demo_name(unsigned index);
dashboard_view_t dashboard_demo_view(unsigned index);
dashboard_view_t dashboard_demo_dense_view(unsigned index);
dashboard_view_t dashboard_demo_icon_view(unsigned index);
