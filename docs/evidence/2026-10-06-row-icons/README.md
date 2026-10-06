# Row icon polarity

2026-10-06. Status marks now follow the motion row's text colour: black on
white working/waiting/uncertain rows, white on black blocked rows. The mark
is drawn directly on the opaque row background, removing the black tile.
The user-approved 12/24px Fusion typography and row geometry are unchanged.

The primary completed this small fix directly, including review, focused
checks, build and hardware acceptance. Native ASan/UBSan checks sample mark
ink and blank corners for working, waiting, stopped, unknown, blocked, error,
per-row stale and whole-feed stale/offline states. All 42 historical static
frame hashes match. Native images are renderer outputs, not board photos.

Flashed only RLCD `94:a9:90:de:d0:04`; three image hashes verified and full
application readback matched the build. The prior application/ELF/bootloader
and partition are retained in local build evidence. Fonts and icon shapes
remain as before. Changes are uncommitted; no push.

The 110-second capture covered all 23 phases and a full 92-second cycle:
338 frames, 228 moving frames, zero errors or frame-budget misses. The worst
frame took 25.238ms against the 40ms budget; internal heap stayed at 331,907
bytes. Boot ELF prefix `1ee2582b7` matches the 1,233,392-byte application.
Native pixels verify icon polarity; physical icon appearance awaits user
observation. Serial access was released and its original ACL restored
exactly; the separate 349 daemon retained its PID and serial owner.

See `acceptance.json`, `summary.json`, `serial.log`, and `recovery.json` for
measured results. `checksums.json` hashes the archive files.
