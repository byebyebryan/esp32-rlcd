# RLCD documentation and project gallery

The root README now presents all three applications with previews, concise
descriptions and direct setup/findings/media links. The live dashboard leads the
gallery. Its project README is a short entry point; current operation and retained
synthetic studies have separate guides. Board/setup documentation now reflects
shared queued-DMA support and the dashboard's independent partition layout.

Five selected native assets cover the live-layout dashboard, the unchanged
benchmark scene and the bring-up pattern. Dashboard names/identities are fictional.
The 14-second story passes through production host projection, wire admission,
expiry, motion and rendering, including partial loss and offline recovery.
Each [project manifest](../../media/README.md) binds exact source/output hashes.

## Validation

- Debug and Release native export produce identical bytes for all five assets.
- Local documentation links/anchors and all three media manifests pass the shared gate.
- Native packing, 40 dashboard tests and the existing renderer/motion checks pass.
- Workflow syntax passes actionlint. The new three-job CI runs native/docs checks
  and independently regenerates Debug/Release gallery assets.
- Representative healthy, reordered, partial, offline and recovered native frames
  were inspected for clipping and consistent host/age/state presentation.

The existing live dashboard and ESP32-349 processes remain active with their
original process IDs. This is documentation/native-media acceptance. Physical
panel/reboot follow-ups retain their prior deferred status.
