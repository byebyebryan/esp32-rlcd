# 12/8-pixel font comparison evidence

Recorded 2026-10-05. [The study](../../../projects/agent-dashboard/docs/font-size-study.md)
describes the fonts and unchanged row geometry.

[images.json](images.json) records exact source/configuration and image hashes;
[readback-result.json](readback-result.json) records the full application match.
[acceptance.json](acceptance.json) summarizes the board gate, while
[summary.json](summary.json) and [serial.log](serial.log) preserve all captured
records. Native/build/flash logs and PBM hash manifests support these checks.

Exact 400 x 300 PNGs show [mixed rows](demo-settled-00-initial-order.png),
[compact working rows](demo-settled-17-compact-capacity.png),
[waiting](demo-settled-18-waiting-only.png),
[blocked overflow](demo-settled-19-blocked-only.png) and feed loss.
All sessions are invented. Physical readability is pending.
