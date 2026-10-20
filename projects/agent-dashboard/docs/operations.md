# Agent dashboard operation

The bridge's default reads the explicit Observer 72-hour working-set profile
through Mesh on Starship and Snap. A member is eligible and either currently
active or recently active; the active branch remains independent of the
72-hour recent window. The display adds a loaded-only filter: current running
runtime is required; unloaded recent history is excluded. Lost evidence for a
previously loaded session retains uncertain context instead of inventing an unload. The full-history `--roster` route is
explicit and has no role in normal USB ticks. ST and SN identify physical hosts; SW marks Snap Work rows. Age is
source-sampled time since conversation activity. Known system helpers and
children are excluded. Current failed turns use an error cross and join blocked
rows in attention; current phases or a fresh in-progress turn clear a preceding
failure. The [live integration contract](live-integration.md) defines membership,
priority, five totals, wire 4 and expiry.

The live bridge keeps bounded restart context in a private per-device file under
`~/.local/state/rlcd-agent-dashboard`. The cache preserves identity, label/project,
host, row order and badge only; restored rows have no current state, validity or
age until Reader admission supports them. A missing, corrupt or route-mismatched
cache fences each physical host until its configured profiles provide a fresh
complete census. Healthy physical hosts initialize independently. Use
`--state-path PATH` to select another private file for live serial operation.
Preview, inspect and roster commands do not open or change this cache.

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
RLCD_OBSERVER_PYTHON="$HOME/.local/share/agent-observer/0.7.0a7-a3983afc-ws72-m4f598719/bin/python"
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
library. The bridge explicitly supplies the fixed working-set profile; generic
Mesh Agent v1 does not admit this endpoint. Use the matching installed Observer
and Mesh wheel artifacts selected by the host bundle, not a same-version
substitute.

The bridge uses Observer a7's working-set read and member-lease interfaces and
Mesh a23 preparation/admission. Reader and helper share a
`WorkingSetAgentProfile`. Normal ticks inspect member bodies, exact scoped
coverage and public lease exports. Each row's current membership/category and
display claims follow their independent deadlines; a response heartbeat cannot
renew them. Positive expiry or partial scope preserves prior identity context
as uncertain; only an admitted negative or current complete census retires it.
Bundle verification pins the profile, 72-hour window, read interfaces and exact
Observer/Mesh wheel archive hashes. Both hosts need the working-set collector
and source/publisher; a reader-only upgrade cannot enable the route.

Run the optional installed-contract checks with the selected Python as well:

```sh
"$RLCD_OBSERVER_PYTHON" -B projects/agent-dashboard/tests/test_prepared_fleet.py -v
"$RLCD_OBSERVER_PYTHON" -B projects/agent-dashboard/tests/test_working_set_consumer.py -v
```

Inspect the full selected roster, label/identity mapping, hidden rows and exclusion
counts without opening USB:

```sh
"$RLCD_OBSERVER_PYTHON" projects/agent-dashboard/scripts/live-dashboard.py --roster
```

Add `--all` for saved/excluded row details. Diagnostics retain bounded Observer
metadata only. The roster diagnostic deliberately materializes complete current
bodies via the original full source. Normal ticks use the separate working-set
source and reconcile exact scopes before device truncation.
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
identities. Starship uses the path above; Snap uses
`/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:DE:D0:04-if00`.
The bridge and bounded live capture accept only those exact identities; the
separate 349 board is not eligible. Another board requires a reviewed identity
change.

## Managed service

The reliability pass installs a versioned host bundle and a user service
`rlcd-agent-dashboard.service`. Chezmoi owns the host selection, launcher, unit and
startup link. Host-specific selection binds each physical host to its exact RLCD
port. User lingering allows startup with the user manager at boot. The service
tolerates absent or busy USB hardware and retries
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
missing, additional or symlinked payloads, an incompatible capability tuple,
and a same-version Observer or Mesh wheel with a different archive hash. Wheel
hashes identify the installed artifacts; the producer acceptance gate separately
checks source, wheel contents and repository parity. Update the host selection
and validate scoped chezmoi targets before service replacement; retain the
previous bundle and exact selection for rollback.

The working-set rollout selects the a7 collector and separately configured
working-set source/publisher on both hosts. Rollback restores that paired role
tuple and the prior bridge/firmware bundle; application-only rollback does not
restore the earlier collector route. Preserve the full `agent` source, Tmux
factories and reader/writer links. Chezmoi's last-applied state can differ after
exact backup restoration: verify affected bytes and links against the retained
backup before any scoped forced reselect. The
[active-feed receipt](../../../docs/evidence/2026-10-16-active-feed/REPORT.md)
records the older wire 2 deployment and its separate rollback boundary.
The [working-set receipt](../../../docs/evidence/2026-10-19-working-set-adoption/REPORT.md)
pins Snap's initial wire-3 selection and matching image. It records the full backup, old tuple restoration,
final readback, native comparison and bounded service/resource observations.
The [Starship synchronization receipt](../../../docs/evidence/2026-10-19-starship-sync/REPORT.md)
records Starship's matching wire-3 client/device selection, full flash backup,
component readback and live expiry/recovery. Its collector and publisher roles
were already selected and remain unchanged. Client rollback restores that host's
old bridge selection and matching firmware; it does not require a producer restart.

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


The current device protocol is wire 4. Its `attention` diagnostic and `!` header
count blocked plus known failed rows. Per-host totals also report waiting,
working, recent and uncertain; recent stays zero because unloaded history is
excluded from this view. Bundle manifests
record `deviceWire` and exact wheel archive hashes. The bridge rejects a mismatched
capability or artifact digest.

For a bounded fictional failure/retry/expiry proof, stop the RLCD service and run:

```sh
python3 projects/agent-dashboard/scripts/capture-failure-case.py --port "$RLCD_PORT"
```

It owns the selected known RLCD port exclusively for sixteen seconds, exercises three
failures and one retry, then stops replies to prove expiry. It performs no
provider reads or actions. The default port is the known Starship RLCD; pass
Snap's exact known by-id path with `--port` when testing Snap. Restore the real
bridge after this device check. Archived wire 2 or wire 3 rollback requires its matching
bridge and firmware pair.
