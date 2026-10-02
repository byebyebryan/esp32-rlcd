# Source from Bash or Zsh: . scripts/env.sh
# Keep the release separate from IDF_VERSION, which EIM's activation changes.
RLCD_IDF_VERSION="v5.5.3"
RLCD_EIM_ROOT="${EIM_ROOT:-$HOME/.espressif}"
RLCD_ACTIVATE="$RLCD_EIM_ROOT/tools/activate_idf_${RLCD_IDF_VERSION}.sh"

if [ ! -f "$RLCD_ACTIVATE" ]; then
    echo "error: $RLCD_ACTIVATE not found. Run ./scripts/setup.sh first." >&2
    return 1 2>/dev/null || exit 1
fi

# EIM's activation script assumes an optional positional argument exists.
. "$RLCD_ACTIVATE" "" || { return 1 2>/dev/null || exit 1; }

if [ "${IDF_VERSION:-}" != "${RLCD_IDF_VERSION#v}" ] || \
   [ ! -f "${IDF_PATH:-}/tools/idf.py" ] || \
   [ ! -x "${IDF_PYTHON_ENV_PATH:-}/bin/python" ]; then
    echo "error: activation did not provide a complete ESP-IDF $RLCD_IDF_VERSION environment." >&2
    echo "See docs/setup.md for installation recovery." >&2
    return 1 2>/dev/null || exit 1
fi

for RLCD_TOOL in xtensa-esp32s3-elf-gcc cmake ninja; do
    if ! command -v "$RLCD_TOOL" >/dev/null 2>&1; then
        echo "error: $RLCD_TOOL missing from the activated toolchain; see docs/setup.md." >&2
        return 1 2>/dev/null || exit 1
    fi
done

echo "ESP-IDF $RLCD_IDF_VERSION activated for esp32-rlcd."
