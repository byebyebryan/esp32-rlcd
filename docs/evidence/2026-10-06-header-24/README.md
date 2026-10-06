# Larger summary with divider

2026-10-06. The header retains `x BLOCKED y WAIT z WORK`, uses doubled Fusion
Pixel 12px text and restores a one-pixel divider at y=23. The AGENTS title
and column labels remain omitted. Optional unknown counts use native 12px
text on the same line to fit the complete 32-session roster.

Rows remain packed without added padding, using native 12px working text
and doubled 24px blocked/waiting text. The body spans y=24..287, fitting
22 working rows or 11 full rows. The preceding simulated-source footer and
packed feed-loss behavior remain. Archived images are actual 400x300 native
renderer outputs, not photographs of the panel.

Native ASan/UBSan and warnings-as-errors checks pass, including 4,488 packed
rectangle cases, chrome polarity, divider, identity and feed-loss checks.
All 42 static frame hashes match the earlier baseline. An independent replay
checks 2,117 settled frames over all 23 phases, with no gaps or priority inversions.

Only RLCD `94:a9:90:de:d0:04` was flashed. All three write hashes verified,
and all 1,233,904 application bytes read back identically. Boot ELF prefix
`bb90e6288` matches the saved build; PSRAM and 400x300 panel initialization
passed. Previous application and full private flash recovery data remain local.

The 110.123-second capture covers all 23 phases and a complete 92-second
cycle: 338 frames, 228 moving frames, one application start, zero errors and
zero 40ms frame-budget misses. Worst frame is 25.694ms. Internal heap stays
at 331,899 bytes; minimum stack watermark is 1,840 bytes. Moving intervals
are 40.000..40.003ms. Device admission counts match the native capacities.

Original serial ACL is restored exactly and the RLCD port is released.
The separate 349 daemon retains its service and serial-owner PIDs. The board
keeps looping for physical inspection; layout acceptance remains a user
observation. The source is still synthetic. Changes are uncommitted; no push.

`checks.json` and `acceptance.json` record the technical gate. Original serial
logs and `summary.json` preserve runtime evidence. Source/build manifests,
readback metadata and `recovery.json` record identity and access recovery.
`change.patch` records this header follow-up against the preceding UI trial.
`checksums.json` hashes all archived files except itself.
