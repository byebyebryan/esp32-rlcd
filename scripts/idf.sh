#!/usr/bin/env bash
set -eo pipefail

RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# EIM's activation detects sourcing using the shell's $0; use a Bash command
# context so activation also works when this wrapper is executed as a script.
# Call the Python entry point directly because idf.py is a shell function.
exec bash -eo pipefail -c '
    RLCD_REPO_ROOT="$1"
    shift
    . "$RLCD_REPO_ROOT/scripts/env.sh"
    cd "$RLCD_REPO_ROOT"
    exec "$IDF_PYTHON_ENV_PATH/bin/python" "$IDF_PATH/tools/idf.py" "$@"
' bash "$RLCD_REPO_ROOT" "$@"
