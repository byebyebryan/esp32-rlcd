#!/usr/bin/env bash
set -euo pipefail
RLCD_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RLCD_APP_ROOT="$(cd "$RLCD_SCRIPT_DIR/.." && pwd)"
RLCD_REPO_ROOT="$(cd "$RLCD_APP_ROOT/../.." && pwd)"
RLCD_OUTPUT_DIR="$RLCD_APP_ROOT/build/native-live"
mkdir -p "$RLCD_OUTPUT_DIR"
"${CC:-cc}" -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
    -I "$RLCD_REPO_ROOT/components/display_rlcd/include" \
    -I "$RLCD_APP_ROOT/components/agent_dashboard/include" \
    "$RLCD_APP_ROOT/tests/feed_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/dashboard_feed.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/agent_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/agent_dashboard_motion.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/fusion_pixel_12_zh_hans.c" \
    "$RLCD_REPO_ROOT/components/display_rlcd/rlcd_frame.c" \
    -o "$RLCD_OUTPUT_DIR/feed"
RLCD_FEED_TEST="$RLCD_OUTPUT_DIR/feed" python3 "$RLCD_APP_ROOT/tests/test_live_dashboard.py" -v
python3 "$RLCD_APP_ROOT/tests/test_runtime.py" -v
python3 "$RLCD_APP_ROOT/tests/test_serial.py" -v
python3 "$RLCD_APP_ROOT/tests/test_bundle.py" -v
python3 "$RLCD_APP_ROOT/tests/test_prepared_fleet.py" -v
