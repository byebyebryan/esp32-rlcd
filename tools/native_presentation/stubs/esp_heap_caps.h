#pragma once
#include <stdbool.h>
#include <stddef.h>
#define MALLOC_CAP_INTERNAL 1
#define MALLOC_CAP_8BIT 2
#define MALLOC_CAP_SPIRAM 4
static inline size_t heap_caps_get_free_size(int caps) { (void)caps; return 0; }
static inline bool heap_caps_check_integrity_all(bool print_errors) { (void)print_errors; return true; }
