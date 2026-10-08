# Synthetic agent roster and motion study

Independent ESP-IDF application for exploring a compact session roster on the
400 × 300 RLCD. The motion view shows a state symbol, name, provider (CX/CC)
and a state-age example. Blocked rows alternate white-on-black and black-on-white
at 1Hz until resolved. Waiting rows stay white on black; working rows stay
black on white. All rows and their text are 24 pixels high, using Fusion Pixel's
native 12-pixel font at scale two. Basic Latin capital height is 16 pixels.
Mixed case and supported Unicode labels retain their supplied characters.
The 276-pixel list admits eleven complete rows with no row/group gaps.
The local model holds up to thirty-two sessions. The earlier five-row layout and fixed
eight-row studies remain in the renderer and native previews.
The motion view has no footer. Its data remains synthetic; the earlier static
screens retain their **DEMO** label.

Motion-view status icons use the earlier shapes and x=8 placement, following
the row text colour directly on its background. Blocked rows share a clock:
500ms in each polarity. Repeated updates retain the phase. Resolution,
inactivity and unavailable evidence stop flashing. On-device feedback accepted
this scheme for roughly one to three blocked requests that clear quickly.

A 24-pixel AGENTS title anchors the header. Right-aligned state icons and
counts use the same 24-pixel font: blocked, waiting and working totals for
the whole active roster, including hidden rows. Uncertain observations add
a question-mark count; `+N` reports hidden rows when necessary. The state
icons use the row shapes at a larger integer scale and remain steady.
A thin divider leaves two white scanlines before the first row, within
the existing 24-pixel header band. Whole-feed loss replaces the title and
counts with a large source-health message; cached work totals are suppressed.
Column labels are omitted. Duplicate project names
gain their supplied short session ID; labels never become identity keys.

There is no live session discovery, host protocol, hook, network connection or
Agent Observer dependency. The presentation structs are local study inputs;
they do not define the shared component's API. The renderer and fixtures are
shared by the native previews and this firmware.
Agent Observer research remains separate: see its
[source study](https://github.com/byebyebryan/agent-observer/blob/main/docs/agent-session-study.md)
and [spike plan](https://github.com/byebyebryan/agent-observer/blob/main/docs/agent-session-spike-plan.md)
for current provider and runtime work.

## Preview without a board

From the repository root:

```sh
./projects/agent-dashboard/scripts/preview-dashboard.sh
./projects/agent-dashboard/scripts/test-dashboard-motion.sh
```

Requires a native C compiler with AddressSanitizer/UndefinedBehaviorSanitizer
and Python 3's standard library. Outputs 42 PBMs, 1-bit PNGs and a comparison
page at `projects/agent-dashboard/build/native-preview/index.html`. The motion
and rectangle suite writes its native scenario and transition PBMs under
`projects/agent-dashboard/build/native-motion/`. Frames are exactly 400 × 300;
browser scaling and monitor contrast do not establish physical readability.

## Build and physical check

After [the normal setup](../../docs/setup.md), build from the repository root:

```sh
./scripts/idf.sh -C projects/agent-dashboard build
```

Flashing replaces the selected board's firmware. Confirm the RLCD's stable
USB identity as described in [the root README](../../README.md), then:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -C projects/agent-dashboard -p "$RLCD_PORT" flash monitor
```

The app uses a 2MiB factory partition for the complete 12px font, keeping the
NVS and PHY partitions at their original addresses.

The default motion demo repeats twenty-three scenarios over 92 seconds, with
four seconds per scenario. Startup logs report the phase count and cycle duration.
It exercises answered waits, prompts, new waits, settling, simultaneous changes,
retargeting, height-based admission, overflow, same-project identity, known
inactivity/readmission, empty groups and feed loss/recovery. See
[the motion proof](docs/ui-motion.md) for its sequence and validation status.
The [urgency-band contract](docs/urgency-bands.md) records the variable-height
refinement and its separate acceptance gates.
The [accepted icon-count header](docs/icon-counts-study.md) records the current
header and footer removal. The [accepted state layout](docs/flashing-rows-study.md)
records the retained row styles and slow flashing. The [uniform-row trial](docs/uniform-rows-study.md)
records the preceding marker/icon-cue comparison. The [title and count refinement](docs/header-title-study.md)
records the retained chrome. The [UI polish](docs/ui-polish.md) records the footer and
feed-loss behavior. The [12px Fusion trial](docs/fusion-12-font-study.md)
records the selected font and earlier device acceptance.
The [earlier 8px Fusion trial](docs/fusion-font-study.md)
records the denser layout rejected during physical review. The earlier
[font-size comparison](docs/font-size-study.md) records the hand-authored 12/8-pixel
bitmaps and preceding 14-pixel baseline.
Rows share eased progress over a 360 ms transition, each along its own start-to-target
path. Downward rows draw behind stationary rows; upward rows draw in front. State
symbols and highlights update immediately, before the slide finishes.
Whole-feed loss settles the last accepted packed layout, retains row heights
and replaces cached work claims with health indicators. Known inactive sessions leave the selected
roster; missing or stale work evidence does not imply inactivity.

For a complete motion trace under the activated IDF Python (the capture must
last longer than the complete-cycle duration reported at startup):

```sh
. scripts/env.sh
python3 projects/agent-dashboard/scripts/capture-dashboard-motion.py \
    --port "$RLCD_PORT" --seconds 110 \
    --reset --output projects/agent-dashboard/build/evidence/dashboard-motion-local
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
python3 projects/agent-dashboard/scripts/capture-dashboard.py \
    --port "$RLCD_PORT" --seconds 100 --reset \
    --output projects/agent-dashboard/build/evidence/dashboard-local
```

Use a new output directory. The capture uses IDF's existing pyserial/esptool
dependencies, resets only the selected board via USB RTS, and checks that all
seven cases were logged with one application start and no logged errors.
Physical readability remains a separate human observation.

In the earlier static view, CX means Codex and CC means Claude Code. A filled triangle means
working, a black exclamation square needs input, a hollow circle settled, a
filled square interrupted, and a black cross square error. A clock/dash/question
mark/slashed circle indicates stale/unavailable/unknown-or-conflicting/unsupported
observations. The header shows PARTIAL instead of totals when any session's
work state is uncertain. Ages are invented state durations, not source freshness.
Settled/idle does not assert task success. The visible ID is removed; the identity
case uses distinct explicit display labels for same-project sessions.
The motion view instead uses row-coloured pixel marks, compact state ages
such as `5s`/`2m`/`1h`, known-state totals plus unknown counts, and conditional
short IDs for duplicate project names. Source update age is separate from
each session's state age.

The static comparison page also includes the earlier X/C symbol layout, normal
CX/CC rows, and a version without the provider field. The earlier static firmware
uses CX/CC with persistent inverse attention rows. The native check verifies that
stale or unavailable work observations cannot retain an attention highlight.
That static study has steady attention highlighting. The current motion view
uses the accepted full-row flashing described above.

[Urgency/age ordering and row motion](docs/ui-motion.md) extend this study
with numeric fixture ages and hidden full identities. The default firmware is
the motion prototype; select **RLCD dashboard study → Use the earlier
seven-screen static layout study** in `menuconfig` to run the seven screens
above and use their capture command. Both modes use invented data.
Select the static option with `./scripts/idf.sh -C projects/agent-dashboard menuconfig`.

To restore the drawing benchmark:

```sh
./scripts/idf.sh -C projects/render-bench -p "$RLCD_PORT" flash
```

To restore the original bring-up pattern:

```sh
./scripts/idf.sh -C projects/bringup -p "$RLCD_PORT" flash
```

See [the UI study notes](docs/ui-study.md) for evidence, boundaries and
open design decisions.
