idf_component_register(SRCS "main.c" "live_main.c" "../demo.c" "../motion_demo.c" INCLUDE_DIRS ".."
                       REQUIRES agent_dashboard display_rlcd esp_timer heap esp_driver_usb_serial_jtag esp_hw_support)
