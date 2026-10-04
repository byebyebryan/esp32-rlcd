#include <inttypes.h>
#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/idf_additions.h"
#include "rlcd_frame.h"
#include "rlcd_panel.h"

static const char *TAG = "rlcd_perf";
static uint8_t background[RLCD_FRAME_BYTES];
static uint32_t animation_frame;

typedef struct {
    uint32_t count;
    uint64_t sum;
    uint32_t min, max;
    uint32_t histogram[100]; // 500 us buckets, last bucket includes overflow.
} timings_t;

static void record(timings_t *t, uint32_t us)
{
    if (!t->count || us < t->min) t->min = us;
    if (us > t->max) t->max = us;
    ++t->count;
    t->sum += us;
    unsigned bucket = us / 500;
    ++t->histogram[bucket < 100 ? bucket : 99];
}

static uint32_t p95_upper(const timings_t *t)
{
    uint32_t total = 0;
    for (unsigned i = 0; i < 100; ++i) {
        total += t->histogram[i];
        if (total >= (t->count * 95 + 99) / 100) {
            return i == 99 ? t->max : (i + 1) * 500;
        }
    }
    return t->max;
}

static void report_times(const char *phase, const char *kind, const timings_t *t)
{
    ESP_LOGI(TAG, "TIMING phase=%s kind=%s n=%" PRIu32
             " mean_us=%" PRIu64 " min_us=%" PRIu32 " max_us=%" PRIu32
             " p95_upper_us=%" PRIu32,
             phase, kind, t->count, t->sum / t->count, t->min, t->max, p95_upper(t));
}

static int bounce(uint32_t step, int limit)
{
    int p = (int)(step % (unsigned)(limit * 2));
    return p > limit ? limit * 2 - p : p;
}

static void draw_animation(uint8_t *buffer, uint32_t frame)
{
    memcpy(buffer, background, sizeof(background));
    int cx = 20 + bounce(frame * 3, 359);
    int cy = 112 + bounce(frame * 2, 163);
    for (int y = -12; y <= 12; ++y) {
        for (int x = -12; x <= 12; ++x) {
            if (x * x + y * y <= 144) {
                // Black rim and white center remain visible over the pattern.
                rlcd_frame_pixel(buffer, cx + x, cy + y, x * x + y * y <= 100);
            }
        }
    }
    // A narrow moving bar exposes incomplete frames and motion artifacts.
    int bar = 8 + bounce(frame * 5, 380);
    for (int y = 104; y < 290; ++y) rlcd_frame_pixel(buffer, bar, y, false);
}

static void draw_only(uint8_t *buffer, bool cached)
{
    timings_t draw = {0};
    for (uint32_t i = 0; i < 256; ++i) {
        int64_t start = esp_timer_get_time();
        if (cached) draw_animation(buffer, i);
        else rlcd_frame_draw_test(buffer, i);
        record(&draw, (uint32_t)(esp_timer_get_time() - start));
        if ((i & 15) == 15) vTaskDelay(1);
    }
    report_times(cached ? "draw_cached" : "draw_full", "draw", &draw);
}

static void run_phase(const char *name, bool cached, bool queued,
                      uint32_t period_ms, uint32_t seconds)
{
    timings_t draw = {0}, transfer = {0}, total = {0};
    uint32_t missed = 0;
    uint32_t idle_start[2] = {
        (uint32_t)ulTaskGetIdleRunTimeCounterForCore(0),
        (uint32_t)ulTaskGetIdleRunTimeCounterForCore(1),
    };
    size_t free_start = heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    int64_t start = esp_timer_get_time();
    TickType_t wake = xTaskGetTickCount();
    while (esp_timer_get_time() - start < (int64_t)seconds * 1000000) {
        int64_t a = esp_timer_get_time();
        if (cached) draw_animation(rlcd_panel_framebuffer(), animation_frame++);
        else rlcd_frame_draw_test(rlcd_panel_framebuffer(), animation_frame++);
        int64_t b = esp_timer_get_time();
        ESP_ERROR_CHECK(queued ? rlcd_panel_present_queued() : rlcd_panel_present());
        int64_t c = esp_timer_get_time();
        record(&draw, (uint32_t)(b - a));
        record(&transfer, (uint32_t)(c - b));
        record(&total, (uint32_t)(c - a));
        if (period_ms) {
            if (xTaskDelayUntil(&wake, pdMS_TO_TICKS(period_ms)) == pdFALSE) ++missed;
        } else if ((total.count & 15) == 0) {
            // Bound idle-task starvation in the polling stress phases.
            // Apply the identical 1 ms gap to both transfer modes for comparison.
            vTaskDelay(1);
        }
    }
    uint32_t elapsed = (uint32_t)(esp_timer_get_time() - start);
    unsigned busy[2];
    for (unsigned core = 0; core < 2; ++core) {
        uint32_t delta = (uint32_t)ulTaskGetIdleRunTimeCounterForCore(core) - idle_start[core];
        uint64_t idle_pct = (uint64_t)delta * 100 / elapsed;
        busy[core] = idle_pct >= 100 ? 0 : 100 - (unsigned)idle_pct;
    }
    size_t free_end = heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    ESP_LOGI(TAG, "RESULT phase=%s frames=%" PRIu32 " elapsed_us=%" PRIu32
             " writes_per_s_x100=%" PRIu64 " cpu0_busy_pct=%u cpu1_busy_pct=%u"
             " missed=%" PRIu32 " internal_before=%zu internal_after=%zu psram_free=%zu",
             name, total.count, elapsed, (uint64_t)total.count * 100000000 / elapsed,
             busy[0], busy[1], missed, free_start, free_end,
             heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    report_times(name, "draw", &draw);
    report_times(name, "transfer", &transfer);
    report_times(name, "total", &total);
    ESP_ERROR_CHECK(heap_caps_check_integrity_all(true) ? ESP_OK : ESP_FAIL);
}

void app_main(void)
{
    ESP_LOGI(TAG, "RLCD drawing benchmark; SPI=10MHz; packed=15000B; CPU=240MHz; -O3; tick=1ms");
    ESP_LOGI(TAG, "Counts are completed SPI writes, not measured panel scan refresh.");
    ESP_ERROR_CHECK(rlcd_panel_init());
    rlcd_frame_draw_test(background, 0);
    draw_only(rlcd_panel_framebuffer(), false);
    draw_only(rlcd_panel_framebuffer(), true);
    run_phase("full_poll", false, false, 0, 6);
    run_phase("cached_poll", true, false, 0, 6);
    run_phase("cached_queue", true, true, 0, 6);
    run_phase("paced_50", true, true, 20, 10);
    // 16 ms is 62.5 requested writes/s; use its actual period in the label.
    run_phase("paced_62_5", true, true, 16, 10);
    ESP_LOGI(TAG, "SUITE_COMPLETE; continuing the cached animation at 50 writes/s.");
    for (;;) run_phase("soak_50", true, true, 20, 10);
}
