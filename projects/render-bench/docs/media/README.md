# Render bench presentation media

The native exporter compiles the unchanged benchmark `main/main.c` with board
stubs, calls its cached `draw_animation` function and uses the shared packed
framebuffer. It never runs the firmware benchmark or supplies invented
performance measurements.

| Asset | Content |
| --- | --- |
| [benchmark.png](benchmark.png) | Exact 400 × 300 cached scene |
| [benchmark-demo.gif](benchmark-demo.gif) | 6.4-second virtual ball/bar animation, including edge reflections |

Samples are 40 ms apart on the scene's virtual 50-write/s sequence. GIF playback
does not measure panel refresh or CPU use. The [recorded performance](../performance.md)
provides the separate hardware timing and physical-observation evidence.

Follow the [shared regeneration guide](../../../../docs/media/README.md).
[manifest.json](manifest.json) records tracked input/output hashes and timing.
