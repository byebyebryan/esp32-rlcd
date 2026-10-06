# Synthetic urgency bands

Date: 2026-10-05. Implemented and flashed; native, build and board timing gates
pass. Physical readability and row-resizing acceptance are pending.
This extends the accepted [motion study](ui-motion.md) with variable row heights.
All data remains invented. The presentation inputs do not define Observer's API.
The follow-up [font-size comparison](font-size-study.md) uses 12/8-pixel text
with this same geometry. The measurements below describe the initial 14-pixel
urgency-band build; its evidence archive remains unchanged.
The later [Fusion font study](fusion-font-study.md) retains the state/membership
and motion rules with 16/8-pixel rows, a 256-pixel list, no boundary gaps and
thirty-two-session fixed storage. Geometry and counts below describe this
earlier urgency-band build.

## State and membership contract

| User-facing state | Meaning in this study | Presentation |
| --- | --- | --- |
| Inactive | Known not open/running; omitted from the active fixture snapshot | No active row |
| Working | Agent turn is progressing without user intervention | Black text on white, 18-pixel row |
| Waiting | Turn has settled and the session awaits another prompt | Black text on white, 26-pixel row |
| Blocked | Turn needs user input, a question answered, or an approval | White text on black, 26-pixel row |

The local model retains its existing work enums: working is `DASH_WORKING`,
waiting is `DASH_SETTLED`, and blocked is `DASH_NEEDS_INPUT`. Existing fixture
errors require intervention and share the blocked band. Interrupted fixtures
are still open, retain their stopped symbol, and share the waiting band;
interruption is not relabeled as successful completion.

Inactivity is a roster-membership fact, not a work-state inference. The fixture
will exercise it by omitting a known inactive identity from a healthy snapshot
and later admitting the same identity again. Saved history and feed silence do
not imply an idle interactive session. Uncertain observations remain a separate
26-pixel band, with unknown age and no cached attention highlight.

Order is blocked, waiting, working, then uncertain. Within trustworthy bands,
known state ages sort oldest first, unknown ages follow, and ties retain prior
order. Hidden complete identities, explicit state episodes and timing provenance
retain their existing meaning. Labels, short IDs and array indices are not keys.

## Layout contract

The 400 x 300 frame keeps its existing fixed header/footer and 215-pixel body
from y=52 through y=266. Full rows stay 26 pixels high. Healthy working rows are
18 pixels high. The initial pass retained 14-pixel names, provider labels and
ages, reducing working-row spacing. The subsequent font comparison uses
12-pixel text in full rows and 8-pixel text in compact rows. State symbols retain
their original polarity, including on blocked rows.

Groups flow together with the existing two-pixel boundary gap. Empty groups
consume no space. There are no permanent group regions or extra heading rows.

Visibility is the highest-priority prefix whose complete rows fit in the body.
Once a row cannot fit, lower-priority rows cannot fill its leftover space.
An all-working roster can show eleven rows; an all-full-size roster shows eight.
The fixed model capacity remains sixteen sessions. Offscreen identities remain
tracked so promotion and demotion preserve identity and age semantics.

Footer overflow uses the admitted count of the latest target layout; transient
row fragments during movement are not additional admissions. Hidden blocked
rows are reported explicitly, including errors requiring intervention; other hidden rows remain
counted. Whole-feed loss suppresses cached work totals, ages and overflow claims.
The motion view uses BLOCK/BLOCKED for intervention and WAIT/WAITING for awaiting
a prompt, avoiding the old ambiguity in its legend/header. The earlier static
study remains unchanged.

## Motion and failure contract

On a valid update, state symbol, inverse styling, age and row height change
immediately. The row and displaced neighbors slide toward the new layout using
shared normalized progress over 360 ms. The row's font changes immediately with
its height in the 12/8-pixel comparison; font size does not animate. Opaque rows
can temporarily cover neighboring row fragments during a crossing, as in the
accepted prototype; they may not superimpose text or escape the body clip.

Downward rows draw first, stationary rows next, upward rows last. A height-only
layout change must also count as a layout change, including one that changes
visibility without changing any row's y position. Latest-target retargeting
starts at the currently displayed positions. The 720 ms burst limit remains.

Removed identities lose cached state/age claims while exiting, but keep their
previous row geometry until departure. Whole-feed loss cancels movement and
freezes positions AND row heights. Health symbols replace cached work symbols;
compact rows are not all expanded in place. Recovery applies the latest healthy
snapshot and recomputes the layout. Individual uncertain rows use full height.

Input validation, bounded strings, atomic rejection, fixed storage, one
framebuffer owner and 10 MHz queued SPI writes retain their existing contracts.
No host bridge, Observer integration, network transport or provider actions are
part of this change.

## Execution and acceptance

The expanded fixture has twenty-three four-second phases (92 seconds). It keeps
the earlier fifteen scenarios and adds explicit working-to-blocked and reverse
transitions, compact capacity, waiting-only, blocked-only, known inactivity,
readmission and an empty roster. A 110-second capture provides startup margin
and proves a completed cycle.

1. Preserve the forty-two existing static preview hashes and the currently
   deployed firmware artifacts for rollback.
2. Delegate one implementation slice to Luna: controller, motion renderer,
   synthetic fixture and native motion tests. The primary owns this plan,
   integration, firmware/capture decisions and overall review.
3. Prove mixed/all-working/all-waiting/all-blocked/empty-group geometry, full-row
   admission and overflow, working-to-blocked promotion, reverse demotion,
   height-only changes, stable identity/ties/ages, rapid retargeting, clipping,
   icon polarity, removal/readmission and frozen geometry on feed loss.
4. Run ASan/UBSan motion/rectangle checks, static previews and the independent
   pixel-packing check. Compare all forty-two static PBMs with the baseline.
   Inspect actual native transition and endpoint frames.
5. Build the default motion firmware and the static fallback independently,
   preserving the default motion configuration for the final deployment.
6. Flash only the already-authorized RLCD identity
   `94:a9:90:de:d0:04`, verify written hashes and application readback, confirm
   boot version/mode/panel initialization, then capture longer than one complete
   synthetic cycle. Require all phases, one application start, no logged errors,
   zero 40 ms frame-budget misses and stable free memory.
7. Record exact source/configuration/image hashes and capture results. Restore
   temporary device access and verify the separate 349 daemon still runs.

The automation gate establishes implementation and board write timing. Physical
readability and whether expanding/contracting rows are easy to track need a new
user observation; prior motion acceptance does not accept this refinement.
No commit, push or release publication is requested.

## Implemented sequence and evidence

The first fifteen scenarios retain the earlier motion/failure study, with the
new geometry. The uncertainty phase also prepares a working row for the next
transition. These additional phases complete the variable-height study:

| Seconds | Scenario | Target roster/visibility |
| --- | --- | --- |
| 60 | Working to blocked | Immediate 18-to-26-pixel expansion and inverse styling |
| 64 | Blocked to working | Immediate 26-to-18-pixel contraction and normal styling |
| 68 | Compact capacity | Twelve working, eleven admitted, one hidden |
| 72 | Waiting only | Twelve waiting, eight admitted, four hidden |
| 76 | Blocked only | Twelve blocked, eight admitted, four hidden blocked |
| 80 | Known inactivity | Visible identity omitted; eleven active, three hidden blocked |
| 84 | Readmission | Same complete identity returns working with a supplied new episode |
| 88 | Empty roster | Zero active rows; no cached overflow |

Luna implemented the controller, renderer, fixture and native tests. The primary
defined the contract, reviewed the implementation and exact frames, integrated
firmware/capture reporting, and performed build/deployment acceptance. Review
also caught a pre-existing burst-rearming defect: a quiet interval now permits
a new transition after a prior burst reached its limit. Its regression passes.

The [recorded checks](../../../docs/evidence/2026-10-05-urgency-bands/checks.json)
pass with these results:

- ASan/UBSan motion checks and 4,488 packed-rectangle/reference comparisons;
  88 motion PBMs generated. Coverage includes early readmission into an exiting
  slot, height-only changes, promotion/demotion, clipping and frozen feed-loss
  geometry.
- All 42 static PBM hashes unchanged; independent 120,000-pixel packing check
  passes. Motion and isolated static builds pass under ESP-IDF 5.5.3; binaries
  are 257,648 and 249,568 bytes respectively.
- Only RLCD `94:a9:90:de:d0:04` flashed. All three write hashes verified; all
  257,648 application bytes read back identically at offset `0x10000`. The
  [image/source manifest](../../../docs/evidence/2026-10-05-urgency-bands/images.json)
  records the exact uncommitted inputs and matches the boot ELF hash prefix.
- The [110.151-second trace](../../../docs/evidence/2026-10-05-urgency-bands/acceptance.json)
  contains all 23 phases, a completed cycle, one application start, 338 frames
  including 228 moving frames, no logged errors and zero 40 ms budget misses.
  Frames took 13.560–18.826 ms; consecutive moving frames were 40.000–40.001 ms
  apart. Internal free memory stayed at 342,835 bytes; minimum stack watermark
  was 1,848 bytes. PSRAM test and panel initialization passed.
- Temporary serial access was removed. The separate `349d.service` remained
  active with the same service/serial-owner PIDs before and after this flash.

The cached app version remains the base revision `06c74f6`; it does not label
the uncommitted refinement. Exact source/image hashes, boot ELF prefix, new
26/18-pixel motion configuration and full application readback establish which
build was tested. The source is not committed or pushed.

Selected exact native PNGs, normalized serial log and complete summary are in
[the evidence archive](../../../docs/evidence/2026-10-05-urgency-bands/README.md).
The board now repeats this 92-second demo. Desk-distance readability of compact
rows and tracking of expansion/contraction remain for a new physical observation.
