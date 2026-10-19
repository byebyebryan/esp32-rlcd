# Snap working-set adoption

The explicit active-plus-recent 72-hour view is implemented and its first Snap
rollout passes live device checks. Final reselection is pending a disconnected
USB dock; the device is left on the verified wire-2 rollback firmware and client. Active membership is
independent of recency; recent parked sessions use a neutral dash and the recent
clock total. Unknown runtime stays unknown. Child/system rows remain excluded.
Full-history diagnostics remain an explicit cached read, without a fallback.

## Pinned implementation

| Component | Exact selection |
| --- | --- |
| RLCD runtime | `443f3dda947ca96d68d573f2ae3ac7159d9b6f20` |
| Observer producer base | `74bc2012ef27e65dc6aad9e3ae48bd9c400d4df2` |
| Observer additive presentation facade | `1eec6c6d8681a3e58bab742d5c130656ab00433c` |
| Mesh candidate | `2fb502da35c0ef9865762c4dc4b486dd30b7e316` |
| Immutable host bundle | `d3fd7b8133f02567371cad18a14e0b45eb55d7f1ddf24bdcc867468bdbdd7808` |
| Snap application image | `b2dca61d4d2647aba0daa98c14394d23d60bfdbc6f71db103ef26c096afd28ae` |
| First deployed client configuration | dotfiles `f78d722`; current canonical client is held at wire 2 |

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
remain independent. Only Snap's client/firmware is in scope for the paired wire-3 migration. Starship's
wire-2 client selection and device are preserved.

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

At 12:30:20, Snap's [whole USB dock disconnects](usb-dock-disconnected.json),
including both display serial identities and other dock devices. The final flash
preflight rejects the absent exact RLCD identity before a write. No other board
is substituted. The matching wire-2 rollback service remains selected and enabled
while the new backend pair is ready. Canonical dotfiles `683936d` also retain
this wire-2 client and records the new wire-3 tuple in a separate staged candidate;
a routine configuration apply cannot create a protocol mismatch. Final wire-3
reselection and post-reselection health/resource verification require the exact
dock/board to return. This goal is not complete.

[Starship preservation](preservation-starship.json) verifies ten untouched managed
targets and six protected unit incarnations. [Snap preservation](preservation-snap.json)
verifies ten rollback/protected targets and five protected unit incarnations,
including 349, full/active publishers and Tmux. Both installed package inventories
and RECORD hashes still match. Snap's matching rollback client remains enabled
with user linger, and the producer/working-set selections match canonical config.
The USB disappearance is recorded as an external observation; it grants no
clearance to reset a hub, substitute another board or touch unrelated devices.

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
