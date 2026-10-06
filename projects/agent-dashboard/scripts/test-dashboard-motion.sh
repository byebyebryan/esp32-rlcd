#!/usr/bin/env bash
set -euo pipefail

RLCD_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RLCD_APP_ROOT="$(cd "$RLCD_SCRIPT_DIR/.." && pwd)"
RLCD_REPO_ROOT="$(cd "$RLCD_APP_ROOT/../.." && pwd)"
RLCD_OUTPUT_DIR="$RLCD_APP_ROOT/build/native-motion"
mkdir -p "$RLCD_OUTPUT_DIR"
"${CC:-cc}" -std=c11 -O1 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I "$RLCD_REPO_ROOT/components/display_rlcd/include" \
    -I "$RLCD_APP_ROOT/components/agent_dashboard/include" \
    "$RLCD_APP_ROOT/tests/rect_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/fusion_pixel_12_zh_hans.c" \
    "$RLCD_REPO_ROOT/components/display_rlcd/rlcd_frame.c" \
    -o "$RLCD_OUTPUT_DIR/test-rect"
"$RLCD_OUTPUT_DIR/test-rect"
"${CC:-cc}" -std=c11 -O1 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I "$RLCD_REPO_ROOT/components/display_rlcd/include" \
    -I "$RLCD_APP_ROOT/components/agent_dashboard/include" \
    -I "$RLCD_APP_ROOT" \
    "$RLCD_APP_ROOT/tests/motion_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/agent_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/fusion_pixel_12_zh_hans.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/agent_dashboard_motion.c" \
    "$RLCD_APP_ROOT/motion_demo.c" "$RLCD_REPO_ROOT/components/display_rlcd/rlcd_frame.c" \
    -o "$RLCD_OUTPUT_DIR/test"
"$RLCD_OUTPUT_DIR/test" "$RLCD_OUTPUT_DIR"
