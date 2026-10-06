# AGENTS title with supporting counts

2026-10-06. This on-device trial restores a 24px AGENTS title on the left
and the existing `x BLOCKED y WAIT z WORK` counts in native 12px text on
the right. The divider is at y=21, with two white scanlines separating it
from the first row. The 24px header and 264px body retain 22 working rows
or 11 full rows. Column labels remain omitted; row/group padding remains zero.

Unknown counts appear beside SIMULATED in the footer. Whole-feed loss uses
a large health heading, suppresses cached counts and retains the last-update
footer. Row typography, priority ordering and packed feed-loss targets remain.
All input is synthetic. Images are actual native 400x300 renderer outputs.

Native ASan/UBSan and warnings-as-errors checks pass, including divider
separation, large title/smaller counts, unknown-footer and existing motion,
identity, polarity and loss checks. All 42 static frames remain byte-identical.
The initial firmware frame also exactly matches the approved title preview.

Selected-board flash, readback, cycle and access-recovery results are recorded
in `acceptance.json`, `checks.json`, `readback.json` and `recovery.json`.
Source/build manifests and the complete serial trace preserve identity and
runtime evidence. `change.patch` records the change from the preceding trial.
`checksums.json` hashes all archive files except itself. Previous firmware and
the full private flash backup remain local. Physical header acceptance is a
user observation.

Technical acceptance passed on RLCD `94:a9:90:de:d0:04`: all three write
hashes verified and all 1,234,096 application bytes read back identically.
Boot ELF prefix `fb1ea6692`, PSRAM and panel initialization match the build.
The 110.124s capture covers all 23 phases and a complete cycle, with 338
frames, 228 moving, zero errors and no frame-budget misses. Worst frame is
25.922ms, internal heap is constant at 331,899 bytes, and minimum stack
watermark is 1,840 bytes. Original ACL and port access are restored;
the separate 349 daemon retains its PIDs. The firmware remains looping.
