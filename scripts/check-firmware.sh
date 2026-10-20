#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
    cat <<'EOF'
Usage: scripts/check-firmware.sh [all|bringup|render-bench|dashboard-live|dashboard-static|dashboard-motion] [--output-root PATH]

Build ESP-IDF v5.5.3 firmware into fresh per-variant directories. With no
variant argument, build all five variants. Set RLCD_IDF_COMMAND to an
executable idf.py path to override the local scripts/idf.sh wrapper.
EOF
}

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

variant=all
variant_seen=false
requested_output_root=
while (($#)); do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --output-root)
            (($# >= 2)) || fail "--output-root needs a path"
            requested_output_root=$2
            shift 2
            ;;
        --output-root=*)
            requested_output_root=${1#*=}
            [[ -n "$requested_output_root" ]] || fail "--output-root needs a path"
            shift
            ;;
        --*)
            fail "unknown option: $1"
            ;;
        *)
            [[ "$variant_seen" == false ]] || fail "choose one variant"
            variant=$1
            variant_seen=true
            shift
            ;;
    esac
done

case "$variant" in
    all|bringup|render-bench|dashboard-live|dashboard-static|dashboard-motion) ;;
    *) fail "unknown firmware variant: $variant" ;;
esac

IDF_COMMAND=${RLCD_IDF_COMMAND:-$REPO_ROOT/scripts/idf.sh}
if [[ "$IDF_COMMAND" != /* ]]; then
    IDF_COMMAND="$REPO_ROOT/$IDF_COMMAND"
fi
[[ -x "$IDF_COMMAND" ]] || fail "ESP-IDF command is not an executable path: $IDF_COMMAND"

cd "$REPO_ROOT"
if ! version_output=$("$IDF_COMMAND" --version 2>&1); then
    printf '%s\n' "$version_output" >&2
    fail "could not query ESP-IDF version from $IDF_COMMAND"
fi
if ! grep -Fqx 'ESP-IDF v5.5.3' <<<"$version_output"; then
    printf '%s\n' "$version_output" >&2
    fail "ESP-IDF v5.5.3 is required"
fi

if [[ -z "$requested_output_root" ]]; then
    OUTPUT_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/rlcd-firmware-ci.XXXXXX")
else
    if [[ "$requested_output_root" == /* ]]; then
        OUTPUT_ROOT=$requested_output_root
    else
        OUTPUT_ROOT="$REPO_ROOT/$requested_output_root"
    fi
    if [[ -e "$OUTPUT_ROOT" ]]; then
        [[ -d "$OUTPUT_ROOT" ]] || fail "output root exists and is not a directory: $OUTPUT_ROOT"
        [[ -z "$(ls -A "$OUTPUT_ROOT")" ]] || fail "output root must be new or empty: $OUTPUT_ROOT"
    else
        mkdir -p "$OUTPUT_ROOT"
    fi
fi

expect_config() {
    local config_file=$1
    local symbol=$2
    local expected=$3
    if ! grep -Fqx "$symbol=$expected" "$config_file"; then
        fail "$config_file does not contain $symbol=$expected"
    fi
}

expect_disabled() {
    local config_file=$1
    local symbol=$2
    if ! grep -Fqx "# $symbol is not set" "$config_file"; then
        fail "$config_file does not disable $symbol"
    fi
}

expect_not_enabled() {
    local config_file=$1
    local symbol=$2
    if grep -Fqx "$symbol=y" "$config_file"; then
        fail "$config_file unexpectedly enables $symbol"
    fi
}

require_binary() {
    local path=$1
    [[ -s "$path" ]] || fail "expected non-empty firmware output: $path"
}

run_variant() {
    local name=$1
    local project app_name variant_root config_file build_dir build_log build_status
    case "$name" in
        bringup)
            project=projects/bringup
            app_name=rlcd-bringup
            ;;
        render-bench)
            project=projects/render-bench
            app_name=rlcd-perf
            ;;
        dashboard-live|dashboard-static|dashboard-motion)
            project=projects/agent-dashboard
            app_name=rlcd-dashboard
            ;;
        *) fail "internal error: unsupported variant $name" ;;
    esac

    variant_root="$OUTPUT_ROOT/$name"
    mkdir -p "$variant_root"
    config_file="$variant_root/sdkconfig"
    build_dir="$variant_root/build"
    build_log="$variant_root/build.log"

    case "$name" in
        dashboard-static)
            cat >"$config_file" <<'EOF'
CONFIG_RLCD_DASHBOARD_STATIC=y
# CONFIG_RLCD_DASHBOARD_LIVE is not set
EOF
            ;;
        dashboard-motion)
            cat >"$config_file" <<'EOF'
# CONFIG_RLCD_DASHBOARD_STATIC is not set
# CONFIG_RLCD_DASHBOARD_LIVE is not set
EOF
            ;;
    esac

    printf 'Building %s with ESP-IDF v5.5.3...\n' "$name"
    if "$IDF_COMMAND" -C "$project" -B "$build_dir" -D "SDKCONFIG=$config_file" build >"$build_log" 2>&1; then
        :
    else
        build_status=$?
        printf 'Build log: %s\n' "$build_log" >&2
        tail -n 100 "$build_log" >&2 || true
        fail "$name build failed with status $build_status"
    fi

    [[ -s "$config_file" ]] || fail "$name did not generate an sdkconfig"
    expect_config "$config_file" CONFIG_IDF_TARGET '"esp32s3"'
    case "$name" in
        dashboard-live)
            expect_config "$config_file" CONFIG_RLCD_DASHBOARD_LIVE y
            expect_disabled "$config_file" CONFIG_RLCD_DASHBOARD_STATIC
            ;;
        dashboard-static)
            expect_config "$config_file" CONFIG_RLCD_DASHBOARD_STATIC y
            # Kconfig omits LIVE because STATIC makes its dependency false.
            expect_not_enabled "$config_file" CONFIG_RLCD_DASHBOARD_LIVE
            ;;
        dashboard-motion)
            expect_disabled "$config_file" CONFIG_RLCD_DASHBOARD_STATIC
            expect_disabled "$config_file" CONFIG_RLCD_DASHBOARD_LIVE
            ;;
    esac

    require_binary "$build_dir/$app_name.bin"
    require_binary "$build_dir/bootloader/bootloader.bin"
    require_binary "$build_dir/partition_table/partition-table.bin"
    printf 'PASS: %s selected the expected configuration and produced firmware binaries (%s)\n' \
        "$name" "$variant_root"
}

printf 'ESP-IDF: 5.5.3\nFirmware CI output: %s\n' "$OUTPUT_ROOT"
if [[ "$variant" == all ]]; then
    for name in bringup render-bench dashboard-live dashboard-static dashboard-motion; do
        run_variant "$name"
    done
else
    run_variant "$variant"
fi
