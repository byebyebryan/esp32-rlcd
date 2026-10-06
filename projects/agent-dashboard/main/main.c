#include <inttypes.h>

#include "demo.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "rlcd_panel.h"
#include "sdkconfig.h"

#if CONFIG_RLCD_DASHBOARD_STATIC
static void run_static_demo(void)
{
    const dashboard_style_t style = {DASH_AGENT_PAIR, true};
    unsigned index = 0;
    for (;;) {
        const dashboard_view_t view = dashboard_demo_icon_view(index);
        const int64_t start = esp_timer_get_time();
        dashboard_draw_styled(rlcd_panel_framebuffer(), &view, style);
        const int64_t drawn = esp_timer_get_time();
        ESP_ERROR_CHECK(rlcd_panel_present_queued());
        ESP_LOGI("rlcd_dashboard", "DEMO layout=attention case=%s draw_us=%" PRId64
                 " transfer_us=%" PRId64 " internal_free=%zu",
                 dashboard_demo_name(index), drawn - start,
                 esp_timer_get_time() - drawn,
                 heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
        ++index;
        vTaskDelay(pdMS_TO_TICKS(12000));
    }
}
#else
#include "dashboard_motion.h"

enum { FRAME_PERIOD_MS = 40, FRAME_BUDGET_US = FRAME_PERIOD_MS * 1000 };
static dashboard_motion_t motion;

static void run_motion_demo(void)
{
    dashboard_motion_init(&motion);
    const int64_t origin_us = esp_timer_get_time();
    const uint64_t cycle_ms = dashboard_motion_demo_cycle_ms();
    size_t previous_phase = SIZE_MAX;
    uint64_t previous_cycle = 0;
    uint64_t previous_second = UINT64_MAX;
    int64_t previous_render_us = 0;
    bool previous_moving = false;
    uint64_t previous_flash_step = UINT64_MAX;
    TickType_t wake_tick = xTaskGetTickCount();
    ESP_LOGI("rlcd_dashboard", "MOTION event=config phases=%zu cycle_ms=%" PRIu64
             " fps=25 duration_ms=%d frame_budget_us=%d capacity=%d model_bytes=%zu"
             " visible_policy=height_prefix full_row_px=%d working_row_px=%d"
             " normal_text_px=%d working_text_px=%d body_top=%d body_bottom=%d"
             " font=fusion_pixel_12_zh_hans font_release=2026.09.25"
             " normal_scale=2 working_scale=2 normal_cap_px=16 working_cap_px=16"
             " header_px=24 summary_px=12 footer_px=12 divider_y=21 header_gap_px=2"
             " chrome=title_counts source=simulated feed_loss=settle_target"
             " waiting_marker_px=0 blocked_flash_hz=1 blocked_flash_half_ms=500"
             " waiting_polarity=inverse working_polarity=normal",
             dashboard_motion_demo_phase_count(), cycle_ms,
             DASHBOARD_MOTION_DURATION_MS, FRAME_BUDGET_US,
             DASHBOARD_MOTION_CAPACITY, sizeof(motion),
             DASHBOARD_MOTION_ROW_HEIGHT, DASHBOARD_MOTION_WORKING_ROW_HEIGHT,
             DASHBOARD_MOTION_TEXT_HEIGHT, DASHBOARD_MOTION_WORKING_TEXT_HEIGHT,
             DASHBOARD_MOTION_BODY_TOP, DASHBOARD_MOTION_BODY_BOTTOM);
    for (;;) {
        const int64_t frame_start_us = esp_timer_get_time();
        const uint64_t elapsed_ms = (uint64_t)(frame_start_us - origin_us) / 1000;
        const bool changed = dashboard_motion_demo_update(&motion, elapsed_ms);
        dashboard_motion_tick(&motion, dashboard_motion_demo_now_ms(elapsed_ms));
        const bool moving = dashboard_motion_active(&motion);
        const bool flashing = dashboard_motion_flashing(&motion);
        const uint64_t flash_step = motion.now_ms / DASHBOARD_MOTION_FLASH_HALF_PERIOD_MS;
        const bool flash_changed = flashing && flash_step != previous_flash_step;
        const size_t phase = dashboard_motion_demo_phase_index(elapsed_ms);
        const uint64_t cycle = elapsed_ms / cycle_ms;
        const uint64_t second = elapsed_ms / 1000;
        if (changed || moving || previous_moving || flash_changed ||
            second != previous_second) {
            const int64_t draw_start_us = esp_timer_get_time();
            dashboard_motion_render(&motion, rlcd_panel_framebuffer());
            const int64_t drawn_us = esp_timer_get_time();
            // This returns only after DMA completes; one task owns the frame.
            ESP_ERROR_CHECK(rlcd_panel_present_queued());
            const int64_t done_us = esp_timer_get_time();
            const int64_t interval_us = moving && previous_moving
                ? frame_start_us - previous_render_us : 0;
            ESP_LOGI("rlcd_dashboard", "MOTION event=frame case=%s tick_ms=%" PRIu64
                     " moving=%d flashing=%d blocked_flash_white=%d draw_us=%" PRId64 " transfer_us=%" PRId64
                     " frame_us=%" PRId64 " interval_us=%" PRId64
                     " deadline_miss=%d internal_free=%zu stack_watermark=%u",
                     dashboard_motion_demo_phase_name(phase), elapsed_ms,
                     moving, flashing, flashing && flash_step % 2 == 1,
                     drawn_us - draw_start_us, done_us - drawn_us,
                     done_us - frame_start_us, interval_us,
                     done_us - frame_start_us > FRAME_BUDGET_US,
                     heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT),
                     (unsigned)uxTaskGetStackHighWaterMark(NULL));
            previous_render_us = frame_start_us;
            previous_second = second;
            previous_flash_step = flash_step;
        }
        if (cycle != previous_cycle) {
            ESP_LOGI("rlcd_dashboard", "MOTION event=cycle cycle=%" PRIu64,
                     cycle);
            previous_cycle = cycle;
        }
        if (phase != previous_phase || changed) {
            ESP_LOGI("rlcd_dashboard", "MOTION event=phase phase=%zu case=%s"
                     " tick_ms=%" PRIu64 " count=%zu feed_health=%d"
                     " visible=%zu overflow=%zu hidden_blocked=%zu",
                     phase, dashboard_motion_demo_phase_name(phase), elapsed_ms,
                     dashboard_motion_count(&motion),
                     dashboard_motion_feed_health(&motion),
                     dashboard_motion_visible_count(&motion),
                     dashboard_motion_overflow_count(&motion),
                     dashboard_motion_hidden_blocked_count(&motion));
            previous_phase = phase;
        }
        previous_moving = moving;
        vTaskDelayUntil(&wake_tick, pdMS_TO_TICKS(FRAME_PERIOD_MS));
    }
}
#endif

void app_main(void)
{
    ESP_ERROR_CHECK(rlcd_panel_init());
#if CONFIG_RLCD_DASHBOARD_STATIC
    run_static_demo();
#else
    run_motion_demo();
#endif
}
