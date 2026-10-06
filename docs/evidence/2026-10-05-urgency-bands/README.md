# Urgency-band evidence

Recorded 2026-10-05 for the synthetic agent-dashboard refinement.
[The contract and results](../../../projects/agent-dashboard/docs/urgency-bands.md)
describe the tested behavior and remaining physical observation.

- [checks.json](checks.json): commands, exit status, native/static regression
  results and device cleanup.
- [images.json](images.json): source/configuration and firmware hashes, explicit
  board identity and matching boot ELF prefix.
- [readback-result.json](readback-result.json): byte-for-byte application match.
- [acceptance.json](acceptance.json): compact board gate and verified phase counts.
- [summary.json](summary.json), [serial.log](serial.log): complete 110-second
  capture summary and normalized log, including all 23 phases and a cycle reset.
- Native/build/flash logs and PBM hash manifests provide the supporting checks.

Selected PNGs are exact 400 x 300 outputs from the native renderer. They include
[compact working](demo-settled-17-compact-capacity.png),
[waiting](demo-settled-18-waiting-only.png),
[blocked overflow](demo-settled-19-blocked-only.png), feed loss,
removal/readmission, empty roster and a transition frame.

All sessions are invented. Native images and successful panel writes do not
establish physical readability or row-resizing acceptance. Those remain pending.
Firmware artifacts, raw capture and the previous-image rollback copies remain
in ignored build output; the full original flash backup remains in private
local state. No firmware binaries or flash backups are committed here.
