# Waveshare ESP32-S3-RLCD-4.2

Board model confirmed for this project on 2026-10-02.

## Hardware baseline

| Resource | Vendor specification |
| --- | --- |
| Module | ESP32-S3-WROOM-1-N16R8 |
| CPU | Dual-core Xtensa LX7, up to 240 MHz |
| Flash | 16 MiB |
| PSRAM | 8 MiB |
| Display | 4.2-inch reflective monochrome LCD, 300 x 400 pixels |
| USB | Native USB programming and serial console via USB-C |
| Inputs | BOOT and KEY buttons; separate PWR button |
| RTC | PCF85063 |
| Temperature/humidity | SHTC3 |
| Audio | ES8311 codec, ES7210 ADC, dual microphones, speaker connector |
| Storage | microSD slot |

The display uses reflected ambient light and has no backlight. Display
orientation and controller initialization must be verified against the vendor
example and physical board during panel bring-up.

## Panel pins and transport

| Signal | GPIO |
| --- | --- |
| MOSI | 12 |
| SCLK | 11 |
| DC | 5 |
| CS | 40 |
| RESET | 41 |
| TE | 6, not read by this firmware |

Pins and register initialization follow the vendor's LVGL V9 example at
`eb1f63427d735a22b9c30e22fa63ebddae1834d3`. The test uses SPI3, mode 0,
10 MHz, landscape coordinates of 400 x 300, and one bit per pixel packed into
2-column by 4-row blocks. See
[component provenance](../components/display_rlcd/UPSTREAM.md).

## Current firmware scope

The app uses flash, PSRAM, the native USB console and the panel pins above.
SPI writes are synchronous, so the framebuffer is updated only after the
previous transfer completes. Buttons and other peripherals are not configured.

The local RLCD USB serial is `94:A9:90:F3:43:74`. It was identified from the
factory app's logs, memory specifications and peripheral startup. The other
connected board, `28:84:85:92:C2:20`, is the active ESP32-349 device.

For validation scope and remaining physical checks, see [bringup.md](bringup.md).

## Primary references

- [Product and hardware overview](https://docs.waveshare.com/ESP32-S3-RLCD-4.2)
- [ESP-IDF instructions and examples](https://docs.waveshare.com/ESP32-S3-RLCD-4.2/ESP-IDF)
- [Schematics and datasheets](https://docs.waveshare.com/ESP32-S3-RLCD-4.2/Resources-And-Documents)
- [Vendor source examples](https://github.com/waveshareteam/ESP32-S3-RLCD-4.2)

Waveshare's ESP-IDF instructions require version 5.5.0 or newer. This project
pins v5.5.3 and installs its own toolchain through [setup.md](setup.md).
The original shared-workspace references are preserved in
[workspace-origin.md](workspace-origin.md).
