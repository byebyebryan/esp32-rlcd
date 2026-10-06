# Fusion Pixel on the RLCD

This is the earlier 16/8-pixel row trial. Physical review found the working
text too small. The current [12px Fusion trial](fusion-12-font-study.md) uses
24/12-pixel rows; this file and its archived evidence retain the earlier result.

Date: 2026-10-05. Flashed and technically verified on the selected RLCD.
Physical readability remains pending.

The user requested wider font coverage and denser working rows. The comparison
used the released Fusion Pixel bitmaps at native 12/8 sizes and native 8px
doubled to 16px. The latter gives an exact two-to-one difference in glyph and
row size, so it is the selected device trial.

## Font and coverage

The motion view uses Fusion Pixel 8px monospaced, Simplified Chinese glyph
variant, pinned to release
[2026.09.25](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.09.25).
Its released BDF is the source of the one-bit data, including baseline,
side bearings and advances. Generated native cells are drawn at scale one or
two; there is no runtime font engine, interpolation or antialiasing.

The complete 8px source set is included, rather than a fixture-only character
subset. The upstream report lists 28,409 characters; the BDF also contains
a default missing-character entry. It covers printable ASCII, Latin-1 and
substantial Chinese, Japanese and Korean text. Coverage is not all Unicode:
unsupported characters use the source replacement glyph. Greek/Cyrillic and
emoji examples intentionally expose remaining gaps in the comparison.

UTF-8 decoding preserves case and supported codepoints. Invalid sequences are
bounded and produce replacement glyphs. Width-based truncation preserves
complete codepoint boundaries and adds an ASCII ellipsis. Display text does
not alter the hidden logical identities. The existing local string-size limits
are byte limits, not Unicode character counts.

The upstream font and dependency notices accompany its vendored source and
generated data. Builds consume local generated assets and need no download.

## Dense layout

| Detail | Selected value |
| --- | --- |
| Panel | 400 x 300, one bit |
| List | y=32 through y=287, 256 pixels |
| Blocked / waiting / uncertain rows | 16 pixels, font at 2x |
| Healthy working rows | 8 pixels, native font |
| Extra row padding / group gaps | Zero |
| Latin capital height | 12 / 6 pixels |
| Basic Latin advance | 8 / 4 pixels |
| Fullwidth advance | 16 / 8 pixels |
| Logical capacity / current-plus-departing tracks | 32 / 64 |

The font grids already include their own vertical space. The renderer uses
smaller bounded state symbols, eight-pixel outside margins, a compact header
and footer, and pixel-measured labels beside fixed provider and age columns.
Blocked rows remain white on black; waiting and working rows are black on white.

Visibility remains the highest-priority complete prefix, with no lower-priority
backfilling. Six full rows plus twenty working rows fill the list exactly.
All-working snapshots admit thirty-two; all-full snapshots admit sixteen.
Hidden blocked counts remain explicit. The earlier static studies retain
their original glyphs and layout.

## Motion and fixture

The established 360ms shared progress, directional layering, retarget bound,
stable identity/age ordering, inactivity/readmission and health handling remain.
Whole-feed loss freezes position and height, replaces cached work claims and
suppresses cached totals. Font scale follows the retained row height during
feed loss or departure, rather than inventing a current working state.

The twenty-three-phase, 92-second fixture adds mixed-case and multilingual
labels and uses thirty-two samples in density and overflow phases. Names,
states and ages remain invented; there is no live data source or host bridge.

## Acceptance

The requested worker-goal-loop routed the bounded font/renderer slice to Luna.
That attempt ended with a model-capacity error. The primary retained and
reviewed partial font assets and geometry, completed the renderer, fixtures and
native coverage, and owned integration review, both builds, flashing, readback
and final device acceptance.

Checks cover deterministic font regeneration, glyph/UTF-8/clipping and
motion invariants under ASan/UBSan, unchanged hashes for all forty-two static
PBMs, the independent panel-packing check, and separate motion/static builds.
The selected RLCD must pass flash hashes, full application readback, boot
identity, panel initialization and a capture longer than one complete cycle,
with all phases, one start, no errors, no 40ms budget misses and stable memory.

The prior application is retained for rollback. Only the confirmed RLCD
`94:a9:90:de:d0:04` is selected; temporary access is restored and the separate
349 daemon is checked afterward. No commit or push is requested.

Desk-distance readability, especially six-pixel capital letters in working
rows, and the appearance of tightly packed multilingual labels need a physical
observation. Successful writes and native images do not establish that result.

## Device result

The final image passed a 110.05-second capture with all twenty-three phases,
one application start and one completed 92-second cycle. The capture contains
338 frames, including 228 moving frames, with no errors or 40ms budget misses.
Worst measured draw time was 12.163ms; total frame time was 25.847ms. Consecutive
moving-frame intervals were exactly 40ms. Free internal heap stayed at 331,907
bytes, and the minimum main-task stack watermark was 1,848 bytes.

On-device startup reports Fusion Pixel 8px zh_hans release 2026.09.25,
scale two/one, 16/8-pixel rows and text cells, 12/6-pixel capital heights,
32-session capacity and body y=32..288. The mixed overflow phase admits 26;
the all-working phase admits 32; waiting-only and blocked-only admit 16.
The latter explicitly reports 16 hidden blocked sessions. Feed-loss,
uncertainty, inactivity and readmission phases passed their expected counts.

Both firmware modes built. The motion application is 766,528 bytes, leaving
282,048 bytes (27%) of the 1MiB factory partition. The static application is
249,488 bytes. The full generated font occupies 507,696 flash bytes, including
340,920 lookup bytes and 166,776 packed bitmap bytes; the board's fixed motion
controller occupies 21,568 bytes. Every encoded source glyph fits its native
cell. Native checks pass with ASan/UBSan, and all 42 original static PBM hashes
are unchanged.

Flashing verified all three image hashes on MAC `94:a9:90:de:d0:04`.
The entire application read back byte-identically at offset `0x10000`:
`1ae51070e4abb8973ec616381f58243c8928fcebdd2b2d5ce87ed0e6d99a9173`.
Boot reported ELF prefix `7413bf261`, matching the final ELF, passed the 8MiB
PSRAM test and initialized the 400x300 panel. Temporary serial access was
restored and the port released. The separate 349 daemon remained active with
its original PID and serial owner.

[Archived evidence](../../../docs/evidence/2026-10-05-fusion-font/README.md)
contains source/build/readback hashes, native frames, boot and frame logs,
complete-cycle summary and acceptance assertions. The previous application
remains available for local rollback. No commit or push was performed.

The board keeps looping the synthetic demo. The all-working screen starts
about 68 seconds into each 92-second cycle and lasts four seconds. Its physical
readability is the next user observation; software checks do not close that gate.
