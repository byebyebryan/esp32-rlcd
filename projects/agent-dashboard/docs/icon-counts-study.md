# Large icon counts without a footer

2026-10-07. At normal viewing distance, the 12px header totals and footer were
hard to read. This refinement removes the motion view's footer and uses the same
24px Fusion Pixel text as AGENTS for every header count.

The right side shows the existing blocked, waiting and working icons beside
their respective counts. Counts include the whole accepted roster, including
offscreen sessions. Uncertain observations add a question-mark count rather
than contributing a cached work state. A final `+N` reports hidden rows.
Blocked totals include errors requiring intervention; waiting totals include
interrupted sessions that remain open. Header icons stay steady while blocked
rows retain their accepted 1Hz flashing.

Header icons use the existing six-pixel marks at scale three, yielding 18px
tiles with up to 15px of ink beside the text's 16px capital height. Numbers
use the pinned 12px font at scale two. Two-digit totals, an unknown count and
overflow fit alongside AGENTS without reducing the font size. No state words
or column labels are added.

The header stays within y=0..23, with its divider at y=21 and two clear
scanlines before the list. Removing the footer extends the body to y=24..299.
Its 276px height still admits eleven complete 24px rows; the remaining 12px
does not admit a partial row. Highest-priority prefix admission, oldest-first
ordering, state ages, full identities, row polarity and motion remain.

Whole-feed loss settles the accepted layout, suppresses cached work claims
and replaces the header with a large FEED STALE/OFFLINE message. The footer's
last-update age and source label are removed. Healthy-update provenance is
still retained internally. All fixture data remains synthetic; this changes
presentation only and does not introduce a backend or wire protocol.

The earlier static study remains unchanged. Native checks cover full-size
counts, uncertainty, whole-roster totals, overflow, maximum-capacity header
fit, framebuffer guards and lost-feed suppression. The user accepted the
refinement after it was flashed: "I like this", then requested commit and push.

## Validation and acceptance

Native ASan/UBSan, warnings-as-errors, UTF-8 and 4,488 rectangle checks pass.
All 42 earlier static frame hashes are unchanged. The ESP-IDF 5.5.3 build
passes; all three flash hashes and the full 1,234,256-byte application
readback match. Only RLCD `94:a9:90:f3:43:74` was flashed.

The 110.092s trace covers all 23 phases and a complete 92-second cycle:
390 frames, 192 moving, no logged errors and zero 40ms frame-budget misses.
Worst frame is 19.879ms, internal heap stays at 331,899 bytes and minimum
stack watermark is 1,744 bytes. Boot ELF prefix `294f84cc2` matches the build.
Serial access is unchanged, the RLCD port is released and the separate 349
service and serial owner are unchanged.

The [evidence archive](../../../docs/evidence/2026-10-07-icon-counts/README.md)
preserves the original pending/uncommitted capture fields. Its later
`review.json` records user acceptance and the publication request. The captured
app version is `2b70553-dirty`; source hashes, ELF identity and readback identify
the accepted build independently of the later commit.

## UI review checkpoint

This is a suitable baseline to retain until live data arrives. Uniform readable
type, steady aggregate counts, inverse waiting rows and flashing blocked rows
support the display's main purpose: noticing when a session needs attention.
Eleven visible rows provide useful density without reducing type size. Stable
identity, oldest-first order and shared-progress motion help track changes;
uncertain evidence cannot keep a cached work or attention claim.

No blocking issue was found in this refinement. Revisit these points with real
labels and update cadence rather than adding presentation features now:

- Distinct long project names can truncate to the same visible label. Short IDs
  are currently added only for exact duplicate supplied project names. Live
  display labels should disambiguate these collisions without becoming keys.
- Header totals include hidden sessions, and `+N` reports their omission. If
  more than eleven sessions routinely need attention, decide how hidden ones
  are reached from the host; this display currently has no paging or actions.
- Replay real episodes, unknown ages, source loss and rapid state changes to
  assess motion and flashing under the actual workload. The current timing
  and acceptance evidence comes from synthetic fixtures.
