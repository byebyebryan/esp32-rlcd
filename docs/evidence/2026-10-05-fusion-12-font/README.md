# Fusion Pixel 12px trial evidence

2026-10-05. User-selected native 12px working / doubled 24px blocked and waiting
rows after finding the previous8px text too small. The252px list y=36..287 fits
21 compact or 10 full rows; it adds no row padding or group gaps. Basic Latin
capitals are 8px and 16px high.

This is synthetic data on RLCD MAC `94:a9:90:de:d0:04`. Native frames are
renderer outputs, not physical photographs. Readability remains for the user.

Luna owned the pinned full 12px BDF, generated data/header/generator, provenance
and missing notices. Primary owned renderer/geometry/clipping, checks, the 2MiB
factory partition, both builds, flash/readback and board acceptance. The full
12px source includes 36,981 entries; standalone and independent all-bit checks
passed. The two vertical kana marks spanning two lines retain their source
bitmaps but are cropped to the current row. The8px font remains available as a
historical asset and is not linked into this firmware.

`partition-check.json` verifies NVS and PHY remain identical while the factory
partition at 0x10000 grows from 1MiB to 2MiB. Prior application/ELF/partition and
bootloader files remain saved in local build evidence for rollback.

`source.json` and `files.json` identify the dirty build. `readback.json` records
full application equality. `serial.raw`, `serial.log`, `summary.json` and
`acceptance.json` record boot and full-cycle validation. Native checks cover
UTF-8, glyph goldens, width truncation, tall-glyph clipping, motion, source loss,
inactivity and readmission. All 42 earlier static frame hashes are unchanged.

No commit or push. Earlier archives are preserved.
See [the study](../../../projects/agent-dashboard/docs/fusion-12-font-study.md).

Final capture passed: 110 seconds, 338 frames including 228 moving, all 23 phases,
one application start, no errors and no 40ms budget misses. Worst frame 25.325ms;
free internal heap stayed 331,907 bytes. Final application readback matched the
1,233,408-byte build; boot ELF prefix `7ec7f256c` matched. Original serial ACL
was restored and the separate 349 daemon retained its process and serial owner.

Runtime goal accounting: 303,779 tokens, 13 minutes 1 second.
