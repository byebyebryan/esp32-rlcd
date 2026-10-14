# Development

This workspace contains independent ESP-IDF applications for one RLCD board.
Keep the root README focused on the hardware and project gallery. Application
behavior, host tools, media and guides belong to their project; shared packing
and panel transport belong in `components/display_rlcd`.

## Workspace layout

| Path | Responsibility |
| --- | --- |
| `projects/agent-dashboard` | Live Observer/Mesh bridge, firmware, native checks and retained synthetic studies |
| `projects/render-bench` | Drawing/SPI workloads and recorded measurements |
| `projects/bringup` | Memory, USB, orientation and packing diagnostics |
| `components/display_rlcd` | Shared packed framebuffer and panel driver |
| `scripts` | Toolchain wrappers, shared checks and gallery export |
| `tools/native_presentation` | Native exporter and board-call stubs |
| `docs/evidence` | Dated source, build, deployment and acceptance records |

Each project is a standalone firmware application. The repository root has no
`CMakeLists.txt` application and no default firmware selection. Root
[`sdkconfig.defaults`](../sdkconfig.defaults) supplies shared board defaults;
each app owns local generated configuration and build output. See
[fresh-machine setup](setup.md) for the pinned ESP-IDF v5.5.3 installation.

## Native checks

Run from the repository root with a host C compiler and Python 3:

```sh
./scripts/check-frame.sh
./projects/agent-dashboard/scripts/test-live-dashboard.sh
./projects/agent-dashboard/scripts/test-dashboard-motion.sh
python3 scripts/check-docs.py
```

The pixel, feed and motion checks use address/undefined-behavior sanitizers.
Documentation checks cover local links/anchors and every project gallery
manifest's source/output hashes. Gallery authoring uses an optional pinned
Pillow environment, described in [presentation media](media/README.md).

[CI](../.github/workflows/checks.yml) runs these native/documentation checks and
regenerates the gallery in Debug and Release modes. It compares PNG/GIF bytes
with the committed assets. These checks leave firmware build, flashed-image
identity and physical acceptance as separate evidence.

## Build and operate

Build with an explicit project path:

```sh
./scripts/idf.sh -C projects/agent-dashboard build
```

The application guides own flashing and host dependencies. For live dashboard
maintenance, follow [operation](../projects/agent-dashboard/docs/operations.md):
the Starship service owns the RLCD serial port, and foreground captures require
exclusive ownership. The sibling ESP32-349 has a separate device and service.

Keep dated evidence intact. Current source, generated media, built firmware,
installed host bundles and physical observations have separate provenance.
Raw frames, logs and build caches remain ignored; publish selected assets and
bounded acceptance metadata.

## Add a project

Create `projects/<name>` with its own ESP-IDF configuration, README and focused
guides. Reuse the shared panel component instead of copying its packing or
transport logic. Keep project-specific fonts, data, host tools and integrations
with the application.

For a showcase application, add a root gallery entry with a preview, a concise
description and links to setup, behavior/findings and media source. Link
diagnostic tools from the workspace and setup guides. Put generated assets and
their manifest in `projects/<name>/docs/media/`. The shared docs check discovers that
manifest automatically; extend the native exporter and CI comparison for a
reproducible preview. Label native/fictional inputs and virtual playback clearly.
