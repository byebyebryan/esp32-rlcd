// Controller sequence adapted from Waveshare's display_bsp.cpp (Apache-2.0).
// Modified: synchronous ESP-IDF SPI transport with an internal DMA framebuffer.
// See UPSTREAM.md and LICENSE.waveshare.
#include "rlcd_panel.h"
#include "rlcd_frame.h"

#include <string.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

enum { PIN_DC = 5, PIN_CS = 40, PIN_SCK = 11, PIN_MOSI = 12, PIN_RST = 41 };
static const char *TAG = "rlcd_panel";
static spi_device_handle_t device;
static uint8_t *framebuffer;

static esp_err_t transmit(const void *data, size_t length)
{
    spi_transaction_t transaction = {.length = length * 8};
    if (length <= sizeof(transaction.tx_data)) {
        transaction.flags = SPI_TRANS_USE_TXDATA;
        memcpy(transaction.tx_data, data, length);
    } else {
        transaction.tx_buffer = data;
    }
    return spi_device_polling_transmit(device, &transaction);
}

static esp_err_t command(uint8_t cmd, const void *parameters, size_t length)
{
    ESP_RETURN_ON_ERROR(gpio_set_level(PIN_DC, 0), TAG, "command GPIO");
    ESP_RETURN_ON_ERROR(transmit(&cmd, 1), TAG, "command transfer");
    if (length) {
        ESP_RETURN_ON_ERROR(gpio_set_level(PIN_DC, 1), TAG, "data GPIO");
        ESP_RETURN_ON_ERROR(transmit(parameters, length), TAG, "data transfer");
    }
    return ESP_OK;
}

typedef struct {
    uint8_t command;
    uint8_t length;
    uint8_t data[10];
} init_command_t;

static esp_err_t commands(const init_command_t *sequence, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        ESP_RETURN_ON_ERROR(command(sequence[i].command, sequence[i].data,
                                    sequence[i].length), TAG, "panel init");
    }
    return ESP_OK;
}

esp_err_t rlcd_panel_init(void)
{
    ESP_RETURN_ON_FALSE(device == NULL, ESP_ERR_INVALID_STATE, TAG, "already initialized");
    const gpio_config_t gpio = {
        .pin_bit_mask = (1ULL << PIN_DC) | (1ULL << PIN_RST),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    ESP_RETURN_ON_ERROR(gpio_config(&gpio), TAG, "GPIO setup");
    const spi_bus_config_t bus = {
        .mosi_io_num = PIN_MOSI, .miso_io_num = -1, .sclk_io_num = PIN_SCK,
        .quadwp_io_num = -1, .quadhd_io_num = -1,
        .max_transfer_sz = RLCD_FRAME_BYTES,
    };
    ESP_RETURN_ON_ERROR(spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO), TAG, "SPI bus");
    const spi_device_interface_config_t config = {
        .clock_speed_hz = 10000000, .mode = 0,
        .spics_io_num = PIN_CS, .queue_size = 1,
    };
    ESP_RETURN_ON_ERROR(spi_bus_add_device(SPI3_HOST, &config, &device), TAG, "SPI device");
    framebuffer = heap_caps_malloc(RLCD_FRAME_BYTES, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    ESP_RETURN_ON_FALSE(framebuffer != NULL, ESP_ERR_NO_MEM, TAG, "framebuffer allocation");
    rlcd_frame_clear(framebuffer, true);

    ESP_RETURN_ON_ERROR(gpio_set_level(PIN_RST, 1), TAG, "reset high");
    vTaskDelay(pdMS_TO_TICKS(50));
    ESP_RETURN_ON_ERROR(gpio_set_level(PIN_RST, 0), TAG, "reset low");
    vTaskDelay(pdMS_TO_TICKS(20));
    ESP_RETURN_ON_ERROR(gpio_set_level(PIN_RST, 1), TAG, "reset release");
    vTaskDelay(pdMS_TO_TICKS(50));

    static const init_command_t power[] = {
        {0xd6, 2, {0x17, 0x02}}, {0xd1, 1, {0x01}},
        {0xc0, 2, {0x11, 0x04}}, {0xc1, 4, {0x69, 0x69, 0x69, 0x69}},
        {0xc2, 4, {0x19, 0x19, 0x19, 0x19}}, {0xc4, 4, {0x4b, 0x4b, 0x4b, 0x4b}},
        {0xc5, 4, {0x19, 0x19, 0x19, 0x19}}, {0xd8, 2, {0x80, 0xe9}},
        {0xb2, 1, {0x02}},
        {0xb3, 10, {0xe5, 0xf6, 0x05, 0x46, 0x77, 0x77, 0x77, 0x77, 0x76, 0x45}},
        {0xb4, 8, {0x05, 0x46, 0x77, 0x77, 0x77, 0x77, 0x76, 0x45}},
        {0x62, 3, {0x32, 0x03, 0x1f}}, {0xb7, 1, {0x13}}, {0xb0, 1, {0x64}},
        {0x11, 0, {0}},
    };
    ESP_RETURN_ON_ERROR(commands(power, sizeof(power) / sizeof(power[0])), TAG, "power init");
    vTaskDelay(pdMS_TO_TICKS(200));
    static const init_command_t display[] = {
        {0xc9, 1, {0x00}}, {0x36, 1, {0x48}}, {0x3a, 1, {0x11}},
        {0xb9, 1, {0x20}}, {0xb8, 1, {0x29}}, {0x21, 0, {0}},
        {0x2a, 2, {0x12, 0x2a}}, {0x2b, 2, {0x00, 0xc7}},
        {0x35, 1, {0x00}}, {0xd0, 1, {0xff}}, {0x38, 0, {0}}, {0x29, 0, {0}},
    };
    ESP_RETURN_ON_ERROR(commands(display, sizeof(display) / sizeof(display[0])), TAG, "display init");
    ESP_LOGI(TAG, "Initialized: SPI3 10 MHz, 400x300, %d-byte framebuffer", RLCD_FRAME_BYTES);
    return ESP_OK;
}

uint8_t *rlcd_panel_framebuffer(void)
{
    return framebuffer;
}

esp_err_t rlcd_panel_present(void)
{
    ESP_RETURN_ON_FALSE(framebuffer != NULL, ESP_ERR_INVALID_STATE, TAG, "not initialized");
    const uint8_t columns[] = {0x12, 0x2a};
    const uint8_t rows[] = {0x00, 0xc7};
    ESP_RETURN_ON_ERROR(command(0x2a, columns, sizeof(columns)), TAG, "column window");
    ESP_RETURN_ON_ERROR(command(0x2b, rows, sizeof(rows)), TAG, "row window");
    return command(0x2c, framebuffer, RLCD_FRAME_BYTES);
}
