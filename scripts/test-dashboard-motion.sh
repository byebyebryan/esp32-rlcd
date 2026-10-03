#!/usr/bin/env bash
set -euo pipefail

RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RLCD_REPO_ROOT"
mkdir -p build/dashboard-motion
"${CC:-cc}" -std=c11 -O1 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I components/display_rlcd/include -I components/agent_dashboard/include \
    tests/rect_dashboard.c components/display_rlcd/rlcd_frame.c \
    -o build/dashboard-motion/test-rect
build/dashboard-motion/test-rect
"${CC:-cc}" -std=c11 -O1 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I components/display_rlcd/include -I components/agent_dashboard/include \
    -I examples/rlcd-dashboard \
    tests/motion_dashboard.c components/agent_dashboard/agent_dashboard.c \
    components/agent_dashboard/agent_dashboard_motion.c \
    examples/rlcd-dashboard/motion_demo.c components/display_rlcd/rlcd_frame.c \
    -o build/dashboard-motion/test
build/dashboard-motion/test build/dashboard-motion
