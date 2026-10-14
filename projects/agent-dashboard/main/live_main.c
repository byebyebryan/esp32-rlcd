#include <inttypes.h>
#include <stdio.h>

#include "dashboard_feed.h"
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_random.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "rlcd_panel.h"

static dashboard_feed_t feed;
static dashboard_motion_t motion;
static char line[DASH_FEED_BYTES + 1];

void dashboard_run_live(void)
{
    usb_serial_jtag_driver_config_t usb = {.tx_buffer_size = 2048, .rx_buffer_size = 32768};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));
    usb_serial_jtag_vfs_use_driver();
    char boot[17];
    snprintf(boot, sizeof(boot), "%08" PRIx32 "%08" PRIx32, esp_random(), esp_random());
    dashboard_feed_init(&feed, boot);
    dashboard_motion_init(&motion);
    ESP_LOGI("rlcd_dashboard", "LIVE wire=1 capacity=32 hosts=2 age=sampled_activity fps=25");
    size_t used = 0;
    bool discard = false, first = true, previous_moving = false;
    uint64_t request_at = 0, flash_step = UINT64_MAX;
    TickType_t wake = xTaskGetTickCount();
    for (;;) {
        const int64_t started_us = esp_timer_get_time();
        const uint64_t now_ms = (uint64_t)started_us / 1000;
        bool changed = false;
        if (first || now_ms - request_at >= DASH_FEED_REQUEST_MS) {
            char request[64];
            int size = dashboard_feed_request(&feed, now_ms, request, sizeof(request));
            if (size > 0 && (size_t)size < sizeof(request))
                usb_serial_jtag_write_bytes(request, (size_t)size, 0);
            request_at = now_ms;
        }
        // Bounded work per frame; driver storage absorbs a complete response.
        for (unsigned chunk = 0; chunk < 16; ++chunk) {
            char bytes[512];
            int size = usb_serial_jtag_read_bytes(bytes, sizeof(bytes), 0);
            if (size <= 0) break;
            for (int i = 0; i < size; ++i) {
                char byte = bytes[i];
                if (byte == '\n') {
                    if (!discard) {
                        if (used && line[used - 1] == '\r') --used;
                        const uint64_t received_ms = (uint64_t)esp_timer_get_time() / 1000;
                        if (dashboard_feed_accept(&feed, line, used, received_ms)) {
                            char ack[100];
                            int length = snprintf(ack, sizeof(ack), "RLCD_ACK seq=%u rows=%zu request=%u crc=%.*s\n",
                                (unsigned)feed.view.sequence, feed.view.row_count, (unsigned)feed.request,
                                8, line + used - 8);
                            usb_serial_jtag_write_bytes(ack, (size_t)length, 0);
                            changed = true;
                        }
                    }
                    used = 0; discard = false;
                } else if (!discard) {
                    if (used == DASH_FEED_BYTES) { used = 0; discard = true; }
                    else line[used++] = byte;
                }
            }
        }
        const uint64_t tick_ms = (uint64_t)esp_timer_get_time() / 1000;
        changed |= dashboard_feed_tick(&feed, &motion, tick_ms);
        bool moving = dashboard_motion_active(&motion);
        bool flashing = dashboard_motion_flashing(&motion);
        uint64_t step = tick_ms / DASHBOARD_MOTION_FLASH_HALF_PERIOD_MS;
        if (first || changed || moving || previous_moving || (flashing && step != flash_step)) {
            dashboard_motion_render(&motion, rlcd_panel_framebuffer());
            ESP_ERROR_CHECK(rlcd_panel_present_queued());
            if (changed || first || esp_timer_get_time() - started_us > 40000) {
                char report[240];
                int length = snprintf(report, sizeof(report),
                    "RLCD_HEALTH health=%d partial=%d rows=%zu blocked=%u waiting=%u working=%u unknown=%u"
                    " frame_us=%" PRId64 " miss=%d heap=%zu stack=%u\n",
                    motion.feed_health, motion.live_partial, motion.count,
                    (unsigned)motion.live_totals[0], (unsigned)motion.live_totals[1],
                    (unsigned)motion.live_totals[2], (unsigned)motion.live_totals[3],
                    esp_timer_get_time() - started_us, esp_timer_get_time() - started_us > 40000,
                    heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT),
                    (unsigned)uxTaskGetStackHighWaterMark(NULL));
                if (length > 0 && (size_t)length < sizeof(report))
                    usb_serial_jtag_write_bytes(report, (size_t)length, 0);
            }
        }
        first = false; previous_moving = moving; flash_step = step;
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(40));
    }
}
