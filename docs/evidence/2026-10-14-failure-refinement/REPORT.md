# Helper and failed-turn dashboard refinement

The consumer implements wire 2 and current failed-turn presentation. Agent
Observer's [independent producer checkpoint](https://github.com/byebyebryan/agent-observer/blob/d499445/docs/evidence/2026-10-14-title-helper/REPORT.md)
first accepted core-only a3 collectors on Snap and Starship. The device's bridge
keeps its accepted a1/a17 reader environment and explicit Agent v3. Observer
API 4/read 6/Service 4 remain unchanged.

## Behavior

Known `thread_title` helpers now classify as system and are excluded from roster
rows, counts, overflow and retained context. Unknown feature tags and ephemeral
user threads retain their classifications. No label blacklist or project
deduplication is applied. The earlier native helper comparison and later
packaged collector gate have distinct evidence bounds; the original helper
identities had already left their daemons by the later sample.

Current running runtime, unknown phase with `native_runtime_error`, and current
failed outcome derive the existing error cross and flashing row style. Known
working/blocked/waiting phases and a current in-progress turn take precedence
over preceding failure. Errors join blocked rows in the attention band and `!`
count. Age uses admitted source-sampled conversation activity. Missing/expired
evidence clears the error, age and flashing. Arbitrary unknown phases remain
unknown. The display reports generic failure; API 4 does not supply the native
capacity-specific category. It performs no provider retry, model change, archive
or unload.

Device wire 2 adds live code 4 and mutually rejects wire-1 tags. Counts, CRC,
bounds, nonce/request/sequence, source leases and request-send expiry remain
strict. `RLCD_HEALTH attention` names blocked plus failed totals. Bundle manifests
record `deviceWire=2`; rollback requires the matching bridge/firmware pair.

## Automated and device evidence

- 47 bridge/native/runtime/serial/bundle tests pass, including the portable
  three-failure/two-helper corpus, retry, phase precedence, evidence expiry,
  heartbeat non-renewal, attention order/capacity, system reclassification beyond
  the USB prefix, protocol rejection and error-containing C admission.
- Native ASan/UBSan motion and packed-frame checks pass; 4,488 rectangle cases
  match the pixel reference. ESP-IDF 5.5.3 clean build passes.
- Native gallery shows error/blocked attention, recovery, partial loss and expiry.
  Five PNG/GIF assets are byte-identical in Debug and Release; provenance and
  local documentation checks pass. These are native previews with fictional
  inputs and virtual time.
- Source freeze `09dd027` passes all [three hosted jobs](https://github.com/byebyebryan/esp32-rlcd/actions/runs/38538192873):
  native, Debug presentation and Release presentation.
- The [immutable bundle](bundle.json) is `3a4b22b4556cb243`, with clean source
  provenance and verified installed dependencies. The [firmware](firmware.json)
  has a 1,242,640-byte application; flashed readback equals its SHA-256
  `df992a713fd8a5cf47e8b45c36b13a9378ba80288d600a1b2b384dad20aefc55`.
- The [device fixture](device-fixture.json) uses fictional inputs and production
  projection/wire code, with no provider reads/actions. Eight CRC/request/row
  acknowledgements cover three failures then one retry. Attention changes 3→2
  while working changes 0→1. Stopping replies clears attention/work and leaves
  three uncertain identities at 10.916 seconds. Firmware reports this transition
  once; a later periodic diagnostic is not required.
- The [real cached-feed capture](live-capture.json) confirms 14 matching healthy
  packets before and 14 after six seconds of silence. Both hosts supply nine
  selected rows; Snap's remaining current failure contributes one attention
  count. Silence clears all work/attention and retains nine uncertain rows.
  Maximum sampled frame time is 17,951 microseconds, with zero deadline misses.

## Rollout and limits

The known RLCD MAC/USB identity is `94:a9:90:f3:43:74`. Only its bridge is stopped
for exclusive serial ownership. A [full 16 MiB backup](backup.json), prior 2 MiB
application slot and bridge/unit/selection copies remain outside Git under
`~/.local/state/esp32-rlcd/backups/20261014T084719Z-94a990f34374-wire2/`.
Bootloader and partition bytes match the prior image; application-only writes
preserve them.

The [paired rollback and final managed gate](managed.json) passes. The prior
wire-1 2 MiB application slot restores byte-for-byte, and its matching
`ccb8f7b3fa388f1d` bridge positively acknowledges the real cached feed. Reselecting
wire 2 repeats exact application readback and starts verified bundle
`3a4b22b4556cb243`. Its managed unit is active with zero restarts and positively
acknowledged current health. Scoped dotfiles publication `2bc0e1f` pins that pair;
ordinary source drift and foreign commits are preserved. Protected non-RLCD
service identities/restart counts and configuration bytes remain equal.

Native Codex sessions/configuration, prepared a2/a18 read CLI, a1/a17 Agent
publishers, Tmux, the historical writer and ESP32-349 retain their independent
ownership. Manual panel/readability and reboot acceptance remain deferred.
Prepared-reader adoption and matched application CPU measurement remain a
separate client pass; this refinement makes no new performance claim.
