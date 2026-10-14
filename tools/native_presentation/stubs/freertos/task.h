#pragma once
#include "FreeRTOS.h"
static inline void vTaskDelay(TickType_t ticks) { (void)ticks; }
static inline TickType_t xTaskGetTickCount(void) { return 0; }
static inline int xTaskDelayUntil(TickType_t *wake, TickType_t ticks) { *wake += ticks; return 1; }
