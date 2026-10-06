# Uniform rows and state markers

The later [flashing-row trial](flashing-rows-study.md) retains equal heights
and replaces the waiting marker and icon cue with the user's state styles.
This document preserves the preceding comparison and its measurements.

2026-10-06. The user requested an on-device trial of equal-height working,
waiting and blocked rows after considering the eleven-row screen capacity.

All rows and row text use 24px tiles: Fusion Pixel 12px at scale two, with
16px Latin capitals. The 264px body at y=24..287 fits eleven complete rows,
with no row padding or group gaps. The model still holds 32 sessions and
admits the highest-priority prefix, reporting hidden and hidden-blocked counts.
Ordering, identity and source-health rules are retained.

Blocked rows stay white on black, with a question mark (or the existing error
mark). Waiting rows stay black on white, with a checkmark and a 3px-wide,
16px-tall black bar at x=8, inset 4px vertically. Working rows stay black on
white, with a chevron and no bar. Icons move to x=12 inside the existing gutter;
name, provider and age columns retain their positions. The title/count header,
divider, two white scanlines and small footer are retained.

A newly observed blocked episode blinks only its icon twice over 900ms,
using 180ms steps, then settles. The whole row never inverts. The cue uses
local observation time, so it also works when state age is unknown. Repeated
snapshots retain the cue's start time. Initial snapshots start steady;
resolution, inactivity and whole-feed loss cancel it. Unchanged feed recovery
does not replay it. A new episode with the same blocked label creates a new
cue. Only visible active requests ask the firmware for additional frames.

Native checks exercise equal heights, eleven-row admission for every state mix,
reordering and feed-loss packing, exact doubled font pixels in both polarities,
waiting marker removal on stale evidence, and icon-only changes without row
motion. Existing static previews remain a separate regression baseline.

Device validation and physical acceptance are recorded separately. The loop
uses synthetic fixtures; on-panel readability remains a user observation.

Only RLCD `94:a9:90:de:d0:04` was flashed. The 1,234,880-byte
application read back identically and boot ELF prefix `a7c03b6e8` matches
the build. A 110.129s capture covers all 23 phases and one complete
92-second cycle: 437 frames, 192 moving frames, no errors or budget
misses. Worst frame is 20.809ms; internal heap stays at
331,131 bytes, with minimum stack watermark 1,728 bytes.
Native ASan/UBSan and warnings-as-errors checks pass; all 42 static frame
hashes remain unchanged. Temporary serial access is restored exactly and the
separate 349 daemon retains its service and serial-owner PIDs. The board
keeps looping for inspection; the trial remains uncommitted.

[Archived evidence](../../../docs/evidence/2026-10-06-uniform-rows/README.md)
records configuration, source/build hashes, readback, native images, the full
device trace and recovery. Physical layout acceptance remains pending.
