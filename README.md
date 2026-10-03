# esp32-rlcd

Bring-up firmware for the Waveshare **ESP32-S3-RLCD-4.2**. The ESP-IDF app logs
boot and memory diagnostics over USB and displays a monochrome panel test.

## Setup from scratch

Start with [the fresh-machine setup guide](docs/setup.md) to install Linux
prerequisites, EIM and USB permissions. Then, from this checkout:

```sh
./scripts/setup.sh
./scripts/idf.sh --version
./scripts/idf.sh build
```

Setup installs **ESP-IDF v5.5.3** and its dependencies into `~/.espressif`,
or validates and reuses that release if it is already installed. A separate
`esp32-349` checkout or prior ESP-IDF installation is not required. Set
`EIM_ROOT` to an absolute directory for a different installation location.

The wrapper activates ESP-IDF and runs from the repository root. To use the
usual interactive commands in Bash or Zsh:

```sh
. scripts/env.sh
idf.py build
```

`sdkconfig.defaults` selects the ESP32-S3 target, 16 MiB flash, 8 MiB octal
PSRAM and native USB-Serial-JTAG console. ESP-IDF generates the ignored local
`sdkconfig` and `build/` directory. There are no registry-managed app dependencies
or repository submodules. The panel component retains its upstream source
reference and license.

## Select the board and flash

List connected boards:

```sh
ls -l /dev/serial/by-id/
```

Identify the RLCD by unplugging/replugging its USB cable and observing which
entry disappears/reappears. ESP32-S3 boards use the same USB product name;
use the full stable path rather than assuming a `ttyACM` number.

Flashing replaces the selected board's firmware. After confirming the RLCD
port, run:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -p "$RLCD_PORT" flash monitor
```

Exit the monitor with **Ctrl+]**. If the board cannot enter the bootloader,
follow [Waveshare's board instructions](https://docs.waveshare.com/ESP32-S3-RLCD-4.2).

Expected application logs include:

```text
rlcd: esp32-rlcd: panel bring-up
rlcd: Target: esp32s3; ESP-IDF: v5.5.3
rlcd: Flash: 16 MiB; PSRAM: 8 MiB
rlcd_panel: Initialized: SPI3 10 MHz, 400x300, 15000-byte framebuffer
rlcd: Panel test ready: RLCD READY, stripes, checkers and moving square.
rlcd: frame=... sent; uptime=...s internal_free=... psram_free=...
```

A frame and heartbeat appear every five seconds. Verify the flash/PSRAM sizes
and let it run for at least a minute without a reset or panic. The screen should
show upright **RLCD READY**, a border with a top-left marker, vertical stripes,
coarse and single-pixel checkerboards, and a moving square with a counter.
Check in good ambient light; this reflective display has no backlight.

Confirm the physical pattern and updates, then power-cycle and verify startup
again. Local tests and successful SPI transfers do not establish physical
display acceptance. Recorded checks are in [docs/bringup.md](docs/bringup.md).

## Native pixel-packing check

```sh
./scripts/check-frame.sh
```

Requires a native C compiler with AddressSanitizer and UndefinedBehaviorSanitizer.
Checks known corner mappings, distinct coverage of every panel pixel, colors,
clipping and pattern bounds. This verifies buffer packing, not the physical panel.

## Scope

For faster animation and drawing/transfer measurements, use the separate
[RLCD performance example](examples/rlcd-perf/README.md).

For a compact coding-agent roster using invented session data, see the
[dashboard UI study](examples/rlcd-dashboard/README.md) and
[layout notes](docs/ui-study.md). Native previews and the separate firmware
example share a renderer. The eight-row symbol layout and directional row
animations have been accepted on the panel; live integration remains pending.
The [ordering and motion proof](docs/ui-motion.md) extends that layout with
synthetic state transitions; its validation is recorded separately.

Shared coding-agent discovery and session-state observation now live in
[Agent Observer](https://github.com/byebyebryan/agent-observer). Its
[source study](https://github.com/byebyebryan/agent-observer/blob/main/docs/agent-session-study.md)
and [spike plan](https://github.com/byebyebryan/agent-observer/blob/main/docs/agent-session-spike-plan.md)
cover Codex and Claude Code, including foreground and daemon-backed runtimes.
The RLCD is an initial consumer target; live data-source proof and host-to-board
integration remain pending.

Board notes and upstream references are in [docs/board.md](docs/board.md).
Recovered shared-workspace setup notes are in
[docs/workspace-origin.md](docs/workspace-origin.md).
The panel uses a small synchronous SPI driver with a 15,000-byte DMA buffer;
LVGL, buttons, sensors, audio, storage, network services and host integration
are not implemented yet.

## Layout

```text
main/                   Boot diagnostics, panel test and heartbeat
components/display_rlcd/ Panel transport, framebuffer packing and test pattern
scripts/                Pinned ESP-IDF setup, activation and command wrapper
tests/                  Native pixel-packing checks
sdkconfig.defaults      Reproducible board configuration
docs/setup.md           Fresh-machine prerequisites, configuration and recovery
docs/board.md           Hardware references and bring-up scope
docs/bringup.md         Local hardware acceptance and evidence
```
