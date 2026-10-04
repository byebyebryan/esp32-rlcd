# RLCD drawing performance: 2026-10-02

Tested on Starship with the Waveshare ESP32-S3-RLCD-4.2, USB serial
`94:A9:90:F3:43:74`. The 349 board and its daemon remained on their separate
port. The baseline was reviewed and published as `6bd7054` before benchmark
work began; these measurements were captured from subsequent benchmark changes
before they were committed.

## Configuration and results

The [separate benchmark app](../README.md) uses ESP-IDF
v5.5.3, 240 MHz CPU, performance optimization (`-O3`), 1 ms scheduler ticks,
the accepted panel initialization and 10 MHz SPI3. Each full-frame write
sends the panel's packed 15,000-byte monochrome buffer from internal DMA RAM.

First 120-second capture, mean times from real hardware:

| Workload | Draw | SPI/wait | Completed writes/s | Core 0 busy |
| --- | --- | --- | --- | --- |
| Full diagnostic redraw, polling | 3.757 ms | 12.116 ms | 62.79 | ~100% |
| Cached ball/bar animation, polling | 0.205 ms | 12.115 ms | 80.81 | ~100% |
| Same cached animation, queued DMA | 0.204 ms | 12.133 ms | 80.81 | ~3% |
| Queued animation, 20 ms pacing | 0.204 ms | 12.132 ms | 50.00 | ~2% |
| Queued animation, 16 ms pacing | 0.204 ms | 12.132 ms | 62.50 | ~3% |

The two cached transport phases isolate the SPI waiting method. Queued DMA
maintains throughput while freeing core 0 during the transfer. It waits for
completion before returning, so the caller retains one-owner framebuffer use.
Core 1 stayed approximately 0-1% busy throughout.

Drawing-only tests measured 3.757 ms per full diagnostic redraw and 0.205 ms
per cached ball/bar frame, each over 256 frames. These are different workloads:
the cached scene copies the static diagnostic pattern and redraws only its
moving ball/bar; the full scene redraws the pattern, square and counter.
They illustrate static drawing cost rather than an identical-scene speedup.
The original bring-up app uses its own debug build configuration.

The first capture contains 6,482 completed writes in fully recorded phases,
including eight 10-second soak windows at 50 writes/s. Both paced tests and
every soak window reported zero missed deadlines. Internal free memory stayed
at 342,899 bytes and PSRAM free memory at 8,386,192 bytes. All phase heap checks
passed, with one application start and no logged errors, panics or reset loops.

A second 55-second capture after a USB RTS reset repeated the complete suite
and another soak window: 2,975 completed writes, the same measured throughput
and CPU percentages, no errors or missed deadlines, and unchanged free memory.

## Physical observation and limits

The user confirmed **"Smooth, no visible artifacts"** for the running ball/bar
animation on 2026-10-02. The final continuous mode is 50 writes/s. This is
physical acceptance of the observed animation; no camera measurement or
separate visual acceptance of every transient stress phase was captured.

The measured transfer time is close to the 12 ms payload floor at 10 MHz.
Reported throughput counts completed SPI writes. Panel scan rate was not
measured, and TE is not sampled. The tests retain the working clock and do not
establish a maximum safe panel clock, partial-update support or performance of
future LVGL/UI workloads. CPU percentages are integer estimates from per-core
idle runtime counters, not a cycle-accurate CPU profile.

USB RTS reset checks establish software restart recovery. Cold boot after
physical power removal remains pending from [bring-up](../../../docs/bringup.md).
The accepted slow bring-up binaries and factory flash backup remain preserved
locally; the benchmark stays running for observation.

## Evidence and reproduction

The linked records are retained unchanged in the root evidence archive. Source
and image paths recorded inside those files describe the workspace layout at
capture time.

- [Benchmark instructions and workload definitions](../README.md)
- [First capture summary](../../../docs/evidence/2026-10-02-perf/run-1-summary.json)
- [First boot, timing and soak log](../../../docs/evidence/2026-10-02-perf/run-1-serial.log)
- [Reset-repeat summary](../../../docs/evidence/2026-10-02-perf/reset-repeat-summary.json)
- [Reset-repeat log](../../../docs/evidence/2026-10-02-perf/reset-repeat-serial.log)
- [Flash log](../../../docs/evidence/2026-10-02-perf/flash.log)
- [Exact source, configuration and image hashes](../../../docs/evidence/2026-10-02-perf/images.json)

The summary records SHA256 digests of normalized and raw captures. Archived
logs normalize line endings and trailing whitespace. Image hashes identify the
flashed benchmark, including its `6bd7054-dirty` app version. Root bring-up and
benchmark builds both passed after the queued transport was added; the existing
native packing check passed during the baseline review.
