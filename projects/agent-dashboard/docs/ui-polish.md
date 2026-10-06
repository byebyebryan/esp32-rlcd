# Summary and source-status chrome

2026-10-06. This refines the user-accepted native 12px working / doubled 24px
blocked and waiting typography. The source remains synthetic. The previous
[font trial](fusion-12-font-study.md) and [row-icon evidence](../../../docs/evidence/2026-10-06-row-icons/README.md)
retain their original geometry and measured results.

The subsequent [24px header refinement](header-24-study.md) restores the larger
summary and divider while retaining this count format, footer and row styling.
The measurements below describe the initial 12px header trial.

The header occupies one native 12px line at y=0. It reports the whole roster's
known blocked, waiting and working counts, adding an explicit unknown count
when some rows lack current state. Whole-feed loss replaces those totals with
source health. There is no AGENTS title or SESSION/AGENT/AGE label strip.

The footer occupies one native 12px line at y=288. Its left side says SIMULATED.
The right reports hidden rows and hidden blocked rows only when necessary.
During stale/offline cases it shows the time since the last successfully
accepted healthy fixture snapshot. Failed input, elapsed ticks and repeated
loss events do not refresh that timestamp. No real provider freshness is
implied. A future source can supply its own context and observation provenance.

The body spans y=12..287, adding 24px without shrinking the accepted font.
It fits 23 all-working rows or 11 full rows. Complete highest-priority prefix
admission, 32 logical sessions, zero row/group padding and fixed metadata
columns remain. Ages use compact lowercase units without leading zeroes.
Duplicate exact project names show their supplied short ID within the name
column; long names reserve the suffix's width before codepoint-safe ellipsis.
Full provider-qualified identities continue to own matching and motion.

Healthy reorders retain their 360ms shared-progress slide and immediate state
and size changes. On whole-feed loss, tracks settle to the last accepted
packed targets; departing rows finish leaving. Heights remain as accepted,
while all cached state claims, inverse highlights, ages and totals are
suppressed. This avoids leaving gaps or covered labels frozen mid-crossing.
Recovery accepts and animates the latest healthy snapshot as before.

Native checks and actual renderer frames, firmware build, selected-board
flash/readback and a full 23-phase device cycle are the technical gate.
Physical acceptance of the revised layout remains a user observation.
The worker owns the bounded controller/renderer/tests change; the primary
owns review, documentation, build, device acceptance and access recovery.
Changes remain uncommitted and are not pushed.

## Technical acceptance

Native sanitizer checks, 42 unchanged static frames and a replay of 2,117
settled frames across all 23 phases pass. Default motion firmware built and
was flashed only to RLCD `94:a9:90:de:d0:04`; all three hashes verified and
the full 1,233,872-byte application read back identically. The 110.127-second
trace covered the complete cycle: 338 frames, 228 moving, no errors or frame
budget misses, worst frame 26.118ms. Boot ELF prefix `9147da547`, PSRAM and
panel initialization match the tested build. Free internal heap stayed at
331,899 bytes; minimum stack watermark was 1,840 bytes.

The source/configuration hashes still match. Serial ACL restoration and port
release passed; the separate 349 daemon retained its PIDs. The board keeps
looping for inspection. [Archived evidence](../../../docs/evidence/2026-10-06-ui-polish/README.md)
records the source/image hashes, reviewed frames, native checks, original
serial capture, measured acceptance and access recovery.
