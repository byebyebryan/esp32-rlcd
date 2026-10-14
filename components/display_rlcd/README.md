# Shared RLCD display support

All three applications share a 400 × 300 landscape, one-bit framebuffer and the
RLCD panel's SPI3 transport. The packed buffer occupies 15,000 bytes in 2-column
by 4-row blocks. A set bit is white; pixel writes clip at the screen bounds.

| Interface | Responsibility |
| --- | --- |
| [rlcd_frame.h](include/rlcd_frame.h) | Pure clear/pixel operations, packing and diagnostic pattern |
| [rlcd_panel.h](include/rlcd_panel.h) | Panel initialization, owned framebuffer and completed full-frame presentation |

Polling and queued-DMA presentation both return after transfer completion. One
owner may then reuse the framebuffer; there is no overlapping second-frame
pipeline. Current initialization uses SPI mode 0 at 10 MHz, with the pins in
[board support](../../docs/board.md). TE is not sampled.

[Native packing checks](../../scripts/check-frame.sh) cover all 120,000 pixels,
clipping and the diagnostic pattern under sanitizers. The
[benchmark findings](../../projects/render-bench/docs/performance.md) record
completed SPI writes separately from panel scan rate.

Application rendering, fonts, feed policy and host integration belong to their
projects. The [Waveshare provenance](UPSTREAM.md) and
[upstream license](LICENSE.waveshare) remain with this component.
