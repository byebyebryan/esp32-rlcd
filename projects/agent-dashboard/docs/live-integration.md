# Live dashboard integration

The first live version reads running Codex sessions across explicitly selected
Snap and Starship hosts through Observer API 4, snapshot/watch 6, Service 4,
Mesh SDK 1 and the explicit `agent-observer.mesh-candidate.v3` profile. The
bridge belongs to this application. Observer remains the observation authority;
Mesh remains the delivery/proof authority. Firmware owns display admission,
expiry, layout and animation. This client performs no provider actions.

## Presentation policy

Confirmed children, system helpers and positively parked sessions are excluded. Current running
sessions are selected even when their historical kind is unknown. Previously
selected identities remain uncertain during loss of evidence; cold saved history
with unknown runtime is excluded. Healthy hosts remain useful when a sibling
fails. A missing host prevents an empty roster from claiming fleet completeness.
An accepted complete inventory may retire omitted display membership; that is
not a provider-session deletion or lifecycle assertion. Partial inventories do
not supply that exclusion.

Current blocked rows flash at 1 Hz; waiting rows remain inverse; working rows
remain normal. Outcome failure/cancellation does not determine current phase.
Uncertain rows lose work styling. Groups are blocked, waiting, working, uncertain.
Within healthy groups, oldest known conversation activity comes first, then
unknown activity; ties preserve previous order. This changes the synthetic
study's exact state-age policy: phase-entry time is unavailable from Observer.

Age is time since conversation activity sampled on the source, calculated from
the source snapshot's `collectedAt`, and shown only while its evidence remains
admitted. It advances only on accepted source views. Device time, delivery time,
native thread updates and latest-turn duration do not replace that clock.
Missing, future or expired activity displays `?`.

Rows retain full Observer identity in the bridge. SHA-256 tokens of its canonical
identity key fit firmware's bounded identity storage; collisions reject the view.
Labels prefer a useful conversation title. Blank titles and the exact generated
`Codex <native ID>` placeholder fall back to current repository metadata, then
cwd, then a bounded identity label. Duplicate rendered titles use distinguishable
project context before short identity suffixes. Renames preserve row identity.
Positively reclassified system rows are also removed from retained context.
The host `--roster` diagnostic maps labels to complete native identities and
explains selection, sampled ages, device capacity and visible membership. Host badges ST/SN replace the redundant CX column.
Labels are sanitized UTF-8; suffixes disambiguate labels at their rendered width.

The bridge orders the complete selected roster, reports whole-roster totals,
and sends at most 32 rows. Eleven complete rows fit the display; overflow includes
rows beyond both the display and device capacity. Counts are qualified per host.
Partial delivery has a visible PARTIAL header; whole-feed loss has an OFFLINE
header and retained identity/layout context. Counts from expired hosts become
uncertain context, never cached blocked/waiting/working claims.

## Device wire 1

USB uses ASCII LF-delimited records alongside ordinary boot/diagnostic logs.
Only tagged records enter the protocol. A device request is:

```text
RLCD?1 <16 lowercase hex boot nonce> <positive request number>
```

Responses are tab-separated ASCII with this field order:

```text
RLCD!1 boot request bridge sequence host_count row_count
  [alias_hex status valid_ms blocked waiting working unknown total] per host
  [identity_sha256 host_index work health valid_ms label_hex age] per row
  crc32
```

The displayed wrapping is explanatory: each response is one physical line.
CRC32 covers every byte before the final tab/checksum. Text fields encode UTF-8
bytes as lowercase hex. Ages are `?`, `+++` or a bounded number with s/m/h/d.
Work codes use the existing C enum: 0 working, 1 blocked, 2 waiting, 5 unknown.
Health codes are 0 current, 1 stale, 2 unavailable, 3 ambiguous, 4 unsupported.
Host status is 0 current, 1 partial, 2 offline, 3 warming.

Limits are 16 KiB per response, 32 rows, two configured hosts, 63 UTF-8 label
bytes, two-byte ASCII host badges, and 65,535 selected identities per host.
All fields, counts, enums, encodings, duplicate identities and checksum must
validate before mutation. Truncated, excessive or malformed lines are discarded.

The device requests its latest view every second. A response must match the
current boot/request and arrive within that request's one-second window. Each
request is consumable once. A bridge restart changes its random incarnation;
sequence must increase within an incarnation. Every view is a replacement.

The bridge rechecks Mesh admission on each request. Current validity is capped
at three seconds and reduced by 100 ms from the remaining required source lease.
All current rows from one host share that host's conservative minimum lease.
Device expiry is anchored to request-send time, not response-receive time;
transport latency therefore shortens authority. Accepted timing assumes normal
monotonic-clock rate over this short bound; the margin and delayed-response
checks are independently tested. Repeated delivery, reconnect, a carrier
heartbeat and a different component cannot renew native evidence.

Firmware checks expiry without needing another packet. Expired hosts retain
labels but lose work, ages and flashing; healthy siblings retain their rows.
If all hosts are unavailable, motion settles to its accepted target geometry.
The host's retained uncertainty cache is bounded and never grants native facts.

## Execution and acceptance

1. Record policy/wire and deterministic projection/admission checks.
2. Implement one SDK subscription, pure projection and a native render path.
   Review live labels, source-sampled ages, ordering and capacity.
3. Exercise USB fragmentation, checksum/bounds failures, delayed/duplicate
   delivery, silence, source expiry and new bridge/device incarnations.
4. Build the live firmware and retain the synthetic modes as explicit studies.
5. Identify the RLCD, back up its full flash, flash/read back, and compare its
   admitted roster with the bridge. Verify loss/recovery independently.

Native previews and serial/readback evidence do not establish physical
readability. Deployment/resource/visual acceptance are recorded separately.
No global services or provider configuration are changed by this integration.

Producer reference: the sibling Agent Observer repository's `docs/api-v4.md`
and `docs/evidence/2026-10-13-system-classification/REPORT.md`. These local source
checkpoints and installed artifacts have separate publication status.
