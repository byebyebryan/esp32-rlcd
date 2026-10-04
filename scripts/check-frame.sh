#!/usr/bin/env bash
set -euo pipefail

RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RLCD_REPO_ROOT"
RLCD_CHECK_FRAME_OUTPUT_DIR="${RLCD_CHECK_FRAME_OUTPUT_DIR:-$RLCD_REPO_ROOT/build/native}"
if [[ "$RLCD_CHECK_FRAME_OUTPUT_DIR" != /* ]]; then
    RLCD_CHECK_FRAME_OUTPUT_DIR="$RLCD_REPO_ROOT/$RLCD_CHECK_FRAME_OUTPUT_DIR"
fi
mkdir -p "$RLCD_CHECK_FRAME_OUTPUT_DIR"
"${CC:-cc}" -std=c11 -O2 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I components/display_rlcd/include \
    tests/test_frame.c components/display_rlcd/rlcd_frame.c \
    -o "$RLCD_CHECK_FRAME_OUTPUT_DIR/test-frame"
exec "$RLCD_CHECK_FRAME_OUTPUT_DIR/test-frame"
