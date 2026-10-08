# Accepted state styling with uniform rows

The subsequent [accepted icon-count header](icon-counts-study.md) retains these
row styles, removes the footer and uses large icon totals with a 276px body.
Measurements below preserve the original flashing-row trial.

2026-10-06. On-device feedback selected 1Hz flashing blocked rows, steady
inverse waiting rows and normal working rows, all at the same height. The
design assumes roughly one to three blocked requests at a time, resolved
shortly. The all-blocked demo remains a stress fixture.

Blocked rows alternate the entire row between white on black and black on
white: one complete cycle each second, with 500ms in each polarity. All
blocked rows use the same monotonic-clock phase. Waiting rows stay white on
black; working rows stay black on white. Icons use the earlier shapes and x=8 placement,
always following the row's text colour without a separate icon background.

All rows and row text retain 24px tiles, using Fusion Pixel 12px at scale two.
The 264px body fits eleven complete rows, without row/group gaps. The AGENTS
title, small totals, divider and footer remain. Ordering and overflow rules
retain the highest-priority complete prefix, with 32 logical sessions.

Flashing continues while a visible blocked request has current evidence;
initial blocked requests also flash. Repeated snapshots do not restart its
phase. Resolved requests, inactive sessions and unavailable work/source
evidence stop flashing. Whole-feed loss settles the accepted layout and
removes cached inverse styling from waiting rows as well. Recovery resumes
the shared clock when current blocked evidence returns.

The firmware requests an additional render only at a changed half-cycle,
alongside existing motion and age updates. It does not continuously render
at 25fps for stationary flashing rows. The existing 40ms loop observes each
half-cycle within one frame tick.

Native checks prove full-row inversion at 500ms and return at 1000ms, two
synchronized blocked rows, unchanged waiting/working rows across phases,
restored icon polarity, no phase reset on repeated snapshots, and stop on
resolution or stale evidence. The user accepted the flashing design after
observing it on the panel, under the expected one-to-three-request workload.
Fixtures are synthetic; live-source integration remains separate.

Only RLCD `94:a9:90:de:d0:04` was flashed. All three write hashes verified;
the 1,234,416-byte application read back identically. Boot ELF prefix
`89e50307c` matches the build. A 110.121s capture covers all 23
phases and a complete 92-second cycle: 390 frames, 192 moving, no
errors or budget misses. Stationary initial rows alternate on 500ms boundaries
within one frame tick; both flash polarities appear and unavailable source
windows stop flashing. Worst frame is 20.703ms, heap stays at
331,899 bytes and minimum stack watermark is 1,808 bytes.

Native sanitizers and warnings-as-errors checks pass; all 42 static frame
hashes remain unchanged. Serial ACL is restored exactly, the RLCD port is
released, and the separate 349 daemon retains its service and serial-owner
PIDs. The board keeps looping. The capture predates acceptance and publication;
its original status is preserved in the archive alongside the later
[review decision](../../../docs/evidence/2026-10-06-flashing-rows/review.json).

[Archived evidence](../../../docs/evidence/2026-10-06-flashing-rows/README.md)
records build identity, native phase images, full trace, readback and recovery.
