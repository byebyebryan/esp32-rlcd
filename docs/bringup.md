# RLCD bring-up: 2026-10-02

Host: Starship. Board: Waveshare ESP32-S3-RLCD-4.2, USB serial
`94:A9:90:F3:43:74`, currently `/dev/ttyACM0`. Commands used the full
`/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_94:A9:90:F3:43:74-if00`
path. The 349 daemon remained on its separate `28:84:85:92:C2:20` board.
Source changes were uncommitted during these checks.

## Results

| Check | Result and evidence boundary |
| --- | --- |
| ESP-IDF build | v5.5.3, ESP32-S3 target; panel app 245,456 bytes |
| Native packing test | Known corners, all 120,000 distinct pixels, colors, clipping and pattern bounds; AddressSanitizer and UndefinedBehaviorSanitizer enabled |
| Flash | Bootloader, partition table and app written; esptool verified all three hashes |
| Memory | 16 MiB flash, 8 MiB PSRAM; startup PSRAM memory test passed |
| USB-only baseline | 67.1 seconds, 14 heartbeats through uptime 65 seconds, constant free memory; USB reset recovery also passed |
| Panel runtime | 67.1 seconds, 14 frames through uptime 65 seconds; no SPI errors, resets or panics |
| Panel free memory | Internal: 353,643 bytes; PSRAM: 8,386,192 bytes, unchanged during capture |
| Panel reset recovery | Another 17 seconds after a USB reset; 4 successful frames through uptime 15 seconds |
| Physical panel test | User confirmed "working" on 2026-10-02 after the panel test was flashed; no photo or measurement was captured |
| Cold boot after power removal | Pending physical power cycle; the recorded reset checks used USB RTS |

The deployed panel app draws **RLCD READY**, a top-left orientation marker,
vertical stripes, coarse and single-pixel checkerboards, and a moving square
with a counter advancing every five seconds. Buttons and other peripherals
are not initialized.

## Evidence

- [USB baseline](evidence/2026-10-02-bringup/usb/serial-summary.json)
- [Panel runtime and reset summary](evidence/2026-10-02-bringup/panel/serial-summary.json)
- [Panel boot log](evidence/2026-10-02-bringup/panel/boot-stability.log)
- [Panel reset log](evidence/2026-10-02-bringup/panel/usb-reset-recovery.log)
- [Panel flash log](evidence/2026-10-02-bringup/panel/flash.log)
- [Image SHA256 values](evidence/2026-10-02-bringup/panel/images.json)

Archived logs normalize line endings and trailing whitespace for Git. The
summaries record both archived and original capture hashes; raw logs remain
under `build/evidence/20261002T172615Z`.

Deployed application binary SHA256:
`dbad4e318e2ee82b1731388061f7a942ef0e6f317aa185f0b90f601a10723aff`

The initial USB-only app and ELF are preserved locally under
`build/evidence/20261002T172615Z` as `m0-rlcd-bringup.bin` and
`m0-rlcd-bringup.elf`. These local build artifacts are ignored by Git.

## Factory recovery

Before either flash, the complete 16,777,216-byte factory flash image was
saved with mode 0600 outside the repository:

`/home/bryan/.local/state/esp32-rlcd/backups/20261002T172615Z-94a990f34374/flash-before.bin`

Factory backup SHA256:
`500cb87fb5e72a117ce91ebe0eb33e15c9abfc6ccb735dbdab46c884c3ce3300`

The adjacent `flash-before.json` records size, digest and a restore command.
The backup contains the prior firmware and settings and is not tracked in Git.
