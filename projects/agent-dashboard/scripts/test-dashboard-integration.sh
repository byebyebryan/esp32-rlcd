#!/usr/bin/env bash
set -euo pipefail
RLCD_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RLCD_PYTHON="${PYTHON:-python3}"
exec "$RLCD_PYTHON" "$RLCD_SCRIPT_DIR/test_dashboard_integration.py"
