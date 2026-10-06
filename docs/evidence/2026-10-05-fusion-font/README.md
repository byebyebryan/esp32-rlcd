# Fusion Pixel 16/8 device evidence

2026-10-05. Final Fusion Pixel 8px monospaced zh_hans release 2026.09.25,
drawn at scale two for full rows and one for working rows. Text cells and rows
are 16/8 pixels; Latin capitals are 12/6 pixels. The list occupies y=32..287,
with no additional row padding or group gaps.

These are synthetic sessions on RLCD MAC `94:a9:90:de:d0:04`.
Native images show renderer output; they are not photographs of the board.
Physical readability and perceived animation remain unaccepted.

Native ASan/UBSan checks cover UTF-8, fallback, source glyph pixels, clipping,
rectangle packing, identity, urgency prefix admission, shared motion progress,
directional compositing, retargeting, source loss, inactivity and readmission.
All 42 earlier static PBM hashes match. `font-metrics.json` checks every one of
the 28,410 encoded source glyphs fits its original native cell.

Both motion and static firmware modes build. Only motion is flashed.
`files.json` records the final build sizes and hashes; `source.json` records
the dirty checkout and exact implementation/config hashes. `readback.json`
records the byte-identical 766,528-byte application at flash offset 0x10000.
`flash.log` verifies the selected MAC and all three written image hashes.
Boot and complete-cycle acceptance is recorded in `acceptance.json` and
`summary.json`, with original serial bytes and normalized boot/frame logs.

The previous application and private full-flash rollback are retained under
local state/build evidence, outside this archive. Earlier study evidence is
unchanged. No commit or push was performed.

The requested worker-goal-loop attempted Luna for the bounded font/renderer
slice. The attempt ended with a model-capacity error. The primary retained and
reviewed useful partial font assets/geometry, completed renderer/fixture/test
integration, and owned both builds, hardware flashing, readback and acceptance.

See [the study](../../../projects/agent-dashboard/docs/fusion-font-study.md).

The final capture passed all 23 phases over 110.05 seconds: 338 frames, 228
moving, one application start, no errors, no deadline misses, 25.847ms worst
frame against a 40ms budget, and constant free internal heap of 331,907 bytes.
The boot ELF prefix `7413bf261` matches the final build. Temporary serial ACL
was restored exactly, the capture port was released, and the separate 349
daemon retained its original main PID and serial owner.

Runtime goal accounting: 439,525 tokens and 26 minutes 15 seconds.
See `goal-result.json` for the recorded completion result.
