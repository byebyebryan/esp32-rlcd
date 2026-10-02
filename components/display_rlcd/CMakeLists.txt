idf_component_register(
    SRCS "rlcd_panel.c" "rlcd_frame.c"
    INCLUDE_DIRS "include"
    REQUIRES esp_driver_gpio esp_driver_spi heap)
