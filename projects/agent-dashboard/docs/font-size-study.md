# Row font-size comparison

Date: 2026-10-05. Historical comparison, implemented and flashed. Native checks, both builds,
application readback and a complete board trace pass; physical readability
remains pending.

The subsequent [Fusion font study](fusion-font-study.md) replaces these
hand-authored motion glyphs with Fusion Pixel 8px at native and doubled scale,
and changes the row geometry. The results below record the earlier 12/8 build.

The first urgency-band pass kept the existing 26-pixel full rows and used
18-pixel working rows. Its legacy 5 x 7 bitmap was doubled to 14-pixel text;
native 7-pixel text was also available, but 12 and 8 were not integer scales.
This choice preserved the previous text size while testing row-height changes.

The follow-up requested smaller text. The motion view now uses hand-authored
7 x 12 bitmaps for full rows and 5 x 8 bitmaps for working rows. Uppercase and
digits actually occupy twelve/eight pixel rows; glyph widths and spacing are
seven plus two and five plus one respectively. These are native one-bit glyphs,
with no runtime resampling or font-library dependency. The earlier static
renderer retains its original bitmap font.

Names, provider labels and ages use the same size within each row. The header
summary and footer use twelve pixels; column labels use eight. The existing
title and state symbols retain their sizes and polarity. Text is vertically
centered, and ages are right-aligned using the selected font's advance.

Row heights remain 26/26/18 for blocked/waiting/working, keeping admission,
ordering and motion geometry constant while comparing fonts. A healthy working
row switches to the small font immediately with its compact geometry. Feed
loss preserves the geometry and its font while suppressing cached work claims.

Native coverage checks actual glyph extents, character separation, inverse
polarity, right-aligned ages, clipping, the existing motion/failure contract,
and all forty-two static PBM hashes. Both firmware modes are built separately;
the selected RLCD must pass application readback and a complete 110-second
trace. The prior 14-pixel firmware is retained in ignored rollback output.

Physical comparison remains open: are twelve-pixel blocked/waiting labels
readable at desk distance, and are eight-pixel working labels still useful
while making their lower urgency clear? Row spacing can be tuned after this
font comparison. No commit or push is requested.

## Recorded result

The [evidence archive](../../../docs/evidence/2026-10-05-font-sizes/README.md)
contains exact native PNGs, source/image hashes and the complete serial trace.
The ASan/UBSan native suite passes, including the twelve/eight-pixel glyph
extent, spacing, inverse-polarity and age-alignment assertions, and 4,488
packed-rectangle comparisons. All forty-two static PBM hashes are unchanged.

Default motion and isolated static builds pass under ESP-IDF 5.5.3. The motion
application is 258,960 bytes. Flashing selected only RLCD `94:a9:90:de:d0:04`;
all three write hashes verified and full application readback at `0x10000`
matched byte for byte. Boot ELF hash matches the recorded image; startup
reports `normal_text_px=12 working_text_px=8` and the unchanged 26/18 row heights.

The 110.151-second trace contains all twenty-three phases, a completed cycle,
one start and 338 frames including 228 moving frames. There are no logged
errors or 40 ms budget misses. Frame writes took 13.774–20.428 ms, free internal
memory stayed at 342,835 bytes, and minimum stack watermark was 1,848 bytes.
The separate 349 daemon retained its service/serial-owner PIDs and remained
active. Temporary RLCD access was removed after capture.
