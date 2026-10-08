# Accepted large icon counts without a footer

2026-10-07. Synthetic dashboard trial on RLCD `94:a9:90:f3:43:74`.
The header uses 24px text beside enlarged state icons, with optional unknown
and hidden-row counts. The footer is removed; the 276px body still admits
eleven complete 24px rows. Accepted row styles and 1Hz flashing remain.

- Native ASan/UBSan, warnings-as-errors, UTF-8 and 4,488 rectangle checks pass.
- All 42 static frame hashes are unchanged.
- ESP-IDF 5.5.3 build and three flash hashes pass; full 1,234,256-byte
  application readback matches. Boot ELF prefix `294f84cc2` matches the build.
- The 110.092s trace covers all 23 phases and a complete 92-second cycle:
  390 frames, 192 moving, no logged errors or 40ms frame-budget misses.
- Worst frame 19.879ms; internal heap stays at 331,899 bytes; minimum
  stack watermark 1,744 bytes.
- Serial ACL and the separate 349 service/serial owner are unchanged;
  the RLCD port is released. Detailed recovery and firmware backups stay local.

Exact native frames cover normal order, overflow, all-working capacity,
all-blocked stress, uncertainty, duplicate long names, stale/offline source,
empty roster and both blocked-row polarities. These are renderer outputs,
not photographs. `compact-capacity` is an earlier fixture name.

The original capture predates user acceptance and publication. Its pending
and uncommitted status fields remain unchanged. `review.json` records the
later user feedback and commit/push request. The captured app version is
`2b70553-dirty`; source hashes, ELF identity and readback establish the build.
Documentation was updated afterward; compiled inputs still match the capture.
`build.log` contains selected build lines; the complete raw build stays local.

[Current design and review checkpoint](../../../projects/agent-dashboard/docs/icon-counts-study.md)
records the accepted layout and the items to revisit with live data.
