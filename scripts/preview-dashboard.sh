#!/usr/bin/env bash
set -euo pipefail

RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RLCD_REPO_ROOT"
mkdir -p build/dashboard-preview
"${CC:-cc}" -std=c11 -O2 -g -Wall -Wextra -Werror \
    -fsanitize=address,undefined \
    -I components/display_rlcd/include -I components/agent_dashboard/include \
    -I examples/rlcd-dashboard \
    tests/preview_dashboard.c components/agent_dashboard/agent_dashboard.c \
    examples/rlcd-dashboard/demo.c components/display_rlcd/rlcd_frame.c \
    -o build/dashboard-preview/render
build/dashboard-preview/render build/dashboard-preview
python3 scripts/dashboard-preview.py build/dashboard-preview
