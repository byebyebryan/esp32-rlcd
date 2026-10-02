#!/usr/bin/env bash
set -euo pipefail

RLCD_IDF_VERSION="v5.5.3"
RLCD_EIM_ROOT="${EIM_ROOT:-$HOME/.espressif}"
RLCD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$RLCD_EIM_ROOT/tools/activate_idf_${RLCD_IDF_VERSION}.sh" ]]; then
    echo "ESP-IDF $RLCD_IDF_VERSION already installed in $RLCD_EIM_ROOT"
else
    if ! command -v eim >/dev/null 2>&1; then
        echo "error: eim not found. Install Espressif's ESP-IDF Installation Manager." >&2
        echo "See $RLCD_REPO_ROOT/docs/setup.md for fresh-machine prerequisites and installation." >&2
        exit 1
    fi
    echo "Installing ESP-IDF $RLCD_IDF_VERSION into $RLCD_EIM_ROOT ..."
    eim install --config "$RLCD_REPO_ROOT/scripts/eim-config.toml" -p "$RLCD_EIM_ROOT" \
        --tool-install-folder-name "$RLCD_EIM_ROOT/tools" \
        --tool-download-folder-name "$RLCD_EIM_ROOT/dist" \
        --activation-script-path-override "$RLCD_EIM_ROOT/tools" \
        --esp-idf-json-path "$RLCD_EIM_ROOT/tools" \
        --config-file-save-path "$RLCD_EIM_ROOT/eim_config.toml"
fi

# An activation file can outlive a partial installation; check the actual tools.
if ! "$RLCD_REPO_ROOT/scripts/idf.sh" --version; then
    echo "error: ESP-IDF installation is incomplete or has the wrong version." >&2
    echo "See $RLCD_REPO_ROOT/docs/setup.md for installation recovery." >&2
    exit 1
fi

echo "Ready. Build with ./scripts/idf.sh build or source scripts/env.sh."
