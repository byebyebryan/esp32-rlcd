# Summary chrome and packed loss layout

2026-10-06. The approved UI polish removes the generic title and column labels,
uses one native 12px summary line and one source/overflow footer line, and
retains the readable 12px working / 24px blocked and waiting row typography.
The body grows from 252px to 276px: 23 working or 11 full rows, no added gaps.

Known counts remain visible with an explicit unknown count. Conditional short
IDs distinguish duplicate project names, and ages use compact lowercase units.
The footer labels invented data SIMULATED; stale/offline update ages refer to
accepted fixture snapshots. No live data source is connected.

Feed loss settles the last accepted packed target layout and finishes exits,
then suppresses cached state claims. Healthy transitions still slide over
360ms. Native images are exact renderer outputs, not photographs of the board.

Luna owns the cohesive controller/renderer/tests edit. The primary defines the
contract, reviews behavior and actual frames, and owns documentation, build,
selected-board flash/readback, capture and serial recovery. Source and rollback
artifacts are retained locally in the ignored build evidence directory.

Native ASan/UBSan and warnings-as-errors checks pass, including 4,488 packed
rectangle cases and focused chrome/provenance/duplicate/loss regressions.
All 42 static frame hashes match. An independent replay audited 2,117 settled
frames over all 23 phases, including stale/offline, with no gaps or priority
inversions. Actual demo and duplicate-name renderer frames are archived here.

Only RLCD `94:a9:90:de:d0:04` was flashed. All three write hashes verified,
and all 1,233,872 application bytes read back identically. Boot ELF prefix
`9147da547` matches the saved build; PSRAM and 400x300 panel initialization
passed. The application has 41% free in its 2MiB factory partition.

The 110.127-second capture contains all 23 phases and a completed 92-second
cycle: 338 frames, 228 moving frames, one application start, zero errors and
zero 40ms frame-budget misses. Worst frame was 26.118ms. Internal heap stayed
at 331,899 bytes; minimum stack watermark was 1,840 bytes. Moving intervals
were 39.999..40.003ms. Board admission counts match native 23/11 capacity and
mixed/overflow/inactivity/readmission fixtures.

Serial access was released and its original ACL restored exactly. The separate
349 daemon kept its service and serial-owner PIDs. The firmware remains
looping for physical inspection. Layout acceptance requires a new user
observation; this provides no live-source or optical timing acceptance.
Changes remain uncommitted; no push.

`acceptance.json`, `checks.json`, `summary.json`, original boot/frame logs,
source/image manifests and `recovery.json` record the technical gate.
`checksums.json` hashes the archive files. The scoped controller/renderer/test
patch is preserved in `scoped-source.patch`; startup metadata and docs are
primary-owned edits outside that worker patch.
