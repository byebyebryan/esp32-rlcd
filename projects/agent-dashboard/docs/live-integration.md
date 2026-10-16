# Live dashboard integration

The bridge reads running Codex conversations across explicitly selected Snap and
Starship hosts through Observer's cached active feed 1 and the explicit
`agent-observer.mesh-active.v1` profile. Observer a7 applies the fixed Codex,
running/current, user/unknown-kind selector once per accepted generation before
service IPC. Mesh a23 owns delivery/proof; Observer owns native facts and scoped
coverage; this application reconciles presentation membership. Firmware owns
packet admission, expiry, layout and animation. This client performs no provider
actions. Full API 4, snapshot/watch 6, Service 4 and full Agent v3 remain available.

The configured Reader feeds public `PreparedActiveAgentWatch` through
`execute_admitted`, sharing the same `ActiveAgentProfile` instance. Active read 1
and Mesh preparation/admission 1 reuse an owned immutable replacement. Raw and
transport Client boundaries stay strict. Each device request reads independently
supported members/fields, current exact nonmembers and current scoped coverage;
raw context and informational uncertainty grant no positive or absence authority.
Complete-empty coverage expires independently of selected bodies. Reconnect
creates a new helper; gap, clock failure and failed admission revoke its cache.

Normal acquisition uses distinct source `agent_active` and local bridge socket
`mesh-plus-agent-active/read.sock`. `--roster` retains source `agent`, the full v3
profile and prepared full read 2, with complete current bodies and exclusion
reasons. There is no silent full-feed fallback for an unsupported active route.
An owned `LibraryMeshAuthority` performs fresh catalog checks with unchanged
five-second idle cadence/check budget, no route reporting and explicit close.

## Presentation policy

Confirmed children, system helpers and positively parked sessions are excluded. Current running
sessions are selected even when their historical kind is unknown. Previously
selected identities remain uncertain during loss of evidence; cold saved history
with unknown runtime is excluded. Healthy hosts remain useful when a sibling
fails. A missing host prevents an empty roster from claiming fleet completeness.
Fresh complete coverage may retire absent members only in its exact host,
provider and namespace. A new namespace cannot clear prior-scope context. This
is presentation reconciliation, not provider deletion or lifecycle management.
Partial omissions, positive expiry, producer pruning/overflow and missed expired
negatives retain existing uncertain context. There is no new hide timeout or
prior-identity query; a later fresh complete scope/current exact decision can
settle it. All reconciliation precedes the 32-row device limit.

Current blocked and known failed rows flash at 1 Hz; waiting rows remain inverse;
working rows remain normal. A current running runtime, unknown phase with
`native_runtime_error`, and current failed outcome derive an error cross. Current
working/blocked/waiting phases and a current in-progress latest turn take
precedence. This display state preserves Observer's phase vocabulary; an older
failure alone supplies no current error claim. Missing or expired evidence stays
uncertain. Groups are attention (blocked plus known failures), waiting, working,
uncertain. The `!` header counts attention.
Within healthy groups, oldest known conversation activity comes first, then
unknown activity; ties preserve previous order. This changes the synthetic
study's exact state-age policy: phase-entry time is unavailable from Observer.

Age is time since conversation activity sampled on the source, calculated from
each member's original current `runtime.observedAt` with `clock=sample`, and
shown only while activity evidence remains admitted and is no later than that
observation. The active DTO omits full snapshot publication `collectedAt`; this
is age at that row's runtime observation. Cached reads/proof emission cannot
advance it. Device/delivery clocks, thread-update times and latest-turn duration
do not replace it.
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

## Device wire 2

USB uses ASCII LF-delimited records alongside ordinary boot/diagnostic logs.
Only tagged records enter the protocol. A device request is:

```text
RLCD?2 <16 lowercase hex boot nonce> <positive request number>
```

Responses are tab-separated ASCII with this field order:

```text
RLCD!2 boot request bridge sequence host_count row_count
  [alias_hex status valid_ms attention waiting working unknown total] per host
  [identity_sha256 host_index work health valid_ms label_hex age] per row
  crc32
```

The displayed wrapping is explanatory: each response is one physical line.
CRC32 covers every byte before the final tab/checksum. Text fields encode UTF-8
bytes as lowercase hex. Ages are `?`, `+++` or a bounded number with s/m/h/d.
Work codes use the existing C enum: 0 working, 1 blocked, 2 waiting, 4 derived error, 5 unknown.
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
Each row is additionally bounded by its own currently supported field deadlines.
An expired history field is masked without discarding supported runtime membership.
Device expiry is anchored to request-send time, not response-receive time;
transport latency therefore shortens authority. Accepted timing assumes normal
monotonic-clock rate over this short bound; the margin and delayed-response
checks are independently tested. Repeated delivery, reconnect, a carrier
heartbeat and a different component cannot renew native evidence.

Firmware checks expiry without needing another packet. Expired hosts retain
labels but lose work, ages and flashing; healthy siblings retain their rows.
If all hosts are unavailable, motion settles to its accepted target geometry.
The host's retained uncertainty cache is bounded and never grants native facts.

The host retains minimal membership metadata for the full selected roster,
bounded to 65,535 identities per host, independently of the 32-row transport
prefix. A partial omission preserves uncertain membership and counts. Positive
child/system/parked evidence removes membership, including identities outside
the transport prefix; accepted complete omission can retire display membership.
Capacity failure is explicit rather than a silent loss of whole-roster counts.
The preceding retention refinement preserved wire 1. Wire 2 adds code 4 to live
admission and counts it in the attention group.

The bridge supervises its subscription and serial workers. Expected source loss
uses bounded retry and lease revocation. Unexpected worker exit/cleanup failure
fails the owner after a bounded cleanup grace. Missing/busy hardware is retried;
hangup closes the descriptor and clears framing before a fresh serial incarnation.
The Starship user service runs a verified installed host bundle and owns startup,
restart and stop. These are application lifecycle responsibilities.

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
The application user service is independently selected; provider configuration
and global system services remain external.

Producer reference: the sibling Agent Observer repository's `docs/api-v4.md`
and `docs/evidence/2026-10-13-system-classification/REPORT.md`. These local source
checkpoints and installed artifacts have separate publication status.

Wire 1 and wire 2 tags are mutually rejected. Rollback requires selecting the
retained matching bridge and firmware pair. The active-feed host migration keeps
wire 2 and firmware unchanged, but rollback must restore its paired collector,
active publisher/source routing and client selections. Tmux, 349, ordinary native
sessions and historical writer remain independent. See the
[active-feed acceptance](../../../docs/evidence/2026-10-16-active-feed/REPORT.md).
