idf_component_register(SRCS "main.c" "../demo.c" "../motion_demo.c" INCLUDE_DIRS ".."
                       REQUIRES agent_dashboard display_rlcd esp_timer heap)
