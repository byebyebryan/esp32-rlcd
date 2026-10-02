#pragma once

#include <stdint.h>
#include "esp_err.h"

// One owner, synchronous transfers; the buffer is reusable after present returns.
esp_err_t rlcd_panel_init(void);
uint8_t *rlcd_panel_framebuffer(void);
esp_err_t rlcd_panel_present(void);
