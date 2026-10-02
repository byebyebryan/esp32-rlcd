# Waveshare panel reference

Initialization bytes, reset timing, pins and landscape pixel mapping are
adapted from Waveshare's ESP32-S3-RLCD-4.2 example at commit
`eb1f63427d735a22b9c30e22fa63ebddae1834d3`:

- [display_bsp.cpp](https://github.com/waveshareteam/ESP32-S3-RLCD-4.2/blob/eb1f63427d735a22b9c30e22fa63ebddae1834d3/02_Example/ESP-IDF/09_LVGL_V9_Test/components/port_bsp/display_bsp.cpp)
- [user_config.h](https://github.com/waveshareteam/ESP32-S3-RLCD-4.2/blob/eb1f63427d735a22b9c30e22fa63ebddae1834d3/02_Example/ESP-IDF/09_LVGL_V9_Test/main/user_config.h)

Copyright 2026 Waveshare. The upstream Apache-2.0 license is retained in
[LICENSE.waveshare](LICENSE.waveshare).

Changes: plain C implementation, synchronous SPI transactions, a 15,000-byte
internal DMA buffer instead of asynchronous LVGL transfers and PSRAM lookup
tables, and a standalone diagnostic pattern. The conservative 10 MHz SPI
clock and controller register values match the LVGL example.

The performance example also provides queued SPI DMA with a blocking completion
wait for the full framebuffer, allowing the owner task to sleep during transfer.
The original polling presentation remains the root bring-up app's default.
