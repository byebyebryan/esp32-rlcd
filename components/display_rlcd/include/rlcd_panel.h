#pragma once

#include <stdint.h>
#include "esp_err.h"

// One owner, synchronous transfers; the buffer is reusable after present returns.
esp_err_t rlcd_panel_init(void);
uint8_t *rlcd_panel_framebuffer(void);
esp_err_t rlcd_panel_present(void);
// Same full-frame write, but blocks the calling task while SPI DMA runs.
// Returns only after completion; retain the same single-owner buffer discipline.
esp_err_t rlcd_panel_present_queued(void);
