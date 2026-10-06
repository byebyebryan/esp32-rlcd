# Title and supporting counts

The later [uniform-row trial](uniform-rows-study.md) retains this header while
using 24px rows for every state. Geometry and measurements below describe
the preceding 24/12px title-header trial.

2026-10-06. The user found the count-only header too similar to the session
rows and preferred the earlier larger AGENTS title with smaller counts.

The 24px Fusion Pixel AGENTS title is left-aligned at x=8. The existing
`x BLOCKED y WAIT z WORK` wording uses native 12px text, right-aligned at
x=392 and vertically centered. Whole-feed loss replaces the healthy header
with a large source-health heading and suppresses cached counts.

The divider moves to y=21, leaving two white scanlines before the body at
y=24. All of this fits inside the existing 24px header. Body height stays
264px: 22 working rows or 11 full rows, without row/group padding.
Column labels remain omitted, and row typography remains 12px working /
24px blocked and waiting.

Unknown counts move beside SIMULATED in the 12px footer. State totals still
include hidden sessions; source loss retains the last-update footer. The
preceding [count-only trial](header-24-study.md) keeps its original evidence.

Native ASan/UBSan and warnings-as-errors checks pass, including divider
separation and the unknown footer. All 42 static frames remain unchanged;
the initial firmware frame is byte-identical to the approved title preview.

Only RLCD `94:a9:90:de:d0:04` was flashed. All three write hashes verified,
and the full 1,234,096-byte application read back identically. Boot ELF prefix
`fb1ea6692`, PSRAM test and panel initialization match the build. A 110.124s
capture covers all 23 phases and one complete cycle: 338 frames, 228 moving,
zero logged errors and no 40ms frame-budget misses. Worst frame is 25.922ms;
internal heap stays at 331,899 bytes and minimum stack watermark is 1,840 bytes.

Original serial access is restored and the separate 349 daemon retains its
service and serial-owner PIDs. The board keeps looping for inspection.
[Archived evidence](../../../docs/evidence/2026-10-06-header-title/README.md)
records the source/build identity, native images, full trace, application
readback and recovery. Physical header acceptance remains a user observation.
The trial remains uncommitted.
