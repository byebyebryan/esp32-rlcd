# Larger summary header

2026-10-06. The summary keeps the existing `x BLOCKED y WAIT z WORK` format
and uses the same doubled Fusion Pixel 12px font as blocked and waiting rows.
The generic AGENTS title and column labels remain omitted.

The header occupies y=0..23, with a one-pixel divider at y=23 and horizontal
insets of 8px. These uppercase glyphs leave that final scanline clear.
An optional unknown count uses native 12px text, vertically centered on the
same line, so all counts fit even at the 32-session model limit.

The body spans y=24..287. Its 264px height fits 22 working rows or 11 full
rows, with no row or group padding. Working text remains native 12px;
blocked and waiting text remains doubled 24px. The 12px footer and packed
feed-loss behavior from the [preceding UI polish](ui-polish.md) remain.

Native ASan/UBSan and warnings-as-errors checks pass. All 42 earlier static
frames remain byte-identical. A replay of 2,117 settled frames across the
23 phases finds no added gaps or priority inversions. Reviewed native frames
show the larger summary, divider, unknown suffix and full row capacities.

Only RLCD `94:a9:90:de:d0:04` was flashed. All three write hashes verified;
the full 1,233,904-byte application read back identically. Boot ELF prefix
`bb90e6288`, PSRAM test and panel initialization match the build. A 110.123s
capture covers every phase and one complete cycle: 338 frames, 228 moving,
zero logged errors and no 40ms frame-budget misses. Worst frame is 25.694ms;
internal heap stays at 331,899 bytes and minimum stack watermark is 1,840 bytes.

Original serial access is restored exactly and the separate 349 daemon
retains its service and serial-owner PIDs. The board remains looping for
physical inspection. The [evidence archive](../../../docs/evidence/2026-10-06-header-24/README.md)
records source/build identity, rendered frames, native checks, application
readback, the complete serial trace and access recovery. Physical layout
acceptance remains a user observation. Changes remain uncommitted; no push.
