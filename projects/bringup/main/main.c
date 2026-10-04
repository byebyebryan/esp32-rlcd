#include <inttypes.h>

#include "esp_chip_info.h"
#include "esp_err.h"
#include "esp_flash.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "rlcd_frame.h"
#include "rlcd_panel.h"

static const char *TAG = "rlcd";

void app_main(void)
{
    esp_chip_info_t chip;
    esp_chip_info(&chip);

    uint32_t flash_bytes = 0;
    ESP_ERROR_CHECK(esp_flash_get_size(NULL, &flash_bytes));

    const size_t psram_bytes = esp_psram_is_initialized()
                                   ? esp_psram_get_size()
                                   : 0;

    ESP_LOGI(TAG, "esp32-rlcd: panel bring-up");
    ESP_LOGI(TAG, "Target: %s; ESP-IDF: %s", CONFIG_IDF_TARGET,
             esp_get_idf_version());
    ESP_LOGI(TAG, "Cores: %u; revision: %u.%u; reset reason: %d",
             (unsigned)chip.cores, (unsigned)(chip.revision / 100),
             (unsigned)(chip.revision % 100), (int)esp_reset_reason());
    ESP_LOGI(TAG, "Flash: %" PRIu32 " MiB; PSRAM: %zu MiB",
             flash_bytes / (1024 * 1024), psram_bytes / (1024 * 1024));

    if (flash_bytes != 16 * 1024 * 1024 || psram_bytes != 8 * 1024 * 1024) {
        ESP_LOGW(TAG, "Expected 16 MiB flash and 8 MiB PSRAM; check board/config");
    }

    ESP_ERROR_CHECK(rlcd_panel_init());
    ESP_LOGI(TAG, "Panel test ready: RLCD READY, stripes, checkers and moving square.");

    uint32_t frame = 0;
    for (;;) {
        rlcd_frame_draw_test(rlcd_panel_framebuffer(), frame);
        ESP_ERROR_CHECK(rlcd_panel_present());
        ESP_LOGI(TAG, "frame=%" PRIu32 " sent; uptime=%" PRId64 "s internal_free=%zu psram_free=%zu",
                 frame++,
                 esp_timer_get_time() / INT64_C(1000000),
                 heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT),
                 heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
