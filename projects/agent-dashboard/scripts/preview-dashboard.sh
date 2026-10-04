#!/usr/bin/env bash
set -euo pipefail

RLCD_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RLCD_APP_ROOT="$(cd "$RLCD_SCRIPT_DIR/.." && pwd)"
RLCD_REPO_ROOT="$(cd "$RLCD_APP_ROOT/../.." && pwd)"
RLCD_OUTPUT_DIR="$RLCD_APP_ROOT/build/native-preview"
mkdir -p "$RLCD_OUTPUT_DIR"
"${CC:-cc}" -std=c11 -O2 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I "$RLCD_REPO_ROOT/components/display_rlcd/include" \
    -I "$RLCD_APP_ROOT/components/agent_dashboard/include" \
    -I "$RLCD_APP_ROOT" \
    "$RLCD_APP_ROOT/tests/preview_dashboard.c" \
    "$RLCD_APP_ROOT/components/agent_dashboard/agent_dashboard.c" \
    "$RLCD_APP_ROOT/demo.c" "$RLCD_REPO_ROOT/components/display_rlcd/rlcd_frame.c" \
    -o "$RLCD_OUTPUT_DIR/render"
"$RLCD_OUTPUT_DIR/render" "$RLCD_OUTPUT_DIR"
python3 "$RLCD_SCRIPT_DIR/dashboard-preview.py" "$RLCD_OUTPUT_DIR"
