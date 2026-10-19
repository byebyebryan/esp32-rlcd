# Snap working-set adoption

Snap now uses the explicit active-plus-recent 72-hour view through the selected
wire-3 client and verified matching firmware. Active membership is independent
of recency; recent parked sessions use a neutral dash and the recent clock total.
Unknown runtime stays unknown. Child/system rows remain excluded. Full-history
diagnostics remain an explicit cached read, without a fallback.

## Pinned implementation

| Component | Exact selection |
| --- | --- |
| RLCD runtime | `443f3dda947ca96d68d573f2ae3ac7159d9b6f20` |
| Observer producer base | `74bc2012ef27e65dc6aad9e3ae48bd9c400d4df2` |
| Observer additive presentation facade | `1eec6c6d8681a3e58bab742d5c130656ab00433c` |
| Mesh candidate | `2fb502da35c0ef9865762c4dc4b486dd30b7e316` |
| Immutable host bundle | `d3fd7b8133f02567371cad18a14e0b45eb55d7f1ddf24bdcc867468bdbdd7808` |
| Snap application image | `b2dca61d4d2647aba0daa98c14394d23d60bfdbc6f71db103ef26c096afd28ae` |
| Final managed configuration | dotfiles `636a90a`; exact active candidate in [activation record](activation.json) |

[Package receipt](pair.json) and [bundle manifest](bundle.json) bind the full
wheel hashes. These are private candidate builds retaining the a7/a23 labels;
the released versions alone do not identify this profile. Original producer
worktrees, released packages, old prefixes and rollback bundles are preserved.
The Observer facade changes are published on the separate
`rlcd-working-set-adoption-20261019` branch.

The normal source is `agent_working_set`, with the public working-set profile,
configured local IPC and fixed SSH to the other host. One shared native collector
per host enables the working-set projection alongside unchanged full/active
contracts. Tmux, historical writer, normal provider workflows and dark delta
remain independent. Only Snap's client/firmware is in scope for the paired wire-3
migration. Starship's wire-2 client selection and device are preserved.

## Expiry and presentation

Observer exports defensive receiving-clock member leases and complete-scope
leases from its existing admitted domain decisions. Membership keeps A OR R;
known-kind support and displayed current fields bound each row. The selected
active/recent branch also bounds its category. Complete coverage expires at the
minimum of its census dependencies, selected memberships and admitted negatives,
including a complete empty scope. Positive expiry does not create a negative.

The host subtracts a 100 ms margin and caps claims at three seconds. Aggregate
counts use the earliest relevant lease across the whole counted roster, including
rows beyond the 32-row USB limit. Individual row validity may outlive a shorter
aggregate lease. The device anchors expiry to its original request time; delayed
serial responses cannot restart the budget. Expired rows retain uncertain context.
Only admitted negatives/current complete scope retire that context.

Wire 3 carries attention, waiting, working, recent and uncertain totals plus
explicit row categories. Active rows precede recent rows; recent rows sort newest
first, followed by retained uncertain context. Eleven rows fit the panel; 32 may
cross USB, with explicit overflow and whole-roster totals. The largest five-total
header plus overflow fits inside the panel. Current fictional presentation assets
were regenerated and visually reviewed; they remain an active demo, with no
claim to demonstrate recent-only membership.

## Validation

- Observer required gate: 1,159 tests, zero skips; 256 Markdown files pass.
- [Installed package suites](installed-focused-314.json): 102 methods on each
  Python 3.14.8/3.11.17, GC disabled, zero failures/errors/skips. Imported package
  bytes match the wheels; installed inventories and RECORD hashes are verified.
- Consumer: 68 tests on each interpreter, native address/undefined sanitizers,
  three motion checks, frame checks, scoped Ruff and documentation/media hashes.
  Runtime source CI passes [run 39309010620](https://github.com/byebyebryan/esp32-rlcd/actions/runs/39309010620).
- [Starship native comparison](native-starship.json): stable complete census of
  404 identities; ten working-set members and 394 expected negatives match.
- [Snap native comparison](native-snap.json): stable complete census of 102
  identities; one recent-only member and 101 expected negatives match.
  Both comparisons have zero unresolved/mismatched membership or compared fields;
  private qualification services/processes are joined and removed. No native
  daemon/session/provider action is taken.
- Fresh final [Starship](native-starship-final.json) and [Snap](native-snap-final.json)
  comparisons after resume again match all 404/102 identities and compared fields,
  with complete stable censuses and no unresolved/mismatched membership. Native
  state has legitimately changed: Snap's member is now active, so the final live
  aggregate is six active plus five recent rows. Both private qualification owners
  are joined with zero return codes; the ordinary daemon is never signalled.
- Actual configured [Starship route](route-scope-starship.json) and
  [Snap route](route-scope-snap.json) pass 25-second IPC/fixed-SSH reads with three
  distinct remote fresh proofs each, complete scopes and no uncertain members.
  Stream retirement clears positive claims. These descriptive client samples use
  0.396/0.632 CPU seconds and 35,556/36,040 KiB maximum RSS; SSH server, collector
  and whole producer costs are outside that sample.
- [Explicit full-history read](explicit-full-read.json) returns 506 diagnostic
  rows through the separate cached full profile. No working-set fallback is used.

## Device and operations

The exact Snap board is `94:a9:90:de:d0:04`, selected by its by-id USB identity.
ESP32-349 `28:84:85:92:C4:3C` is outside the operation. The fresh
[16 MiB backup](hardware-backup.json) matches all three prior wire-2 components
before any write. It remains private at
`~/.local/state/rlcd-working-set-adoption/20261019T183334Z/hardware/flash-wire2-before.bin`.
Its SHA-256 is `6b9bfd32f5da95ffbfa159c6cb42c4171cd15243242624d3b092f677a669d5a4`.

The [fresh IDF 5.5.3 build](firmware-build.json) uses the existing live-mode
SDK configuration byte-for-byte, DIO/80 MHz/16 MiB flash and the same three
offsets. [Readback](hardware-new.json) matches bootloader, partition table and
application exactly. The [first live capture](live-first.json) confirms CRC,
request and row identity for 26 initial and 25 recovery acknowledgements. Its
snapshot contains five active plus six recent parked sessions, complete scope
and no uncertain rows. Silence clears all current counts and retains eleven
uncertain rows. Both windows have zero frame deadline misses; maximum observed
frame time is 19,187 microseconds, internal free heap at least 291,003 bytes and
stack watermark at least 4,776 bytes.

The [initial managed service](client-initial-health.json) is healthy with eleven
rows, six recent sessions, zero uncertainty and zero restarts. The bounded
[fictional device probe](fictional-device.json) passes failed-turn attention,
retry transition, exact acknowledgement and silence expiry checks.

Paired rollback restores eleven managed targets on Snap and seven on Starship
byte-for-byte, then [all three old firmware components](hardware-old.json) pass
readback. The [unchanged old client](old-service-rollback.json) executes as its
managed service and supplies twelve independently captured CRC/request/count
checked acknowledgements over wire 2. This does not qualify its native data:
partial source coverage remains visible on the older producer. The first probe
incorrectly expected repeated recovery events, which are transition diagnostics;
the corrected probe captures per-frame acknowledgements from the unchanged
verbose bridge. The original failed probe is retained privately.

Both new producer selections are restored with exact old-preimage checks. The
first dry-run asks about this goal's known manual rollback; the final helper
uses explicit force only after the byte-for-byte preimage comparison, preserving
both diagnostic and final logs.

At 12:30:20, Snap's [whole USB dock disconnected](usb-dock-disconnected.json),
including both display identities and other dock devices. The flash preflight
rejected the absent exact identity before a write. Dotfiles `683936d` retained the
matching old wire-2 client while the candidate stayed pinned. No hub reset or
substitute board was used. That safe-hold history and its receipts remain intact.

After the user resumed, both exact devices returned. A fresh
[read-only preflight](hardware-resume-before.json) proved all three prior wire-2
images were still byte-identical. [Final wire-3 readback](hardware-new-final.json)
then matched the first deployment's bootloader, partition table, application and
whole readback digest. Dotfiles `636a90a` activates only the matching Snap client
with the exact old-file preimage guards. The [managed service](client-final-health.json)
is active, enabled with user linger, and has zero restarts. Its
[post-window health](client-final-window-health.json) reports eleven rows, six
active/five recent, complete scope, zero uncertainty, no acknowledgement errors
and zero recorded frame-deadline misses. Data counts are snapshots, not fixed
expected roster sizes.

Final [Starship preservation](preservation-starship-final.json) verifies ten
untouched targets, seven selected producer targets and six protected unit
incarnations. Final [Snap preservation](preservation-snap-final.json) verifies six
untouched targets, eleven selected producer/client targets and five protected
unit incarnations, including 349, full/active publishers and Tmux. Both installed
package inventories/RECORD hashes still match. Starship's device/client stays on
its exact old wire-2 selection. Private wheels, full flash backup, old images,
rollback bundles, native/source evidence and original producer worktrees remain
preserved.

## Descriptive operating window

The [Snap](resource-snap-final.json) and [Starship](resource-starship-final.json)
65-second samples cover the selected systemd cgroups under normal concurrent
load. All invocations remain stable with zero restarts. Memory below is end-of-
window current / unit lifetime peak, not a unique physical/RSS sum or an admission
ledger limit.

| Host / unit | CPU, percent of one core | Current / lifetime peak, MiB |
| --- | ---: | ---: |

| snap / collector | 1.015% | 31.34 / 44.42 |
| snap / working-set publisher | 0.200% | 19.52 / 21.57 |
| snap / RLCD client | 3.688% | 32.72 / 37.40 |
| starship / collector | 1.876% | 40.82 / 56.53 |
| starship / working-set publisher | 0.000% | 19.56 / 21.22 |
| starship / RLCD client | 0.602% | 43.73 / 47.14 |

Starship's RLCD row measures its preserved old active client. Remote SSH server/
bridge processes and the native daemon outside these units are excluded; the
publisher row does not include those remote bridge processes. These observations
establish behavior for the current small view, not the producer CPU ceiling,
dense/burst capacity, inclusive 32/64 MiB physical ownership, or an RSS plateau.

The [completion audit](completion-audit.json) maps the requested outcome to its
actual evidence. The [receipt](completion.json) identifies the final active pair;
all source/configuration changes are published, with normal fast-forward Snap
checkouts. Firmware runtime remains the pinned `443f3dd`; later commits contain
only evidence/media-provenance updates.

## Acceptance boundary

This is a scoped operational adoption with installed/native comparison on these
two hosts and the exact Snap board. It is not a producer release or universal
native/resource/performance acceptance. Dense/burst/slow-peer behavior, inclusive
physical memory/RSS plateau and whole-producer CPU/cost matrices retain their
prior qualification scope. Delta remains dark with its failed/open gates.
Manual panel readability/contrast, physical unplug/replug and cold host reboot
remain separate checks. No Starship device or 349 rollout is included.

Luna implemented the cohesive consumer, parser/rendering, tests and current media
slice. The primary reviewed deadlines, added the public facade exports, verified
the immutable packages/native routes, and owns deployment, rollback and final
acceptance. Helper scripts here are frozen recipes with explicit paths and
preimage/no-overwrite guards; use a fresh scratch directory and the pinned source
helpers for replay rather than overwriting current prefixes or prior receipts.
