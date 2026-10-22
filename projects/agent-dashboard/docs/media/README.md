# Agent dashboard presentation media

These current previews use the fictional active-demo story through the host
projection, wire 5 admission, expiry, motion and renderer. They use ST/SN host
badges and contain no provider conversation data. The story has no recent-only
members, so these images do not demonstrate working-set membership or its
recent-row category and totals. The live policy is documented in the
[integration contract](../live-integration.md).

| Asset | Content |
| --- | --- |
| [dashboard.png](dashboard.png) | Exact 400 × 300 roster with seven fictional conversations |
| [dashboard-demo.gif](dashboard-demo.gif) | 14-second virtual story: blocked/error flashing, a recovered turn, row movement, one-host loss, whole-feed expiry and recovery |

[story.json](story.json) owns the fictional names and initial phases/ages. The
exporter admits replacement packets every virtual second, samples frames every
40 ms, and leaves a gap long enough for firmware to expire all work claims.
Recovery uses a fresh bridge incarnation. These samples exercise display paths;
they do not establish native provider semantics or physical panel performance.

Follow the [shared regeneration guide](../../../../docs/media/README.md).
[manifest.json](manifest.json) records source/output hashes and timing. The
[integration contract](../live-integration.md) defines real data/expiry policy;
the [release receipt](../../../../docs/evidence/2026-10-13-release-refinement/REPORT.md)
records live-device and deployment acceptance separately.
