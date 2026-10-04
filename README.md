# esp32-rlcd hardware workspace

This repository holds three independent ESP-IDF applications for the Waveshare
ESP32-S3-RLCD-4.2. Select an application explicitly for every build or flash;
there is no default application at the repository root.

| Application | Purpose | Instructions |
| --- | --- | --- |
| Bring-up | Boot diagnostics, panel test and heartbeat | [projects/bringup](projects/bringup/README.md) |
| Render bench | Drawing and SPI workload measurements | [projects/render-bench](projects/render-bench/README.md) |
| Agent dashboard | Synthetic roster and motion study | [projects/agent-dashboard](projects/agent-dashboard/README.md) |

## Set up and build

Follow the [fresh-machine setup guide](docs/setup.md), then build the bring-up
application from the repository root:

```sh
./scripts/setup.sh
./scripts/idf.sh --version
./scripts/idf.sh -C projects/bringup build
./scripts/check-frame.sh
```

`--version` does not need an application selection. For interactive ESP-IDF
commands, source `scripts/env.sh` and pass the same project path to `idf.py`:

```sh
. scripts/env.sh
idf.py -C projects/bringup menuconfig
```

Each application owns its generated `sdkconfig` and `build/` directory. The
root [`sdkconfig.defaults`](sdkconfig.defaults) supplies shared board defaults;
the benchmark adds its own optimization and timing overrides. Existing ignored
root and former `examples/` build/configuration artifacts remain local history;
the project commands above do not select them.

## Shared hardware resources

The applications use the shared [display component](components/display_rlcd/)
for panel transport and frame packing. The root `tests/test_frame.c` and
`scripts/check-frame.sh` check native pixel packing independently of an app.
Board wiring and upstream references are in [docs/board.md](docs/board.md);
recorded physical bring-up results are in [docs/bringup.md](docs/bringup.md).
The component retains its [upstream provenance](components/display_rlcd/UPSTREAM.md)
and license. The shared-workspace history is in
[docs/workspace-origin.md](docs/workspace-origin.md).

The immutable [`docs/evidence/`](docs/evidence/) archive contains prior build,
capture and board records. Source and image paths inside those records describe
the workspace layout at capture time.

## Flash a selected application

Identify the board by unplugging and reconnecting its USB cable, then use its
stable `/dev/serial/by-id/` path. Flashing replaces the selected board's
firmware:

```sh
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -C projects/bringup -p "$RLCD_PORT" flash monitor
```

Exit the monitor with **Ctrl+]**. If the board cannot enter its bootloader,
follow [Waveshare's board instructions](https://docs.waveshare.com/ESP32-S3-RLCD-4.2).

Replace `projects/bringup` with the selected application directory to build or
flash another app. Local native checks and successful SPI writes do not replace
physical panel observation.
