# Board bring-up application

This app logs ESP32-S3 boot and memory diagnostics over USB, initializes the
shared RLCD panel component, and displays the monochrome panel test.

Expect `rlcd: Target: esp32s3; ESP-IDF: v5.5.3`, 16 MiB flash, 8 MiB PSRAM,
and a frame heartbeat every five seconds. The reflective panel should show
upright **RLCD READY**, a border and top-left marker, vertical stripes, coarse
and single-pixel checkerboards, and a moving square with a counter. Check in
good ambient light; the display has no backlight. Let it run for at least a
minute, then power-cycle and confirm startup again. SPI transfer success alone
does not establish physical display acceptance.

From the repository root, install the pinned toolchain using
[the setup guide](../../docs/setup.md), then build and flash this project
explicitly:

```sh
./scripts/idf.sh -C projects/bringup build
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -C projects/bringup -p "$RLCD_PORT" flash monitor
```

The frame-packing check is shared by all applications and runs on the host:

```sh
./scripts/check-frame.sh
```

The app uses the root [shared board defaults](../../sdkconfig.defaults) and
[display component](../../components/display_rlcd/). See [board notes](../../docs/board.md)
for wiring and upstream references, and [recorded bring-up results](../../docs/bringup.md)
for the historical physical checks.
