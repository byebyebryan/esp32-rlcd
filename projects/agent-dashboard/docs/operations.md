# Agent dashboard operation

The default firmware accepts a bounded USB feed from the host bridge. The bridge
reads running Codex sessions on Starship and Snap through the accepted Observer
API 4 / Service 4 / Mesh Agent v3 interfaces. ST and SN identify hosts. Age shows
source-sampled time since conversation activity, rather than time spent blocked
or waiting. Known system helpers and children are excluded. Current failed turns show an error
cross and join blocked rows in the attention count; current phases or a fresh
in-progress turn clear a preceding failure. Useful conversation titles lead
row labels; repository names are fallbacks, with project context or short identity
suffixes only when rendered names collide. The accepted row styles and animation
remain. See the
[live integration contract](live-integration.md) for policy, wire and expiry.

## Verify the application

Build and run the native checks:

```sh
./projects/agent-dashboard/scripts/test-live-dashboard.sh
./projects/agent-dashboard/scripts/test-dashboard-motion.sh
./scripts/idf.sh -C projects/agent-dashboard build
```

## Cached preview and roster

Live acquisition needs the accepted Observer/Mesh Python environment. On the
RLCD host it is:

```sh
RLCD_OBSERVER_PYTHON="$HOME/.local/share/rlcd-agent-dashboard-python/a6-a22-e01a7129-5ac484d7/bin/python"
mkdir -p projects/agent-dashboard/build/live-preview
"$RLCD_OBSERVER_PYTHON" projects/agent-dashboard/scripts/live-dashboard.py \
    --preview projects/agent-dashboard/build/live-preview/frame.txt
projects/agent-dashboard/build/native-live/feed \
    projects/agent-dashboard/build/live-preview/frame.txt \
    projects/agent-dashboard/build/live-preview/live.pbm
python3 projects/agent-dashboard/scripts/dashboard-preview.py \
    projects/agent-dashboard/build/live-preview --live
```

The preview uses firmware's C admission and renderer. Data stays in ignored local
build output. Native checks require only a C compiler and Python's standard
library. The bridge explicitly supplies Agent profile v3; the generic Mesh v1
Agent reader does not admit this endpoint.

The bridge uses Observer a6 prepared read interface 2 with Mesh a22 preparation,
admission and selection interfaces 1. Reader and helper share an AgentProfile;
owned admitted replacements avoid repeated aggregate admission. Each device tick
decodes eligible running conversation bodies and reads full-current identity
summaries for membership and positive exclusions. Context exports contain no row
bodies. A heartbeat cannot renew native evidence; gap, expiry, clock failure and
disconnect still revoke claims. Reconnect creates a new prepared watch. Bundle
verification records these capabilities and the exact accepted dependency tuple.

Run the optional installed-contract checks with the selected Python as well:

```sh
"$RLCD_OBSERVER_PYTHON" -B projects/agent-dashboard/tests/test_prepared_fleet.py -v
```

Inspect the full selected roster, label/identity mapping, hidden rows and exclusion
counts without opening USB:

```sh
"$RLCD_OBSERVER_PYTHON" projects/agent-dashboard/scripts/live-dashboard.py --roster
```

Add `--all` for saved/excluded row details. Diagnostics retain bounded Observer
metadata only. The roster diagnostic deliberately materializes complete current
bodies; normal device ticks use selected bodies and full-current summaries.
The roster's age meaning is explicitly conversation activity.
The [refinement receipt](../../../docs/evidence/2026-10-13-dashboard-refinement/REPORT.md)
records the classification, naming, installed tuple and device acceptance.
The [reliability receipt](../../../docs/evidence/2026-10-13-live-reliability/REPORT.md)
records membership, supervised workers, serial recovery, managed startup and
separate physical operation gates.

## Foreground bridge

After building/flashing the confirmed RLCD, run the bridge in the foreground:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:F3:43:74-if00'
"$RLCD_OBSERVER_PYTHON" projects/agent-dashboard/scripts/live-dashboard.py \
    --port "$RLCD_PORT" --verbose
```

Use `--seconds 60` for a bounded run, or Ctrl+C to stop. The bridge owns the serial
port exclusively and closes its Mesh subscription on exit. It does not reset the
board or create a background service. This first rollout pins the known RLCD
identity; another board requires a reviewed identity change.

## Managed service

The reliability pass installs a versioned host bundle and a Starship user service
`rlcd-agent-dashboard.service`. Chezmoi owns the host selection, launcher, unit and
startup link. Starship's existing user lingering allows startup with the user
manager at boot. The service tolerates absent or busy USB hardware and retries
without taking another owner's port. A device hangup closes the old descriptor;
reconnection uses fresh framing and bridge identity. Unexpected worker termination
fails the owner visibly, and normal service stop releases its owned resources.

After installation, inspect the cached roster with `rlcd-agent-dashboard --roster`.
The [release and logging receipt](../../../docs/evidence/2026-10-13-release-refinement/REPORT.md)
records the current quiet runtime, scoped source publication and release gates.
Use `systemctl --user status rlcd-agent-dashboard.service` and
`journalctl --user -u rlcd-agent-dashboard.service` for operation. Stop it with
`systemctl --user stop rlcd-agent-dashboard.service` before opening a foreground
bridge, capture or firmware tool; restore it with `systemctl --user start
rlcd-agent-dashboard.service`. The service's selected runtime and manifest hash
are recorded in `~/.config/rlcd-agent-dashboard/selection.json`.

`RLCD_EVENT` journal records distinguish Mesh retry, source health, serial
missing/busy/hangup, missing acknowledgements and worker failure. Repeated failure
events are limited. Validated `device_health` records include feed state, counts
and sampled render/heap/stack diagnostics once a minute and when feed health,
partial state or deadline status changes. Routine per-frame ACK/health/summary
output requires `--verbose`, which is useful for bounded foreground captures.
The production unit uses the quiet default. Device acknowledgements prove packet
admission; ACK events also report changes in source admission after warm-up or
source loss. Diagnostic health reports cannot acknowledge a request or renew source
leases. Source leases still determine current observations. The earlier
transient-service recovery is dated evidence in the refinement receipt.

## Bundles and rollback

Build a host bundle after source checks and a local source checkpoint:

```sh
python3 projects/agent-dashboard/scripts/dashboard-bundle.py build \
    --python "$RLCD_OBSERVER_PYTHON" \
    --output "$HOME/.local/share/rlcd-agent-dashboard"
```

The returned manifest hash identifies an immutable directory containing the
bridge, its helpers and font metrics source. The verifier rejects changed,
missing, additional or symlinked payloads and an incompatible dependency tuple.
Update the host selection and validate scoped chezmoi targets before service
replacement; retain the previous bundle and exact selection for rollback.

## Expiry and captures

The board requests replacements every second and expires current claims within
three seconds of the last supported request. Stale rows stop flashing and lose
their age/work claims. Healthy hosts remain useful during partial loss; failed
hosts retain uncertain identity context. A large PARTIAL header qualifies the
view, with a compact `?` when saturated counts need space. Counts above 99 display
`99+`. Whole-feed loss shows FEED OFFLINE. USB power alone does not establish a feed.

The synthetic modes remain available in menuconfig. Disable **Use the live
Observer USB dashboard** for the motion demo; enable **Use the earlier seven-screen
static layout study** for the static demo.

To capture a bounded live run, silence expiry and a bridge restart:

```sh
python3 projects/agent-dashboard/scripts/capture-live-dashboard.py \
    --python "$RLCD_OBSERVER_PYTHON" --port "$RLCD_PORT" --seconds 25 \
    --output projects/agent-dashboard/build/live-device-NEW
```

Use a new output directory and close any existing bridge or monitor first. The
capture compares accepted frame checksums and row counts, then requires source
loss and successful live reacquisition. Physical readability remains a separate
observation. The first [implementation and device receipt](../../../docs/evidence/2026-10-13-live-dashboard/REPORT.md)
records initial automated/native acceptance; the refinement receipt above records
the completed physical review.

For installed-artifact acceptance, add `--bridge` with the selected bundle's
`scripts/live-dashboard.py` and use its selected Python. Without that option the
capture runs the source sibling. Both paths run with isolated Python imports;
source success alone does not verify an installed bundle.


The current device protocol is wire 2. Its `attention` health diagnostic and `!`
header count blocked plus known failed rows. Bundle manifests record `deviceWire`;
restore the archived wire-1 bridge and firmware together when rolling back.

For a bounded fictional failure/retry/expiry proof after selecting wire 2, stop
the RLCD service and run `python3 projects/agent-dashboard/scripts/capture-failure-case.py`.
It owns the known RLCD port exclusively for sixteen seconds, exercises three
failures and one retry, then stops replies to prove expiry. It performs no
provider reads or actions. Restore the real bridge after this device check.
