# Notes recovered from the shared ESP32-S3 workspace

The repository now named `esp32-349` originally covered the RLCD-4.2 and
Touch-LCD-3.49 boards. Its initial shared setup was committed on 2026-09-22;
the 349 standalone refactor on 2026-09-29 removed the RLCD vendor submodule
and replaced the shared root README.

The review on 2026-10-02 covered the initial tree, the last shared README
before the split, setup history and current documentation. The shared tree
contained a general smoke test and later 349 apps. RLCD-specific material
consisted of the board summary, toolchain requirement, upstream reference and
pinned vendor submodule; there was no separate RLCD application or acceptance
document to transfer.

## Carried forward

| Recovered note | Standalone location |
| --- | --- |
| RLCD module, flash/PSRAM, reflective monochrome panel and onboard peripherals | [board.md](board.md) |
| ESP-IDF v5.5.3 through EIM, target `esp32s3`, RLCD minimum IDF 5.5.0 | [setup.md](setup.md) and `scripts/eim-config.toml` |
| Arch serial access through `uucp`, followed by a new login | [setup.md](setup.md), with Debian/Ubuntu's `dialout` equivalent |
| Reuse detection through the actual EIM activation file | `scripts/setup.sh`, extended with environment/tool validation |
| RLCD vendor URL and source pin | [panel component provenance](../components/display_rlcd/UPSTREAM.md) |

The historical RLCD submodule pin was
`eb1f63427d735a22b9c30e22fa63ebddae1834d3`, the same source revision used by
this repository's panel implementation. The component retains its upstream
license and adaptation notes. The full vendor example tree is available at
that source link when needed; it is not a bootstrap dependency.

The old README also recorded an optional Arduino stack: ESP32 core 3.3.0,
LVGL 8.3.11/9.3.0 and SensorLib 0.3.1. Those are historical reference versions;
this repository's build and setup use ESP-IDF.

## Bootstrap changes for this repository

The fresh-machine guide includes prerequisites and EIM installation before
SDK setup. It uses an ordinary repository clone and builds from the root,
replacing the shared workspace's `projects/` and vendor-submodule layout.

EIM's `recurse_submodules` setting controls ESP-IDF's own dependencies.
It is enabled for a complete fresh SDK installation even though this app
repository has no submodules. All EIM paths are set explicitly so an
`EIM_ROOT` override relocates tools and activation as well as SDK source.
Generated machine-specific settings remain separate from shared defaults.

## Historical sources

- [Initial shared README](https://github.com/byebyebryan/esp32-349/blob/8289a6092f2212cd5b074cd8782ed86f08e8c278/README.md), commit `8289a60`.
- [Initial vendor pins](https://github.com/byebyebryan/esp32-349/tree/8289a6092f2212cd5b074cd8782ed86f08e8c278/vendor).
- [Activation-file reuse fix](https://github.com/byebyebryan/esp32-349/commit/32c1b00164ae051a09c2b28057db4de4b7dd6586), commit `32c1b00`.
- [349 standalone split](https://github.com/byebyebryan/esp32-349/commit/93f693a5c6604499d323f6496d1f33c9c0f7ac9f), commit `93f693a`.
