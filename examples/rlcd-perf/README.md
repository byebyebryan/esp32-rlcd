# RLCD drawing and transfer benchmark

On-device drawing, SPI and CPU tests for the Waveshare ESP32-S3-RLCD-4.2.
This separate app shares the panel component with the root bring-up app.
The working panel initialization, 10 MHz SPI clock and full-frame packing
are retained. No LVGL or other managed component is required.

## Build, flash and capture

Complete [the repository setup](../../docs/setup.md), then run from its root:

```sh
./scripts/idf.sh -C examples/rlcd-perf build
RLCD_PORT='/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_YOUR_BOARD-if00'
./scripts/idf.sh -C examples/rlcd-perf -p "$RLCD_PORT" flash
. scripts/env.sh
python scripts/capture-perf.py --port "$RLCD_PORT" --seconds 120 --reset \
    --output build/evidence/perf-local
```

Use a new output directory for every capture. The capture uses IDF's pyserial
and esptool dependencies, writes a normalized log and JSON summary, and prints
each phase result. `--reset` restarts the selected board using USB RTS; it is
not a cold power-cycle check. Close other monitors using that port first.

To return to the original slow diagnostic screen:

```sh
./scripts/idf.sh -p "$RLCD_PORT" flash
```

The example inherits the root board defaults and additionally enables compiler
performance optimization (`-O3` in IDF v5.5.3), 1 ms FreeRTOS ticks and task
runtime statistics using `esp_timer`. The root bring-up configuration is separate.

## Workloads and sequence

| Phase | Work | Duration |
| --- | --- | --- |
| `draw_full` | Rebuild the diagnostic pattern, moving square and counter; no SPI | 256 frames |
| `draw_cached` | Copy a 15 KB static pattern, draw a ball and vertical bar; no SPI | 256 frames |
| `full_poll` | Diagnostic redraw plus polling full-frame SPI | 6 seconds |
| `cached_poll` | Cached ball/bar animation plus polling SPI | 6 seconds |
| `cached_queue` | Same ball/bar drawing with queued SPI DMA and a completion wait | 6 seconds |
| `paced_50` | Queued ball/bar animation every 20 ms | 10 seconds |
| `paced_62_5` | Queued ball/bar animation every 16 ms | 10 seconds |
| `soak_50` | Continue the queued animation every 20 ms | Repeating 10-second windows |

The full diagnostic redraw and cached ball animation are different workloads;
their timing illustrates the cost of rebuilding static content. The two cached
transport phases use identical drawing and isolate polling versus queued SPI.
Unpaced phases insert a 1 ms delay every 16 frames in both modes to let the idle
task run during polling. This gap is included in the reported write rate.
Drawing and transfer measurements exclude pacing delays.

Queued presentation blocks the caller until DMA has completed, permitting other
tasks to run during the transfer. It does not overlap drawing with transfer and
does not introduce a second DMA framebuffer. The single owner may reuse the
buffer after either presentation function returns.

## Reading results

`RESULT` reports completed writes, elapsed time, per-core busy percentages,
missed pacing deadlines and free memory. `TIMING` reports drawing, transfer and
combined work in microseconds. The p95 value is an upper bound from 500 us
histogram buckets; the maximum is recorded directly.

CPU is estimated from the IDF `IDLE0`/`IDLE1` runtime counters over the phase,
with unsigned subtraction for counter wrap. Integer percentages are approximate;
small activity can round up to 1%. This follows the corrected measurement used
in the 349 demo and avoids relying on an unwired LVGL idle hook.

Every phase checks heap integrity. Watch for changing free memory, errors,
panics, reset loops and missed deadlines. Inspect the display in ambient light:
the ball and thin bar should move over intact stripes and checkerboards without
trails or incomplete frames. The title and original `0000` counter are static
in the cached scene.

At 10 MHz a 15,000-byte payload alone needs 12 ms, giving an ideal wire ceiling
of 83.3 writes/s before commands and software overhead. A completed SPI write
does not establish panel scan rate or visible frame rate. TE is not sampled;
smoothness and tearing require physical observation.

Recorded local results: [drawing performance](../../docs/performance.md).
