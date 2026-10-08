# Fusion Pixel 12px device trial

The [accepted icon-count header](icon-counts-study.md) uses 24px rows for every
state and a footerless 276px body, admitting eleven complete rows. It retains
the [accepted flashing-row styles](flashing-rows-study.md). Measurements below preserve
the original font trial and subsequent icon refinement.

2026-10-05. The user found the native 8px working text too small and selected
native 12px working rows with doubled 24px blocked/waiting rows. The urgency
order, inverse blocked rows, zero extra padding/group gaps and existing motion
and health behavior remain.

Fusion Pixel 12px monospaced zh_hans release 2026.09.25 has 36,981 encoded
source entries, including the default entry. Its ascent/descent are 10/2;
basic Latin cap height is 8px, giving 8px working and 16px full-size capitals.
The complete source glyph table is linked, with pinned BDF provenance and
notices. The 8px source asset remains available for the earlier trial but is
not linked into the current firmware.

Rows are 12px and 24px, with no extra vertical padding. The body spans
`y=36..287` (252 pixels), admitting 21 all-working sessions or 10 full rows.
The mixed 2 blocked / 4 waiting / 26 working fixture admits 15 rows. Capacity
remains 32 logical sessions; hidden blocked counts remain explicit.

Labels preserve UTF-8 and case, use pixel-width truncation at codepoint
boundaries, and replace unsupported or invalid characters visibly. The two
source vertical kana repeat marks U+3031/U+3032 span two font lines and are
cropped to the current row's native cell, preventing overlap with neighbors.

The larger complete font requires a 2MiB factory application partition instead
of 1MiB. Its offset remains 0x10000, and NVS/PHY offsets and sizes are unchanged.
The prior image and partition table are saved for rollback. Only RLCD
`94:a9:90:de:d0:04` is selected for flashing; the other board's daemon stays active.

Native checks, both firmware builds, flash/readback, boot and a full 23-phase
cycle passed. Physical readability is still the user's observation.
No commit or push is requested.

## Board result

The 110-second capture contains 338 frames, including 228 moving frames, all
23 phases, one application start and one complete 92-second cycle. No errors
or 40ms frame-budget misses occurred. Worst draw time was 11.652ms; worst total
frame time 25.325ms. Consecutive moving frames were 39.998..40.003ms apart. Free
internal heap stayed 331,907 bytes, with 1,736 bytes minimum stack watermark.

The 1,233,408-byte application fits the 2MiB factory partition with 41% free and
read back byte-identically. Boot ELF prefix `7ec7f256c` matches the final build;
PSRAM and 400x300 panel initialization passed. The complete font occupies
974,517 flash bytes. The static application remains 249,488 bytes.

The board reports 21 visible all-working rows and 10 full rows. Mixed overflow,
feed-loss/recovery, uncertainty, inactivity and readmission counts match the
native fixtures. Temporary ACL access was restored exactly, the capture port
was released, and the other board's 349 daemon retained its PID and serial owner.

[Archived evidence](../../../docs/evidence/2026-10-05-fusion-12-font/README.md)
contains hashes, native frames, original boot/frame logs and acceptance checks.
The firmware keeps looping. Physical readability remains the next observation.

## Icon refinement

2026-10-06. The user judged the 12/24px text reasonable and requested correction
of inverse check/question marks on white rows. Status marks now follow row
text colour, drawing black directly on white rows and white on blocked rows.
There is no separate black icon tile. Fonts, icon shapes, positions and row
density are retained. Unknown and feed-loss marks use the white row's black
foreground, suppressing cached attention claims as before.

The refinement is flashed and running on RLCD `94:a9:90:de:d0:04`. Native
polarity checks, the unchanged 42 static frames, full application readback,
and the 110-second / 23-phase device capture passed. There were no frame
budget misses; worst frame was 25.238ms. Serial permissions were restored
exactly. [Icon evidence](../../../docs/evidence/2026-10-06-row-icons/README.md)
records the build and recovery; physical icon appearance awaits observation.
