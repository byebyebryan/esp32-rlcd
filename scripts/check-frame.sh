#!/usr/bin/env bash
set -euo pipefail

RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RLCD_REPO_ROOT"
mkdir -p build/native
"${CC:-cc}" -std=c11 -O2 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I components/display_rlcd/include \
    tests/test_frame.c components/display_rlcd/rlcd_frame.c \
    -o build/native/test-frame
exec build/native/test-frame
