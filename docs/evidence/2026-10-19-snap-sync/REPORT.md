# Snap repository, service and RLCD synchronization

2026-10-19. The Snap checkout, managed bridge and physical RLCD are synchronized
to the accepted active-feed application. The service is active and enabled at
boot. Starship's upstream native observation is unavailable, so the normal live
display remains partial. This is not complete native-feed acceptance.

## Installed state

- Runtime source: `55a2b54eb15261c61d99df3f87c444baf42ed6a7`, published on `main`.
  Snap fast-forwarded from `358d265`; existing generated configuration was saved.
- Managed source: dotfiles `ac011724bcf87510b72366d72afeddb7ce476c9a`.
  Only RLCD launcher, selection, unit and startup targets were applied on Snap.
  Starship's running selection was not changed.
- Immutable bundle: `757d037d2ca3abb5`, manifest SHA-256
  `757d037d2ca3abb5249905b062cb2ddb10064cf31dd88fa08375c89ac04eca70`.
  Dependencies remain Observer `0.7.0a7` / Mesh `0.1.0a23` and the explicit
  `agent-observer.mesh-active.v1` profile. Working-set and delta remain gated.
- Snap RLCD: MAC `94:a9:90:de:d0:04`, stable USB path ending
  `94:A9:90:DE:D0:04-if00`. Passive serial output first confirmed the old RLCD
  motion demo. The bridge and live-capture allowlist now include this exact
  board alongside the existing Starship RLCD.
- `rlcd-agent-dashboard.service` is enabled, running with zero automatic
  restarts at capture. Snap user lingering is enabled. A narrowly matched
  `/etc/udev/rules.d/70-esp32-rlcd-snap.rules` grants group `bryan` mode `0660`
  only to this board. Port ownership matches the service PID.

## Firmware and checks

ESP-IDF v5.5.3 built a fresh configuration with live USB enabled and static study
disabled. The old generated configuration and complete 16 MiB flash image were
preserved before flashing. Backup SHA-256 is
`86ede5a19ac73c727be611a805a2517b04028611b96a56c85afe10b9f62c6e0c`.
Backup and private logs are on Snap at
`~/.local/state/esp32-rlcd/backups/20261019T164832Z-snap-sync/`.

The flashed bootloader, partition table and 1,242,640-byte application read back
byte-for-byte equal to their build artifacts. Application SHA-256 is
`243ca45f8a18f43d72e9ecb4357ec34f6340c759a0db305b2ab807e65261d4d2`.
The generated build is preserved under its explicit local Git exclusion.

The existing native/stdlib suites pass 47 tests; the selected installed
environment additionally passes all seven prepared and nine active consumer
tests without skips. Per-host template, unit and immutable bundle checks pass.
The bounded fictional wire-2 device probe passes failure/retry acknowledgements,
attention counts and silence expiry: eight exact three-row ACKs, followed by
expired work claims. Only the verified Snap port was substituted in that probe.
The board was reset afterward to clear fictional presentation context before
starting the real service.

## Live source limitation

The initial installed live capture receives 26 physical acknowledgements, but
fails its complete populated-feed requirement with `insufficient_live_admission`.
SSH and Mesh delivery work; Starship's cached Observer snapshot reports
`native_identity_mapping_conflict`, and its original component receipts are
unavailable. A local Starship read independently shows the same failure.
Snap's own source is current with zero selected rows at the captured sample.

The managed service reports physical ACK recovery and device health with
`partial=1`, zero rows and no current work claims. No source validation was
weakened, and no provider conversation, native daemon or collector was restarted
to bypass the identity conflict. Full native-feed acceptance remains open.

The separate 349 board stays on its own `28:84:85:92:C4:3C` port. Its journal
shows separate maintenance/restart during this window; this task issued no
349 stop, flash or configuration commands. No unchanged-incarnation claim is
made for that concurrent work.

[Structured results](summary.json) retain the exact source, artifact, readback,
service and scoped check identities. Visual panel/readability and a physical
host reboot/unplug cycle were not observed in this update.
