idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_hw_support esp_system esp_timer esp_psram spi_flash heap display_rlcd)
