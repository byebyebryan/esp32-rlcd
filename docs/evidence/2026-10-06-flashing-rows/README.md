# Slow blocked-row flashing trial

2026-10-06. RLCD `94:a9:90:de:d0:04` only; synthetic UI capture taken before publication.
Blocked rows alternate full-row polarity at 1Hz (500ms each half); waiting
stays white on black, working stays black on white. All rows/text remain
24px with eleven complete visible rows. Icons use the preceding accepted
shapes and placement, following row polarity. The waiting bar and finite
icon cue are removed.

- Native ASan/UBSan, warnings-as-errors, UTF-8 and 4,488 rectangle checks pass.
- All 42 static frame hashes remain unchanged.
- Three flash hashes pass; full 1,234,416-byte application readback
  matches; boot ELF prefix `89e50307c` matches the build.
- A 110.121s trace covers all 23 phases and one full 92-second
  cycle: 390 frames, 192 moving, no errors or budget misses.
- Stationary blocked rows change polarity twice per second within one 40ms
  tick; waiting and working are steady. Resolution and unavailable evidence
  stop flashing. The source-loss fixtures begin healthy and lose their
  source during motion, so their stop assertions use recorded health timing.
- Worst frame 20.703ms; heap constant 331,899 bytes; minimum
  stack watermark 1,808 bytes.
- Original serial ACL restored exactly and port released; separate 349
  service and serial-owner PIDs unchanged. Recovery data remains private.

`acceptance.json` and `checks.json` record technical acceptance; source/build
identity, readback, serial trace and native phase images are included.
`blocked-flash-black/white` proves full-row polarity changes with unchanged
waiting and working rows. `compact-capacity` is a historical fixture name
that now exercises eleven full-height working rows.

The board keeps looping. After this capture, the user accepted the on-device
flashing layout for one to three short-lived blocked requests and requested
review, commit and push. `review.json` records that decision. Original capture
status fields remain unchanged. No live data source is integrated.

[Design contract](../../../projects/agent-dashboard/docs/flashing-rows-study.md)
records the layout and shared clock.
