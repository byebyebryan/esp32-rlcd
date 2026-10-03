# Synthetic agent roster and motion study

Separate ESP-IDF example for exploring a compact session roster on the
400 × 300 RLCD. The current eight-row layout shows a state symbol, name,
provider (CX/CC) and a state-age example. Current waits/errors have white text
on black rows. The earlier five-row layout and eight-row table with visible IDs
are retained in the renderer and native previews.
Every screen is marked **DEMO**.

Status icons retain their original white-on-black polarity on highlighted
rows; only the row text and background reverse.

There is no live session discovery, host protocol, hook, network connection or
Agent Observer dependency. The presentation structs are local study inputs;
they do not define the shared component's API. The renderer and fixtures are
shared by the native previews and this firmware.

## Preview without a board

From the repository root:

```sh
./scripts/preview-dashboard.sh
```

Requires a native C compiler with AddressSanitizer/UndefinedBehaviorSanitizer
and Python 3's standard library. Outputs 42 PBMs, 1-bit PNGs and a comparison
page at `build/dashboard-preview/index.html`. Frames are exactly 400 × 300;
browser scaling and monitor contrast do not establish physical readability.

## Build and physical check

After [the normal setup](../../docs/setup.md), build from the repository root:

```sh
./scripts/idf.sh -C examples/rlcd-dashboard build
```

Flashing replaces the selected board's firmware. Confirm the RLCD's stable
USB identity as described in [the root README](../../README.md), then:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -C examples/rlcd-dashboard -p "$RLCD_PORT" flash monitor
```

The default motion demo repeats every 60 seconds, with four seconds per scenario.
It exercises answered waits, prompts, new waits, settling, simultaneous changes,
retargeting, overflow, same-project identity and feed loss/recovery. See
[the motion proof](../../docs/ui-motion.md) for its sequence and validation status.
Rows share eased progress over a 360 ms transition, each along its own start-to-target
path. Downward rows draw behind stationary rows; upward rows draw in front. State
symbols and highlights update immediately, before the slide finishes.

For a complete motion trace under the activated IDF Python:

```sh
. scripts/env.sh
python scripts/capture-dashboard-motion.py --port "$RLCD_PORT" --seconds 95 \
    --reset --output build/evidence/dashboard-motion-local
```

In the optional static study, screens cycle every 12 seconds:

| Screen | Question to inspect |
| --- | --- |
| roster | Are eight names, state symbols, provider and age readable at desk distance? |
| overflow | Is `+3 MORE` clear, without implying all sessions are visible? |
| stale | Does the stale source clearly suppress old work/wait claims? |
| offline | Is retained identity distinguishable from unavailable current state? |
| empty | Is an available feed with no live sessions distinguishable from a lost feed? |
| uncertainty | Are stale, offline, conflicting, unsupported and unknown rows distinct? |
| identity | Can two sessions in one project be distinguished? Are truncated names, missing metadata and errors legible? |

Logs report the synthetic case, drawing/queued-transfer times and free internal
memory. This is a layout and readability check, not a production performance
benchmark or proof of real provider transitions. Exit the monitor with Ctrl+].

For a complete static trace, close the monitor and run under the activated IDF Python:

```sh
. scripts/env.sh
python scripts/capture-dashboard.py --port "$RLCD_PORT" --seconds 100 --reset \
    --output build/evidence/dashboard-local
```

Use a new output directory. The capture uses IDF's existing pyserial/esptool
dependencies, resets only the selected board via USB RTS, and checks that all
seven cases were logged with one application start and no logged errors.
Physical readability remains a separate human observation.

In the current view, CX means Codex and CC means Claude Code. A filled triangle means
working, a black exclamation square needs input, a hollow circle settled, a
filled square interrupted, and a black cross square error. A clock/dash/question
mark/slashed circle indicates stale/unavailable/unknown-or-conflicting/unsupported
observations. The header shows PARTIAL instead of totals when any session's
work state is uncertain. Ages are invented state durations, not source freshness.
Settled/idle does not assert task success. The visible ID is removed; the identity
case uses distinct explicit display labels for same-project sessions.

The comparison page also includes the earlier X/C symbol layout, normal CX/CC
rows, and a version without the provider field. The selected firmware style is
CX/CC with persistent inverse attention rows. The native check verifies that
stale or unavailable work observations cannot retain an attention highlight.
A brief entry pulse remains a separate proposal; attention highlighting is steady.

[Urgency/age ordering and row motion](../../docs/ui-motion.md) extend this study
with numeric fixture ages and hidden full identities. The default firmware is
the motion prototype; select **RLCD dashboard study → Use the earlier
seven-screen static layout study** in `menuconfig` to run the seven screens
above and use their capture command. Both modes use invented data.

To restore the drawing benchmark:

```sh
./scripts/idf.sh -C examples/rlcd-perf -p "$RLCD_PORT" flash
```

To restore the original bring-up pattern:

```sh
./scripts/idf.sh -p "$RLCD_PORT" flash
```

See [the UI study notes](../../docs/ui-study.md) for evidence, boundaries and
open design decisions.
